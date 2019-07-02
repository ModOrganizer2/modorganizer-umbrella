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
import errno
import itertools
import logging
import os
import shutil
import patch
from glob import glob
from subprocess import Popen

from config import config
from unibuild import Project
from unibuild.modules import build, sourceforge, urldownload, urldownloadany, Patch
from unibuild.projects import python, sip, qt5
from unibuild.utility import lazy
from unibuild.utility.config_utility import qt_inst_path, make_sure_path_exists
from unibuild.utility.lazy import doclambda

icu_version = config['icu_version']
pyqt_version = config['pyqt_version']
python_version = config.get('python_version', "3.7") + config.get('python_version_minor', ".0")
pyqt_dev = False
if config['pyqt_dev_version']:
    pyqt_version += ".dev" + config['pyqt_dev_version']
    pyqt_dev = True
qt_binary_install = config["paths"]["qt_binary_install"]
__build_base_path = config["__build_base_path"]

enabled_modules = ["QtCore", "QtGui", "QtWidgets", "_QOpenGLFunctions_2_1"]


def pyqt5_env():
    res = config['__environment'].copy()
    res['path'] = ";".join([os.path.join(qt_binary_install, "bin"),
        os.path.join(python.python['build_path'])]) + ";" + res['path']
    res['LIB'] = os.path.join(__build_base_path, "install", "libs") + ";" + res['LIB']
    res['CL'] = "/MP"
    res['PYTHONHOME'] = python.python['build_path']
    return res


def copy_pyd(context):
    # fix fir pre compiled deps
    for file in glob(os.path.join(config["paths"]["build"], "PyQt5-{}".format(pyqt_version), "*.bat")):
        shutil.copy(file, os.path.join(python.python['build_path']))
    # for f in glob(os.path.join(build_path, openssl_path, "bin", "ssleay32.dll")):
    #      shutil.copy(f, os.path.join(dest_bin))
    make_sure_path_exists(os.path.join(__build_base_path, "install", "bin", "plugins", "data", "PyQt5"))
    srcdir = os.path.join(python.python['build_path'], "Lib", "site-packages", "PyQt5")
    dstdir = os.path.join(__build_base_path, "install", "bin", "plugins", "data", "PyQt5")
    shutil.copy(os.path.join(srcdir, "__init__.py"), os.path.join(dstdir, "__init__.py"))
    for module in enabled_modules:
        shutil.copy(
            os.path.join(srcdir, module + ".pyd"),
            os.path.join(dstdir, module + ".pyd")
        )
        try:
            shutil.copy(
                os.path.join(srcdir, module + ".pyi"),
                os.path.join(dstdir, module + ".pyi")
            )
        except FileNotFoundError:
            pass

    return True


def copy_init_patch(context):
    shutil.copy2(
        os.path.join(config['__Umbrella_path'], "patches", "PyQt5_init.py"),
        os.path.join(context['build_path'], "__init__.py")
    )
    return True


def init_patch(context):
    try:
        savedpath = os.getcwd()
        os.chdir(context["build_path"])
        pset = patch.fromfile(os.path.join(config['__Umbrella_path'], "patches", "pyqt5_configure_init.patch"))
        pset.apply()
        os.chdir(savedpath)
        return True
    except OSError:
        return False


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
                proc = Popen([os.path.join(python.python['build_path'], "PCbuild", "amd64", "python.exe"), "configure.py",
                     "--confirm-license",
                     "-b", bp,
                     "--verbose",
                     "-d", os.path.join(bp, "Lib", "site-packages"),
                     "-v", os.path.join(bp, "sip", "PyQt5"),
                     "--sip-incdir", os.path.join(bp, "Include")]
                     + list(itertools.chain(*[("--enable", s) for s in enabled_modules])),
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


if config.get('Appveyor_Build', True):
    Project("PyQt5") \
            .depend(build.Execute(copy_pyd)
                    .depend(Patch.Copy([os.path.join(qt_inst_path(), "bin", "Qt5Core.dll"),
                                        os.path.join(qt_inst_path(), "bin", "Qt5Xml.dll")],
                            doclambda(lambda: python.python['build_path'], "python path"))
                            .depend(build.Execute(copy_init_patch)
                                    .depend(urldownload.URLDownload(
                                                config.get('prebuilt_url') + "PyQt5_gpl-prebuilt-{0}.7z"
                                                .format(pyqt_version), name="PyQt5-prebuilt", clean=False
                                            )
                                            .set_destination("python-{}".format(python_version))
                                            .depend("sip")
                                            .depend("Qt5")
                                            )
                                    )
                            )
                    )
else:
    pyqt_source = urldownloadany.URLDownloadAny((
                    urldownload.URLDownload("https://www.riverbankcomputing.com/static/Downloads/PyQt5/{0}/PyQt5_gpl-{0}.zip".format(pyqt_version), tree_depth=1),
                    urldownload.URLDownload("https://www.riverbankcomputing.com/static/Downloads/PyQt5/PyQt5_gpl-{0}.zip".format(pyqt_version), tree_depth=1),
                    sourceforge.Release("pyqt", "PyQt5/PyQt-{0}/PyQt5_gpl-{0}.zip".format(pyqt_version), tree_depth=1)))

    Project("PyQt5") \
        .depend(build.Execute(copy_pyd)
                .depend(Patch.Copy([os.path.join(qt_inst_path(), "bin", "Qt5Core.dll"),
                                    os.path.join(qt_inst_path(), "bin", "Qt5Xml.dll")],
                                   doclambda(lambda: python.python['build_path'], "python path"))
                        .depend(build.Make(environment=lazy.Evaluate(pyqt5_env)).install()
                                .depend(PyQt5Configure()
                                        .depend("sip")
                                        .depend("Qt5")
                                        .depend(build.Execute(init_patch)
                                                .depend(pyqt_source)
                                                )
                                        )
                                )
                        )
                )
