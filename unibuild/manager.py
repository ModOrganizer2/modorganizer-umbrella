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


import networkx as nx
from utility.singleton import Singleton


class TaskManager(object):
    """
    manages task dependency graph
    """
    __metaclass__ = Singleton

    def __init__(self):
        self.__topLevelTask = []

    def add_task(self, task):
        self.__topLevelTask.append(task)

    def get_task(self, name):
        for task in self.__topLevelTask:
            if task.name == name:
                return task
        return None

    def create_graph(self, parameters):
        graph = nx.DiGraph()
        for task in self.__topLevelTask:
            self.__add_task(graph, task, parameters, 0)

        graph.concentrate = True
        return graph

    def enable(self, graph, node):
        """
        recursively enable the node
        :param graph:
        :param node:
        :return:
        """
        for suc in graph.neighbors(node):
            self.enable(graph, suc)
        graph.node[node]["enable"] = True

    def enable_all(self, graph):
        for node in graph.nodes():
            if graph.in_degree(node) == 0:
                self.enable(graph, node)

    def __add_task(self, graph, task, parameters, level):
        if not graph.has_node(task.name):
            graph.add_node(task.name, color='red' if level == 0 else 'blue', peripheries=max(1, 2 - level),
                           task=task, enable=False)

        for dependency in task.dependencies:
            self.__add_task(graph, dependency, parameters, level + 1)
            graph.add_edge(task.name, dependency.name)


def register_project(task):
    TaskManager().add_task(task)
