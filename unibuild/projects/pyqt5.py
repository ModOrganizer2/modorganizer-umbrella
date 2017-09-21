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


from unibuild.modules import sourceforge, build, Patch
from unibuild.utility import lazy
from unibuild.utility.lazy import doclambda
from unibuild import Project
from config import config
from subprocess import Popen
from glob import glob
import errno
import shutil
import os
import logging

import qt5  # import to get at qt version information
import sip
import python

icu_version = config['icu_version']

def make_sure_path_exists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


def pyqt5_env():
    res = config['__environment'].copy()
    res['path'] = ";".join([
        os.path.join(config['paths']['build'], "qt5", "bin"),
        os.path.join(config['paths']['build'], "sip-{}".format(sip.sip_version), "sipgen"),
        ]) + ";" + res['path']
    res['LIB'] = os.path.join(config["__build_base_path"], "install", "libs") + ";" + res['LIB']
    res['pythonhome'] = python.python['build_path']
    return res


def copy_pyd(context):
        make_sure_path_exists(os.path.join(config["__build_base_path"], "install", "bin", "plugins", "data", "PyQt5"))
        srcdir = os.path.join(python.python['build_path'], "Lib", "site-packages", "PyQt5")
        dstdir = os.path.join(config["__build_base_path"], "install", "bin", "plugins", "data", "PyQt5")
        shutil.copy(os.path.join(srcdir, "__init__.py"),dstdir)
        shutil.copy(os.path.join(srcdir, "QtCore.pyd"), dstdir)
        shutil.copy(os.path.join(srcdir, "QtGui.pyd"),dstdir)
        shutil.copy(os.path.join(srcdir, "QtWidgets.pyd"), dstdir)
        return True


class PyQt5Configure(build.Builder):
    def __init__(self):
        super(PyQt5Configure, self).__init__()

    @property
    def name(self):
        return "pyqt configure"

    def process(self, progress):
        soutpath = os.path.join(self._context["build_path"], "stdout.log")
        serrpath = os.path.join(self._context["build_path"], "stderr.log")
        with open(soutpath, "w") as sout:
            with open(serrpath, "w") as serr:
                bp = python.python['build_path']

                proc = Popen([os.path.join(python.python['build_path'],"PCbuild","amd64","python.exe"), "configure.py", "--confirm-license",
                              "-b", bp,
                              "-d", os.path.join(bp, "Lib", "site-packages"),
                              "-v", os.path.join(bp, "sip", "PyQt5"),
                              "--sip-incdir", os.path.join(bp, "Include"),
                              "--spec=win32-msvc"],
                             env=pyqt5_env(),
                             cwd=self._context["build_path"],
                             shell=True,
                             stdout=sout, stderr=serr)
                proc.communicate()
                if proc.returncode != 0:
                    logging.error("failed to run pyqt configure.py (returncode %s), see %s and %s",
                                  proc.returncode, soutpath, serrpath)
                    return False

        return True


Project("PyQt5") \
    .depend(build.Execute(copy_pyd)
            .depend(Patch.Copy([os.path.join(qt5.qt_inst_path, "bin", "Qt5Core.dll"),
                                os.path.join(qt5.qt_inst_path, "bin", "Qt5Xml.dll"),
                                os.path.join(config['paths']['build'], "icu" , "dist", "lib", "icudt{}.dll".format(icu_version)),
                                os.path.join(config['paths']['build'], "icu", "dist", "lib", "icuin{}.dll".format(icu_version)),
                                os.path.join(config['paths']['build'], "icu", "dist", "lib", "icuuc{}.dll".format(icu_version))],
                               doclambda(lambda: python.python['build_path'], "python path"))
                    .depend(build.Make(environment=lazy.Evaluate(pyqt5_env)).install()
                            .depend(PyQt5Configure()
                                    .depend("sip")
                                    .depend("Qt5")
                                    .depend(sourceforge.Release("pyqt",
                                                                "PyQt5/PyQt-{0}/PyQt5_gpl-{0}.zip"
                                                                .format(qt5.qt_version),
                                                                tree_depth=1))
                                    )
                            )
                    )
            )

