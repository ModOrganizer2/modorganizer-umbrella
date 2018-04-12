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
boost_version = config['boost_version']
boost_tag_version = ".".join(filter(None, [boost_version, config['boost_version_tag']]))
boost_folder = os.path.join(build_path,"boost_{}".format(boost_tag_version).replace(".", '_'))
gtest_folder = os.path.join(build_path,"googletest")

usvfs = Project("usvfs")


def usvfs_environment():
    env = config['__environment'].copy()
    env['BOOST_PATH'] = boost_folder
    return env


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

usvfs \
    .depend(msbuild.MSBuild("usvfs.sln", vs_target, os.path.join(build_path, "usvfs", "vsbuild"),
                            "{}".format("x64" if config['architecture'] == 'x86_64' else "x86"),
                            None, None, None, usvfs_environment())
            .depend("boost" + suffix)
            .depend("GTest" + suffix)
            .depend(github.Source(config['Main_Author'], "usvfs", config['Main_Branch'])))
