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
        self.__data = None
        self.__func = func

    def __evaluate(self):
        if self.__data is None:
            self.__data = self.__func()

    def __getattr__(self, item):
        self.__evaluate()
        return getattr(self.__data, item)

    def __getitem__(self, item):
        self.__evaluate()
        return self.__data[item]

    def __str__(self):
        self.__evaluate()
        return str(self.__data)

    def __len__(self):
        if self.__data is not None:
            return len(self.__data)
        else:
            return 0

    def __iter__(self):
        self.__evaluate()
        return iter(self.__data)

    def __add__(self, other):
        self.__evaluate()
        return self.__data + other


class Lazy(object):
    def __init__(self, val):
        if callable(val):
            self.__value = None
            self.__func = val
        else:
            self.__value = val
            self.__func = None

    def __call__(self):
        if self.__func is not None:
            self.__value = self.__func()
            self.__func = None
        return self.__value

    def type(self):
        if self.__value is None:
            return None
        else:
            return type(self.__value)

    def peek(self):
        if self.__value is None:
            return self.__func.func_doc
        else:
            return self.__value


def doclambda(func, doc):
    func.__doc__ = doc
    return func