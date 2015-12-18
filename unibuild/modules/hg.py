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


from unibuild.modules.repository import Repository
from subprocess import Popen
from config import config
import os
import logging


class Clone(Repository):
    def __init__(self, url, branch):
        super(Clone, self).__init__(url, branch)

    def prepare(self):
        self._context["build_path"] = self._output_file_path

    def process(self, progress):
        if os.path.isdir(self._output_file_path):
            proc = Popen([config['paths']['hg'], "pull", "-u"],
                         cwd=self._output_file_path,
                         env=config["__environment"])
        else:
            proc = Popen([config['paths']['hg'], "clone", "-b", self._branch,
                          self._url, self._context["build_path"]],
                         env=config["__environment"])
        proc.communicate()
        if proc.returncode != 0:
            logging.error("failed to clone repository %s (returncode %s)", self._url, proc.returncode)
            return False

        return True

    @staticmethod
    def _expiration():
        return config.get('repo_update_frequency', 60 * 60 * 24)   # default: one day

    def set_destination(self, destination_name):
        self._output_file_path = os.path.join(config["paths"]["build"], destination_name)
        return self
