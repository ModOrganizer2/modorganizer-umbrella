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


from build import Builder
from subprocess import Popen
from config import config
import shutil
import logging
import os


class MSBuild(Builder):

    def __init__(self, solution, project=None):
        super(MSBuild, self).__init__()
        self.__solution = solution
        self.__project = project

    @property
    def name(self):
        if self._context is None:
            return "msbuild"
        else:
            return "msbuild {0}".format(self._context.name)

    def applies(self, parameters):
        return True

    def fulfilled(self):
        return False

    def process(self, progress):
        if "build_path" not in self._context:
            logging.error("source path not known for {},"
                          " are you missing a matching retrieval script?".format(self._context.name))
            return False

        soutpath = os.path.join(self._context["build_path"], "stdout.log")
        serrpath = os.path.join(self._context["build_path"], "stderr.log")

        with open(soutpath, "w") as sout:
            with open(serrpath, "w") as serr:
                args = ["msbuild", self.__solution, "/m", "/property:Configuration=Release"]
                if self.__project:
                    args.append("/target:{}".format(self.__project))
                proc = Popen(
                    args,
                    shell=True,
                    cwd=self._context['build_path'],
                    env=config["__environment"],
                    stdout=sout, stderr=serr)
                proc.communicate()
                if proc.returncode != 0:
                    logging.error("failed to generate makefile (returncode %s), see %s and %s",
                                  proc.returncode, soutpath, serrpath)
                    return False

        return True
