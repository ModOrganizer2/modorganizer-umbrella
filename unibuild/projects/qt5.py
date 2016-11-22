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


from unibuild import Project, Task
from unibuild.modules import build, patch, git, urldownload, sourceforge, dummy
from config import config
import os
import itertools
from glob import glob
import shutil
import python


from unibuild.projects import openssl, cygwin,  icu

qt_download_url = "http://download.qt.io/official_releases/qt"
qt_download_ext = "tar.gz"
qt_version = "5.5"
qt_version_minor = "1"
qt_inst_path = "{}/qt5".format(config["paths"]["build"]).replace("/", os.path.sep)
grep_version = "2.5.4"
# these two should be deduced from the config
qt_bin_variant = "msvc2015"
grep_version = "2.5.4"

platform = "win32-msvc2015"

#if config.get('prefer_binary_dependencies', False):
if False:
    # binary installation disabled because there is no support currently for headless installation
    filename = "qt-opensource-windows-x86-{variant}{arch}-{ver}.{ver_min}.exe".format(
        url=qt_download_url,
        ver=qt_version,
        ver_min=qt_version_minor,
        variant=qt_bin_variant,
        arch="_64" if config['architecture'] == 'x86_64' else ""
    )
    qt5 = Project("Qt5") \
        .depend(build.Run(filename, working_directory=config['paths']['download'])
                .depend(urldownload.URLDownload(
                    "{url}/{ver}/{ver}.{ver_min}/{filename}"
                    .format(url=qt_download_url,
                            ver=qt_version,
                            ver_min=qt_version_minor,
                            filename=filename))))
else:
    skip_list = ["qtactiveqt", "qtandroidextras", "qtenginio",
                "qtserialport", "qtsvg", "qtwebengine",
                "qtwayland", "qtdoc", "qtconnectivity", "qtwebkit-examples"]

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

    grep = Project('grep') \
        .depend(sourceforge.Release("gnuwin32", "grep/{0}/grep-{0}-bin.zip".format(grep_version))
                .set_destination("grep"))\
        .depend(sourceforge.Release("gnuwin32", "grep/{0}/grep-{0}-dep.zip".format(grep_version))
                .set_destination("grep"))

    flex = Project('flex') \
        .depend(sourceforge.Release("winflexbison", "win_flex_bison-latest.zip"))

    def webkit_env():
        result = config['__environment'].copy()

        result['Path'] = result['Path'] + ";" + ";".join([
            os.path.join(grep['build_path'], "bin"),
            flex['build_path'],
            os.path.dirname(config['paths']['ruby']),
            os.path.dirname(config['paths']['perl']),
            os.path.join(config["paths"]["build"], "qt5", "bin"),
            os.path.join(config['paths']['build'], "icu", "dist", "bin"),
            os.path.join(config['paths']['build'], "icu", "dist", "lib"),
            os.path.join(config["paths"]["build"], "qt5.git", "gnuwin32","bin"),
        ])
        result['INCLUDE'] += os.path.join(config['paths']['build'], "icu", "dist", "include") + ";" + \
                             os.path.join(config['paths']['build'], "Win64OpenSSL-1_0_2j", "include")
        result['LIB'] += os.path.join(config['paths']['build'], "icu", "dist", "lib") + ";" + \
                         os.path.join(config['paths']['build'], "Win64OpenSSL-1_0_2j", "lib", "VC")

        return result

    # TODO using openssl['Build_path'] here breaks things, Possibly use the same setup as we do for the progress tracking to log build_paths per project and read from file using function

    def qt5_environment():
        result = config['__environment'].copy()
        result['Path'] = result['Path'] + ";" + ";".join([
            os.path.join(config['paths']['build'], "icu", "dist", "bin"),
            os.path.join(config['paths']['build'], "icu", "dist", "lib"),
            os.path.join(config['paths']['build'], "jom")])
        result['INCLUDE'] += os.path.join(config['paths']['build'], "icu", "dist", "include") + ";" + \
                             os.path.join(config['paths']['build'], "Win64OpenSSL-1_0_2j", "include")
        result['LIB'] += os.path.join(config['paths']['build'], "icu", "dist", "lib") + ";" + \
                         os.path.join(config['paths']['build'], "Win64OpenSSL-1_0_2j", "lib", "VC")
        result['LIBPATH'] += os.path.join(config['paths']['build'], "icu", "dist", "lib")
        return result

    webkit_patch = patch.Replace("qtwebkit/Source/WebCore/platform/text/TextEncodingRegistry.cpp",
                                 "#if OS(WINDOWS) && USE(WCHAR_UNICODE)",
                                 "#if OS(WINCE) && USE(WCHAR_UNICODE)")

    build_webkit = build.Run(r"perl Tools\Scripts\build-webkit --qt --release",
                             environment=webkit_env,
                             working_directory=lambda: os.path.join(qt5['build_path'], "qtwebkit"),
                             name="build webkit") \
        .depend('grep').depend('flex')

    # comment to build webkit
    #build_webkit = dummy.Success("webkit")

    init_repo = build.Run("perl init-repository", name="init qt repository") \
        .set_fail_behaviour(Task.FailBehaviour.CONTINUE) \
        .depend(git.Clone("git://code.qt.io/qt/qt5.git", qt_version))

    build_qt5 = build.Run(r"jom.exe -j {}".format(config['num_jobs']),
                           environment=qt5_environment(),
                           working_directory=lambda: os.path.join(qt5['build_path']))

    install_qt5 = build.Run(r"nmake install",
                           environment=qt5_environment(),
                           working_directory=lambda: os.path.join(qt5['build_path']))


    def Copy_ICU_Libs(context):
        for f in glob(os.path.join(config['paths']['build'], "icu", "dist", "lib", "*54.lib")):
            shutil.copy(f,  os.path.join(config["paths"]["build"], "qt5", "bin"))
        return True



    qt5 = Project("Qt5") \
        .depend(build.Install()
                .depend(build_webkit
                    .depend(build.Execute(Copy_ICU_Libs)
                    .depend(install_qt5
                        .depend(build_qt5
                                .depend("jom")
                                .depend(build.Run(configure_cmd, name="configure qt",environment=qt5_environment())
                                        .depend("icu")
                                                .depend(patch.Replace("qtbase/configure.bat",
                                                             "if not exist %QTSRC%.gitignore goto sconf", "")
                                                        .depend(webkit_patch
                                                                .depend(init_repo)
                                                        )
                                                )
                                                .depend("openssl")
                                        )
                                )
                            )
                        )
                    )
                )



