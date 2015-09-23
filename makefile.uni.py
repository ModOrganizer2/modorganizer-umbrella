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
from unibuild.modules import github, cmake
from config import config


"""
Settings
"""

config["build_type"] = "RelWithDebInfo"
modorganizer_branch = "master"

loot_version = "v0.8.0"


"""
Projects
"""


from unibuild.projects import sevenzip, qt5, boost, zlib


Project("Spdlog") \
    .depend(github.Source("gabime", "spdlog", "master"))

Project("CppFormat") \
    .depend(github.Source("cppformat", "cppformat", "master"))

Project("LootApi") \
    .depend(github.Release("loot", "loot", loot_version, "LOOT.API.{}".format(loot_version), "7z")
            .set_destination("lootapi"))


for git_path, path, install, dependencies in [
    ("modorganizer-archive",          "archive",                 True,  ["7zip"]),
    ("modorganizer-uibase",           "uibase",                  True,  ["Qt5", "boost"]),
    ("modorganizer-lootcli",          "lootcli",                 True,  ["LootApi", "Qt5", "boost"]),
    ("modorganizer-esptk",            "esptk",                   False, ["boost"]),
    ("modorganizer-bsatk",            "bsatk",                   False, ["zlib"]),
    ("modorganizer-nxmhandler",       "nxmhandler",              True,  ["Qt5"]),
    ("modorganizer-python_runner",    "python_runner",           True,  ["boost"]),
    ("modorganizer-game_features",    "plugin/game_features",    False, ["Qt5", "modorganizer-uibase"]),
    ("modorganizer-game_gamebryo",    "plugin/game_gamebryo",    False, ["Qt5", "modorganizer-uibase",
                                                                         "modorganizer-game_features"]),
    ("modorganizer-game_skyrim",      "plugin/game_skyrim",      True,  ["Qt5", "modorganizer-uibase",
                                                                         "modorganizer-game_gamebryo",
                                                                         "modorganizer-game_features"]),
    ("modorganizer-tool_nmmimport",   "plugin/tool_nmmimport",   True,  ["Qt5", "modorganizer-uibase",
                                                                         "modorganizer-archive"]),
    ("modorganizer-tool_inieditor",   "plugin/tool_inieditor",   True,  ["Qt5", "modorganizer-uibase"]),
#    ("modorganizer-preview_dds",      "plugin/preview_dds",      True,  ["Qt5", "modorganizer-uibase"]),
    ("modorganizer-preview_base",     "plugin/preview_base",     True,  ["Qt5", "modorganizer-uibase"]),
    ("modorganizer-diagnose_basic",   "plugin/diagnose_basic",   True,  ["Qt5", "modorganizer-uibase"]),
    ("modorganizer-check_fnis",       "plugin/check_fnis",       True,  ["Qt5", "modorganizer-uibase"]),
    ("modorganizer-installer_bain",   "plugin/installer_bain",   True,  ["Qt5", "modorganizer-uibase"]),
    ("modorganizer-installer_manual", "plugin/installer_manual", True,  ["Qt5", "modorganizer-uibase"]),
    ("modorganizer-installer_bundle", "plugin/installer_bundle", True,  ["Qt5", "modorganizer-uibase"]),
    ("modorganizer-installer_quick",  "plugin/installer_quick",  True,  ["Qt5", "modorganizer-uibase"]),
    ("modorganizer-installer_fomod",  "plugin/installer_fomod",  True,  ["Qt5", "modorganizer-uibase"]),
    ("modorganizer-plugin_python",    "plugin/plugin_python",    True,  ["Qt5", "boost", "modorganizer-uibase"]),
    ("modorganizer",                  "modorganizer",            True,  ["Qt5", "boost",
                                                                         "modorganizer-uibase", "modorganizer-archive",
                                                                         "modorganizer-bsatk", "modorganizer-esptk",
                                                                         "modorganizer-game_features"]),
]:
    build_step = cmake.CMake().arguments([
                                         "-DCMAKE_BUILD_TYPE={}".format(config["build_type"]),
                                         "-DDEPENDENCIES_DIR={}/build".format(config["__build_base_path"]),
                                         "-DCMAKE_INSTALL_PREFIX:PATH={}/install".format(config["__build_base_path"])
                                         ])
    for dep in dependencies:
        build_step.depend(dep)

    if install:
        build_step.install()

    Project(git_path)\
        .depend(build_step
                .depend(github.Source("TanninOne", git_path, modorganizer_branch)
                        .set_destination(path))
                )
