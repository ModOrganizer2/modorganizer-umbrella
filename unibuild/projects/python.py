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
import errno
import os
import shutil
from glob import glob

from config import config
from unibuild.modules import build, github, msbuild
from unibuild.project import Project
from unibuild.utility.visualstudio import get_visual_studio_2017

path_install = config["paths"]["install"]
python_version = config['python_version']
python_version_minor = config['python_version_minor']


def make_sure_path_exists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


def python_environment():
    result = config['__environment'].copy()
    result['Path'] += ";" + os.path.dirname(config['paths']['svn'])
    return result


def upgrade_args():
    env = config['__environment']
    devenv_path = os.path.join(config['paths']['visual_studio_base'], "Common7", "IDE")
    # MSVC2017 supports building with the MSVC2015 toolset though this will break here, Small work around to make sure devenv.exe exists
    # If not try MSVC2017 instead
    res = os.path.isfile(os.path.join(devenv_path, "devenv.exe"))
    if res:
        return [os.path.join(devenv_path, "devenv.exe"),
                "PCBuild/pcbuild.sln",
                "/upgrade"]
    return [os.path.join(get_visual_studio_2017('15.0'), "..", "..", "..", "Common7", "IDE", "devenv.exe"),
            "PCBuild/pcbuild.sln", "/upgrade"]

def install(context):
    make_sure_path_exists(os.path.join(path_install, "libs"))
    path_segments = [context['build_path'], "PCbuild"]
    if config['architecture'] == "x86_64":
        path_segments.append("amd64")
    path_segments.append("*.lib")
    shutil.copy(os.path.join(python['build_path'], "PC", "pyconfig.h"),
                os.path.join(python['build_path'], "Include", "pyconfig.h"))
    for f in glob(os.path.join(*path_segments)):
        shutil.copy(f, os.path.join(path_install, "libs"))
    return True

def download(context):
    return True


python = Project("Python") \
    .depend(build.Execute(install)
            .depend(msbuild.MSBuild("PCBuild/PCBuild.sln", "python,pyexpat",
                                    project_PlatformToolset=config['vc_platformtoolset'])
                    .depend(build.Run(upgrade_args, name="upgrade python project")
                            .depend(github.Source("LePresidente", "cpython-1", config.get('python_version', "2.7"), shallowclone=True) \
                                    .set_destination("python-{}".format(python_version + python_version_minor))))))
