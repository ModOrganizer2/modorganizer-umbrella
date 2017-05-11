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
from unibuild.modules import github, Patch
from config import config
import os


lz4_version = "v1.7.4"

Project("lz4") \
            .depend(Patch.Copy(os.path.join(config['paths']['build'], "lz4", "dll", "liblz4.dll"),
                               os.path.join(config["paths"]["install"], "bin", "dlls"))
                    .depend(github.Release("lz4", "lz4", lz4_version, "lz4_{0}_win{1}".format(lz4_version.replace(".","_"),"64" if config['architecture'] == 'x86_64' else "32"),"zip")
                    .set_destination("lz4")
                )
                    )

