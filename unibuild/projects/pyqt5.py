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
from unibuild.modules import build, urldownload, urldownloadany, pipdownload, Patch
from unibuild.projects import python, sip, qt5
from unibuild.utility.config_utility import qt_inst_path, make_sure_path_exists
from unibuild.utility.lazy import doclambda

icu_version = config['icu_version']
pyqt_version = config['pyqt_version']
pyqt_pypi_hash = config['pyqt_pypi_hash']
pyqt_builder_version = config['pyqt_builder_version']
python_version = config.get('python_version', "3.7") + config.get('python_version_minor', ".0")
pyqt_dev = False
arch = "{}".format("" if config['architecture'] == 'x86' else "amd64")
if config['pyqt_dev_version']:
    pyqt_version += ".dev" + config['pyqt_dev_version']
    pyqt_dev = True
qt_binary_install = config["paths"]["qt_binary_install"]
__build_base_path = config["__build_base_path"]

enabled_modules = ["QtCore", "QtGui", "QtWidgets", "QtOpenGL", "_QOpenGLFunctions_2_0",
                   "_QOpenGLFunctions_2_1", "_QOpenGLFunctions_4_1_Core"] #, "_QOpenGLFunctions_ES2"]


def pyqt5_env():
    res = config['__environment'].copy()
    res['path'] = ";".join([os.path.join(qt_binary_install, "bin"),
                            os.path.join(python.python["build_path"], "PCbuild", arch),
                            os.path.join(python.python['build_path']),
                            os.path.join(python.python['build_path'], 'Scripts')])\
                  + ";" + res['path']
    res['LIB'] = os.path.join(__build_base_path, "install", "libs") + ";" + res['LIB']
    res['CL'] = "/MP"
    res['PYTHONHOME'] = python.python['build_path']
    return res


def copy_files(context):
    make_sure_path_exists(os.path.join(__build_base_path, "install", "bin", "plugins", "data", "PyQt5"))
    srcdir = os.path.join(python.python['build_path'], "Lib", "site-packages", "PyQt5")
    dstdir = os.path.join(__build_base_path, "install", "bin", "plugins", "data", "PyQt5")
    shutil.copy(os.path.join(srcdir, "__init__.py"), os.path.join(dstdir, "__init__.py"))
    pyqt_sip_ver = config["pyqt_sip_version"].split('.')
    shutil.copy(os.path.join(sip.sip["build_path"], "sipbuild", "module", "source", "{}.{}".format(pyqt_sip_ver[0], pyqt_sip_ver[1]), "sip.pyi"),
                os.path.join(dstdir, "sip.pyi"))
    for file in glob(os.path.join(srcdir, "sip*")):
        shutil.copy(file, dstdir)
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
    shutil.rmtree(os.path.join(dstdir, "uic"))
    shutil.copytree(
        os.path.join(srcdir, "uic"),
        os.path.join(dstdir, "uic"),
        ignore=shutil.ignore_patterns("__pycache__"))

    return True


def install_builder(context):
    soutpath = os.path.join(context["build_path"], "stdout.log")
    serrpath = os.path.join(context["build_path"], "stderr.log")
    with open(soutpath, "w") as sout:
        with open(serrpath, "w") as serr:
            bp = python.python['build_path']

            logging.debug("Ensuring pip exists")
            proc = Popen([os.path.join(bp, "PCbuild", arch, "python.exe"), "-m", "ensurepip"],
                env=config["__environment"],
                cwd=bp,
                shell=True,
                stdout=sout, stderr=serr)
            proc.communicate()
            if proc.returncode != 0:
                logging.error("failed to run sip setup.py (returncode %s), see %s and %s",
                              proc.returncode, soutpath, serrpath)
                return False

            logging.debug("Ensure PyQt-builder is available")
            proc = Popen([os.path.join(bp, "PCbuild", arch, "python.exe"), "-m", "pip", "install", "PyQt-builder=={}".format(pyqt_builder_version)],
                env=pyqt5_env(),
                cwd=context["build_path"],
                shell=True,
                stdout=sout, stderr=serr)
            proc.communicate()
            if proc.returncode != 0:
                logging.error("failed to install PyQt-builder (returncode %s), see %s and %s",
                              proc.returncode, soutpath, serrpath)
                return False
    return True


def patch_pyqt_installer(context):
    patch_file = os.path.join(config['__Umbrella_path'], "patches", "pyqt5_configure.patch")
    savedpath = os.getcwd()
    tarpath = os.path.join(python.python['build_path'], "Lib", "site-packages", "pyqtbuild")
    os.chdir(tarpath)
    pset = patch.fromfile(patch_file)
    if pset.apply() is False:
        raise Exception('Unable to apply PyQt-builder patch, the patchset likely requires an update')
    os.chdir(savedpath)
    return True


def build_pyqt(context):
    soutpath = os.path.join(context["build_path"], "stdout.log")
    serrpath = os.path.join(context["build_path"], "stderr.log")
    with open(soutpath, "w") as sout:
        with open(serrpath, "w") as serr:
            bp = python.python['build_path']
            logging.debug("Run sip-install")
            proc = Popen([os.path.join(bp, "Scripts", "sip-install.exe"), "--confirm-license", "--verbose",
                          "--pep484-pyi", "--link-full-dll",
                          "--build-dir", os.path.join(context['build_path'], 'build'),
                          "--enable", "pylupdate", "--enable", "pyrcc"]
                         + list(itertools.chain(*[("--enable", s) for s in enabled_modules])),
                         env=pyqt5_env(),
                         cwd=context["build_path"],
                         shell=True,
                         stdout=sout, stderr=serr)
            proc.communicate()
            if proc.returncode != 0:
                logging.error("failed to run sip-install (returncode %s), see %s and %s",
                              proc.returncode, soutpath, serrpath)
                return False
    return True


def prep_sip_pyqt_module(context):
    soutpath = os.path.join(context["build_path"], "stdout.log")
    serrpath = os.path.join(context["build_path"], "stderr.log")
    with open(soutpath, "w") as sout:
        with open(serrpath, "w") as serr:
            bp = python.python['build_path']
            logging.debug("Run sip-module")
            proc = Popen([os.path.join(bp, "Scripts", "sip-module.exe"), "--sdist", "PyQt5.sip"],
                         env=pyqt5_env(),
                         cwd=config["paths"]["download"],
                         shell=True,
                         stdout=sout, stderr=serr)
            proc.communicate()
            if proc.returncode != 0:
                logging.error("failed to run sip-module (returncode %s), see %s and %s",
                              proc.returncode, soutpath, serrpath)
                return False

    return True


def install_sip_pyqt_module(context):
    soutpath = os.path.join(context["build_path"], "stdout.log")
    serrpath = os.path.join(context["build_path"], "stderr.log")
    with open(soutpath, "w") as sout:
        with open(serrpath, "w") as serr:
            bp = python.python['build_path']
            logging.debug("Installing PyQt5.sip")
            proc = Popen([os.path.join(bp, "PCbuild", arch, "python.exe"), "-m", "pip", "install",
                          os.path.join(config["paths"]["download"], "PyQt5_sip-{}.tar.gz".format(config["pyqt_sip_version"]))],
                env=config["__environment"],
                cwd=bp,
                shell=True,
                stdout=sout, stderr=serr)
            proc.communicate()
            if proc.returncode != 0:
                logging.error("failed to install PyQt5.sip (returncode %s), see %s and %s",
                              proc.returncode, soutpath, serrpath)
                return False
    return True


if config.get('Appveyor_Build', True):
    Project("PyQt5") \
            .depend(build.Execute(copy_files)
                    .depend(Patch.Copy([os.path.join(qt_inst_path(), "bin", "Qt5Core.dll"),
                                        os.path.join(qt_inst_path(), "bin", "Qt5Xml.dll")],
                            doclambda(lambda: os.path.join(python.python["build_path"], "PCbuild", arch), "python path"))
                            .depend(
                                    urldownload.URLDownload(
                                        config.get('prebuilt_url') + "PyQt5_gpl-prebuilt-{0}.7z"
                                        .format(pyqt_version), name="PyQt5-prebuilt", clean=False
                                    )
                                    .set_destination("python-{}".format(python_version))
                                    .depend("sip")
                                    .depend("Qt5")
                                    )
                            )
                    )
else:
    if pyqt_dev:
        pyqt_source = urldownloadany.URLDownloadAny((
            urldownload.URLDownload(
                "https://www.riverbankcomputing.com/static/Downloads/PyQt5/{0}/PyQt5-{0}.zip".format(pyqt_version),
                tree_depth=1),
            urldownload.URLDownload(
                "https://www.riverbankcomputing.com/static/Downloads/PyQt5/{0}/PyQt5_gpl-{0}.zip".format(pyqt_version),
                tree_depth=1),
            urldownload.URLDownload(
                "https://www.riverbankcomputing.com/static/Downloads/PyQt5/PyQt5_gpl-{0}.zip".format(pyqt_version),
                tree_depth=1)))
    else:
        # The following does not work cleanly until pip download no longer runs setup.py
        #pyqt_source = pipdownload.PIPDownload("PyQt5", pyqt_version, tree_depth=1)
        pyqt_source = urldownload.URLDownload(
            "https://files.pythonhosted.org/packages/{}/PyQt5-{}.tar.gz".format(pyqt_pypi_hash, pyqt_version),
            tree_depth=1
        )

    Project("PyQt5") \
        .depend(build.Execute(copy_files)
                .depend(Patch.Copy([os.path.join(qt_inst_path(), "bin", "Qt5Core.dll"),
                                    os.path.join(qt_inst_path(), "bin", "Qt5Xml.dll")],
                                   doclambda(lambda: os.path.join(python.python["build_path"], "PCbuild", arch), "python path"))
                        .depend(build.Execute(install_sip_pyqt_module)
                                .depend(build.Execute(prep_sip_pyqt_module)
                                        .depend(build.Execute(build_pyqt)
                                                .depend(build.Execute(patch_pyqt_installer)
                                                        .depend(build.Execute(install_builder)
                                                                .depend("sip")
                                                                .depend("Qt5")
                                                                .depend(pyqt_source)
                                                                )
                                                        )
                                                )
                                        )
                                )
                        )
                )
