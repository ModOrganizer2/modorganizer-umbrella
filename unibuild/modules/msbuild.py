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

from build import Builder
from config import config


class MSBuild(Builder):
    def __init__(self, solution, project=None, working_directory=None, project_platform=None,
                 project_PlatformToolset=None, verbosity=None):
        super(MSBuild, self).__init__()
        self.__solution = solution
        self.__project = project
        self.__working_directory = working_directory
        self.__project_platform = project_platform
        self.__project_platformtoolset = project_PlatformToolset
        self.__verbosity = verbosity

    @property
    def name(self):
        suffix_32 = "" if config['architecture'] == 'x86_64' else "_32"
        if self._context is None:
            return "msbuild" + suffix_32
        else:
            return "msbuild{} {}".format(suffix_32, self._context.name)

    def applies(self, parameters):
        return True

    def fulfilled(self):
        return False

    def process(self, progress):
        if "build_path" not in self._context:
            logging.error("source path not known for {},"
                          " are you missing a matching retrieval script?".format(self._context.name))
            return False

        verbosity = "minimal" if self.__verbosity is None else self.__verbosity
        lverbosity = "normal" if self.__verbosity is None else self.__verbosity
        args = ["msbuild",
          self.__solution,
          "/maxcpucount",
          "/property:Configuration=Release",
          "/verbosity:"+verbosity,
          "/consoleloggerparameters:Summary",
          "/fileLogger",
          "/fileloggerparameters:Summary;Verbosity="+lverbosity
        ]

        if self.__project_platform is None:
            args.append("/property:Platform={}"
                        .format("x64" if config['architecture'] == 'x86_64' else "win32"))
        else:
            args.append("/property:Platform={}".format(self.__project_platform))

        if self.__project_platformtoolset is not None:
            args.append("/property:PlatformToolset={}"
                        .format(self.__project_platformtoolset))

        if self.__project:
            args.append("/target:{}".format(self.__project))

        wdir = str(self.__working_directory or self._context["build_path"])
        print "{}> {}".format(wdir, ' '.join(args))
        proc = Popen(
            args,
            shell=True,
            cwd=wdir,
            env=config["__environment"])
        proc.communicate()
        if proc.returncode != 0:
            logging.error("failed to generate makefile (returncode %s), see %s",
                          proc.returncode, os.path.join(wdir, "msbuild.log"))
            return False

        return True
