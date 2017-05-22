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
from unibuild import Project
from unibuild.modules import build, msbuild, Patch, github
from unibuild.utility import lazy
from config import config
import os
from buildtools import log
from buildtools.buildsystem.visualstudio import (ProjectType,
                                                 VisualStudio2015Solution,
                                                 VS2015Project)


def prepare_nmm(context):
    sln = VisualStudio2015Solution()
    sln.LoadFromFile(os.path.join(context['build_path'],'NexusClient.sln'))
    ncc_csproj = os.path.join(context['build_path'],"..",'NexusClientCLI', 'NexusClientCLI', 'NexusClientCLI.csproj')
    if not os.path.isfile(ncc_csproj):
        log.critical('NOT FOUND: %s', ncc_csproj)
    else:
        log.info('FOUND: %s', ncc_csproj)
    changed = False
    projfile = VS2015Project()
    projfile.LoadFromFile(ncc_csproj)
    projguid = projfile.PropertyGroups[0].element.find('ProjectGuid').text
    log.info('ProjectGuid = %s', projguid)
    if "NexusClientCli" not in sln.projectsByName:
        newproj = sln.AddProject('NexusClientCli', ProjectType.CSHARP_PROJECT, ncc_csproj, guid=projguid)
        log.info('Adding project %s (%s) to NexusClient.sln', newproj.name, newproj.guid)
        changed = True
    else:
        newproj = sln.projectsByName['NexusClientCli']
        log.info('Project %s (%s) already exists in NexusClient.sln', newproj.name, newproj.guid)
        if newproj.projectfile != ncc_csproj:
            log.info('Changing projectfile: %s -> %s', newproj.projectfile, ncc_csproj)
            newproj.projectfile = ncc_csproj
            changed = True
    if changed:
        log.info('Writing NexusClientCli.sln')
        sln.SaveToFile(os.path.relpath(os.path.join(ncc['build_path'],"..","nmm",'NexusClientCli.sln'))) # So we don't get conflicts when pulling.
        return True


init_repos = github.Source("Nexus-Mods", "Nexus-Mod-Manager", "master") \
                                    .set_destination(os.path.join("NCC", "nmm"))


ncc = Project("NCC") \
    .depend(build.Run(r"publish.bat"
                     .format("-debug" if config['build_type'] == "Debug" else "-release",
                              os.path.join(config["paths"]["install"], "bin")),
                      working_directory=lazy.Evaluate(lambda: os.path.join(ncc['build_path'], "..", "NexusClientCli")))
           .depend(msbuild.MSBuild(os.path.join(config['paths']['build'],"NCC","nmm",'NexusClientCli.sln'),
                       working_directory=lazy.Evaluate(lambda: os.path.join(ncc['build_path'], "..", "nmm")),project_platform="Any CPU")
            .depend(build.Execute(prepare_nmm, name="append NexusClientCli project to NMM")

                .depend(init_repos).depend(github.Source(config['Main_Author'], "modorganizer-NCC", "master") \
                                    .set_destination(os.path.join("NCC", "NexusClientCli"))
                                    ))))




