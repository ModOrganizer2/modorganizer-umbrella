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
from unibuild.modules import build, sourceforge
from config import config
from glob import glob
import shutil
import os
import errno


udis_version = "1.7"
udis_version_minor = "2"


def make_sure_path_exists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


def install(context):
    make_sure_path_exists(os.path.join(config["paths"]["install"], "libs"))
    for f in glob(os.path.join(context['build_path'], "*.lib")):
        shutil.copy(f, os.path.join(config["paths"]["install"], "libs"))
    return True


Project("Udis86") \
    .depend(build.Execute(install)
            .depend((build.CPP().type(build.STATIC_LIB)
                     .sources("libudis86", ["libudis86/decode.c",
                                            "libudis86/itab.c",
                                            "libudis86/syn.c",
                                            "libudis86/syn-att.c",
                                            "libudis86/syn-intel.c",
                                            "libudis86/udis86.c"])
                     .custom("libudis86/itab.c",
                             cmd="{python} scripts/ud_itab.py docs/x86/optable.xml"
                                 " libudis86".format(**config["__environment"]))
                     )
                    .depend(sourceforge.Release("udis86", "udis86/{0}/udis86-{0}.{1}.tar.gz".format(udis_version,
                                                                                                    udis_version_minor),
                                                tree_depth=1))
                    )
            )
