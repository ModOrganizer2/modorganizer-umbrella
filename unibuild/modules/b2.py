__author__ = 'Tannin'


from unibuild.builder import Builder
from subprocess import Popen
import os
import logging


class B2(Builder):

    def __init__(self):
        super(B2, self).__init__()
        self.__arguments = []

    @property
    def name(self):
        if self._context is None:
            return "b2"
        else:
            return "b2 {0}".format(self._context.name)

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
                             stdout=sout, stderr=serr)
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
