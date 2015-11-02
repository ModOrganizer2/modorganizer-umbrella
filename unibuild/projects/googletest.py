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
from unibuild.modules import cmake, googlecode, build
from config import config
import shutil
import os
from glob import glob


googletest_version = "1.7.0"


def install(context):
    for f in glob(os.path.join(context['build_path'], "build", "*.lib")):
        shutil.copy(f, os.path.join(config["__build_base_path"], "install", "libs"))
    return True


Project("GTest") \
    .depend(build.Execute(install)
            .depend(cmake.CMake().arguments(["-Dgtest_force_shared_crt=ON",
                                             "-DCMAKE_BUILD_TYPE={0}".format(config["build_type"])
                                             ])
                    .depend(googlecode.Release("googletest", "gtest-{0}.zip".format(googletest_version), 1)))
            )
