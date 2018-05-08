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
import os

from buildtools import log
from buildtools.buildsystem.visualstudio import ProjectType, VisualStudio2015Solution, VS2015Project
from config import config
from unibuild import Project
from unibuild.modules import build, msbuild, github
from unibuild.utility import lazy

build_path = config['paths']['build']


def prepare_nmm(context):
    sln = VisualStudio2015Solution()
    sln.LoadFromFile(os.path.join(build_path, "Nexus-Mod-Manager", 'NexusClient.sln'))
    ncc_csproj = os.path.join(build_path, 'NexusClientCLI', 'NexusClientCLI', 'NexusClientCLI.csproj')
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
        sln.SaveToFile(os.path.relpath(os.path.join(build_path, "Nexus-Mod-Manager", 'NexusClientCli.sln'))) # So we dont get conflicts when pulling
        return True


# https://github.com/Nexus-Mods/Nexus-Mod-Manager/commit/03448e0eb02e08f37d7b66507d0537ab67841321 broke fomod installation
# until this is fixed we lock NMM to the latest nexus release.
Project("ncc") \
    .depend(build.Run(r"publish.bat".format("-debug" if config['build_type'] == "Debug" else "-release",
                              os.path.join(config["paths"]["install"], "bin")),
                      working_directory=lazy.Evaluate(lambda: os.path.join(build_path, "NexusClientCli")))
            .depend(msbuild.MSBuild(os.path.join(build_path, "Nexus-Mod-Manager", 'NexusClientCli.sln'),
                                    working_directory=lazy.Evaluate(lambda: os.path.join(build_path, "Nexus-Mod-Manager")),
                                    project_platform="Any CPU")
                    .depend(build.Execute(prepare_nmm, name="append NexusClientCli project to NMM")
                            .depend(github.Source("Nexus-Mods", "Nexus-Mod-Manager", config["nmm_version"], None, False))
                                    .depend(github.Source(config['Main_Author'], "modorganizer-NCC", config["Main_Branch"])
                                                  .set_destination("NexusClientCli")))))
