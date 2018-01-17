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
from config import config, vs_editions, program_files_folders
from subprocess import Popen, PIPE
import imp
import sys
import traceback
import logging
import networkx as nx
import tempfile
import os.path
import argparse
import re
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
            # neither pydot nor pygraphviz reliably find graphviz on windows. gotta do everything myself...
            from subprocess import call
            graph_file_name = os.path.join(os.getcwd(), "graph.dot")
            write_dot(graph, graph_file_name)
            call([config['paths']['graphviz'],
                    "-Tpng", "-Edir=back", "-Gsplines=ortho", "-Grankdir=BT", "-Gconcentrate=true", "-Nshape=box",
                    "-Gdpi=192",
                    graph_file_name,
                    "-o", "{}.png".format(filename)])
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


def vc_year(vc_version):
    if vc_version == "15.0":
        return "2017"
    elif vc_version == "14.0":
        return "2015"
    else:
        ""

        # No entries for vs 2017 in the stadard registry, check environment then look in the default installation dir


def get_visual_studio_2017_or_more(vc_version):
    try:
        if os.environ["VisualStudioVersion"] == vc_version:
            p = os.path.join(os.environ["VSINSTALLDIR"], "VC", "Auxiliary", "Build")
            f = os.path.join(p, "vcvarsall.bat")
            res = os.path.isfile(f)
            if res is not None:
                return os.path.realpath(p)
            else:
                res = None
    except:
        res = None

    try:
        p = os.path.join(config['vc_CustomInstallPath'], "VC", "Auxiliary", "Build")
        f = os.path.join(p, "vcvarsall.bat")
        res = os.path.isfile(f)
        if res is None:
            res = None
        elif res:
            return os.path.realpath(p)
        else:
            res = None
    except:
        res = None

    for edition in vs_editions:
        s = os.environ["ProgramFiles(x86)"]
        p = os.path.join(s, "Microsoft Visual Studio", vc_year(vc_version), edition, "VC", "Auxiliary", "Build")
        f = os.path.join(p, "vcvarsall.bat")
        if os.path.isfile(f):
            config['paths']['visual_studio_basedir'] = os.path.join(s, "Microsoft Visual Studio", vc_year(vc_version),
                                                                    edition)
            return os.path.realpath(p)


def get_visual_studio_2015_or_less(vc_version):
    res = ""
    try:
        s = os.environ["ProgramFiles(x86)"]
        p = os.path.join(s, "Microsoft Visual Studio {}".format(vc_version), "VC")
        f = os.path.join(p, "vcvarsall.bat")
        if os.path.isfile(f):
            config['paths']['visual_studio_basedir'] = os.path.join(s, "Microsoft Visual Studio {}".format(vc_version))
            return os.path.realpath(p)
        else:
            res = None
    except:
        res = None

    if res == None:
        try:
            s = os.environ["ProgramFiles(x86)"]
            p = os.path.join(s, "Microsoft Visual Studio", "Shared", vc_version, "VC")
            f = os.path.join(p, "vcvarsall.bat")

            if os.path.isfile(f):
                config['paths']['visual_studio_basedir'] = os.path.join(s, "Microsoft Visual Studio", "Shared",
                                                                        vc_version)
                return os.path.realpath(p)
            else:
                res = None
        except:
            res = None

    # We should try the custom VC install path as well
    if res == None:
        try:
            p = os.path.join(config['vc_CustomInstallPath'], "VC")
            f = os.path.join(p, "vcvarsall.bat")
            if os.path.isfile(f):
                config['paths']['visual_studio_basedir'] = os.path.join(config['vc_CustomInstallPath'])
                return os.path.realpath(p)
            else:
                res = None
        except:
            res = None


def visual_studio(vc_version):
    config["paths"]["visual_studio"] = get_visual_studio_2015_or_less(vc_version) if vc_version < "15.0" \
        else get_visual_studio_2017_or_more(vc_version)
    if not config["paths"]["visual_studio"]:
        logging.error("Unable to find vcvarsall.bat, please make sure you have 'Common C++ tools' Installed."
          " If you have changed the default installation folder for VS please set the 'vc_CustomInstallPath' in the config.py file"
          " to the folder you installed VS to (this folder should contain a 'VC' subfolder).")
        sys.exit(1)


def visual_studio_environment():
    # when using visual studio we need to set up the environment correctly
    arch = "amd64" if config["architecture"] == 'x86_64' else "x86"
    test = config['paths']['visual_studio']
    if config['paths']['visual_studio']:
        proc = Popen([os.path.join(config['paths']['visual_studio'], "vcvarsall.bat"), arch, "&&", "SET"],
                     stdout=PIPE, stderr=PIPE)
        stdout, stderr = proc.communicate()

        if "Error in script usage. The correct usage is" in stderr:
            logging.error("failed to set up environment (returncode %s): %s", proc.returncode, stderr)
            return False

        if "Error in script usage. The correct usage is" in stdout:
            logging.error("failed to set up environment (returncode %s): %s", proc.returncode, stderr)
            return False

        if proc.returncode != 0:
            logging.error("failed to set up environment (returncode %s): %s", proc.returncode, stderr)
            return False
    else:
        sys.exit(1)

    vcenv = CIDict()

    for line in stdout.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            vcenv[key] = value
    return vcenv


def get_qt_install(qt_version, qt_minor_version, vc_version):
    res = None
    # We only use the 64bit version of QT in MO2 so this should be fine.

    try:
        for baselocation in program_files_folders:
            p = os.path.join(baselocation, "Qt", "Qt{}".format(qt_version + "." + qt_minor_version
                                                               if qt_minor_version != '' else qt_version),
                             "{}".format(qt_version + "." + qt_minor_version
                                         if qt_minor_version != '' else qt_version),
                             "msvc{0}_64".format(vc_year(vc_version)))
            f = os.path.join(p, "bin", "qmake.exe")
            if os.path.isfile(f):
                return os.path.realpath(p)
    except:
        res = None

    # We should try the custom VC install path as well
    if res is None:
        try:
            p = os.path.join(config['qt_CustomInstallPath'], "{}".format(qt_version + "." + qt_minor_version
                                                                         if qt_minor_version != '' else qt_version),
                             "msvc{0}_64".format(vc_year(vc_version)))
            f = os.path.join(p, "bin", "qmake.exe")
            if os.path.isfile(f):
                return os.path.realpath(p)
        except:
            res = None


def qt_install(qt_version, qt_minor_version, vc_version):
    config["paths"]["qt_binary_install"] = get_qt_install(qt_version, qt_minor_version, vc_version)
    if not config["paths"]["qt_binary_install"]:
        logging.error("Unable to find qmake.exe, please make sure you have QT {} installed. If it is installed "
                      "please point the 'qt_CustomInstallPath' in the config.py to your Qt installation."
                      .format(qt_version + "." + qt_minor_version if qt_minor_version != '' else qt_version))
        sys.exit(1)


def init_config(args):
    # some tools gets confused onto what constitutes . (OpenSSL and maybe CMake)
    args.destination = os.path.realpath(args.destination)

    for d in config['paths'].keys():
        if isinstance(config['paths'][d], str):
            config['paths'][d] = config['paths'][d].format(base_dir=os.path.abspath(args.destination),
                                                           build_dir=args.builddir,
                                                           progress_dir=args.progressdir,
                                                           install_dir=args.installdir)

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

    visual_studio(config["vc_version"])  # forced set after args are evaluated
    if config['prefer_binary_dependencies']:
        qt_install(config["qt_version"], config["qt_minor_version"], config["vc_version"])
    config['__Default_environment'] = os.environ
    config['__environment'] = visual_studio_environment()
    test = config['__environment']
    config['__build_base_path'] = os.path.abspath(args.destination)
    config['__Umbrella_path'] = os.getcwd()

    if 'PYTHON' not in config['__environment']:
        config['__environment']['PYTHON'] = sys.executable

def dump_config():
    # logging.debug("config['__environment']=%s", config['__environment'])
    logging.debug("  Config: config['__build_base_path']=%s", config['__build_base_path'])
    # logging.debug("  Config: config['paths']['graphviz']=%s", config['paths']['graphviz'])
    logging.debug("  Config: config['paths']['cmake']=%s", config['paths']['cmake'])
    logging.debug("  Config: config['paths']['git']=%s", config['paths']['git'])
 #   logging.debug("  Config: config['paths']['perl']=%s", config['paths']['perl'])
 #   logging.debug("  Config: config['paths']['ruby']=%s", config['paths']['ruby'])
 #   logging.debug("  Config: config['paths']['svn']=%s", config['paths']['svn'])
    logging.debug("  Config: config['paths']['7z']=%s", config['paths']['7z'])
    logging.debug("  Config: config['paths']['python']=%s", config['paths']['python'])
    logging.debug("  Config: config['paths']['visual_studio']=%s", config['paths']['visual_studio'])
    logging.debug("  Config: config['vc_version']=%s", config['vc_version'])

def check_config():
    if config['prefer_binary_dependencies']:
        if not config['__environment']: return False
        if not config['__build_base_path']: return False
        # if not config['paths']['graphviz']: return False
        if not config['paths']['cmake']: return False
        if not config['paths']['git']: return False
        #if not config['paths']['perl']: return False
        #if not config['paths']['ruby']: return False
        #if not config['paths']['svn']: return False
        if not config['paths']['7z']: return False
        if not config['paths']['python']: return False
        if not config['paths']['visual_studio']: return False
    return True

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
    parser.add_argument('-f', '--file', default='makefile.uni.py', help='sets the build script')
    parser.add_argument('-d', '--destination', default='.', help='output directory (base for download and build)')
    parser.add_argument('-s', '--set', action='append', help='set configuration parameters')
    parser.add_argument('-g', '--graph', action='store_true', help='update dependency graph')
    parser.add_argument('-b', '--builddir', default='build', help='update build directory')
    parser.add_argument('-p', '--progressdir', default='progress', help='update progress directory')
    parser.add_argument('-i', '--installdir', default='install', help='update progress directory')
    parser.add_argument('target', nargs='*', help='make target (if Check, check pre requisites)')
    args = parser.parse_args()

    init_config(args)

    for d in ["download", "build", "progress", "install"]:
        if not os.path.exists(config["paths"][d]):
            os.makedirs(config["paths"][d])

    dump_config()
    if not check_config():
        logging.error("Missing pre requisite")
        return False

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
                        logging.debug("finished project \"{}\"".format(node))
                    else:
                        logging.debug("run task \"{}\"".format(node))
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
                logging.error("Task {} failed: {}".format(task.name, e))
                raise

            build_graph.remove_node(node)

        independent = extract_independent(build_graph)


if __name__ == "__main__":
    try:
        exitcode = main()
        if not exitcode == 0:
            sys.exit(exitcode)
    except Exception, e:
        traceback.print_exc(file=sys.stdout)
        sys.exit(1)
