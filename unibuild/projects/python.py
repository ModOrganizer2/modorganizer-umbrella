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


from unibuild.project import Project
from unibuild.modules import urldownload, msbuild, build
from unibuild.utility.lazy import Evaluate
from config import config
import os


python_version = "2.7.10"


def python_environment():
    result = config['__environment'].copy()
    result['Path'] += ";" + os.path.dirname(config['paths']['svn'])
    return result


python = Project("Python")\
    .depend(msbuild.MSBuild("PCBuild/python.vcxproj")
            .depend(build.Run(Evaluate(lambda: [os.path.join(config['__environment']['DevEnvDir'], "devenv.exe"),
                                                "PCBuild/pcbuild.sln",
                                                "/upgrade"]),
                              name="upgrade python project")
                    .depend(build.Run(r"Tools\buildbot\external-common.bat", environment=python_environment())
                            .depend(urldownload.URLDownload("https://www.python.org/ftp/python/{0}/Python-{0}.tgz"
                                                            .format(python_version), 1)
                                    )
                            )
                    )
            )
