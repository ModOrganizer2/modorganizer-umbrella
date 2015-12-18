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
from unibuild.modules import github, cmake, patch, git, hg, msbuild, build
from unibuild.utility import lazy, FormatDict
from config import config
from functools import partial
from string import Formatter
import os


"""
Settings
"""

loot_version = "v0.8.0"


"""
Projects
"""


from unibuild.projects import sevenzip, qt5, boost, zlib, python, sip, pyqt5


Project("LootApi") \
    .depend(patch.Copy("loot32.dll", os.path.join(config['__build_base_path'], "install", "bin", "loot"))
            .depend(github.Release("loot", "loot", loot_version, "LOOT.API.{}".format(loot_version), "7z")
                    .set_destination("lootapi"))
            )

tl_repo = git.SuperRepository("modorganizer_super")


# install compiled mo components

""" doesn't build through msbuild but builds fine in IDE??
.depend(msbuild.MSBuild("../nmm/NexusClient.sln", "NexusClientCli",
                        working_directory=lazy.Evaluate(lambda: os.path.join(ncc['build_path'], "..", "nmm")))
"""
ncc = Project("NCC") \
    .depend(build.Run("powershell .\\publish.ps1 {0} -outputPath {1}"
                      .format("-debug" if config['build_type'] == "Debug" else "-release",
                              os.path.join(config['__build_base_path'], "install", "bin")),
                      working_directory=lazy.Evaluate(lambda: ncc['build_path']))
            .depend(patch.Copy("NexusClient.sln", "../nmm/NexusClient.sln")
                    .depend(github.Source("TanninOne", "modorganizer-NCC", "master")
                            .set_destination(os.path.join("NCC", "NexusClientCli"))
                            .depend(hg.Clone("http://hg.code.sf.net/p/nexusmodmanager/codehgdev45")
                                    .set_destination(os.path.join("NCC", "nmm"))
                                    )
                            )
                    )
            )
#            )

Project("modorganizer-game_features") \
    .depend(github.Source("TanninOne", "modorganizer-game_features", "master", super_repository=tl_repo)
            .set_destination("game_features"))

for git_path, path, branch, dependencies in [
    ("modorganizer-archive",           "archive",           "master",          ["7zip", "Qt5"]),
    ("modorganizer-uibase",            "uibase",            "master",          ["Qt5", "boost"]),
    ("modorganizer-lootcli",           "lootcli",           "master",          ["LootApi", "Qt5", "boost"]),
    ("modorganizer-esptk",             "esptk",             "master",          ["boost"]),
    ("modorganizer-bsatk",             "bsatk",             "master",          ["zlib"]),
    ("modorganizer-nxmhandler",        "nxmhandler",        "master",          ["Qt5"]),
    ("modorganizer-helper",            "helper",            "master",          ["Qt5"]),
    ("modorganizer-game_gamebryo",     "game_gamebryo",     "new_vfs_library", ["Qt5", "modorganizer-uibase",
                                                                                "modorganizer-game_features"]),
    ("modorganizer-game_oblivion",     "game_oblivion",     "master",          ["Qt5", "modorganizer-uibase",
                                                                                "modorganizer-game_gamebryo",
                                                                                "modorganizer-game_features"]),
    ("modorganizer-game_fallout3",     "game_fallout3",     "master",          ["Qt5", "modorganizer-uibase",
                                                                                "modorganizer-game_gamebryo",
                                                                                "modorganizer-game_features"]),
    ("modorganizer-game_fallout4",     "game_fallout4",     "master",          ["Qt5", "modorganizer-uibase",
                                                                                "modorganizer-game_gamebryo",
                                                                                "modorganizer-game_features"]),
    ("modorganizer-game_falloutnv",    "game_falloutnv",    "master",          ["Qt5", "modorganizer-uibase",
                                                                                "modorganizer-game_gamebryo",
                                                                                "modorganizer-game_features"]),
    ("modorganizer-game_skyrim",       "game_skyrim",       "master",          ["Qt5", "modorganizer-uibase",
                                                                                "modorganizer-game_gamebryo",
                                                                                "modorganizer-game_features"]),
    ("modorganizer-tool_inieditor",    "tool_inieditor",    "master",          ["Qt5", "modorganizer-uibase"]),
    ("modorganizer-tool_inibakery",    "tool_inibakery",    "master",          ["modorganizer-uibase"]),
    ("modorganizer-tool_configurator", "tool_configurator", "master",          ["PyQt5"]),
    ("modorganizer-preview_base",      "preview_base",      "master",          ["Qt5", "modorganizer-uibase"]),
    ("modorganizer-diagnose_basic",    "diagnose_basic",    "master",          ["Qt5", "modorganizer-uibase"]),
    ("modorganizer-check_fnis",        "check_fnis",        "master",          ["Qt5", "modorganizer-uibase"]),
    ("modorganizer-installer_bain",    "installer_bain",    "master",          ["Qt5", "modorganizer-uibase"]),
    ("modorganizer-installer_manual",  "installer_manual",  "master",          ["Qt5", "modorganizer-uibase"]),
    ("modorganizer-installer_bundle",  "installer_bundle",  "master",          ["Qt5", "modorganizer-uibase"]),
    ("modorganizer-installer_quick",   "installer_quick",   "master",          ["Qt5", "modorganizer-uibase"]),
    ("modorganizer-installer_fomod",   "installer_fomod",   "master",          ["Qt5", "modorganizer-uibase"]),
    ("modorganizer-installer_ncc",     "installer_ncc",     "master",          ["Qt5", "modorganizer-uibase", "NCC"]),
    ("modorganizer-bsa_extractor",     "bsa_extractor",     "master",          ["Qt5", "modorganizer-uibase"]),
    ("modorganizer-plugin_python",     "plugin_python",     "master",          ["Qt5", "boost", "Python", "modorganizer-uibase",
                                                                                "sip"]),
    ("modorganizer",                   "modorganizer",      "new_vfs_library", ["Qt5", "boost",
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

    build_step.depend(github.Source("TanninOne", git_path, branch, super_repository=tl_repo)
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
