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
from unibuild.modules import sourceforge, build
from subprocess import Popen
from config import config
import os
import logging
import python


sip_version = "4.16.9"


class SipConfigure(build.Builder):
    def __init__(self):
        super(SipConfigure, self).__init__()

    @property
    def name(self):
        return "sip configure"

    def process(self, progress):
        soutpath = os.path.join(self._context["build_path"], "stdout.log")
        serrpath = os.path.join(self._context["build_path"], "stderr.log")
        with open(soutpath, "w") as sout:
            with open(serrpath, "w") as serr:
                bp = python.python['build_path']

                proc = Popen([config['paths']['python'](), "configure.py",
                              "-b", bp,
                              "-d", os.path.join(bp, "Lib", "site-packages"),
                              "-v", os.path.join(bp, "sip"),
                              "-e", os.path.join(bp, "include")
                              ],
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
    .depend(build.Make().install()
            .depend("Python")
            .depend(SipConfigure()
                    .depend(sourceforge.Release("pyqt", "sip/sip-{0}/sip-{0}.zip".format(sip_version), 1))
                    )
            )
