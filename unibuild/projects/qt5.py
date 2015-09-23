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
from unibuild.modules import build, patch, git, urldownload
from config import config
import unibuild.utility.lazy as lazy
import os
import multiprocessing

qt_download_url = "http://download.qt.io/official_releases/qt"
qt_download_ext = "tar.gz"
qt_version = "5.5"
qt_version_minor = "0"


skip_list = ["qtactiveqt", "qtandroidextras", "qtenginio", "qtsensors",
             "qtserialport", "qtsvg", "qtwebkit", "qttools", "qtwebchannel",
             "qtwayland", "qtdoc", "qtconnectivity", "qtwebkit-examples"]

nomake_list = ["tests", "examples"]

platform = "win32-msvc2013"

num_jobs = multiprocessing.cpu_count() * 2

configure_cmd = ("configure.bat -platform {platform} -debug-and-release -force-debug-info -opensource -confirm-license "
                 "-mp -no-compile-examples -no-angle -opengl desktop -no-icu -prefix {path}/qt5) "
                 "{skip} {nomake}").format(path=config["paths"]["build"],
                                           platform=platform,
                                           skip=" ".join(["-skip {}".format(s) for s in skip_list]),
                                           nomake=" ".join(["-nomake {}".format(n) for n in nomake_list]))

jom = Project("jom") \
    .depend(urldownload.URLDownload("http://download.qt.io/official_releases/jom/jom.zip"))

Project("Qt5") \
    .depend(build.Make(lazy.Evaluate(lambda: os.path.join(jom["build_path"], "jom.exe -j {}".format(num_jobs)))).install()
            .depend("jom")
            .depend(build.Run(configure_cmd)
                    .depend(patch.Replace("qtbase/configure.bat", "if not exist %QTSRC%.gitignore goto sconf", "")
                            .depend(build.Run("perl init-repository --no-webkit "
                                              "-module-subset=qtbase,qtwidgets,qtxmlpatterns,qtdeclarative,qtnetwork,"
                                              "qtquickcontrols,qtwinextras,qtwebengine")
                                    .set_fail_behaviour(Task.FailBehaviour.CONTINUE)
                                    .depend(git.Clone("git://code.qt.io/qt/qt5.git", "5.5")
                                            )
                                    )
                            )
                    )
            )
