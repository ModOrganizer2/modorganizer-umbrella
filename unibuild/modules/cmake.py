__author__ = 'Tannin'


from unibuild.builder import Builder
from subprocess import Popen
from config import config
import os.path
import logging
import shutil


class CMake(Builder):

    def __init__(self):
        super(CMake, self).__init__()
        self.__arguments = []
        self.__install = False

    @property
    def name(self):
        if self._context is None:
            return "cmake"
        else:
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

        build_path = os.path.join(self._context["build_path"], "build")
        if os.path.exists(build_path):
            shutil.rmtree(build_path)
        os.mkdir(build_path)

        soutpath = os.path.join(self._context["build_path"], "stdout.log")
        serrpath = os.path.join(self._context["build_path"], "stderr.log")

        with open(soutpath, "w") as sout:
            with open(serrpath, "w") as serr:
                proc = Popen(
                    [config["paths"]["cmake"], "-G", "NMake Makefiles", ".."] + self.__arguments,
                    cwd=build_path,
                    env=config["__environment"],
                    stdout=sout, stderr=serr)
                proc.communicate()
                if proc.returncode != 0:
                    logging.error("failed to generate makefile (returncode %s), see %s and %s",
                                  proc.returncode, soutpath, serrpath)
                    return False

                proc = Popen([config['tools']['make'], "verbose=1"],
                             shell=True,
                             env=config["__environment"],
                             cwd=build_path,
                             stdout=sout, stderr=serr)
                proc.communicate()
                if proc.returncode != 0:
                    logging.error("failed to build (returncode %s), see %s and %s",
                                  proc.returncode, soutpath, serrpath)
                    return False

                if self.__install:
                    proc = Popen([config['tools']['make'], "install"],
                                 shell=True,
                                 env=config["__environment"],
                                 cwd=build_path,
                                 stdout=sout, stderr=serr)
                    proc.communicate()
                    if proc.returncode != 0:
                        logging.error("failed to install (returncode %s), see %s and %s",
                                      proc.returncode, soutpath, serrpath)
                        return False

        return True
