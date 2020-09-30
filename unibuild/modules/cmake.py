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
import os.path
import multiprocessing
import re
import shutil
from subprocess import PIPE, Popen

from config import config
from unibuild.builder import Builder
from unibuild.utility.context_objects import on_exit
from unibuild.utility.enum import enum
from unibuild.utility.visualstudio import vc_year


class CMake(Builder):
    def __init__(self):
        super(CMake, self).__init__()
        self.__arguments = []
        self.__install = False

    @property
    def name(self):
        if config['architecture'] == 'x86_64':
          suffix = ""
        else:
          suffix = "_32"

        if self._context is None:
            return "cmake" + suffix
        return "cmake{} {}".format(suffix, self._context.name)

    def applies(self, parameters):
        return True

    def fulfilled(self):
        return False

    def arguments(self, arguments):
        self.__arguments = arguments
        return self

    def install(self):
        self.__install = True
        return self

    def process(self, progress):
        if "build_path" not in self._context:
            logging.error("source path not known for {},"
                          " are you missing a matching retrieval script?".format(self._context.name))
            return False

        if config['architecture'] == 'x86_64':
          suffix = ""
        else:
          suffix = "_32"

        # prepare for out-of-source build
        build_path = os.path.join(self._context["build_path"], "build" + suffix)
        # if os.path.exists(build_path):
        #    shutil.rmtree(build_path)
        try:
            os.mkdir(build_path)
        except Exception:
            pass
        soutpath = os.path.join(self._context["build_path"], "stdout" + suffix + ".log")
        serrpath = os.path.join(self._context["build_path"], "stderr" + suffix + ".log")

        try:
            with on_exit(lambda: progress.finish()):
                with open(soutpath, "w") as sout:
                    with open(serrpath, "w") as serr:
                        cmdline = [config["paths"]["cmake"], "-G", "NMake Makefiles", ".."] + self.__arguments
                        print("{}> {}".format(build_path, ' '.join(cmdline)))
                        proc = Popen(cmdline,
                            cwd=build_path,
                            env=config["__environment"],
                            stdout=sout, stderr=serr)
                        proc.communicate()
                        if proc.returncode != 0:
                            raise Exception("failed to generate makefile (returncode %s), see %s and %s" % (proc.returncode, soutpath, serrpath))

                        cmdline = [config['tools']['make'], "verbose=1"]
                        print("{}> {}".format(build_path, ' '.join(cmdline)))
                        proc = Popen(cmdline,
                                     shell=True,
                                     env=config["__environment"],
                                     cwd=build_path,
                                     stdout=PIPE, stderr=serr)
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

                        if self.__install:
                            cmdline = [config['tools']['make'], "install"]
                            print("{}> {}".format(build_path, ' '.join(cmdline)))
                            proc = Popen(cmdline,
                                         shell=True,
                                         env=config["__environment"],
                                         cwd=build_path,
                                         stdout=sout, stderr=serr)
                            proc.communicate()
                            if proc.returncode != 0:
                                raise Exception("failed to install (returncode %s), see %s and %s" % (proc.returncode, soutpath, serrpath))

        except Exception as e:
            logging.exception(e)
            return False
        return True


class CMakeEdit(Builder):
    Type = enum(VC=1, CodeBlocks=2)

    def __init__(self, ide_type):
        super(CMakeEdit, self).__init__()
        self.__arguments = []
        self.__type = ide_type

    @property
    def name(self):
        if self._context is None:
            return "cmake edit"

        return "cmake edit {}".format(self._context.name)

    def applies(self, parameters):
        return True

    def fulfilled(self):
        return False

    def arguments(self, arguments):
        self.__arguments = arguments
        return self

    def __vc_year(self, version):
        if version == "12.0":
            return "2013"
        elif version == "14.0":
            return "2015"
        elif version == "15.0":
            return "2017"
        elif version == "16.0":
            return "2019"

    def __generator_name(self):
        if self.__type == CMakeEdit.Type.VC:
            return "Visual Studio {} {}" \
                .format(config['vs_version'].split('.')[0], self.__vc_year(config['vs_version']))
        elif self.__type == CMakeEdit.Type.CodeBlocks:
            return "CodeBlocks - NMake Makefiles"

    def prepare(self):
        self._context['edit_path'] = os.path.join(self._context['build_path'], "edit")

    def process(self, progress):
        if "build_path" not in self._context:
            logging.error("source path not known for {},"
                          " are you missing a matching retrieval script?".format(self._context.name))
            return False

        if os.path.exists(self._context['edit_path']):
            shutil.rmtree(self._context['edit_path'])
        os.mkdir(self._context['edit_path'])

        soutpath = os.path.join(self._context["build_path"], "stdout.log")
        serrpath = os.path.join(self._context["build_path"], "stderr.log")

        with open(soutpath, "w") as sout:
            with open(serrpath, "w") as serr:
                proc = Popen([config["paths"]["cmake"], "-G", self.__generator_name(), ".."] + self.__arguments,
                    cwd=self._context['edit_path'],
                    env=config["__environment"],
                    stdout=sout, stderr=serr)
                proc.communicate()
                if proc.returncode != 0:
                    logging.error("failed to generate makefile (returncode %s), see %s and %s",
                                  proc.returncode, soutpath, serrpath)
                    return False

        return True

class CMakeVS(Builder):
    def __init__(self):
        super(CMakeVS, self).__init__()
        self.__arguments = []
        self.__install = False

    @property
    def name(self):
        if self._context is None:
            return "cmake"

        return "cmake {0}".format(self._context.name)

    def applies(self, parameters):
        return True

    def fulfilled(self):
        return False

    def arguments(self, arguments):
        self.__arguments = arguments
        return self

    def install(self):
        self.__install = True
        return self

    def process(self, progress):
        if "build_path" not in self._context:
            logging.error("source path not known for {},"
                          " are you missing a matching retrieval script?".format(self._context.name))
            return False

        # prepare for out-of-source vs build
        build_path = os.path.join(self._context["build_path"], "vsbuild")
        if os.path.exists(build_path):
            shutil.rmtree(build_path)
        try:
            os.mkdir(build_path)
        except Exception:
            pass

        soutpath = os.path.join(self._context["build_path"], "vs_stdout.log")
        serrpath = os.path.join(self._context["build_path"], "vs_stderr.log")

        vs_generator = "Visual Studio {0} {1}".format(config['vs_version'].split(".", 1)[0],vc_year(config['vs_version']))
        # Updated for latest versions of CMake > 3.1 - VS 2019 does not allow use of the deprecated method
        vs_generator_arch = "x64"
        if config["architecture"] == "x86":
            vs_generator_arch = "Win32"

        try:
            with on_exit(lambda: progress.finish()):
                with open(soutpath, "w") as sout:
                    with open(serrpath, "w") as serr:
                        proc = Popen([config["paths"]["cmake"], "-G", vs_generator, "-A", vs_generator_arch, ".."] + self.__arguments,
                            cwd=build_path,
                            env=config["__environment"],
                            stdout=sout, stderr=serr)
                        proc.communicate()
                        if proc.returncode != 0:
                            raise Exception("failed to generate vs project (returncode %s), see %s and %s" % (proc.returncode, soutpath, serrpath))

        except Exception as e:
            logging.exception(e)
            return False

        return True


class CMakeJOM(Builder):
    def __init__(self):
        super(CMakeJOM, self).__init__()
        self.__arguments = []
        self.__install = False

    @property
    def name(self):
        if config['architecture'] == 'x86_64':
          suffix = ""
        else:
          suffix = "_32"

        if self._context is None:
            return "cmake" + suffix
        return "cmake{} {}".format(suffix, self._context.name)

    def applies(self, parameters):
        return True

    def fulfilled(self):
        return False

    def arguments(self, arguments):
        self.__arguments = arguments
        return self

    def install(self):
        self.__install = True
        return self

    def jom_environment(self):
        result = config["__environment"].copy()
        result["PATH"] += ";{}".format(os.path.dirname(os.path.abspath(config["paths"]["jom"])))
        return result

    def process(self, progress):
        if "build_path" not in self._context:
            logging.error("source path not known for {},"
                          " are you missing a matching retrieval script?".format(self._context.name))
            return False

        if config['architecture'] == 'x86_64':
          suffix = ""
        else:
          suffix = "_32"

        # prepare for out-of-source build
        build_path = os.path.join(self._context["build_path"], "build" + suffix)
        # if os.path.exists(build_path):
        #    shutil.rmtree(build_path)
        try:
            os.mkdir(build_path)
        except Exception:
            pass
        soutpath = os.path.join(self._context["build_path"], "stdout" + suffix + ".log")
        serrpath = os.path.join(self._context["build_path"], "stderr" + suffix + ".log")

        try:
            with on_exit(lambda: progress.finish()):
                with open(soutpath, "w") as sout:
                    with open(serrpath, "w") as serr:
                        cmdline = [config["paths"]["cmake"], "-G", "NMake Makefiles JOM", ".."] + self.__arguments
                        print("{}> {}".format(build_path, ' '.join(cmdline)))
                        proc = Popen(cmdline,
                            cwd=build_path,
                            env=self.jom_environment(),
                            stdout=sout, stderr=serr)
                        proc.communicate()
                        if proc.returncode != 0:
                            raise Exception("failed to generate makefile (returncode %s), see %s and %s" % (proc.returncode, soutpath, serrpath))

                        cmdline = [config['paths']['jom'], "/D", "/J", multiprocessing.cpu_count().__str__()]
                        print("{}> {}".format(build_path, ' '.join(cmdline)))
                        proc = Popen(cmdline,
                                     shell=True,
                                     env=config["__environment"],
                                     cwd=build_path,
                                     stdout=PIPE, stderr=serr)
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

                        if self.__install:
                            cmdline = [config['paths']['jom'], "install", "/D", "/J", multiprocessing.cpu_count().__str__()]
                            print("{}> {}".format(build_path, ' '.join(cmdline)))
                            proc = Popen(cmdline,
                                         shell=True,
                                         env=config["__environment"],
                                         cwd=build_path,
                                         stdout=sout, stderr=serr)
                            proc.communicate()
                            if proc.returncode != 0:
                                raise Exception("failed to install (returncode %s), see %s and %s" % (proc.returncode, soutpath, serrpath))

        except Exception as e:
            logging.exception(e)
            return False
        return True