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
import logging
import os.path
import sys


program_files_folders = [os.environ['ProgramFiles(x86)'],
    os.environ['ProgramFiles'],
    os.environ['ProgramW6432'],
    "C:\\",
    "D:\\"]

def qt_inst_path():
    from config import config
    if config['binary_qt']:
        qt_inst_path = config["paths"]["qt_binary_install"]
    else:
        qt_inst_path = "{}/qt5".format(build_path).replace("/", os.path.sep)
    return qt_inst_path

def cmake_parameters():
    from config import config

    paths_build = config['paths']['build']

    cmake_parameters = ["-DCMAKE_BUILD_TYPE={}".format(config["build_type"]),
                        "-DDEPENDENCIES_DIR={}".format(paths_build),
                        "-DBOOST_ROOT={}/boost_{}".format(paths_build, config["boost_version"]),
                        "-DLOOT_API_PATH={}/lootapi-{}-{}".format(paths_build, config["loot_version"], config["loot_commit"]),
                        "-DLZ4_ROOT={}/lz4-{}".format(paths_build, config["lz4_version"]),
                        "-DQT_ROOT={}".format(qt_inst_path()),
                        "-DZLIB_ROOT={}/zlib-{}".format(paths_build, config["zlib_version"])]

    if config.get('optimize', False):
        cmake_parameters.append("-DOPTIMIZE_LINK_FLAGS=\"/LTCG /INCREMENTAL:NO /OPT:REF /OPT:ICF\"")
    return cmake_parameters

def bitness():
    from config import config
    return "x64" if config['architecture'] == "x86_64" else "Win32"


def get_from_hklm(path, name, wow64=False):
    from _winreg import QueryValueEx, OpenKey, HKEY_LOCAL_MACHINE, KEY_READ, KEY_WOW64_32KEY
    flags = KEY_READ
    if wow64:
        flags |= KEY_WOW64_32KEY

    # avoids crashing if a product is not present
    try:
        with OpenKey(HKEY_LOCAL_MACHINE, path, 0, flags) as key:
            return QueryValueEx(key, name)[0]
    except Exception:
        return None
