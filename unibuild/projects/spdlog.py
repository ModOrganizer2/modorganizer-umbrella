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

# TODO This is really old, should by updated to 0.13

from unibuild import Project
from unibuild.modules import cmake, github
from config import config

Project("spdlog") \
    .depend(cmake.CMake().arguments(
    [
        "-DCMAKE_INSTALL_PREFIX:PATH={}".format(config["paths"]["install"].replace('\\', '/')),
        "-DCMAKE_BUILD_TYPE={0}".format(config["build_type"]),
    ]).install()
                    .depend(github.Source("TanninOne", "spdlog", "master").set_destination("spdlog")
                    )
            )
