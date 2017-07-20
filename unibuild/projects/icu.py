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
from unibuild.modules import build, sourceforge, Patch
from config import config
import subprocess
import os
import logging

icu_version = config['icu_version']
icu_version_minor = config['icu_version_minor']

# installation happens concurrently in separate process. We need to wait for all relevant files to exist,
# and can determine failure only by timeout
timeout = 15   # seconds


def icu_environment():
    s = ""
    MSVCFolders = ("Microsoft Visual Studio","MSBuild","Framework","Windows Kits","Microsoft SDK", "HTML Help")
    result = config['__environment'].copy()
    a = result['PATH']
    for x in a.split(";"):
        if any(word in x for word in MSVCFolders):
            if s:
                s += x + ";"
            else:
                s = x + ";"
        else:
            if "cygwin" not in x:
                s +=os.path.join(config['paths']['build'], "cygwin", "bin") + ";" + x + ";"
            else:
                s += x + ";"
    result['PATH'] = s
    return result


# Warning, build_run only works for me if cygwin is first after VS in the path (as requested in readme)
# So I change my path before calling unimake.py
build_icu = build.Run("make && make install".format(os.path.join(config['paths']['build'], "cygwin", "bin")),
                      name="ICU Make",
                      environment=icu_environment(),
                      working_directory=lambda: os.path.join(config["paths"]["build"], "icu", "source"))


# Warning this won't work if there are Embarcadero compiler definition in your path
class ConfigureIcu(build.Builder):
    def __init__(self):
        super(ConfigureIcu, self).__init__()

    @property
    def name(self):
        return "icu configure"

    def process(self, progress):
            from distutils.spawn import find_executable
            res = find_executable("cygpath", os.path.join(config['paths']['build'], "cygwin", "bin"))
            if res is not None:
                current_dir_cygwin = subprocess.check_output("{0} {1}"
                                .format(res,
                                os.path.join(config["paths"]["build"], "icu", "dist")))

            soutpath = os.path.join(self._context["build_path"], "stdout.log")
            serrpath = os.path.join(self._context["build_path"], "stderr.log")
            with open(soutpath, "w") as sout:
                with open(serrpath, "w") as serr:
                    res = find_executable("bash", os.path.join(config['paths']['build'], "cygwin", "bin"))
                    proc = subprocess.Popen([res, "runConfigureICU", "Cygwin/MSVC", "--prefix"
                                            , "{}".format(current_dir_cygwin)],
                             env=icu_environment(),
                             cwd=os.path.join(self._context["build_path"], "source"),
                             shell=True,
                             stdout=sout, stderr=serr)
                proc.communicate()
                if proc.returncode != 0:
                    logging.error("failed to run icu runConfigureICU (returncode %s), see %s and %s",
                                  proc.returncode, soutpath, serrpath)
                    return False

            return True


Convert_icu = build.Run(r"dos2unix -f configure",
                        environment=icu_environment(),
                        working_directory=lambda: os.path.join(config["paths"]["build"], "icu", "source"))

icu = Project('icu') \
        .depend(build_icu
                .depend(ConfigureIcu()
                        .depend(Convert_icu
                                .depend(Patch.Replace("source/io/ufile.c",
                                                      "#if U_PLATFORM_USES_ONLY_WIN32_API",
                                                      "#if U_PLATFORM_USES_ONLY_WIN32_API && _MSC_VER < 1900")
                                        .depend(sourceforge.Release("icu","ICU4C/{0}.{1}/icu4c-{0}_{1}-src.tgz"
                                                                    .format(icu_version,icu_version_minor),tree_depth=1)
                                                                            .set_destination("icu")
                                                )
                                        )
                                )
                        )
                )\
        .depend("cygwin")
