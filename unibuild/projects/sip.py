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
import logging
import os.path
import shutil
from glob import glob
from subprocess import Popen

from config import config
from unibuild import Project
from unibuild.modules import build, sourceforge, urldownload
from unibuild.projects import python

sip_version = config['sip_version']
python_version = config.get('python_version', "3.7") + config.get('python_version_minor', ".0")
python_path = os.path.join(config['paths']['build'], "python-{}".format(config['python_version'] + config['python_version_minor']))
sip_url = sourceforge.Release("pyqt", "sip/sip-{0}/sip-{0}.zip".format(sip_version), 1)


def sip_environment():
    result = config['__environment'].copy()
    result['LIB'] += os.path.join(python_path, "PCbuild", "amd64")
    logging.debug(os.path.join(os.path.join(config['paths']['build'], "Python-{}".format(config['python_version'] + config['python_version_minor'])), "PCbuild", "amd64"))
    return result


def make_sure_path_exists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


def copy_pyd(context):
    make_sure_path_exists(os.path.join(config["__build_base_path"], "install", "bin", "plugins", "data"))
    os.makedirs(os.path.join(config["__build_base_path"], "install", "bin", "plugins", "data", "PyQt5"))
    for f in glob(os.path.join(python_path, "Lib", "site-packages", "PyQt5", "sip.pyd")):
        shutil.copy(f, os.path.join(config["__build_base_path"],
                                    "install", "bin", "plugins", "data", "PyQt5", "sip.pyd"))
    return True


class SipConfigure(build.Builder):
    def __init__(self):
        super(SipConfigure, self).__init__()

    @property
    def name(self):
        return "sip configure module"

    def process(self, progress):
        soutpath = os.path.join(self._context["build_path"], "stdout.log")
        serrpath = os.path.join(self._context["build_path"], "stderr.log")
        with open(soutpath, "w") as sout:
            with open(serrpath, "w") as serr:
                logging.debug("123 %s", python.python['build_path'])
                bp = python.python['build_path']

                proc = Popen([os.path.join(bp, "PCbuild", "amd64", "python.exe"), "configure.py",
                     "-b", bp,
                     "-d", os.path.join(bp, "Lib", "site-packages"),
                     "-v", os.path.join(bp, "sip"),
                     "-e", os.path.join(bp, "include"),
                     "--sip-module=PyQt5.sip"],
                    env=config["__environment"],
                    cwd=self._context["build_path"],
                    shell=True,
                    stdout=sout, stderr=serr)
                proc.communicate()
                if proc.returncode != 0:
                    logging.error("failed to run sip configure.py (returncode %s), see %s and %s",
                                  proc.returncode, soutpath, serrpath)
                    return False

        return True


Project('sip') \
    .depend(build.Execute(copy_pyd)
            .depend(build.Make(environment=sip_environment()).install()
                    .depend(SipConfigure()
                            .depend("Python")
                            .depend(sip_url))))
