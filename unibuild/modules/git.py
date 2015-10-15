from subprocess import Popen
from config import config
import os
import logging
from repository import Repository


class Clone(Repository):
    def __init__(self, url, branch):
        super(Clone, self).__init__(url, branch)

    def prepare(self):
        self._context["build_path"] = self._output_file_path

    def process(self, progress):
        if os.path.isdir(self._output_file_path):
            proc = Popen([config['paths']['git'], "pull"],
                         cwd=self._output_file_path,
                         env=config["__environment"])
        else:
            proc = Popen([config['paths']['git'], "clone", "-b", self._branch,
                          self._url, self._context["build_path"]],
                         env=config["__environment"])
        proc.communicate()
        if proc.returncode != 0:
            logging.error("failed to clone repository %s (returncode %s)", self._url, proc.returncode)
            return False

        return True

    @staticmethod
    def _expiration():
        return 60 * 60 * 24  # one day

    def set_destination(self, destination_name):
        self._output_file_path = os.path.join(config["paths"]["build"], destination_name)
        return self
