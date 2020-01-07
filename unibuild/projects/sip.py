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
import logging
import os.path
import shutil
import patch

from glob import glob
from subprocess import Popen

from config import config
from unibuild import Project
from unibuild.modules import build, pipdownload
from unibuild.projects import python

sip_version = config['sip_version']
sip_dev = False
arch = "{}".format("" if config['architecture'] == 'x86' else "amd64")


if config['sip_dev_version']:
    sip_version += ".dev" + config['sip_dev_version']
    sip_dev = True


python_version = config.get('python_version', "3.7") + config.get('python_version_minor', ".0")
python_path = os.path.join(config['paths']['build'], "python-{}".format(config['python_version'] + config['python_version_minor']))

sip_url = pipdownload.PIPDownload("sip", sip_version, tree_depth=1)


def sip_environment():
    result = config['__environment'].copy()
    result['LIB'] += os.path.join(python_path, "PCbuild", arch)
    logging.debug(os.path.join(os.path.join(config['paths']['build'], "Python-{}".format(config['python_version'] + config['python_version_minor'])), "PCbuild", arch))
    return result


class SipSetup(build.Builder):
    def __init__(self):
        super(SipSetup, self).__init__()

    @property
    def name(self):
        return "sip setup module"

    def process(self, progress):
        soutpath = os.path.join(self._context["build_path"], "stdout.log")
        serrpath = os.path.join(self._context["build_path"], "stderr.log")

        with open(soutpath, "w") as sout:
            with open(serrpath, "w") as serr:
                bp = python.python['build_path']

                logging.debug("Ensuring pip exists")
                proc = Popen([os.path.join(bp, "PCbuild", arch, "python.exe"), "-m", "ensurepip"],
                    env=sip_environment(),
                    cwd=bp,
                    shell=True,
                    stdout=sout, stderr=serr)
                proc.communicate()
                if proc.returncode != 0:
                    logging.error("failed to run sip setup.py (returncode %s), see %s and %s",
                                  proc.returncode, soutpath, serrpath)
                    return False

                logging.debug("SIP base setup")
                proc = Popen([os.path.join(bp, "PCbuild", arch, "python.exe"), "setup.py", "install"],
                    env=sip_environment(),
                    cwd=self._context["build_path"],
                    shell=True,
                    stdout=sout, stderr=serr)
                proc.communicate()
                if proc.returncode != 0:
                    logging.error("failed to run sip setup.py (returncode %s), see %s and %s",
                                  proc.returncode, soutpath, serrpath)
                    return False

                if config["Appveyor_Build"] is False:
                    logging.debug("Generating sip.h")
                    proc = Popen([os.path.join(bp, "Scripts", "sip-module.exe"), "--sip-h", "PyQt5.sip"],
                                 env=sip_environment(),
                                 cwd=config["paths"]["download"],
                                 shell=True,
                                 stdout=sout, stderr=serr)
                    proc.communicate()
                    if proc.returncode != 0:
                        logging.error("failed to run sip-module (returncode %s), see %s and %s",
                                      proc.returncode, soutpath, serrpath)
                        return False

                    logging.debug("Copy sip.h into python includes")
                    shutil.copy(os.path.join(config["paths"]["download"], "sip.h"), os.path.join(bp, "Include", "sip.h"))

        return True

    def patch_siputils(self):
        patch_file = os.path.join(config['__Umbrella_path'], "patches", "siputils.py.patch")
        savedpath = os.getcwd()
        os.chdir(self._context["build_path"])
        pset = patch.fromfile(patch_file)
        pset.apply()
        os.chdir(savedpath)

sip = Project('sip').depend(SipSetup()
                      .depend("Python")
                      .depend(sip_url))
