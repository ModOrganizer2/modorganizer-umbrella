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


import eggs
from unibuild.manager import TaskManager
from unibuild.progress import Progress
from unibuild.project import Project
from unibuild import Task
from unibuild.utility import CIDict
from config import config, vs_editions, get_from_hklm
from subprocess import Popen, PIPE
import imp
import sys
import logging
import networkx as nx
import tempfile
import os.path
import argparse
import re

def progress_callback(job, percentage):
    if not percentage and not job:
        sys.stdout.write("\n")
    else:
        pb_length = 50
        filled = int((pb_length * percentage) / 100)  # cast to int may be necessary in python 3
        #sys.stdout.write("\r%d%%" % percentage)
        sys.stdout.write("\r%s [%s%s] %d%%" % (job, "=" * filled, " " * (pb_length - filled), percentage))

    sys.stdout.flush()


def draw_graph(graph, filename):
    if config['paths']['graphviz']:
        # neither pydot nor pygraphviz reliably find graphviz on windows. gotta do everything myself...
        from subprocess import call
        graph_file_name = os.path.join(os.getcwd(), "graph.dot")
        nx.write_dot(graph, graph_file_name)

        call([config['paths']['graphviz'],
              "-Tpng", "-Edir=back", "-Gsplines=ortho", "-Grankdir=BT", "-Gconcentrate=true", "-Nshape=box", "-Gdpi=192",
              graph_file_name,
              "-o", "{}.png".format(filename)])
    else:
        print("graphviz path not set")


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


def vc_year(vc_version):
    return "2017" if vc_version == "15.0" else ""


# No entries for vs 2017 in the stadard registry, check environment then look in the default installation dir
def get_visual_studio_2017_or_more(vc_version):
    try:
        if os.environ["VisualStudioVersion"] == vc_version:
            p = os.path.join(os.environ["VSINSTALLDIR"], "VC", "Auxiliary", "Build")
            f = os.path.join(p, "vcvarsall.bat")
            res = os.path.isfile(f)
            if res is not None:
               return os.path.realpath(p)
    except:
        res = None

    for edition in vs_editions:
        s = os.environ["ProgramFiles(x86)"]
        p = os.path.join(s, "Microsoft Visual Studio", vc_year(vc_version), edition, "VC", "Auxiliary", "Build")
        f = os.path.join(p, "vcvarsall.bat")
        if os.path.isfile(f):
            return os.path.realpath(p)


def get_visual_studio_2015_or_less(vc_version):
    return os.path.realpath(
        os.path.join(get_from_hklm(r"SOFTWARE\Microsoft\VisualStudio\{}".format(vc_version),
                                   "InstallDir", True),
                     "..", "..", "VC"
                     )
    )


def visual_studio(vc_version):
    config["paths"]["visual_studio"] = get_visual_studio_2015_or_less(vc_version) if vc_version < "15.0" else get_visual_studio_2017_or_more(vc_version)


def visual_studio_environment():
    # when using visual studio we need to set up the environment correctly
    arch = "amd64" if config["architecture"] == 'x86_64' else "x86"
    proc = Popen([os.path.join(config['paths']['visual_studio'], "vcvarsall.bat"), arch, "&&", "SET"],
                     stdout=PIPE, stderr=PIPE)
    stdout, stderr = proc.communicate()
    if proc.returncode != 0:
        logging.error("failed to set up environment (returncode %s): %s", proc.returncode, stderr)
        return False

    vcenv = CIDict()

    for line in stdout.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            vcenv[key] = value
    return vcenv


def init_config(args):
    for d in config['paths'].keys():
        if isinstance(config['paths'][d], str):
            config['paths'][d] = config['paths'][d].format(base_dir=os.path.abspath(args.destination))

    if args.set:
        for setting in args.set:
            key, value = setting.split('=', 2)
            path = key.split('.')
            cur = config
            for ele in path[:-1]:
                cur = cur.setdefault(ele, {})
            cur[path[-1]] = value

    if config['architecture'] not in ['x86_64', 'x86']:
        raise ValueError("only architectures supported are x86 and x86_64")

    visual_studio(config["vc_version"]) # forced set after args are evaluated
    config['__environment'] = visual_studio_environment()
    config['__build_base_path'] = os.path.abspath(args.destination)

    if 'PYTHON' not in config['__environment']:
        config['__environment']['PYTHON'] = sys.executable

    qtcreator_config_path = r"C:/Users/modorganizer/AppData/Roaming/QtProject"

    if os.path.isdir(qtcreator_config_path):
        from ConfigParser import RawConfigParser
        parser = RawConfigParser()
        parser.read(os.path.join(qtcreator_config_path, "qtcreator.ini"))
        config['qt_environment_id'] = parser.get('ProjectExplorer', 'Settings\\EnvironmentId')
        config['qt_environment_id'] = re.sub(r"@ByteArray\((.*)\)", r"\1", config['qt_environment_id'])

        import xml.etree.ElementTree as ET
        tree = ET.parse(os.path.join(qtcreator_config_path, "qtcreator", "profiles.xml"))
        root = tree.getroot()

        profiles = []

        for profile in root.findall("data/valuemap"):
            profiles.append((profile.find("value[@key='PE.Profile.Id']").text,
                             profile.find("value[@key='PE.Profile.Name']").text))

        arch = "64bit" if config["architecture"] == 'x86_64' else "32bit"
        profiles = filter(lambda x: arch in x[1], sorted(profiles, reverse=True))[0]

        config['qt_profile_id'] = profiles[0]
        config['qt_profile_name'] = profiles[1].replace("%{Qt:Version}", "5.5.1")

        """
        kits = sorted([kit.text
                       for kit in root.findall("./data/valuemap/value[@key='Name']")
                       if arch in kit.text],
                      reverse=True)[0]

        print(kits)
        """


def recursive_remove(graph, node):
    if not isinstance(graph.node[node]["task"], Project):
        for ancestor in graph.predecessors(node):
            recursive_remove(graph, ancestor)
    graph.remove_node(node)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', default='makefile.uni.py', help='sets the build script')
    parser.add_argument('-d', '--destination', default='.', help='output directory (base for download and build)')
    parser.add_argument('-s', '--set', action='append', help='set configuration parameters')
    parser.add_argument('-g', '--graph', action='store_true', help='update dependency graph')
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

    if args.graph:
        draw_graph(build_graph, "graph")

    cycles = list(nx.simple_cycles(build_graph))
    if cycles:
        logging.error("There are cycles in the build graph")
        for cycle in cycles:
            logging.info(", ".join(cycle))
        return 1

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
                        logging.debug("finished project \"{}\"".format(node))
                    else:
                        logging.debug("run task \"{}\"".format(node))
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
                    sys.stdout.write("\n")
            except Exception, e:
                logging.error("Task {} failed: {}".format(task.name, e))
                raise

            build_graph.remove_node(node)

        independent = extract_independent(build_graph)


if __name__ == "__main__":
    main()
