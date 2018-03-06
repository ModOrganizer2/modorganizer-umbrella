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


import logging
import os
from subprocess import Popen

from config import config
from unibuild.builder import Builder


class Bootstrap(Builder):
    def __init__(self):
        super(Bootstrap, self).__init__()
        self.__arguments = []

    @property
    def name(self):
        return "bootstrap"

    def applies(self, parameters):
        return True

    def fulfilled(self):
        return False

    def process(self, progress):
        if "build_path" not in self._context:
            logging.error("source path not known for {},"
                          " are you missing a matching retrieval script?".format(self.name()))
        soutpath = os.path.join(self._context["build_path"], "stdout.log")
        serrpath = os.path.join(self._context["build_path"], "stderr.log")
        with open(soutpath, "a") as sout:
            with open(serrpath, "a") as serr:
                print "{}> {}".format(self._context["build_path"], "bootstrap.bat")
                proc = Popen(["cmd.exe", "/C", "bootstrap.bat"], cwd=self._context["build_path"],
                             stdout=sout, stderr=serr, env=config['__environment'])
                proc.communicate()
                if proc.returncode != 0:
                    logging.error("failed to bootstrap (returncode %s), see %s and %s",
                                  proc.returncode, soutpath, serrpath)
                    return False
        return True

class B2(Builder):
    def __init__(self, name=None, build_path=None):
        super(B2, self).__init__()
        self.__arguments = []
        self.__name = name
        self.__build_path = build_path

    @property
    def name(self):
        if self._context is None:
            return "b2"
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
        build_path = self.__build_path
        if build_path is None:
          if "build_path" in self._context:
            build_path = self._context["build_path"]
          else:
            logging.error("source path not known for {},"
                          " are you missing a matching retrieval script?".format(self.name()))
        soutpath = os.path.join(build_path, "stdout.log")
        serrpath = os.path.join(build_path, "stderr.log")
        with open(soutpath, "a") as sout:
            with open(serrpath, "a") as serr:
                cmdline = ["b2.exe"]
                if self.__arguments:
                    cmdline.extend(self.__arguments)

                print "{}> {}".format(build_path, ' '.join(cmdline))
                proc = Popen(cmdline, cwd=build_path, stdout=sout, stderr=serr, shell=True, env=config['__environment'])
                proc.communicate()
                if proc.returncode != 0:
                    logging.error("failed to build (returncode %s), see %s and %s",
                                  proc.returncode, soutpath, serrpath)
                    return False
        return True
