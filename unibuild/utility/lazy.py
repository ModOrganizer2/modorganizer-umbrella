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


class Get(object):
    def __init__(self, dictionary, key):
        super(Get, self).__init__()
        self.__dict = dictionary
        self.__key = key

    def __get__(self, instance, owner):
        return self.__dict[self.__key]


class Evaluate(object):
    def __init__(self, func):
        super(Evaluate, self).__init__()
        self.__func = func

    def __get__(self, instance, owner):
        return self.__func()
