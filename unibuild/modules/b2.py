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


import logging
import os
from subprocess import Popen

from config import config
from unibuild.builder import Builder


class B2(Builder):
    def __init__(self, name=None):
        super(B2, self).__init__()
        self.__arguments = []
        self.__name = name

    @property
    def name(self):
        if self._context is None:
            return "b2"
        else:
            return "b2 {}_{}".format(self._context.name, self.__name)

    def applies(self, parameters):
        return True

    def fulfilled(self):
        return False

    def arguments(self, arguments):
        if arguments is None:
            self.__arguments = []
        else:
            self.__arguments = arguments
        return self

    def process(self, progress):
        if "build_path" not in self._context:
            logging.error("source path not known for {},"
                          " are you missing a matching retrieval script?".format(self.name()))
        soutpath = os.path.join(self._context["build_path"], "stdout.log")
        serrpath = os.path.join(self._context["build_path"], "stderr.log")
        with open(soutpath, "a") as sout:
            with open(serrpath, "a") as serr:
                proc = Popen(["cmd.exe", "/C", "bootstrap.bat"], cwd=self._context["build_path"],
                             stdout=sout, stderr=serr, env=config['__environment'])
                proc.communicate()
                if proc.returncode != 0:
                    logging.error("failed to bootstrap (returncode %s), see %s and %s",
                                  proc.returncode, soutpath, serrpath)
                    return False

                cmdline = ["b2.exe"]
                if self.__arguments:
                    cmdline.extend(self.__arguments)

                proc = Popen(cmdline, cwd=self._context["build_path"], stdout=sout, stderr=serr, shell=True)
                proc.communicate()
                if proc.returncode != 0:
                    logging.error("failed to build (returncode %s), see %s and %s",
                                  proc.returncode, soutpath, serrpath)
                    return False
        return True
