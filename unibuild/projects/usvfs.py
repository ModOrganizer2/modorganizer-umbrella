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
import logging
import os.path
import sys

from config import config
from unibuild import Project
from unibuild.modules import build, cmake, dummy, msbuild, github

build_path = config["paths"]["build"]
suffix = "" if config['architecture'] == 'x86_64' else "_32"
vs_target = "Clean;Build" if config['rebuild'] else "Build"


# TODO change dynamicaly
boost_folder = "boost_{}".format(config["boost_version"])
gtest_folder = "googletest"


usvfs = Project("usvfs")

for (project32, dependencies) in [("boost", ["boost_prepare"]),
      ("GTest", []),
      ("usvfs", [])]:
  if config['architecture'] == 'x86_64':
    unimake32 = \
      build.Run_With_Output(r'"{0}" unimake.py -d "{1}" --set architecture="x86" -b "build" -p "progress" -i "install" "{2}"'.format(sys.executable, config['__build_base_path'], project32),
        name="unimake_x86_{}".format(project32),
        environment=config['__Default_environment'],
        working_directory=os.path.join(os.getcwd()))
    for dep in dependencies:
        unimake32.depend(dep)
    Project(project32 + "_32").depend(unimake32)
  else:
    Project(project32 + "_32").dummy().depend(project32)


# TODO remove after repo merge
def replace_paths(context):
    with open(os.path.join(build_path, "usvfs", "vsbuild", "external_dependencies.props"), 'r') as file:
        lines = file.readlines()
        # keep whitespaces at the beginning for formatting
        lines[4] = "    <BOOST_PATH>..\..\{}</BOOST_PATH>\n".format(boost_folder)
        lines[5] = "    <GTEST_PATH>..\..\{}</GTEST_PATH>\n".format(gtest_folder)
        file.seek(0)
        # clean file first or we leave trailing characters behind
        with open(os.path.join(build_path, "usvfs", "vsbuild", "external_dependencies.props"), 'w') as file:
            file.writelines(lines)
    return True


usvfs \
    .depend(msbuild.MSBuild("usvfs.sln", vs_target, os.path.join(build_path, "usvfs", "vsbuild"),
                           "{}".format("x64" if config['architecture'] == 'x86_64' else "x86"))
            .depend(build.Execute(replace_paths)
                    .depend("boost" + suffix)
                            .depend("GTest" + suffix)
                                    .depend(github.Source(config['Main_Author'], "usvfs", "0.3.1.0-Beta"))))
