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


from unibuild import Task
from unibuild.builder import Builder
from unibuild.utility.lazy import Lazy
from subprocess import Popen
from config import config
import os.path
import logging

STATIC_LIB = 1
SHARED_LIB = 2
EXECUTABLE = 3


class CPP(Builder):

    def __init__(self, cflags=None):
        super(CPP, self).__init__()
        self.__type = EXECUTABLE
        self.__targets = []
        self.__cflags = cflags or ["-nologo", "-O2", "-MD"]

    @property
    def name(self):
        if self._context is None:
            return "custom build"
        else:
            return "custom build {0}".format(self._context.name)

    def fulfilled(self):
        return False

    def type(self, build_type):
        self.__type = build_type
        return self

    def __gen_build_cmd(self, target, files):
        if self.__type == STATIC_LIB:
            return "link.exe /lib /nologo /out:{0}.lib {1}".format(
                target, " ".join([self.__to_obj(f) for f in files]))
        else:
            raise NotImplementedError("type {} not yet implemented", self.__type)

    def sources(self, target, files, top_level=True):
        self.__targets.append((target, files, self.__gen_build_cmd(target, files), top_level))
        return self

    def custom(self, target, dependencies=None, cmd=None, top_level=False):
        self.__targets.append((target, dependencies, cmd, top_level))
        return self

    @staticmethod
    def __to_obj(filename):
        return "{}.obj".format(os.path.splitext(os.path.basename(filename))[0])

    def gen_makefile(self, path):
        with open(os.path.join(path, "unimakefile"), "w") as mf:
            mf.write("CFLAGS={}\n\n".format(" ".join(self.__cflags)))
            for target in self.__targets:
                files = target[1] or []
                for f in files:
                    mf.write("{}:\n".format(self.__to_obj(f)))
                    mf.write("\t{cl} -c $(CFLAGS) -Fo {file}\n\n".format(cl="cl", file=f))

                mf.write("{0}: {1}\n\t{2}\n\n".format(target[0],
                                                      " ".join([self.__to_obj(f) for f in files]),
                                                      target[2] or ""))

            mf.write("all: {}\n".format(" ".join([target[0]
                                                  for target in self.__targets
                                                  if target[3]])))

    def process(self, progress):
        path = self._context["build_path"]

        self.gen_makefile(path)

        soutpath = os.path.join(self._context["build_path"], "stdout.log")
        serrpath = os.path.join(self._context["build_path"], "stderr.log")
        with open(soutpath, "a") as sout:
            with open(serrpath, "a") as serr:
                command = "{} /f unimakefile all".format(config["tools"]["make"])
                sout.write("running {} in {}\n".format(command, self._context['build_path']))
                proc = Popen(command,
                             env=config["__environment"],
                             cwd=self._context["build_path"],
                             shell=True,
                             stdout=sout, stderr=serr)
                proc.communicate()
                if proc.returncode != 0:
                    logging.error("failed to build custom makefile (returncode %s), see %s and %s",
                                  proc.returncode, soutpath, serrpath)
                    return False
        return True


class Install(Builder):
    def __init__(self, make_tool=None):
        super(Install, self).__init__()
        self.__make_tool = Lazy(make_tool or config['tools']['make'])

    @property
    def name(self):
        if self._context is None:
            return "make install"
        else:
            return "make install {0}".format(self._context.name)

    def process(self, progress):
        if "build_path" not in self._context:
            logging.error("source path not known for {},"
                          " are you missing a matching retrieval script?".format(self.name()))
        soutpath = os.path.join(self._context["build_path"], "stdout.log")
        serrpath = os.path.join(self._context["build_path"], "stderr.log")

        with open(soutpath, "a") as sout:
            with open(serrpath, "a") as serr:
                proc = Popen([self.__make_tool(), "install"],
                             shell=True,
                             env=config["__environment"],
                             cwd=self._context["build_path"],
                             stdout=sout, stderr=serr)
                proc.communicate()
                if proc.returncode != 0:
                    logging.error("failed to install (returncode %s), see %s and %s",
                                  proc.returncode, soutpath, serrpath)
                    return False
        return True


class Make(Builder):
    def __init__(self, make_tool=None, environment=None, working_directory=None):
        super(Make, self).__init__()
        self.__install = False
        self.__make_tool = Lazy(make_tool or config['tools']['make'])
        self.__environment = Lazy(environment)
        self.__working_directory = Lazy(working_directory)

    @property
    def name(self):
        if self._context is None:
            return "make"
        else:
            return "make {0}".format(self._context.name)

    def install(self):
        self.__install = True
        return self

    def process(self, progress):
        if "build_path" not in self._context:
            logging.error("source path not known for {},"
                          " are you missing a matching retrieval script?".format(self.name()))
        soutpath = os.path.join(self._context["build_path"], "stdout.log")
        serrpath = os.path.join(self._context["build_path"], "stderr.log")

        with open(soutpath, "a") as sout:
            with open(serrpath, "a") as serr:
                environment = dict(self.__environment()
                                   if self.__environment() is not None
                                   else config["__environment"])
                cwd = str(self.__working_directory()
                          if self.__working_directory() is not None
                          else self._context["build_path"])

                proc = Popen(self.__make_tool().split(" "),
                             env=environment,
                             cwd=cwd,
                             shell=True,
                             stdout=sout, stderr=serr)
                proc.communicate()
                if proc.returncode != 0:
                    logging.error("failed to run make (returncode %s), see %s and %s",
                                  proc.returncode, soutpath, serrpath)
                    return False

                if self.__install:
                    proc = Popen([config['tools']['make'], "install"],
                                 shell=True,
                                 env=environment,
                                 cwd=cwd,
                                 stdout=sout, stderr=serr)
                    proc.communicate()
                    if proc.returncode != 0:
                        logging.error("failed to install (returncode %s), see %s and %s",
                                      proc.returncode, soutpath, serrpath)
                        return False

        return True


class Execute(Builder):
    def __init__(self, function, name=None):
        super(Execute, self).__init__()
        self.__function = function
        self.__name = name

    @property
    def name(self):
        if self._context is None:
            return "execute {}".format(self.__name or self.__function.func_name)
        else:
            return "execute {}_{}".format(self._context.name, self.__name or self.__function.func_name)

    def process(self, progress):
        return self.__function(context=self._context)


class Run(Builder):
    def __init__(self, command, fail_behaviour=Task.FailBehaviour.FAIL, environment=None, working_directory=None,
                 name=None):
        super(Run, self).__init__()
        self.__command = Lazy(command)
        self.__name = name
        self.__fail_behaviour = fail_behaviour
        self.__environment = Lazy(environment)
        self.__working_directory = Lazy(working_directory)

    @property
    def name(self):
        if self.__name:
            return "run {}".format(self.__name)
        else:
            return "run {}".format(self.__command.peek().split()[0]).replace("\\", "/")

    def process(self, progress):
        if "build_path" not in self._context:
            logging.error("source path not known for {},"
                          " are you missing a matching retrieval script?".format(self.name))

        soutpath = os.path.join(self._context["build_path"], "stdout.log")
        serrpath = os.path.join(self._context["build_path"], "stderr.log")
        with open(soutpath, "w") as sout:
            with open(serrpath, "w") as serr:
                environment = dict(self.__environment()
                                   if self.__environment() is not None
                                   else config["__environment"])
                cwd = str(self.__working_directory()
                          if self.__working_directory() is not None
                          else self._context["build_path"])

                sout.write("running {} in {}".format(self.__command(), cwd))
                proc = Popen(self.__command(),
                             env=environment,
                             cwd=cwd,
                             shell=True,
                             stdout=sout, stderr=serr)
                proc.communicate()
                if proc.returncode != 0:
                    logging.error("failed to run %s (returncode %s), see %s and %s",
                                  self.__command(), proc.returncode, soutpath, serrpath)
                    return False

        return True

class Run_With_Output(Builder):
    def __init__(self, command, fail_behaviour=Task.FailBehaviour.FAIL, environment=None, working_directory=None,
                 name=None):
        super(Run_With_Output, self).__init__()
        self.__command = Lazy(command)
        self.__name = name
        self.__fail_behaviour = fail_behaviour
        self.__environment = Lazy(environment)
        self.__working_directory = Lazy(working_directory)

    @property
    def name(self):
        if self.__name:
            return "run {}".format(self.__name)
        else:
            return "run {}".format(self.__command.peek().split()[0]).replace("\\", "/")

    def process(self, progress):

            environment = dict(self.__environment()
                                   if self.__environment() is not None
                                   else config["__environment"])
            cwd = str(self.__working_directory()
                          if self.__working_directory() is not None
                          else self._context["build_path"])


            proc = Popen(self.__command(),
                             env=environment,
                             cwd=cwd,
                             shell=True)
            proc.communicate()
            if proc.returncode != 0:
                if isinstance(proc.returncode , (str, unicode)):
                    logging.error("failed to run %s (returncode %s), see %s and %s",
                                  self.__command(), proc.returncode)
                    return False
                else:
                    logging.error("failed to run {} (returncode {})".format(self.__command(), proc.returncode))
                    return False

            return True
