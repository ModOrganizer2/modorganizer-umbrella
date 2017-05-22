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


from unibuild.project import Project
from unibuild.modules import github, msbuild, build, urldownload
from config import config
from unimake import get_visual_studio_2017_or_more
import os
import shutil
from glob import glob
import errno


python_version = config.get('python_version', "2.7") + config.get('python_version_minor', ".12")
python_toolset = config.get('vc_platformtoolset', "v140")
python_url = "https://www.python.org/ftp/python"

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
    devenv_path = os.path.join(config['paths']['visual_studio_basedir'], "Common7", "IDE")
    #MSVC2017 supports building with the MSVC2015 toolset though this will break here, Small work around to make sure devenv.exe exists
    #If not try MSVC2017 instead
    res = os.path.isfile(os.path.join(devenv_path, "devenv.exe"))
    if res:
        return [os.path.join(devenv_path, "devenv.exe"),
            "PCBuild/pcbuild.sln",
            "/upgrade"]
    else:
        return [os.path.join(get_visual_studio_2017_or_more('15.0'),"..","..","..","Common7", "IDE", "devenv.exe"),
            "PCBuild/pcbuild.sln",
            "/upgrade"]

#if config.get('prefer_binary_dependencies', False):
if False:
    # the python installer registers in windows and prevent further installations. This means this installation
    # would interfere with the rest of the system
    filename = "python-{0}{1}.msi".format(
        python_version,
        ".amd64" if config['architecture'] == "x86_64" else ""
    )

    python = Project("Python") \
        .depend(build.Run("msiexec /i {0} TARGETDIR={1} /qn ADDLOCAL=DefaultFeature,SharedCRT"
                          .format(os.path.join(config['paths']['download'], filename),
                                  os.path.join(config['paths']['build'], "python-{}".format(python_version))
                                  )
                          )
                .depend(urldownload.URLDownload("{0}/{1}/{2}"
                                                .format(python_url,
                                                        python_version,
                                                        filename
                                                        )
                                                )
                        )
                )
else:
    def install(context):
        make_sure_path_exists(os.path.join(config["paths"]["install"], "libs"))
        path_segments = [context['build_path'], "PCbuild"]
        if config['architecture'] == "x86_64":
            path_segments.append("amd64")
        path_segments.append("*.lib")
        shutil.copy(os.path.join(python['build_path'],"PC", "pyconfig.h"),os.path.join(python['build_path'], "Include","pyconfig.h"))
        for f in glob(os.path.join(*path_segments)):
            shutil.copy(f, os.path.join(config["paths"]["install"], "libs"))
        return True

    python = Project("Python") \
         .depend(build.Execute(install)
                 .depend(msbuild.MSBuild("PCBuild/PCBuild.sln", "python,pyexpat",
                                         project_PlatformToolset=python_toolset)
#                 .depend(build.Run(r'PCBuild\\build.bat -e -c Release -m -p {} "/p:PlatformToolset={}"'.format("x64" if config['architecture'] == 'x86_64' else "x86",config['vc_platform']),
#                                   environment=python_environment(),
#                                   working_directory=lambda: os.path.join(python['build_path']))
                            .depend(build.Run(upgrade_args, name="upgrade python project")
                                         .depend(github.Source("LePresidente", "cpython", config.get('python_version', "2.7"))\
										     .set_destination("python-{}".format(python_version))))
                        )
                )
