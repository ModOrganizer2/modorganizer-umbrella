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
import eggs
from unibuild.manager import TaskManager
from unibuild.progress import Progress
from unibuild.project import Project
from unibuild import Task
from config import config
import imp
import sys
import traceback
import logging
from unibuild.utility.config_setup import init_config, dump_config, check_config
import networkx as nx
import os.path
import argparse
from networkx.drawing.nx_pydot import write_dot

exitcode = 0


def progress_callback(job, percentage):
    if not percentage and not job:
        sys.stdout.write("\n")
    else:
        pb_length = 50
        filled = int((pb_length * percentage) / 100)  # cast to int may be necessary in python 3
        # sys.stdout.write("\r%d%%" % percentage)
        sys.stdout.write("\r%s [%s%s] %d%%" % (job, "=" * filled, " " * (pb_length - filled), percentage))

    sys.stdout.flush()


def draw_graph(graph, filename):
    try:
        if config['paths']['graphviz']:
            # neither pydot nor pygraphviz reliably find graphviz on windows.  gotta do everything myself...
            from subprocess import call
            graph_file_name = os.path.join(os.getcwd(), "graph.dot")
            write_dot(graph, graph_file_name)
            call([config['paths']['graphviz'],
                    "-Tpdf", "-Edir=back", "-Gsplines=ortho", "-Grankdir=BT", "-Gconcentrate=true", "-Nshape=box",
                    "-Gdpi=192",
                    graph_file_name,
                    "-o", "{}.pdf".format(filename)])
        else:
            print("graphviz path not set")
    except KeyError:
        print("graphviz path not set, No graph support")


def extract_independent(graph):
    """
    :param graph:
    :type graph: nx.DiGraph
    :return:
    """
    independent = []
    for node in graph.nodes():
        if graph.out_degree(node) == 0:
            independent.append(node)
    return independent


def recursive_remove(graph, node):
    if not isinstance(graph.node[node]["task"], Project):
        for ancestor in graph.predecessors(node):
            recursive_remove(graph, ancestor)
    graph.remove_node(node)


def main():
    time_format = "%(asctime)-15s %(message)s"
    logging.basicConfig(format=time_format, level=logging.DEBUG)
    logging.debug("  ==== Unimake.py started ===  ")

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', metavar='file', default='makefile.uni.py', help='sets the build script file. eg: -f makefile.uni.py')
    parser.add_argument('-d', '--destination', metavar='path', default='.', help='output directory for all generated folder and files .eg: -d E:/MO2')
    parser.add_argument('-s', '--set', metavar='option=value', action='append', help='set configuration parameters. most of them are in config.py. eg: -s paths.build=build')
    parser.add_argument('-g', '--graph', action='store_true', help='update dependency graph')
    parser.add_argument('-b', '--builddir', metavar='directory', default='build', help='sets build directory. eg: -b build')
    parser.add_argument('-p', '--progressdir', metavar='directory', default='progress', help='sets progress directory. eg: -p progress')
    parser.add_argument('-i', '--installdir', metavar='directory', default='install', help='set install directory. eg: -i directory')
    parser.add_argument('target', nargs='*', help='make this target. eg: modorganizer-archive modorganizer-uibase (you need to delete the progress file. will be fixed eventually)')
    args = parser.parse_args()

    init_config(args)

    for d in ["download", "build", "progress", "install"]:
        if not os.path.exists(config["paths"][d]):
            os.makedirs(config["paths"][d])

    dump_config()
    if not check_config():
        logging.error("Missing pre requisite")
        return False

    py_dir = os.path.dirname(config["paths"]["python"])
    if py_dir.lower() not in os.environ["PATH"].lower().split(os.pathsep):
        os.environ["PATH"] += os.pathsep + py_dir
 
    logging.debug("  Build: args.target=%s", args.target)
    logging.debug("  Build: args.destination=%s", args.destination)

    for target in args.target:
        if target == "Check":
            return True

    logging.debug("building dependency graph")
    manager = TaskManager()
    imp.load_source(args.builddir, args.file)
    build_graph = manager.create_graph({})
    assert isinstance(build_graph, nx.DiGraph)

    if args.graph:
        draw_graph(build_graph, "graph")

    cycles = list(nx.simple_cycles(build_graph))
    if cycles:
        logging.error("There are cycles in the build graph")
        for cycle in cycles:
            logging.info(", ".join(cycle))
        return 1

    ShowOnly = config['show_only']
    RetrieveOnly = config['retrieve_only']
    ToolsOnly = config['tools_only']

    if args.target:
        for target in args.target:
            manager.enable(build_graph, target)
    else:
        manager.enable_all(build_graph)

    logging.debug("processing tasks")
    independent = extract_independent(build_graph)

    while independent:
        for node in independent:
            task = build_graph.node[node]['task']
            try:
                task.prepare()
                if build_graph.node[node]['enable'] and not task.already_processed():
                    progress = Progress()
                    progress.set_change_callback(progress_callback)
                    if isinstance(task, Project):
                        logging.debug("finished project \"%s\"", node)
                    else:
                        logging.debug("run task \"%s\"", node)
                    if not ShowOnly:
                        Retrieve = (-1 != node.find("retrieve")) or (-1 != node.find("download")) or (-1 != node.find("repository"))
                        Tool = (-1 == node.find("modorganizer")) and (-1 == node.find("githubpp"))
                        DoProcess = (Retrieve or not RetrieveOnly) and (Tool or not ToolsOnly)
                        if DoProcess:
                            if task.process(progress):
                                task.mark_success()
                            else:
                                if task.fail_behaviour == Task.FailBehaviour.FAIL:
                                    logging.critical("task %s failed", node)
                                    exitcode = 1
                                    return 1
                                elif task.fail_behaviour == Task.FailBehaviour.SKIP_PROJECT:
                                    recursive_remove(build_graph, node)
                                    break
                                elif task.fail_behaviour == Task.FailBehaviour.CONTINUE:
                                    # nothing to do
                                    pass
                        else:
                            logging.critical("task %s skipped", node)
                        sys.stdout.write("\n")
            except Exception, e:
                logging.error("Task %s failed: %s", task.name, e)
                raise

            build_graph.remove_node(node)

        independent = extract_independent(build_graph)


if __name__ == "__main__":
    try:
        if sys.version < "3":
            exitcode = main()
            if not exitcode == 0:
                sys.exit(exitcode)
        else:
            logging.error("You started unimake with Python 3 but we only support Python 2!")
            sys.exit(1)
    except Exception, e:
        traceback.print_exc(file=sys.stdout)
        sys.exit(1)
