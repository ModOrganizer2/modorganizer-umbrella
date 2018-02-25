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


class CIDict(dict):
    """
    case insensitive dictionary
    based on this Stack Overflow post:
     http://stackoverflow.com/questions/2082152/case-insensitive-dictionary/32888599
    """

    def __init__(self, *args, **kwargs):
        super(CIDict, self).__init__(*args, **kwargs)
        self.__convert_keys()

    def copy(self):
        return self.__class__(super(CIDict, self).copy())

    def __getitem__(self, key):
        return super(CIDict, self).__getitem__(self.__class__.__key(key))

    def __setitem__(self, key, value):
        super(CIDict, self).__setitem__(self.__class__.__key(key), value)

    def __delitem__(self, key):
        return super(CIDict, self).__delitem__(self.__class__.__key(key))

    def __contains__(self, key):
        return super(CIDict, self).__contains__(self.__class__.__key(key))

    def has_key(self, key):
        return super(CIDict, self).__contains__(self.__class__.__key(key))

    def pop(self, key, *args, **kwargs):
        return super(CIDict, self).pop(self.__class__.__key(key), *args, **kwargs)

    def get(self, key, *args, **kwargs):
        return super(CIDict, self).get(self.__class__.__key(key), *args, **kwargs)

    def setdefault(self, key, *args, **kwargs):
        return super(CIDict, self).setdefault(self.__class__.__key(key), *args, **kwargs)

    def update(self, e=None, **f):
        super(CIDict, self).update(self.__class__(e))
        super(CIDict, self).update(self.__class__(**f))

    @classmethod
    def __key(cls, key):
        return key.lower() if isinstance(key, basestring) else key

    def __convert_keys(self):
        for k in list(self.keys()):
            v = super(CIDict, self).pop(k)
            self.__setitem__(k, v)
