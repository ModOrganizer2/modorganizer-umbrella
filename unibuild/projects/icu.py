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
from unibuild.modules import build, sourceforge, patch
from config import config
import subprocess
import os

icu_version = "54"
icu_version_minor = "1"

def icu_environment():
    result = config['__environment'].copy()
    result['Path'] += ";" + os.path.join(config['paths']['build'], "cygwin", "bin")
    return result

build_icu = build.Run(r"make && make install",
                      environment=icu_environment(),
                      working_directory=lambda: os.path.join(config["paths"]["build"], "icu", "source"))

current_dir_cygwin = subprocess.check_output(r"cygpath {}".format(os.path.join(config["paths"]["build"], "icu", "dist")),
                        shell=True,
                        env=icu_environment())

configure_icu = build.Run(r"bash runConfigureICU Cygwin/MSVC --prefix {}".format(current_dir_cygwin),
                      environment=icu_environment(),
                      working_directory=lambda: os.path.join(config["paths"]["build"], "icu", "source"))

Convert_icu = build.Run(r"dos2unix -f configure",
                    environment=icu_environment(),
                    working_directory=lambda: os.path.join(config["paths"]["build"], "icu", "source"))

icu = Project('icu') \
        .depend(build_icu
                .depend(configure_icu
                        .depend(Convert_icu
                            .depend(patch.Replace("source/io/ufile.c",
                                                      "#if U_PLATFORM_USES_ONLY_WIN32_API", "#if U_PLATFORM_USES_ONLY_WIN32_API && _MSC_VER < 1900")
                                .depend(sourceforge.Release("icu","ICU4C/{0}.{1}/icu4c-{0}_{1}-src.zip"
                                                      .format(icu_version,icu_version_minor),tree_depth=1)
                                                                .set_destination("icu")))))).depend("cygwin")
