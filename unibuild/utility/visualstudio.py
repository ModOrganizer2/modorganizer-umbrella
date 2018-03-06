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
from unibuild.utility import CIDict
from subprocess import Popen, PIPE


# To detect the editon of VS installed as of VS 2017
vs_editions = ["enterprise",
    "professional",
    "community",]


# No entries for vs 2017 in the stadard registry, check environment then look in the default installation dir
def get_visual_studio_2017_or_more(vc_version):
    try:
        if os.environ["VisualStudioVersion"] == vc_version:
            p = os.path.join(os.environ["VSINSTALLDIR"], "VC", "Auxiliary", "Build")
            f = os.path.join(p, "vcvarsall.bat")
            res = os.path.isfile(f)
            if res is not None:
                return os.path.realpath(p)
            else:
                res = None
    except Exception:
        res = None

    try:
        p = os.path.join(config['vc_CustomInstallPath'], "VC", "Auxiliary", "Build")
        f = os.path.join(p, "vcvarsall.bat")
        res = os.path.isfile(f)
        if res is None:
            res = None
        elif res:
            return os.path.realpath(p)
        else:
            res = None
    except Exception:
        res = None

    for edition in vs_editions:
        s = os.environ["ProgramFiles(x86)"]
        p = os.path.join(s, "Microsoft Visual Studio", vc_year(vc_version), edition, "VC", "Auxiliary", "Build")
        f = os.path.join(p, "vcvarsall.bat")
        if os.path.isfile(f):
            config['paths']['visual_studio_basedir'] = os.path.join(s, "Microsoft Visual Studio", vc_year(vc_version),
                                                                    edition)
            return os.path.realpath(p)


def vc_year(vc_version):
    if vc_version == "15.0":
        return "2017"
    else:
        logging.error("Visual Studio %s is not supported", vc_version)


def visual_studio(vc_version):
    config["paths"]["visual_studio"] = get_visual_studio_2015_or_less(vc_version) if vc_version < "15.0" \
        else get_visual_studio_2017_or_more(vc_version)
    if not config["paths"]["visual_studio"]:
        logging.error("Unable to find vcvarsall.bat, please make sure you have 'Common C++ tools' Installed."
          " If you have changed the default installation folder for VS please set the 'vc_CustomInstallPath' in the config.py file"
          " to the folder you installed VS to (this folder should contain a 'VC' subfolder).")
        sys.exit(1)


def visual_studio_environment():
    # when using visual studio we need to set up the environment correctly
    arch = "amd64" if config["architecture"] == 'x86_64' else "x86"
    if config['paths']['visual_studio']:
        proc = Popen([os.path.join(config['paths']['visual_studio'], "vcvarsall.bat"), arch, "&&", "SET"],
                     stdout=PIPE, stderr=PIPE)
        stdout, stderr = proc.communicate()

        if "Error in script usage. The correct usage is" in stderr:
            logging.error("failed to set up environment (returncode %s): %s", proc.returncode, stderr)
            return False

        if "Error in script usage. The correct usage is" in stdout:
            logging.error("failed to set up environment (returncode %s): %s", proc.returncode, stderr)
            return False

        if proc.returncode != 0:
            logging.error("failed to set up environment (returncode %s): %s", proc.returncode, stderr)
            return False
    else:
        sys.exit(1)

    vcenv = CIDict()

    for line in stdout.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            vcenv[key] = value
    return vcenv
