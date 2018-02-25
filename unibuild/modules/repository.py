# Copyright (C) 2015 Sebastian Herbord.  All rights reserved.
# Copyright (C) 2016 - 2018 Mod Organizer contributors.  All rights reserved.
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
import os

from config import config
from unibuild.retrieval import Retrieval


class Repository(Retrieval):
    def __init__(self, url, branch):
        super(Repository, self).__init__()
        self._url = url
        self._branch = branch
        self._dir_name = os.path.basename(self._url)
        self._output_file_path = os.path.join(config["paths"]["build"], self._dir_name)

    @property
    def name(self):
        return "retrieve {0}".format(self._dir_name)
