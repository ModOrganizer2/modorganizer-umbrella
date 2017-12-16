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


import multiprocessing
import os
from _winreg import *

from unibuild.utility.lazy import Lazy

global missing_prerequisites
missing_prerequisites = False


def path_or_default(filename, *default):
    from distutils.spawn import find_executable
    defaults = gen_search_folders(*default)
    res = find_executable(filename, os.environ['PATH'] + ";" + ";".join(defaults))
    if res is None:
        print 'Cannot find', filename, 'on your path or in', os.path.join('', *default)
        global missing_prerequisites
        missing_prerequisites = True
    return res


def get_from_hklm(path, name, wow64=False):
    flags = KEY_READ
    if wow64:
        flags |= KEY_WOW64_32KEY

    # avoids crashing if a product is not present
    try:
        with OpenKey(HKEY_LOCAL_MACHINE, path, 0, flags) as key:
            return QueryValueEx(key, name)[0]
    except:
        return ""


# To detect the editon of VS installed as of VS 2017
vs_editions = [
    "enterprise",
    "professional",
    "community",
]

program_files_folders = [
    os.environ['ProgramFiles(x86)'],
    os.environ['ProgramFiles'],
    os.environ['ProgramW6432'],
    "C:\\",
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
    'architecture': 'x86_64',  # Don't change this as we spawn the usvfs x86 build later on.
    'vc_version': '15.0',
    'vc_platformtoolset': 'v141',
    'vc_CustomInstallPath': '',  # If you installed VC to a custom location put the full path here
    # eg. E:\Microsoft Visual Studio 14.0
    'qt_CustomInstallPath': '',  # If you installed QT to a custom location put the full path here
    # eg. Z:\Dev\QT
    'build_type': "RelWithDebInfo",
    'rebuild': True,   # if set, does a clean build of the VS projects (for now only usvfs)
    'offline': False,  # if set, non-mandatory network requests won't be made.
    # This is stuff like updating source repositories. The initial
    # download of course can't be supressed.
    'prefer_binary_dependencies': True,  # Work in progress
    'optimize': True,  # activate link-time code generation and other optimization.
    # This massively increases build time but produces smaller
    # binaries and marginally faster code
    'Installer': True,  # Used to create installer at end of build, Forces everything to be built
    'repo_update_frequency': 60 * 60 * 24,  # in seconds
    'num_jobs': multiprocessing.cpu_count() + 1,

    'Main_Author': 'LePresidente',  # the current maintainer
    'Distrib_Author': 'TanninOne',  # the current distribution (and the original Author)
    'Work_Author': 'Hugues92',  # yourself

    'qt_version': '5.9',  # currently evolving
    'qt_minor_version': '2',  # place the qt minor version here if only it is not zero, otherwise leave blank
    'pyqt_version': '5.9',  # pyqt version doesn't always match qt. So it is now a seperate config
    'openssl_version': '1.0.2n',  # changes often, so better to edit here
    'zlib_version': '1.2.11',  # changes often, so better to edit here
    'grep_version': '2.5.4',  # moved here as commented in qt5.py
    'boost_version': '1.65.1',  # for -DBOOST_ROOT, also, it is either to change from here
    'vc_version_for_boost': '14.1',  # boost 1.63 does not support VS 2017 yet
    'python_version': '2.7',  # used below and in python.py
    'python_version_minor': '.13',  # used in python.py
    'icu_version': '59',  # used in PyQt5
    'icu_version_minor': '1',  # for consistency
    'WixToolSet_Version_Binary': '311',  # Wix Binary Version

    'show_only': False,
    'retrieve_only': False,                 # download everything as a reference (to keep track of local edits). Do modorganizer_super first :)
    'tools_only': False,                    # Build dependencies except modorganizer targets
}

config['paths'] = {
    'download': "{base_dir}\\downloads",
    'build': "{base_dir}\\{build_dir}",
    'progress': "{base_dir}\\{progress_dir}",
    'install': "{base_dir}\\{install_dir}",
#   'graphviz': path_or_default("dot.exe", "Graphviz2.38", "bin"),
    'cmake': path_or_default("cmake.exe", "CMake", "bin"),
    'git': path_or_default("git.exe", "Git", "bin"),
    #'perl': path_or_default("perl.exe", "StrawberryPerl", "bin"),
    #'ruby': path_or_default("ruby.exe", "Ruby22-x64", "bin"),
    #'svn': path_or_default("svn.exe", "SlikSvn", "bin"),
    '7z': path_or_default("7z.exe", "7-Zip"),
    # we need a python that matches the build architecture
    'python': Lazy(lambda: os.path.join(
        get_from_hklm(r"SOFTWARE\Python\PythonCore\{}\InstallPath".format(config['python_version']),
                      "", config['architecture'] == "x86"),
        "python.exe")),
    'visual_studio_base': "",
    'qt_binary_install': "",
    'visual_studio': ""  # will be set in unimake.py after args are evaluated
}

if missing_prerequisites:
    print '\nMissing prerequisites listed above - cannot continue'
    exit(1)
