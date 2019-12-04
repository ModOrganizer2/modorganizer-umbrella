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
import logging
from config import config
from unibuild import Project
from unibuild.modules import cmake, github, build, Patch

build_path = os.path.join(config['paths']['build'])

# emulates shutil.copytree() with dirs_exist_ok=True
def copytree_fixed(src, dst, symlinks=False, ignore=None):
    if not os.path.exists(dst):
        os.makedirs(dst, exist_ok=True)

    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            copytree_fixed(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)

def copy_stylesheets(context, dir):
    src = os.path.join(build_path, dir)
    dst = os.path.join(config["paths"]["install"], "bin", "stylesheets")
    logging.info("copying stylesheets from {} to {}".format(src, dst))
    # once python 3.8 becomes a requirement, this can be replaced by:
    # shutil.copytree(src, dst, dirs_exist_ok=True)
    copytree_fixed(src, dst)
    return True

def create_stylesheet_project(author, name, filename, extension="7z"):
    version = "v" + config[name + "_version"]
    dir = name + "-" + version

    Project(name) \
        .depend(build.Execute(lambda context: copy_stylesheets(context, dir))
        .depend(github.Release(author, name, version, filename, extension)))

create_stylesheet_project("6788-00", "paper-light-and-dark", "Paper-Light-and-Dark")
create_stylesheet_project("6788-00", "paper-automata", "Paper-Automata")
create_stylesheet_project("6788-00", "paper-mono", "Paper-Mono")
create_stylesheet_project("6788-00", "1809-dark-mode", "1809-Dark-Mode")
