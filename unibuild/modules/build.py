
__author__ = 'Tannin'


from unibuild.builder import Builder
from subprocess import Popen
from config import config
from unibuild import Task
import os.path
import logging

STATIC_LIB = 1
SHARED_LIB = 2
EXECUTABLE = 3


class CPP(Builder):

    def __init__(self):
        super(CPP, self).__init__()
        self.__type = EXECUTABLE
        self.__targets = []

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
            for target in self.__targets:
                files = target[1] or []
                for f in files:
                    mf.write("{0}: {1}\n\n".format(self.__to_obj(f), f))

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
                proc = Popen("{} /f unimakefile all".format(config["tools"]["make"]),
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


class Make(Builder):
    def __init__(self, make_tool=None):
        super(Make, self).__init__()
        self.__install = False
        self.__make_tool = make_tool or config['tools']['make']

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
                proc = Popen(self.__make_tool.split(" "),
                             env=config["__environment"],
                             cwd=self._context["build_path"],
                             shell=True,
                             stdout=sout, stderr=serr)
                proc.communicate()
                #-debug-and-release -force-debug-info -opensource -confirm-license -mp -no-compile-examples -nomake tests -nomake examples -no-angle -opengl desktop -no-icu -skip qtactiveqt -skip qtandroidextras -skip qtenginio -skip qtsensors -skip qtserialport -skip qtsvg -skip qtwebkit -skip qtpim -skip qttools -skip qtwebchannel -skip qtwayland -skip qtdoc -skip qtconnectivity -skip qtwebkit-examples
                if proc.returncode != 0:
                    logging.error("failed to run make (returncode %s), see %s and %s",
                                  proc.returncode, soutpath, serrpath)
                    return False

                if self.__install:
                    proc = Popen([config['tools']['make'], "install"],
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


class Run(Builder):
    def __init__(self, command, fail_behaviour=Task.FailBehaviour.FAIL):
        super(Run, self).__init__()
        self.__command = command
        self.__fail_behaviour = fail_behaviour

    @property
    def name(self):
        return "run {}".format(self.__command.split()[0])

    def process(self, progress):
        if "build_path" not in self._context:
            logging.error("source path not known for {},"
                          " are you missing a matching retrieval script?".format(self.name))
        soutpath = os.path.join(self._context["build_path"], "stdout.log")
        serrpath = os.path.join(self._context["build_path"], "stderr.log")
        with open(soutpath, "w") as sout:
            with open(serrpath, "w") as serr:
                sout.write("running {}".format(self.__command))
                proc = Popen(self.__command,
                             env=config["__environment"],
                             cwd=self._context["build_path"],
                             shell=True,
                             stdout=sout, stderr=serr)
                proc.communicate()
                if proc.returncode != 0:
                    logging.error("failed to run %s (returncode %s), see %s and %s",
                                  self.__command, proc.returncode, soutpath, serrpath)
                    return False

        return True


