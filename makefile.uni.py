# Copyright (C) 2015 Sebastian Herbord.  All rights reserved.
# Copyright (C) 2016 - 2018 Mod Organizer contributors.
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
from unibuild.modules import github, cmake, Patch, git, hg, msbuild, build, dummy, urldownload
from unibuild.projects import sevenzip, qt5, boost, zlib, python, sip, pyqt5, ncc, nasm, openssl, googletest, lz4, WixToolkit
from unibuild.utility import lazy, FormatDict
from config import config
from functools import partial
from string import Formatter
import os
import sys

loot_version = "0.12.4"
commit_id = "gec946b5"

# TODO modorganizer-lootcli needs an overhaul as the api has changed alot
def bitness():
    return "x64" if config['architecture'] == "x86_64" else "Win32"

def bitnessLoot():
    return "64" if config['architecture'] == "x86_64" else "32"

Project("LootApi") \
    .depend(Patch.Copy("loot_api.dll", os.path.join(config["paths"]["install"], "bin", "loot"))
        .depend(github.Release("loot", "loot-api", config['loot_version'],
                               "loot_api-{}-0-{}_update-deps-win{}".format(config['loot_version'], config['loot_commit'], bitnessLoot()), "7z", tree_depth=1)
                .set_destination("lootapi")))

tl_repo = git.SuperRepository("modorganizer_super")

def gen_userfile_content(project):
    with open("CMakeLists.txt.user.template", 'r') as f:
        res = Formatter().vformat(f.read(), [], FormatDict({
            'build_dir': project['edit_path'],
            'environment_id': config['qt_environment_id'],
            'profile_name': config['qt_profile_name'],
            'profile_id': config['qt_profile_id']
        }))
        return res


cmake_parameters = ["-DCMAKE_BUILD_TYPE={}".format(config["build_type"]),
    "-DDEPENDENCIES_DIR={}".format(config["paths"]["build"]),
    #	boost git version "-DBOOST_ROOT={}/build/boostgit",
    "-DBOOST_ROOT={}/boost_{}".format(config["paths"]["build"], config["boost_version"].replace(".", "_")),
    "-DQT_ROOT={}".format(qt5.qt_inst_path)]

if config.get('optimize', False):
    cmake_parameters.append("-DOPTIMIZE_LINK_FLAGS=\"/LTCG /INCREMENTAL:NO /OPT:REF /OPT:ICF\"")

usvfs = Project("usvfs")

suffix_32 = "" if config['architecture'] == 'x86_64' else "_32"
for (project32, dependencies) in [("boost", ["boost_prepare"]),
      ("GTest", []),
      ("usvfs", [])]:
  if config['architecture'] == 'x86_64':
    unimake32 = \
      build.Run_With_Output(r'"{0}" unimake.py -d "{1}" --set architecture="x86" -b "build" -p "progress" -i "install" {2}'.format(sys.executable, config['__build_base_path'], project32),
        name="unimake_x86_{}".format(project32),
        environment=config['__Default_environment'],
        working_directory=os.path.join(os.getcwd()))
    for dep in dependencies:
        unimake32.depend(dep)
    Project(project32 + "_32").depend(unimake32)
  else:
    Project(project32 + "_32").dummy().depend(project32)

# usvfs build:
vs_target = "Clean;Build" if config['rebuild'] else "Build"
usvfs_build = \
    msbuild.MSBuild("usvfs.sln", vs_target,
                    os.path.join(config["paths"]["build"], "usvfs", "vsbuild"),
                    "x64" if config['architecture'] == 'x86_64' else "x86")
usvfs_build.depend(github.Source(config['Main_Author'], "usvfs", "0.3.1.0-Beta")
    .set_destination("usvfs"))
usvfs_build.depend("boost" + suffix_32)
usvfs_build.depend("GTest" + suffix_32)
usvfs.depend(usvfs_build)

for author, git_path, path, branch, dependencies, Build in [(config['Main_Author'], "modorganizer-game_features", "game_features", "master", [], False),
    (config['Main_Author'], "modorganizer-archive", "archive", "API_9.20", ["7zip", "Qt5", "boost"], True),
    (config['Main_Author'], "modorganizer-uibase", "uibase", "QT5.7", ["Qt5", "boost"], True),
    (config['Main_Author'], "modorganizer-lootcli", "lootcli", "master", ["LootApi", "boost"], True),
    (config['Main_Author'], "modorganizer-esptk", "esptk", "master", ["boost"], True),
    (config['Main_Author'], "modorganizer-bsatk", "bsatk", "master", ["zlib", "boost"], True),
    (config['Main_Author'], "modorganizer-nxmhandler", "nxmhandler", "master", ["Qt5", "modorganizer-uibase"], True),
    (config['Main_Author'], "modorganizer-helper", "helper", "master", ["Qt5","boost"], True),
    (config['Main_Author'], "modorganizer-game_gamebryo", "game_gamebryo", "new_vfs_library",
     ["Qt5", "modorganizer-uibase",
      "modorganizer-game_features", "lz4"], True),
    (config['Main_Author'], "modorganizer-game_oblivion", "game_oblivion", "master", ["Qt5", "modorganizer-uibase",
                                                                                      "modorganizer-game_gamebryo",
                                                                                      "modorganizer-game_features"],
     True),
    (config['Main_Author'], "modorganizer-game_fallout3", "game_fallout3", "master", ["Qt5", "modorganizer-uibase",
                                                                                      "modorganizer-game_gamebryo",
                                                                                      "modorganizer-game_features"],
     True),
    (config['Main_Author'], "modorganizer-game_fallout4", "game_fallout4", "master", ["Qt5", "modorganizer-uibase",
                                                                                      "modorganizer-game_gamebryo",
                                                                                      "modorganizer-game_features"],
     True),
    (config['Main_Author'], "modorganizer-game_fallout4vr", "game_fallout4vr", "master", ["Qt5", "modorganizer-uibase",
                                                                                      "modorganizer-game_gamebryo",
                                                                                      "modorganizer-game_features"],
     True),
    (config['Main_Author'], "modorganizer-game_falloutnv", "game_falloutnv", "master", ["Qt5", "modorganizer-uibase",
                                                                                        "modorganizer-game_gamebryo",
                                                                                        "modorganizer-game_features"],
     True),
    (config['Main_Author'], "modorganizer-game_skyrim", "game_skyrim", "master", ["Qt5", "modorganizer-uibase",
                                                                                  "modorganizer-game_gamebryo",
                                                                                  "modorganizer-game_features"], True),
    (config['Main_Author'], "modorganizer-game_skyrimSE", "game_skyrimse", "dev", ["Qt5", "modorganizer-uibase",
                                                                            "modorganizer-game_gamebryo",
                                                                            "modorganizer-game_features"], True),
    (config['Main_Author'], "modorganizer-tool_inieditor", "tool_inieditor", "master", ["Qt5", "modorganizer-uibase"],
     True),
    (config['Main_Author'], "modorganizer-tool_inibakery", "tool_inibakery", "master", ["modorganizer-uibase"], True),
    (config['Main_Author'], "modorganizer-tool_configurator", "tool_configurator", "QT5.7", ["PyQt5"], True),
    (config['Main_Author'], "modorganizer-preview_base", "preview_base", "master", ["Qt5", "modorganizer-uibase"], True),
    (config['Main_Author'], "modorganizer-diagnose_basic", "diagnose_basic", "master", ["Qt5", "modorganizer-uibase"],
     True),
    (config['Main_Author'], "modorganizer-check_fnis", "check_fnis", "master", ["Qt5", "modorganizer-uibase"], True),
    (config['Main_Author'], "modorganizer-installer_bain", "installer_bain", "QT5.7", ["Qt5", "modorganizer-uibase"],
     True),
    (config['Main_Author'], "modorganizer-installer_manual", "installer_manual", "QT5.7", ["Qt5", "modorganizer-uibase"],
    True),
    (config['Main_Author'], "modorganizer-installer_bundle", "installer_bundle", "master",
     ["Qt5", "modorganizer-uibase"], True),
    (config['Main_Author'], "modorganizer-installer_quick", "installer_quick", "master", ["Qt5", "modorganizer-uibase"],
     True),
    (config['Main_Author'], "modorganizer-installer_fomod", "installer_fomod", "master", ["Qt5", "modorganizer-uibase"],
     True),
    (config['Main_Author'], "modorganizer-installer_ncc", "installer_ncc", "master",
     ["Qt5", "modorganizer-uibase", "NCC"], True),
    (config['Main_Author'], "modorganizer-bsa_extractor", "bsa_extractor", "master", ["Qt5", "modorganizer-uibase"],
     True),
    (config['Main_Author'], "modorganizer-plugin_python", "plugin_python", "master",
     ["Qt5", "boost", "Python", "modorganizer-uibase",
      "sip"], True),
    (config['Main_Author'], "githubpp", "githubpp", "master", ["Qt5"], True),
    (config['Main_Author'], "modorganizer", "modorganizer", "new_vfs_library", ["Qt5", "boost", "usvfs_32",
                                                                      "modorganizer-uibase", "modorganizer-archive",
                                                                      "modorganizer-bsatk", "modorganizer-esptk",
                                                                      "modorganizer-game_features",
                                                                      "usvfs", "githubpp", "NCC", "openssl"], True),]:
    build_step = cmake.CMake().arguments(cmake_parameters + ["-DCMAKE_INSTALL_PREFIX:PATH={}".format(config["paths"]["install"])]) \
        .install()

    for dep in dependencies:
        build_step.depend(dep)

    project = Project(git_path)

    if Build:
        vs_step = cmake.CMakeVS().arguments(cmake_parameters + ["-DCMAKE_INSTALL_PREFIX:PATH={}".format(config["paths"]["install"])]) \
            .install()

        for dep in dependencies:
            vs_step.depend(dep)

        project.depend(vs_step.depend(github.Source(author, git_path, branch, super_repository=tl_repo)
                                         .set_destination(path)))
    else:
        project.depend(github.Source(author, git_path, branch, super_repository=tl_repo)
                       .set_destination(path))


def python_zip_collect(context):
    import libpatterns
    import glob
    from zipfile import ZipFile

    ip = os.path.join(config["paths"]["install"], "bin")
    bp = python.python['build_path']

    with ZipFile(os.path.join(ip, "python27.zip"), "w") as pyzip:
        for pattern in libpatterns.patterns:
            for f in glob.iglob(os.path.join(bp, pattern)):
                pyzip.write(f, f[len(bp):])

    return True


Project("python_zip") \
    .depend(build.Execute(python_zip_collect)
            .depend("Python"))

if config['Installer']:
    # build_installer = cmake.CMake().arguments(cmake_parameters
    # +["-DCMAKE_INSTALL_PREFIX:PATH={}/installer".format(config["__build_base_path"])]).install()
    wixinstaller = Project("WixInstaller")

    wixinstaller.depend(github.Source(config['Main_Author'], "modorganizer-WixInstaller", "VSDev", super_repository=tl_repo)
        .set_destination("WixInstaller")) \
        .depend("modorganizer").depend("usvfs").depend("usvfs_32")
