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
import errno
import itertools
import os
import shutil
from glob import glob

from config import config
from unibuild import Project, Task
from unibuild.modules import build, git, urldownload

build_path = config['paths']['build']
grep_version = config['grep_version']
icu_version = config['icu_version']
openssl_version = config['openssl_version']
qt_version = config['qt_version']
qt_version_minor = config['qt_version_minor']

if config['__environment']['APPVEYOR'] == "True":
    qt_version_minor = config['qt_version_minor_appveyor']

def bitnessQt():
    return "64" if config['architecture'] == "x86_64" else "32"

def variant():
    return "msvc2013" if config['vc_version'] == "12.0" else "msvc2015" if config['vc_version'] == "14.0" else "msvc2017"

qt_bin_variant = variant()
platform = "win32-{0}".format(variant())

def make_sure_path_exists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

if config.get('binary_qt', True):
    qt5 = Project("Qt5")
else:
    # import source packages only if we build from source
    from unibuild.projects.icu import icu

    #We should probably nuke this section as it is not being used, this is to git rid of the error from flake8.
    qt_inst_path = ""

    skip_list = ["qtactiveqt", "qtandroidextras", "qtenginio",
                 "qtserialport", "qtsvg",
                 "qtwayland", "qtdoc", "qtconnectivity"]
    nomake_list = ["tests", "examples"]
    configure_cmd = lambda: " ".join(["configure.bat",
                                      "-platform", platform,
                                      "-debug-and-release", "-force-debug-info",
                                      "-opensource", "-confirm-license", "-icu",
                                      "-mp", "-no-compile-examples",
                                      "-no-angle", "-opengl", "desktop",
                                      "-ssl", "-openssl-linked",
                                      "OPENSSL_LIBS=\"-lssleay32MD -llibeay32MD -lgdi32 -lUser32\"",
                                      "-prefix", qt_inst_path] \
                                     + list(itertools.chain(*[("-skip", s) for s in skip_list])) \
                                     + list(itertools.chain(*[("-nomake", n) for n in nomake_list])))

    jom = Project("jom") \
        .depend(urldownload.URLDownload("http://download.qt.io/official_releases/jom/jom.zip"))

    def qt5_environment():
        result = config['__environment'].copy()
        result['Path'] = ";".join([os.path.join(build_path, "icu", "dist", "bin"),
            os.path.join(build_path, "icu", "dist", "lib"),
            os.path.join(build_path, "jom")]) + ";" + result['Path']
        result['INCLUDE'] = os.path.join(build_path, "icu", "dist", "include") + ";" + \
                            os.path.join(build_path, "Win{}OpenSSL-{}".format(bitnessQt(),
                                         openssl_version.replace(".", "_")), "include") + ";" + \
                            result['INCLUDE']
        result['LIB'] = os.path.join(build_path, "icu", "dist", "lib") + ";" + \
                        os.path.join(build_path, "Win{}OpenSSL-{}".format(bitnessQt(),
                                     openssl_version.replace(".", "_")), "lib", "VC") + ";" + \
                        result['LIB']
        result['LIBPATH'] = os.path.join(build_path, "icu", "dist", "lib") + ";" + result['LIBPATH']
        return result

    init_repo = build.Run("perl init-repository", name="init qt repository") \
        .set_fail_behaviour(Task.FailBehaviour.CONTINUE) \
        .depend(git.Clone("http://code.qt.io/qt/qt5.git", qt_version))  # Internet proxy could refuse git protocol

    build_qt5 = build.Run(r"jom.exe -j {}".format(config['num_jobs']),
                          environment=qt5_environment(),
                          name="Build Qt5",
                          working_directory=lambda: os.path.join(build_path))

    install_qt5 = build.Run(r"nmake install",
                            environment=qt5_environment(),
                            name="Install Qt5",
                            working_directory=lambda: os.path.join(build_path))

    def copy_icu_libs(context):
        for f in glob(os.path.join(build_path, "icu", "dist", "lib", "icu*{}.dll".format(icu_version))):
            shutil.copy(f, os.path.join(build_path, "qt5", "bin"))
        return True

    qt5 = Project("Qt5") \
        .depend(build.Execute(copy_icu_libs)
            .depend(install_qt5
                .depend(build_qt5
                    .depend("jom")
                        .depend(build.Run(configure_cmd,
                                name="configure qt",
                                environment=qt5_environment())
                            .depend(init_repo)
                                .depend("icu")
                                    .depend("openssl")))))
