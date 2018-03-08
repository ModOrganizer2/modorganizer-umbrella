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
from unibuild.modules import github, Patch

loot_version = config['loot_version']
loot_commit = config['loot_commit']

def bitnessLoot():
    return "64" if config['architecture'] == "x86_64" else "32"

# TODO modorganizer-lootcli needs an overhaul as the api has changed alot
Project("lootapi") \
    .depend(Patch.Copy("loot_api.dll", os.path.join(config["paths"]["install"], "bin", "loot"))
            .depend(github.Release("loot", "loot-api", loot_version,
                               "loot_api-{}-0-{}_update-deps-win{}".format(loot_version, loot_commit, bitnessLoot()), "7z", tree_depth=1)
                          .set_destination("lootapi-{}-{}".format(loot_version, loot_commit))))