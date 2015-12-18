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


from _winreg import *
from unibuild.utility.lazy import Evaluate
import os


def path_or_default(filename, defaults):
    from distutils.spawn import find_executable
    return find_executable(filename, os.environ['PATH'] + ";" + ";".join(defaults))


def get_from_hklm(path, name, wow64=False):
    flags = KEY_READ
    if wow64:
        flags |= KEY_WOW64_32KEY

    with OpenKey(HKEY_LOCAL_MACHINE, path, 0, flags) as key:
        return QueryValueEx(key, name)[0]


program_files_folders = [
    os.environ['ProgramFiles(x86)'],
    os.environ['ProgramFiles'],
    "D:\\"
]


def gen_search_folders(*subpath):
    return [
        os.path.join(search_folder, *subpath)
        for search_folder in program_files_folders
    ]

config = {
    'tools': {
        'make': "nmake",
    },
    'architecture': 'x86_64',
    'vc_version':   '12.0',
    'build_type': "RelWithDebInfo",
    'ide_projects': True,
    'repo_update_frequency': 60 * 60 * 24,  # in seconds
    'prefer_binary_dependencies': False # currently non-functional
}

config['paths'] = {
    'download':      "{base_dir}\\downloads",
    'build':         "{base_dir}\\build",
    'progress':      "{base_dir}\\progress",
    'graphviz':      path_or_default("dot.exe",   gen_search_folders("Graphviz2.38", "bin")),
    'cmake':         path_or_default("cmake.exe", gen_search_folders("CMake", "bin")),
    'git':           path_or_default("git.exe",   gen_search_folders("Git", "bin")),
    'hg':            path_or_default("hg.exe",    gen_search_folders("TortoiseHg")),
    'perl':          path_or_default("perl.exe",  gen_search_folders("StrawberryPerl", "bin")),
    'ruby':          path_or_default("ruby.exe",  gen_search_folders("Ruby22-x64", "bin")),
    'svn':           path_or_default("svn.exe",   gen_search_folders("SlikSvn", "bin")),
    # we need a python that matches the build architecture
    'python':        Evaluate(lambda: os.path.join(get_from_hklm(r"SOFTWARE\Python\PythonCore\2.7\InstallPath",
                                                                 "", config['architecture'] == "x86"),
                                                   "python.exe")),
    'visual_studio': os.path.realpath(
        os.path.join(get_from_hklm(r"SOFTWARE\Microsoft\VisualStudio\{}".format(config['vc_version']),
                                   "InstallDir", True),
                     "..", "..", "VC"
                     )
    )
}
