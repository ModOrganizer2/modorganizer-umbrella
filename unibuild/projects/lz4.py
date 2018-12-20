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
import os.path

from config import config
from unibuild import Project
from unibuild.modules import github, Patch

lz4_version = 'v' + config['lz4_version']
lz4_version_minor = ".".join([_f for _f in [lz4_version, config['lz4_version_minor']] if _f])
lz_path = os.path.join(config['paths']['build'], "lz4-{}".format(lz4_version))

Project("lz4") \
    .depend(Patch.Copy(os.path.join(lz_path, "dll", "liblz4.so.{0}.dll".format(lz4_version[1:])),
                       os.path.join(config["paths"]["install"], "bin", "dlls")).set_filename("liblz4.dll")
            .depend(github.Release("lz4", "lz4", lz4_version_minor, "lz4_{0}_win{1}".format(lz4_version.replace(".", "_"),
                               "64" if config['architecture'] == 'x86_64' else "32"), "zip")
                          .set_destination("lz4-{}".format(lz4_version))))
