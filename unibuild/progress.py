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


class Progress(object):
    def __init__(self):
        self.__minimum = 0
        self.__maximum = 100
        self.__value = 0
        self.__job = ""
        self.__changeCallback = None

    @property
    def maximum(self):
        return self.__maximum

    @maximum.setter
    def maximum(self, new_value):
        self.__maximum = new_value

    @property
    def minimum(self):
        return self.__minimum

    @minimum.setter
    def minimum(self, new_value):
        self.__minimum = new_value

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, new_value):
        self.__value = new_value
        self.__call_callback()

    @property
    def job(self):
        return self.__job

    @job.setter
    def job(self, new_job):
        self.__job = new_job
        self.__call_callback()

    def __call_callback(self):
        if self.__changeCallback is not None:
            self.__changeCallback(self.__job, self.__value * 100 / self.__maximum)

    def finish(self):
        self.__changeCallback(None, None)

    def set_change_callback(self, callback):
        self.__changeCallback = callback
