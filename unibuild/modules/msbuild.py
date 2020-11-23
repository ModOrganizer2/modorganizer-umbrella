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
import logging
import os
import re
from subprocess import PIPE, Popen

from unibuild.utility.context_objects import on_exit
from unibuild.modules.build import Builder
from unibuild.utility.lazy import Lazy
from config import config


class MSBuild(Builder):
    def __init__(self, solution, project=None, working_directory=None, project_platform=None,
                 reltarget=None, project_PlatformToolset=None, verbosity=None, environment=None,
                 project_WindowsTargetPlatformVersion=None, project_AdditionalParams=None):
        super(MSBuild, self).__init__()
        self.__solution = solution
        self.__project = project
        self.__working_directory = working_directory
        self.__project_platform = project_platform
        self.__reltarget = reltarget
        self.__project_platformtoolset = project_PlatformToolset
        self.__project_WindowsTargetPlatformVersion = project_WindowsTargetPlatformVersion
        self.__project_AdditionalParams = project_AdditionalParams
        self.__verbosity = verbosity
        self.__environment = Lazy(environment)

    @property
    def name(self):
        suffix_32 = "" if config['architecture'] == 'x86_64' else "_32"
        suffix_project = (" " + self.__project) if self.__project else ""
        if self._context is None:
            return "msbuild" + suffix_32 + suffix_project
        return "msbuild{}{} {}".format(suffix_32, suffix_project, self._context.name)

    def applies(self, parameters):
        return True

    def fulfilled(self):
        return False

    def process(self, progress):
        if "build_path" not in self._context:
            logging.error("source path not known for {},"
                          " are you missing a matching retrieval script?".format(self._context.name))
            return False

        if config['architecture'] == 'x86_64':
            suffix = ""
        else:
            suffix = "_32"

        soutpath = os.path.join(self._context["build_path"], "stdout" + suffix + ".log")
        serrpath = os.path.join(self._context["build_path"], "stderr" + suffix + ".log")


        try:
            with on_exit(lambda: progress.finish()):
                with open(soutpath, "w") as sout:
                    with open(serrpath, "w") as serr:
                        verbosity = "minimal" if self.__verbosity is None else self.__verbosity
                        lverbosity = "normal" if self.__verbosity is None else self.__verbosity
                        reltarget = "Release" if self.__reltarget is None else self.__reltarget
                        environment = dict(self.__environment()
                                           if self.__environment() is not None
                                           else config["__environment"])

                        args = ["msbuild",
                          self.__solution,
                          "/maxcpucount",
                          "/property:Configuration=" + reltarget,
                          "/verbosity:" + verbosity,
                          "/consoleloggerparameters:Summary",
                          "/fileLogger",
                          "/property:RunCodeAnalysis=false",
                          "/fileloggerparameters:Summary;Verbosity=" + lverbosity]


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

                        if self.__project_WindowsTargetPlatformVersion is None:
                            args.append("/p:WindowsTargetPlatformVersion={}".format(config['vc_TargetPlatformVersion']))
                        else:
                            args.append("/p:WindowsTargetPlatformVersion={}".format(self.__project_WindowsTargetPlatformVersion))

                        if self.__project_AdditionalParams:
                            for param in self.__project_AdditionalParams:
                                args.append(param)

                        wdir = str(self.__working_directory or self._context["build_path"])
                        print("{}> {}".format(wdir, ' '.join(args)))
                        proc = Popen(args,
                            env=environment,
                            shell=True,
                            cwd=wdir,
                            stdout=PIPE,
                            stderr=serr)
                        progress.job = "Compiling"
                        progress.maximum = 100
                        while proc.poll() is None:
                            while True:
                                line = proc.stdout.readline().decode("utf-8")
                                if line != '':
                                    match = re.search("^\\[([0-9 ][0-9 ][0-9])%\\]", line)
                                    if match is not None:
                                        progress.value = int(match.group(1))
                                    sout.write(line)
                                else:
                                    break

                        if proc.returncode != 0:
                            raise Exception("failed to build (returncode %s), see %s and %s" % (proc.returncode, soutpath, serrpath))
        #proc.communicate()
        # if proc.returncode != 0:
        #     logging.error("failed to generate makefile (returncode %s), see %s",
        #                   proc.returncode, os.path.join(wdir, "msbuild.log"))
        #     return False

        except Exception as e:
            logging.exception(e)
            return False
        return True
