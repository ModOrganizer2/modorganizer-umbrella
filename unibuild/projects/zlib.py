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


import os

from config import config
from unibuild import Project
from unibuild.modules import cmake, urldownload

zlib_version = config['zlib_version']

Project("zlib") \
    .depend(cmake.CMake().arguments(["-DCMAKE_BUILD_TYPE={0}".format(config["build_type"]),
                                     "-DCMAKE_INSTALL_PREFIX:PATH={}".format(
                                         os.path.join(config["paths"]["build"], "zlib"))
                                     ]).install()
            .depend(urldownload.URLDownload("http://zlib.net/zlib-{}.tar.gz".format(zlib_version), 1)))
