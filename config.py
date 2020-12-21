# Copyright (C) 2015 Sebastian Herbord.  All rights reserved.
# Copyright (C) 2016 - 2019 Mod Organizer contributors.
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

from unibuild.utility import config_utility
from unibuild.utility.lazy import Lazy


def path_or_default(filename, default):
    from distutils.spawn import find_executable
    for path in default:
        defaults = gen_search_folders(*path)
    res = find_executable(filename, os.environ['PATH'] + ";" + ";".join(defaults))
    if res is None:
        print('Cannot find', filename, 'on your path or in', os.path.join('', *default[0]))
    return res


def gen_search_folders(*subpath):
    return [
        os.path.join(search_folder, *subpath)
        for search_folder in config_utility.program_files_folders
    ]


config = {

    'Appveyor_Build': False, #Should only be used for the AppVeyor build as it will use as many prebuilt binaries as possible
    'Release_Build': False,  #Used to override certain versions in umbrella when doing an officail release

                            #eg. Using the usvfs_version below instead of the Main_Branch config

    'override_build_version': '', #used to override the modorganizer.exe output version, useful for Appveyor nightlies and dev builds.

    'vc_CustomInstallPath': '',  # If you installed VC to a custom location put the full path here
                                 # eg.  'E:\Microsoft Visual Studio 14.0'
    'qt_CustomInstallPath': r'',  # If you installed QT to a custom location put the full path here
                                  # eg.  r'Z:\Dev\QT' if you have Z:\Dev\QT\5.10.0\msvc2017_64\bin\qmake.exe
                                  # The r before the start of the string prevents backslashes being treated as special characters
    'build_type': "RelWithDebInfo", # build type.  other possible types could be Debug.  not tested
    'rebuild': True,  # if set, does a clean build of the VS projects (for now only usvfs)
    'offline': False,  # if set, non-mandatory network requests won't be made eg: updating source repositories.
                      # The initial download of course can't be supressed.

    'prefer_binary_dependencies': True,  # Try to use official binary package/SDKs.  Won't work for all stuff
    # works for: 7z, CMake, Git, Perl, Python, Visual Studio
    'binary_qt': True, # use binary Qt5 from the offical website
    'binary_boost': True, # Custom prebuilt boost compiled by MO2 team and uploaded to https://github.com/ModOrganizer2/3rdParty_Dependencies
    'binary_lz4': True, # Custom prebuilt lz4 to get around issues with latest releases uploaded to https://github.com/ModOrganizer2/3rdParty_Dependencies
    'shallowclone': True, # reduces size of repos drastically
    'repo_update_frequency': 60 * 60 * 12,  # in seconds
    'num_jobs': multiprocessing.cpu_count() + 1,

    'progress_method': 'folders', # Changes how the progress files are generated
                               # flat:    All files in one folder, <project>_complete_<task>.txt (default)
                               # folders: <project>\<task>_complete.txt

    'Main_Author': 'ModOrganizer2',  # the current maintainer
    'Dev_Branch': "master",
    'Release_Branch': "2_3_0",
    'Feature_Branch': None, # Specify a branch or None to disable, used in place of the build branch when found
    'Distrib_Author': 'TanninOne',  # the current distribution (and the original Author)
    'Work_Author': '',  # yourself

    # manualy set all versions
    '7zip_version': '19.00',
    'boost_version': '1.74.0',
    'boost_version_tag': '',
    'fmt_version': '7.0.3',
    'googletest_version': '1.8.0', # unused. We use the latest source
    'grep_version': '3.3',
    'icu_version': '67',
    'icu_version_minor': '1',
    'loot_version': '0.16.1',
    'loot_commit': 'gd8c9b98',
    'loot_branch': '0.16.1',
    'lz4_version': '1.9.2',
    'lz4_version_minor': '', # leave empty if no patch version (1.2.3.x)
    'nasm_version': '2.15.05',
    'nuget_version': '5.7.0',
    'nmm_version': '0.71.2',
    'openssl_version': '1.1.1h',
    'pyqt_version': '5.15.1',
    'pyqt_pypi_hash': '1d/31/896dc3dfb6c81c70164019a6cbba6ab037e3af7653d9ca60ccc874ee4c27',
    'pyqt_dev_version': '', # leave empty for a standard release
    'pyqt_builder_version': '1.5.0',
    'pyqt_sip_version': '12.8.1',
    'python_version': '3.8',
    'python_version_minor': '.6',
    'bzip2_version': '1.0.6', # For python
    'sip_version': '5.4.0',
    'sip_dev_version': '', # leave empty for a standard release
    'spdlog_version': 'v1.8.0',
    'qt_version': '5.15',
    'qt_version_minor': '0',
    'qt_version_appveyor': '5.15',
    'qt_version_minor_appveyor': '1',
    'qt_vs_version': '16.0',
    'vc_platformtoolset': 'v142',
    'vc_TargetPlatformVersion': '10.0.19041.0',
    'vs_version': '16.0',
    'vc_version_for_boost': '14.2',
    'WixToolset_version': '311',
    'zlib_version': '1.2.11',
    'explorer++_version': '1.3.5',
    'libbsarch_version': '0.0.8',

    #stylesheets
    'paper-light-and-dark_version': '6.0',
    'paper-automata_version': '2.2',
    'paper-mono_version': '2.1',
    '1809-dark-mode_version': '2.0',
    'ModOrganizer_Style_Morrowind_version': '1.0',

    #the usvfs version below will only be used if
    'usvfs_version': 'v0.4.8',

    'optimize': True,  # activate link-time code generation and other optimization.  This massively increases build time but
                       # produces smaller binaries and marginally faster code
    'Installer': False, # Used to create installer at end of build, Forces everything to be built
    'show_only': False,
    'retrieve_only': False,                 # download everything as a reference (to keep track of local edits).  Do modorganizer_super first :)
    'tools_only': False,                    # Build dependencies except modorganizer targets
    'tools': {'make': "nmake"},
    'architecture': 'x86_64',  # Don't change this as we spawn the usvfs x86 build later on.

    # Transifex Translation configuration
    'transifex_Enable': False, # this should only be changed to true when doing a release
    'transifex_API': '', # you can generate an api at https://www.transifex.com/user/settings/api/
    'transifex-client_version': '0.13.6',
    'transifex_minimum_percentage': '60',

    #url used for all prebuilt downloads
    'prebuilt_url': "https://github.com/ModOrganizer2/modorganizer-umbrella/releases/download/1.1/"
}


config['paths'] = {
    'download': "{base_dir}\\downloads",
    'build': "{base_dir}\\{build_dir}",
    'progress': "{base_dir}\\{progress_dir}",
    'install': "{base_dir}\\{install_dir}",
    # 'graphviz': path_or_default("dot.exe", [["Graphviz2.38", "bin"]]),
    'cmake': path_or_default("cmake.exe", [["CMake", "bin"]]),
    'git': path_or_default("git.exe", [["Git", "bin"]]),
    'perl': path_or_default("perl.exe", [["StrawberryPerl", "perl", "bin"], ["Strawberry", "perl", "bin"]]),
    #'svn': path_or_default("svn.exe", [["SlikSvn", "bin"]]),
    '7z': path_or_default("7z.exe", [["7-Zip"]]),
    # we need a python that matches the build architecture
    'python': "", # Registry Key can be in multiple places. set in config_setup.py
    'jom': "",
    'visual_studio_base': "",
    'qt_binary_install': "",
    'visual_studio': ""  # will be set in unimake.py after args are evaluated
}
