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


from unibuild.modules import sourceforge, build
from unibuild.utility import lazy
from unibuild import Project
from config import config
from subprocess import Popen
import os
import logging

import qt5  # import to get at qt version information
import sip
import python


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

                env = config['__environment'].copy()
                env['path'] = env['path'] + ";" + ";".join([
                    os.path.join(config["paths"]["build"], "qt5", "bin"),
                    os.path.join(config["paths"]["build"], "sip-{}".format(sip.sip_version)),
                ])

                proc = Popen([str(config['paths']['python']), "configure.py", "--confirm-license",
                              "-b", bp, "-d", bp, "-v", bp],
                             env=env,
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
    .depend(build.Make().install()
            .depend(PyQt5Configure()
                    .depend("sip").depend("Qt5")
                    .depend(sourceforge.Release("pyqt",
                                                "PyQt5/PyQt-{0}.{1}/PyQt-gpl-{0}.{1}.zip"
                                                .format(qt5.qt_version, qt5.qt_version_minor),
                                                tree_depth=1))
                    )
            )

