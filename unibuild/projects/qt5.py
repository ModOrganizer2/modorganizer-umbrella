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
from unibuild.modules import build, patch, git, urldownload, sourceforge
from config import config
import unibuild.utility.lazy as lazy
import os
import multiprocessing

qt_download_url = "http://download.qt.io/official_releases/qt"
qt_download_ext = "tar.gz"
qt_version = "5.5"
qt_version_minor = "1"
qt_bin_variant = "msvc2013"


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

    platform = "win32-msvc2013"

    num_jobs = multiprocessing.cpu_count() * 2

    configure_cmd = ("configure.bat -platform {platform} -debug-and-release -force-debug-info -opensource -confirm-license "
                    "-mp -no-compile-examples -no-angle -opengl desktop -prefix {path}/qt5 "
                    "{skip} {nomake}").format(path=config["paths"]["build"],
                                            platform=platform,
                                            skip=" ".join(["-skip {}".format(s) for s in skip_list]),
                                            nomake=" ".join(["-nomake {}".format(n) for n in nomake_list]))

    jom = Project("jom") \
        .depend(urldownload.URLDownload("http://download.qt.io/official_releases/jom/jom.zip"))


    grep_version = "2.5.4"


    grep = Project('grep') \
        .depend(urldownload.URLDownload("http://downloads.sourceforge.net/project/gnuwin32/grep/{0}/grep-{0}-bin.zip"
                                        .format(grep_version)))\
        .depend(sourceforge.Release("gnuwin32", "grep/{0}/grep-{0}-dep.zip".format(grep_version)))

    flex = Project('flex') \
        .depend(urldownload.URLDownload("http://downloads.sourceforge.net/project/winflexbison/win_flex_bison-latest.zip"))


    def webkit_env():
        print(config['paths'])
        result = config['__environment'].copy()

        result['Path'] = result['Path'] + ";" + ";".join([
            os.path.join(grep['build_path'], "bin"),
            flex['build_path'],
            os.path.dirname(config['paths']['ruby']),
            os.path.dirname(config['paths']['perl']),
            os.path.join(config["paths"]["build"], "qt5.git", "gnuwin32", "bin"),
            os.path.join(config["paths"]["build"], "qt5", "bin")
        ])

        from pprint import pprint
        pprint(result)


        return result


    qt5 = Project("Qt5") \
        .depend(build.Make(lazy.Evaluate(lambda: os.path.join(jom["build_path"], "jom.exe -j {}".format(num_jobs))))
                .install()
                .depend(build.Run(r"perl Tools\Scripts\build-webkit --qt --release",
                                environment=lazy.Evaluate(webkit_env),
                                working_directory=lazy.Evaluate(lambda: os.path.join(qt5['build_path'], "qtwebkit")),
                                name="build webkit")
                        .depend("jom").depend('grep').depend('flex')
                        .depend(build.Run(configure_cmd)
                                .depend(patch.Replace("qtbase/configure.bat",
                                                    "if not exist %QTSRC%.gitignore goto sconf", "")
                                        .depend(build.Run("perl init-repository", name="init qt repository")
                                                .set_fail_behaviour(Task.FailBehaviour.CONTINUE)
                                                .depend(git.Clone("git://code.qt.io/qt/qt5.git", qt_version)
                                                        )
                                                )
                                        )
                                )
                        )
                )
    working_directory=lazy.Evaluate(lambda: os.path.join(qt5.qt5['build_path'], "qtwebkit")),
