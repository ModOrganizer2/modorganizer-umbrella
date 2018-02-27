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


class Version(object):
    def __init__(self, version_string):
        self.__versionString = version_string

    def __eq__(self, other):
        return self.__versionString == other.__versionString

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        return self.__versionString < other.__versionString

    def __gt__(self, other):
        return self.__versionString > other.__versionString

    def __ge__(self, other):
        return self.__versionString >= other.__versionString

    def __le__(self, other):
        return self.__versionString <= other.__versionString
