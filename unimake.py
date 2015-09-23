import eggs
from unibuild.manager import TaskManager
from unibuild.progress import Progress
from unibuild.project import Project
from unibuild import Task
from config import config
from subprocess import Popen, PIPE
import imp
import sys
import logging
import networkx as nx
import tempfile
import os.path
import argparse


def progress_callback(percentage):
    sys.stdout.write("\r%d%%" % percentage)
    sys.stdout.flush()


def draw_graph(graph, filename):
    # neither pydot nor pygraphviz reliably find graphviz on windows. gotta do everything myself...
    from subprocess import call

    graph_file_name = os.path.join(tempfile.gettempdir(), "graph.dot")
    nx.write_dot(graph, graph_file_name)

    call([config['paths']['graphviz'], "-Tpng", graph_file_name, "-o", "{}.png".format(filename)])


def extract_independent(graph):
    """
    :param graph:
    :type graph: nx.DiGraph
    :return:
    """
    independent = []
    for node in graph.nodes_iter():
        if graph.out_degree(node) == 0:
            independent.append(node)
    return independent


def visual_studio_environment():
    # when using visual stuio we need to set up the environment correctly
    arch = "amd64" if config["architecture"] == 'x86_64' else "x86"
    proc = Popen([os.path.join(config['paths']['visual_studio'], "vcvarsall.bat"), arch, "&&", "SET"],
                 stdout=PIPE, stderr=PIPE)
    stdout, stderr = proc.communicate()
    if proc.returncode != 0:
        logging.error("failed to set up environment (returncode %s): %s", proc.returncode, stderr)
        return False

    vcenv = {}

    for line in stdout.splitlines():
        key, value = line.split("=", 1)
        vcenv[key] = value
    return vcenv


def init_config(args):
    for d in config["paths"].keys():
        config["paths"][d] = config["paths"][d].format(base_dir=args.destination)
    config["__environment"] = visual_studio_environment()
    config["__build_base_path"] = args.destination
    if "PYTHON" not in config["__environment"]:
        config["__environment"]["PYTHON"] = sys.executable


def recursive_remove(graph, node):
    if not isinstance(graph.node[node]["task"], Project):
        for ancestor in graph.predecessors(node):
            recursive_remove(graph, ancestor)
    graph.remove_node(node)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', default='makefile.uni.py', help='sets the build script')
    parser.add_argument('-d', '--destination', default='.', help='output directory (base for download and build)')
    parser.add_argument('target', nargs='*', help='make target')
    args = parser.parse_args()

    init_config(args)

    for d in ["download", "build", "progress"]:
        if not os.path.exists(config["paths"][d]):
            os.makedirs(config["paths"][d])

    time_format = "%(asctime)-15s %(message)s"
    logging.basicConfig(format=time_format, level=logging.DEBUG)

    logging.debug("building dependency graph")
    manager = TaskManager()
    imp.load_source("build", args.file)
    build_graph = manager.create_graph({})
    assert isinstance(build_graph, nx.DiGraph)

    draw_graph(build_graph, "graph")

    if args.target:
        for target in args.target:
            manager.enable(build_graph, target)
    else:
        manager.enable_all(build_graph)

    logging.debug("processing tasks")
    independent = extract_independent(build_graph)
    while independent:
        for node in independent:
            task = build_graph.node[node]["task"]
            task.prepare()
            if build_graph.node[node]["enable"] and not task.already_processed():
                progress = Progress()
                progress.set_change_callback(progress_callback)
                logging.debug("run task \"{0}\"".format(node))
                if task.process(progress):
                    task.mark_success()
                else:
                    if task.fail_behaviour == Task.FailBehaviour.FAIL:
                        logging.critical("task %s failed", node)
                        return 1
                    elif task.fail_behaviour == Task.FailBehaviour.SKIP_PROJECT:
                        recursive_remove(build_graph, node)
                        break
                    elif task.fail_behaviour == Task.FailBehaviour.CONTINUE:
                        # nothing to do
                        pass

            build_graph.remove_node(node)

        independent = extract_independent(build_graph)


if __name__ == "__main__":
    main()
