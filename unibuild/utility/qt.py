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
import logging
import os.path
import sys
import shutil

from config import config
from unibuild.utility.config_utility import program_files_folders
from unibuild.utility.visualstudio import vc_year


def get_qt_install(qt_version, qt_version_minor, vc_version):
    # Start with the custom Qt install path, overrides automatic detection
    try:
        p = os.path.join(config['qt_CustomInstallPath'], "{}".format(qt_version + "." + qt_version_minor
                                                                    if qt_version_minor != '' else qt_version),
                             "msvc{0}_64".format(vc_year(vc_version)))
        f = os.path.join(p, "bin", "qmake.exe")
        if os.path.isfile(f):
            return os.path.realpath(p)
    except Exception:
        pass

    try:
        for baselocation in program_files_folders:
            # Offline installer default location
            p = os.path.join(baselocation, "Qt", "Qt{}".format(qt_version + "." + qt_version_minor
                             if qt_version_minor != '' else qt_version), "{}".format(qt_version + "." + qt_version_minor
                             if qt_version_minor != '' else qt_version), "msvc{0}_64".format(vc_year(vc_version)))
            f = os.path.join(p, "bin", "qmake.exe")
            if os.path.isfile(f):
                return os.path.realpath(p)
            # Online installer default location
            p = os.path.join(baselocation, "Qt", "{}".format(qt_version + "." + qt_version_minor
                                                             if qt_version_minor != '' else qt_version),
                             "msvc{0}_64".format(vc_year(vc_version)))
            f = os.path.join(p, "bin", "qmake.exe")
            if os.path.isfile(f):
                return os.path.realpath(p)
    except Exception:
        pass

    # Look in the path
    try:
        f = shutil.which("qmake.exe")
        if f is not None and os.path.isfile(f):
            return os.path.realpath(f)
    except Exception:
        pass

    # Look for qtcreator.exe, which is in %qt%/Tools/QtCreator/bin, then walk
    # back up to the root from there
    try:
        f = shutil.which("qtcreator.exe")
        if f is not None and os.path.isfile(f):
            root = os.path.join(os.path.dirname(f), "..", "..", "..")

            p = os.path.join(root, "{}".format(qt_version + "." + qt_version_minor
                                               if qt_version_minor != '' else qt_version),
                             "msvc{0}_64".format(vc_year(vc_version)))
            f = os.path.join(p, "bin", "qmake.exe")
            if os.path.isfile(f):
                return os.path.realpath(p)
    except Exception:
        pass

    return None


def qt_install(qt_version, qt_version_minor, vc_version):
    config["paths"]["qt_binary_install"] = get_qt_install(qt_version, qt_version_minor, vc_version)
    if not config["paths"]["qt_binary_install"]:
        if qt_version_minor != '':
            qt_v = qt_version + "." + qt_version_minor
        else:
            qt_v = qt_version
        logging.error("Unable to find qmake.exe, please make sure you have QT %s installed. If it is installed "
                      "please point the 'qt_CustomInstallPath' in the config.py to your Qt installation.", qt_v)
        sys.exit(1)

def get_base_qt_path():
    return os.path.join(config["paths"]["qt_binary_install"], "..", "..")
