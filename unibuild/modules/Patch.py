# Copyright (C) 2015 Sebastian Herbord.  All rights reserved.
# Copyright (C) 2016 - 2018 Mod Organizer contributors.
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
import os.path
import shutil

from unibuild.task import Task
from unibuild.utility.lazy import Lazy


class Replace(Task):
    def __init__(self, filename, search, substitute):
        super(Replace, self).__init__()
        self.__file = filename
        self.__search = search
        self.__substitute = substitute

    @property
    def name(self):
        return "Replace in {}".format(self.__file)

    def process(self, progress):
        full_path = os.path.join(self._context["build_path"], self.__file)
        with open(full_path, "r") as f:
            data = f.read()

        data = data.replace(self.__search, self.__substitute)

        with open(full_path, "w") as f:
            f.write(data)
        return True


class Copy(Task):
    def __init__(self, source, destination):
        super(Copy, self).__init__()
        if isinstance(source, str):
            source = [source]
        self.__source = Lazy(source)
        self.__destination = Lazy(destination)
        self.__filename = ""

    def set_filename(self, name):
        self.__filename = name
        return self

    @property
    def name(self):
        if self.__source.type() == list:
            src = self.__source()[0]
        else:
            src = self.__source.peek()
        return "Copy_{}_".format(os.path.basename(src))

    def process(self, progress):
        if os.path.isabs(self.__destination()):
            full_destination = self.__destination()
        else:
            full_destination = os.path.join(self._context["build_path"], self.__destination())

        final_filepath = full_destination;
        if self.__filename:
            final_filepath = os.path.join(full_destination, self.__filename)

        for source in self.__source():
            if not os.path.isabs(source):
                source = os.path.join(self._context["build_path"], source)
            if not os.path.exists(full_destination):
                os.makedirs(full_destination)
            if os.path.isfile(source):
                shutil.copy(source, final_filepath)
            else:
                print("{} doesn't exist, Can't copy".format(source))

        return True


class CreateFile(Task):
    def __init__(self, filename, content):
        super(CreateFile, self).__init__()
        self.__filename = filename
        self.__content = Lazy(content)

    @property
    def name(self):
        if self._context is not None:
            return "Create File {}-{}".format(self._context.name, self.__filename)
        return "Create File {}".format(self.__filename)

    def process(self, progress):
        full_path = os.path.join(self._context["build_path"], self.__filename)
        with open(full_path, 'w') as f:
            # the call to str is necessary to ensure a lazy initialised content is evaluated now
            f.write(self.__content())

        return True
