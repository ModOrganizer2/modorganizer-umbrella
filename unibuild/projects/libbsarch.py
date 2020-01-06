# Copyright (C) 2015 Sebastian Herbord.  All rights reserved.
# Copyright (C) 2016 - 2019 Mod Organizer contributors.
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
import shutil

from config import config
from unibuild import Project
from unibuild.modules import github, build


def bitness():
    from config import config
    return "x64" if config['architecture'] == "x86_64" else "x86"


libbsarch_version = config['libbsarch_version']
libbsarch_path = os.path.join(config['paths']['build'], "libbsarch-{}-{}".format(libbsarch_version, bitness()))


def deploy_dll(context):
    if not os.path.exists(os.path.join(config["paths"]["install"], "bin", "dlls")):
        os.mkdir(os.path.join(config["paths"]["install"], "bin", "dlls"))
    shutil.copy(
        os.path.join(libbsarch_path, "libbsarch.dll"),
        os.path.join(config["paths"]["install"], "bin", "dlls", "libbsarch.dll")
    )
    return True


Project("libbsarch").depend(
    build.Execute(deploy_dll).depend(
        github.Release(
            "deorder",
            "libbsarch",
            version=libbsarch_version,
            filename="libbsarch-{}-release-{}".format(libbsarch_version, bitness()),
            extension="7z",
            tree_depth=1
        ).set_destination(libbsarch_path)
    )
)
