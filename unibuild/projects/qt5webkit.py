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


from unibuild import Project
from unibuild.modules import urldownload, build
from unibuild.projects import qt5
from unibuild.utility import lazy
from config import config
import os


grep_version = "2.5.4"


grep = Project('grep') \
    .depend(urldownload.URLDownload("http://downloads.sourceforge.net/project/gnuwin32/grep/{0}/grep-{0}-bin.zip"
                                    .format(grep_version)))

flex = Project('flex') \
    .depend(urldownload.URLDownload("http://downloads.sourceforge.net/project/winflexbison/win_flex_bison-latest.zip"))


def webkit_env():
    result = config['__environment'].copy()

    result['Path'] = ";".join(result['Path'] + [os.path.join(grep['build_path'], "bin"),
                                                flex['build_path'],
                                                os.path.dirname(config['paths']['ruby']),
                                                os.path.dirname(config['paths']['perl'])])
    return result

Project('webkit') \
    .depend('grep').depend('flex') \
    .depend(build.Run(r"perl Tools\Scripts\build-webkit --qt --release",
                      environment=lazy.Evaluate(webkit_env),
                      working_directory=lazy.Evaluate(lambda: qt5.qt5['build_path'])))
