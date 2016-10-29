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


from subprocess import Popen
from config import config
from repository import Repository
import os
import logging
from unibuild import Task
from urlparse import urlparse, urlsplit


class SuperRepository(Task):
    def __init__(self, name):
        super(SuperRepository, self).__init__()
        self.__name = name
        self.__context_data = {}
        self.prepare()

    def prepare(self):
        self.__context_data['build_path'] = os.path.join(config['__build_base_path'], "build", self.__name)

    @property
    def path(self):
        return self.__context_data['build_path']

    @property
    def name(self):
        return self.__name

    def __getitem__(self, key):
        return self.__context_data[key]

    def __setitem__(self, key, value):
        self.__context_data[key] = value

    def __contains__(self, keys):
        return self.__context_data.__contains__(keys)

    def process(self, progress):
        if not os.path.isdir(self.path):
            os.makedirs(self.path)
            proc = Popen([config['paths']['git'], "init"],
                         cwd=self.path,
                         env=config['__environment'])
            proc.communicate()
            if proc.returncode != 0:
                logging.error("failed to init superproject %s (returncode %s)", self._name, proc.returncode)
                return False

        return True


class Clone(Repository):
    def __init__(self, url, branch, super_repository=None, update=True):
        super(Clone, self).__init__(url, branch)

        self.__super_repository = super_repository
        self.__base_name = os.path.basename(self._url)
        self.__update = update
        if self.__super_repository is not None:
            self._output_file_path = os.path.join(self.__super_repository.path, self.__determine_name())
            self.depend(super_repository)

    def __determine_name(self):
        return self.__base_name

    def prepare(self):
        self._context['build_path'] = self._output_file_path

    def process(self, progress):
        proc = None
        if os.path.exists(os.path.join(self._output_file_path, ".git")):
            if self.__update and not config.get('offline', False):
                proc = Popen([config['paths']['git'], "pull"],
                             cwd=self._output_file_path,
                             env=config["__environment"])
        else:
            if self.__super_repository is not None:
                proc = Popen([config['paths']['git'], "submodule", "add",
                              "--force", "--name", self.__base_name,
                              self._url, self.__base_name
                              ],
                             cwd=self.__super_repository.path,
                             env=config['__environment'])
            else:
                proc = Popen([config['paths']['git'], "clone", "-b", self._branch,
                              self._url, self._context["build_path"]],
                             env=config["__environment"])

        if proc is not None:
            proc.communicate()
            if proc.returncode != 0:
                logging.error("failed to clone repository %s (returncode %s)", self._url, proc.returncode)
                return False

        return True

    @staticmethod
    def _expiration():
        return config.get('repo_update_frequency', 60 * 60 * 24)   # default: one day

    def set_destination(self, destination_name):
        self.__base_name = destination_name.replace("/", os.path.sep)
        if self.__super_repository is not None:
            self._output_file_path = os.path.join(self.__super_repository.path, self.__base_name)
        else:
            self._output_file_path = os.path.join(config["paths"]["build"], self.__base_name)
        return self
