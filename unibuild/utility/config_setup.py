
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
import logging
import os.path
import sys

from config import config
from unibuild.utility.visualstudio import visual_studio, visual_studio_environment
from unibuild.utility.qt import qt_install
from unibuild.utility.lazy import Evaluate, Lazy


def get_from_hklm(hkey ,path, name, wow64=False):
    from _winreg import QueryValueEx, OpenKey, HKEY_CURRENT_USER, HKEY_LOCAL_MACHINE, KEY_READ, KEY_WOW64_32KEY
    flags = KEY_READ
    if wow64:
        flags |= KEY_WOW64_32KEY

    # avoids crashing if a product is not present
    try:
        with OpenKey(HKEY_LOCAL_MACHINE if hkey == "HKEY_LOCAL_MACHINE" else HKEY_CURRENT_USER, path, 0, flags) as key:
            return QueryValueEx(key, name)[0]
    except Exception:
        return None


def init_config(args):
    # some tools gets confused onto what constitutes .  (OpenSSL and maybe CMake)
    args.destination = os.path.realpath(args.destination)

    for d in config['paths'].keys():
        if isinstance(config['paths'][d], str):
            config['paths'][d] = config['paths'][d].format(base_dir=os.path.abspath(args.destination),
                                                           build_dir=args.builddir,
                                                           progress_dir=args.progressdir,
                                                           install_dir=args.installdir)

    python = get_from_hklm("HKEY_LOCAL_MACHINE", r"SOFTWARE\Python\PythonCore\{}\InstallPath".format(config['python_version']), "")
    if python is None:
        python = get_from_hklm("HKEY_CURRENT_USER", r"SOFTWARE\Python\PythonCore\{}\InstallPath".format(config['python_version']), "")
    if python is not None:
        config['paths']['python'] = os.path.join(python, "python.exe")
    else:
        config['paths']['python'] = sys.executable

    # parse -s argument.  Example -s paths.build=bin would set config[paths][build] to bin
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
        qt_install(config["qt_version"], config["qt_version_minor"], config["vc_version"])
    config['__Default_environment'] = os.environ
    config['__environment'] = visual_studio_environment()
    config['__build_base_path'] = os.path.abspath(args.destination)
    config['__Umbrella_path'] = os.getcwd()

    if 'PYTHON' not in config['__environment']:
        config['__environment']['PYTHON'] = sys.executable

def dump_config():
    #logging.debug("config['__environment']=%s", config['__environment'])
    logging.debug("  Config: config['__build_base_path']=%s", config['__build_base_path'])
    #logging.debug(" Config: config['paths']['graphviz']=%s", config['paths']['graphviz'])
    logging.debug("  Config: config['paths']['cmake']=%s", config['paths']['cmake'])
    logging.debug("  Config: config['paths']['git']=%s", config['paths']['git'])
    logging.debug("  Config: config['paths']['perl']=%s", config['paths']['perl'])
    #logging.debug(" Config: config['paths']['ruby']=%s", config['paths']['ruby'])
    #logging.debug(" Config: config['paths']['svn']=%s", config['paths']['svn'])
    logging.debug("  Config: config['paths']['7z']=%s", config['paths']['7z'])
    logging.debug("  Config: config['paths']['python']=%s", config['paths']['python'])
    logging.debug("  Config: config['paths']['visual_studio']=%s", config['paths']['visual_studio'])
    logging.debug("  Config: config['vc_version']=%s", config['vc_version'])


def check_config():
    if config['prefer_binary_dependencies']:
        if not config['__environment']:
            return False
        if not config['__build_base_path']:
            return False
        #if not config['paths']['graphviz']:
        #   return False
        if not config['paths']['cmake']:
            return False
        if not config['paths']['git']:
            return False
        if not config['paths']['perl']:
            return False
        #if not config['paths']['ruby']:
        #   return False
        #if not config['paths']['svn']:
        #   return False
        if not config['paths']['7z']:
            return False
        if not config['paths']['python']:
            return False
        if not config['paths']['visual_studio']:
            return False
    return True
