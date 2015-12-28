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


from task import Task
from manager import TaskManager, register_project


class Project(Task):

    def __init__(self, name):
        super(Project, self).__init__()
        self.__name = name
        self.__context_data = {}
        self.__enabled = False
        register_project(self)

    @property
    def name(self):
        return self.__name

    @property
    def enabled(self):
        return self.__enabled

    @enabled.setter
    def enabled(self, value):
        self.__enabled = value

    def __getitem__(self, key):
        return self.__context_data[key]

    def __setitem__(self, key, value):
        self.__context_data[key] = value

    def __contains__(self, keys):
        return self.__context_data.__contains__(keys)

    def set_context_item(self, key, value):
        self.__context_data[key] = value
        return self

    def applies(self, parameters):
        return True

    def process(self, progress):
        return True

    def depend(self, task):
        if type(task) == str:
            task_obj = TaskManager().get_task(task)
            if task_obj is None:
                raise KeyError("unknown project \"{}\"".format(task))
            else:
                task = task_obj
        else:
            task.set_context(self)
        return super(Project, self).depend(task)
