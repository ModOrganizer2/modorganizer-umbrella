# Copyright (C) 2015 Sebastian Herbord. All rights reserved.
#
# This file is part of Mod Organizer.
#
# Mod Organizer is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Mod Organizer is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Mod Organizer.  If not, see <http://www.gnu.org/licenses/>.


from unibuild import Project
from unibuild.modules import github, cmake, patch, git
from unibuild.utility import lazy, FormatDict
from config import config
from functools import partial
from string import Formatter
import os


"""
Settings
"""

modorganizer_branch = "master"

loot_version = "v0.8.0"


"""
Projects
"""


from unibuild.projects import sevenzip, qt5, boost, zlib, python, sip


Project("LootApi") \
    .depend(github.Release("loot", "loot", loot_version, "LOOT.API.{}".format(loot_version), "7z")
            .set_destination("lootapi"))

tl_repo = git.SuperRepository("modorganizer_super")

Project("modorganizer-game_features") \
    .depend(github.Source("TanninOne", "modorganizer-game_features", modorganizer_branch, super_repository=tl_repo)
            .set_destination("game_features"))

for git_path, path, dependencies in [
    ("modorganizer-archive",          "archive",                 ["7zip", "Qt5"]),
    ("modorganizer-uibase",           "uibase",                  ["Qt5", "boost"]),
    ("modorganizer-lootcli",          "lootcli",                 ["LootApi", "Qt5", "boost"]),
    ("modorganizer-esptk",            "esptk",                   ["boost"]),
    ("modorganizer-bsatk",            "bsatk",                   ["zlib"]),
    ("modorganizer-nxmhandler",       "nxmhandler",              ["Qt5"]),
    ("modorganizer-helper",           "helper",                  ["Qt5"]),
    ("modorganizer-game_gamebryo",    "game_gamebryo",    ["Qt5", "modorganizer-uibase",
                                                                  "modorganizer-game_features"]),
    ("modorganizer-game_oblivion",    "game_oblivion",    ["Qt5", "modorganizer-uibase",
                                                                  "modorganizer-game_gamebryo",
                                                                  "modorganizer-game_features"]),
    ("modorganizer-game_fallout3",    "game_fallout3",    ["Qt5", "modorganizer-uibase",
                                                                  "modorganizer-game_gamebryo",
                                                                  "modorganizer-game_features"]),
    ("modorganizer-game_falloutnv",   "game_falloutnv",   ["Qt5", "modorganizer-uibase",
                                                                  "modorganizer-game_gamebryo",
                                                                  "modorganizer-game_features"]),
    ("modorganizer-game_skyrim",      "game_skyrim",      ["Qt5", "modorganizer-uibase",
                                                                  "modorganizer-game_gamebryo",
                                                                  "modorganizer-game_features"]),
    ("modorganizer-tool_nmmimport",   "tool_nmmimport",   ["Qt5", "modorganizer-uibase",
                                                                  "modorganizer-archive"]),
    ("modorganizer-tool_inieditor",   "tool_inieditor",   ["Qt5", "modorganizer-uibase"]),
    ("modorganizer-preview_base",     "preview_base",     ["Qt5", "modorganizer-uibase"]),
    ("modorganizer-diagnose_basic",   "diagnose_basic",   ["Qt5", "modorganizer-uibase"]),
    ("modorganizer-check_fnis",       "check_fnis",       ["Qt5", "modorganizer-uibase"]),
    ("modorganizer-installer_bain",   "installer_bain",   ["Qt5", "modorganizer-uibase"]),
    ("modorganizer-installer_manual", "installer_manual", ["Qt5", "modorganizer-uibase"]),
    ("modorganizer-installer_bundle", "installer_bundle", ["Qt5", "modorganizer-uibase"]),
    ("modorganizer-installer_quick",  "installer_quick",  ["Qt5", "modorganizer-uibase"]),
    ("modorganizer-installer_fomod",  "installer_fomod",  ["Qt5", "modorganizer-uibase"]),
    ("modorganizer-plugin_python",    "plugin_python",    ["Qt5", "boost", "Python", "modorganizer-uibase",
                                                                  "sip"]),
    ("modorganizer",                  "modorganizer",            ["Qt5", "boost",
                                                                  "modorganizer-uibase", "modorganizer-archive",
                                                                  "modorganizer-bsatk", "modorganizer-esptk",
                                                                  "modorganizer-game_features"]),
]:
    build_step = cmake.CMake().arguments(
        [
            "-DCMAKE_BUILD_TYPE={}".format(config["build_type"]),
            "-DDEPENDENCIES_DIR={}/build".format(config["__build_base_path"]),
            "-DCMAKE_INSTALL_PREFIX:PATH={}/install".format(config["__build_base_path"])
        ]
    ).install()

    for dep in dependencies:
        build_step.depend(dep)

    build_step.depend(github.Source("TanninOne", git_path, modorganizer_branch, super_repository=tl_repo)
                      .set_destination(path))

    project = Project(git_path)

    if config['ide_projects']:
        def gen_userfile_content(project):
            with open("CMakeLists.txt.user.template", 'r') as f:
                res = Formatter().vformat(f.read(), [], FormatDict({'build_dir': project['edit_path']}))
                return res

        project.depend(
            patch.CreateFile("CMakeLists.txt.user", lazy.Evaluate(partial(gen_userfile_content, project))).depend(
                cmake.CMakeEdit(cmake.CMakeEdit.Type.CodeBlocks).arguments(
                    [
                        "-DCMAKE_BUILD_TYPE={}".format(config["build_type"]),
                        "-DDEPENDENCIES_DIR={}/build".format(config["__build_base_path"]),
                        "-DCMAKE_INSTALL_PREFIX:PATH={}/install".format(config['__build_base_path'].replace('\\', '/'))
                    ]
                ).depend(
                    build_step
                )
            )
        )
    else:
        project.depend(build_step)

