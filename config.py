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
import multiprocessing
import os

from unibuild.utility import config_utility
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


def gen_search_folders(*subpath):
    return [
        os.path.join(search_folder, *subpath)
        for search_folder in config_utility.program_files_folders
    ]


config = {
    'vc_CustomInstallPath': '',  # If you installed VC to a custom location put the full path here
                                 # eg.  'E:\Microsoft Visual Studio 14.0'
    'qt_CustomInstallPath': '',  # If you installed QT to a custom location put the full path here
                                 # eg.  'Z:\Dev\QT'
    'build_type': "RelWithDebInfo", # build type.  other possible types could be Debug.  not tested
    'rebuild': True,  # if set, does a clean build of the VS projects (for now only usvfs)
    'offline': False,  # if set, non-mandatory network requests won't be made eg: updating source repositories.
                      # The initial download of course can't be supressed.

    'prefer_binary_dependencies': True,  # Try to use official binary package/SDKs.  Won't work for all stuff
    # works for: 7z, CMake, Git, Perl, Python, Visual Studio
    'binary_qt': True, # use binary Qt5 from the offical website
    'shallowclone': True, # reduces size of repos drastically
    'repo_update_frequency': 60 * 60 * 12,  # in seconds
    'num_jobs': multiprocessing.cpu_count() + 1,

    'Main_Author': 'Modorganizer2',  # the current maintainer
    'Main_Branch': "Develop",
    'Distrib_Author': 'TanninOne',  # the current distribution (and the original Author)
    'Work_Author': '',  # yourself

    # manualy set all versions
    '7zip_version': '18.01',
    'boost_version': '1.66.0',
    'googletest_version': '1.8.0', # unused. We use the latest source
    'grep_version': '2.5.4',
    'icu_version': '59',
    'icu_version_minor': '1',
    'loot_version': '0.12.4',
    'loot_commit': 'gec946b5',
    'lz4_version': 'v1.7.4',
    'nasm_version': '2.13.03',
    'openssl_version': '1.0.2n',
    'pyqt_version': '5.10',
    'python_version': '2.7',
    'python_version_minor': '.14',
    'sip_version': '4.19.8',
    'qt_version': '5.10',
    'qt_version_minor': '0',
    'vc_platformtoolset': 'v141',
    'vc_version': '15.0',
    'vc_version_for_boost': '14.1',
    'WixToolset_version': '311',
    'zlib_version': '1.2.11',

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
    'transifex-client_version': '0.13.1',
    'transifex_minimum_percentage': '60'
}
config['paths'] = {
    'download': "{base_dir}\\downloads",
    'build': "{base_dir}\\{build_dir}",
    'progress': "{base_dir}\\{progress_dir}",
    'install': "{base_dir}\\{install_dir}",
    # 'graphviz': path_or_default("dot.exe", "Graphviz2.38", "bin"),
    'cmake': path_or_default("cmake.exe", "CMake", "bin"),
    'git': path_or_default("git.exe", "Git", "bin"),
    'perl': path_or_default("perl.exe", "StrawberryPerl", "perl", "bin"),
    #'ruby': path_or_default("ruby.exe", "Ruby22-x64", "bin"),
    #'svn': path_or_default("svn.exe", "SlikSvn", "bin"),
    '7z': path_or_default("7z.exe", "7-Zip"),
    # we need a python that matches the build architecture
    'python': Lazy(lambda: os.path.join(config_utility.get_from_hklm(r"SOFTWARE\Python\PythonCore\{}\InstallPath".format(config['python_version']),
                      ""), "python.exe")),
    'visual_studio_base': "",
    'qt_binary_install': "",
    'visual_studio': ""  # will be set in unimake.py after args are evaluated
}
if missing_prerequisites:
    print '\nMissing prerequisites listed above - cannot continue'
    exit(1)
