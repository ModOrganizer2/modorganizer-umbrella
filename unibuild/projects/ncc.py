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

from unibuild import Project
from unibuild.modules import build, msbuild, patch, github
from unibuild.utility import lazy
from unimake import get_visual_studio_2017_or_more
from config import config
import os

def upgrade_args():
    env = config['__environment']
    devenv_path = env['DevEnvDir'] if 'DevEnvDir' in env\
        else os.path.join(config['paths']['visual_studio_basedir'], "Common7", "IDE")
    #MSVC2017 supports building with the MSVC2015 toolset though this will break here, Small work around to make sure devenv.exe exists
    #If not try MSVC2017 instead
    res = os.path.isfile(os.path.join(devenv_path, "devenv.exe"))
    if res:
        return [os.path.join(devenv_path, "devenv.exe"),
            "NexusClient.sln",
            "/upgrade"]
    else:
        return [os.path.join(get_visual_studio_2017_or_more('15.0'),"..","..","..","Common7", "IDE", "devenv.exe"),
            "NexusClient.sln",
            "/upgrade"]

ncc = Project("NCC") \
    .depend(build.Run(r"publish.bat"
                     .format("-debug" if config['build_type'] == "Debug" else "-release",
                              os.path.join(config['__build_base_path'], "install", "bin")),
                      working_directory=lazy.Evaluate(lambda: ncc['build_path']))
#            .depend(msbuild.MSBuild("../nmm/NexusClient.sln",
#                        working_directory=lazy.Evaluate(lambda: os.path.join(ncc['build_path'], "..", "nmm")))
#            .depend(build.Run(upgrade_args, name="upgrade ncc project")
#            .depend(patch.Copy("NexusClient.sln", "../nmm")
                .depend(github.Source(config['Main_Author'], "modorganizer-NCC", "master")
                            .set_destination(os.path.join("NCC", "NexusClientCli"))
                            .depend(github.Source("Nexus-Mods", "Nexus-Mod-Manager", "master")
                                    .set_destination(os.path.join("NCC", "nmm"))
                                    )
                            )
               )
#            )
#)
#)

