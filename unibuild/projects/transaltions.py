# Copyright (C) 2015 Sebastian Herbord.  All rights reserved.
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
import glob
import os.path
import shutil

from config import config
from unibuild import Project
from unibuild.modules import build, github, Patch


# TODO: transifex
version = "v2.1.0"

def transaltions_install(context):
    for file in glob.iglob(os.path.join(config["paths"]["build"], "translations-{}".format(version), "*.qm")):
        if os.path.isfile(file):
            shutil.copy2(file, os.path.join(config["paths"]["install"], "bin", "translations"))
    return True

Project("translations") \
    .depend(build.Execute(transaltions_install)
        .depend(github.Release("LePresidente", "modorganizer", version, "translations", extension="7z", tree_depth=1)
                .set_destination("translations-{}".format(version))))