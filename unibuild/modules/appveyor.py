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

from unibuild import Task


class SetProjectFolder(Task):
    def __init__(self, projectpath):
        super(SetProjectFolder, self).__init__()
        self.__projectpath = projectpath

    def prepare(self):
        if 'build_path' not in self._context:
            output_file_path = os.path.join(self.__projectpath)
            self._context['build_path'] = output_file_path

    @property
    def name(self):
        return "setting appveyor project path to {}".format(self.__projectpath)

    def process(self, progress):
        if not os.path.isdir(self.__projectpath):
            logging.error("failed to set appveyor project dir to  %s, doesn't exist", self.__projectpath)
            return False
        return True
