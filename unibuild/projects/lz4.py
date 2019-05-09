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
import os.path
import shutil

from config import config
from unibuild import Project
from unibuild.utility import lazy
from unibuild.modules import github, msbuild, build, Patch
from unibuild.utility.visualstudio import get_visual_studio

lz4_version = 'v' + config['lz4_version']
lz4_version_minor = ".".join([_f for _f in [lz4_version, config['lz4_version_minor']] if _f])
lz_path = os.path.join(config['paths']['build'], "lz4-{}".format(lz4_version_minor))


def bitness():
    from config import config
    return "x64" if config['architecture'] == "x86_64" else "Win32"


def lz4_environment():
    result = config['__environment'].copy()
    return result


def upgrade_args():
    devenv_path = os.path.join(config['paths']['visual_studio_base'], "Common7", "IDE")
    # MSVC2017 supports building with the MSVC2015 toolset though this will break here,
    # Small work around to make sure devenv.exe exists
    # If not try MSVC2017 instead
    res = os.path.isfile(os.path.join(devenv_path, "devenv.exe"))
    if res:
        return [os.path.join(devenv_path, "devenv.exe"),
                os.path.join(lz_path, "visual", "VS2017", 'lz4.sln'),
                "/upgrade"]
    return [os.path.join(get_visual_studio(config["vc_version"]), "..", "..", "..", "Common7", "IDE", "devenv.exe"),
            os.path.join(lz_path, "visual", "VS2017", 'lz4.sln'), "/upgrade"]


def copy_binaries(context):
    shutil.rmtree(
        os.path.join(lz_path, "bin")
    )
    shutil.copytree(
        os.path.join(lz_path, "visual", "VS2017", "bin", "{}_Release".format(bitness())),
        os.path.join(lz_path, "bin")
    )
    return True


Project("lz4").depend(
    Patch.Copy(
            os.path.join(lz_path, "bin", "liblz4.pdb"),
            os.path.join(config["paths"]["install"], "pdb")
    ).depend(
        Patch.Copy(
            os.path.join(lz_path, "bin", "liblz4.dll"),
            os.path.join(config["paths"]["install"], "bin", "dlls")
        ).depend(
            build.Execute(
                copy_binaries
            ).depend(
                msbuild.MSBuild(
                    os.path.join(lz_path, "visual", "VS2017", 'lz4.sln'),
                    project="liblz4-dll",
                    working_directory=lazy.Evaluate(lambda: os.path.join(lz_path)),
                    project_platform=bitness(),
                    reltarget="Release"
                ).depend(
                    build.Run(
                        upgrade_args,
                        name="upgrade lz4 project"
                    ).depend(
                        github.Source(
                            "lz4", "lz4", lz4_version_minor
                        ).set_destination(lz_path)
                    )
                )
            )
        )
    )
)
