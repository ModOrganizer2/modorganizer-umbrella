# Copyright (C) 2015 Sebastian Herbord.  All rights reserved.
# Copyright (C) 2016 - 2019 Mod Organizer contributors.
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
import patch
from glob import glob
from subprocess import Popen
import logging

from config import config
from unibuild.modules import build, github, msbuild, urldownload, sourceforge
from unibuild.project import Project
from unibuild.projects import openssl
from unibuild.utility.visualstudio import get_visual_studio
from unibuild.utility.config_utility import make_sure_path_exists

path_install = config["paths"]["install"]
python_version = config['python_version']
python_version_minor = config['python_version_minor']
bzip2_version = config['bzip2_version']
openssl_version = config['openssl_version']
build_path = config["paths"]["build"]


def bitness():
    return "amd64" if config["architecture"] == "x86_64" else "win32"


def python_environment(context):
    result = config['__environment'].copy()
    result['PYTHONHOME'] = context["build_path"]
    return result


def patch_openssl_props(context):
    patch_file = os.path.join(config['__Umbrella_path'], "patches", "python_openssl_path.patch")
    savedpath = os.getcwd()
    tarpath = os.path.join(context["build_path"])
    os.chdir(tarpath)
    pset = patch.fromfile(patch_file)
    pset.apply()
    os.chdir(savedpath)
    return True


def upgrade_args():
    devenv_path = os.path.join(config['paths']['visual_studio_base'], "Common7", "IDE")
    # MSVC2017 supports building with the MSVC2015 toolset though this will break here,
    # Small work around to make sure devenv.exe exists
    # If not try MSVC2017 instead
    res = os.path.isfile(os.path.join(devenv_path, "devenv.exe"))
    if res:
        return [os.path.join(devenv_path, "devenv.exe"),
                "PCBuild/pcbuild.sln",
                "/upgrade"]
    return [os.path.join(get_visual_studio(config["vc_version"]), "..", "..", "..", "Common7", "IDE", "devenv.exe"),
            "PCBuild/pcbuild.sln", "/upgrade"]


def python_prepare(context):
    shutil.copy(os.path.join(python['build_path'], "PC", "pyconfig.h"),
                os.path.join(python['build_path'], "Include", "pyconfig.h"))
    return True


class PydCompiler(build.Builder):
    def __init__(self):
        super(PydCompiler, self).__init__()

    @property
    def name(self):
        return "pyd compiler"

    def process(self, progress):
        soutpath = os.path.join(self._context["build_path"], "stdout.log")
        serrpath = os.path.join(self._context["build_path"], "stderr.log")

        with open(soutpath, "w") as sout:
            with open(serrpath, "w") as serr:
                logging.debug("Packaging python files")
                bp = self._context['build_path']
                pyp = os.path.join(bp, "PCbuild", "{}".format(bitness()))

                proc = Popen([os.path.join(bp, "python.bat"), "PC/layout",
                              "-vv",
                              "-s", bp,
                              "-b", pyp,
                              "-t", os.path.join(pyp, "pythoncore_temp"),
                              "--copy", os.path.join(pyp, "pythoncore"),
                              "--preset-embed"
                              ],
                    env=python_environment(self._context),
                    cwd=bp,
                    shell=True,
                    stdout=sout, stderr=serr)
                proc.communicate()
                if proc.returncode != 0:
                    logging.error("failed to run cpython PC/layout gen (returncode %s), see %s and %s",
                                  proc.returncode, soutpath, serrpath)
                    return False

        return True


def install(context):
    make_sure_path_exists(os.path.join(path_install, "libs"))
    make_sure_path_exists(os.path.join(context["build_path"], "libs"))
    make_sure_path_exists(os.path.join(path_install, "bin"))
    path_segments = [context['build_path'], "PCbuild", bitness()]
    for f in glob(os.path.join(*path_segments, "*.lib")):
        shutil.copy(f, os.path.join(path_install, "libs"))
    for f in glob(os.path.join(*path_segments, "*.lib")):
        shutil.copy(f, os.path.join(context["build_path"], "libs"))
    shutil.copy(os.path.join(*path_segments, "python{}.dll".format(python_version.replace(".", ""))), os.path.join(path_install, "bin"))
    shutil.copy(os.path.join(*path_segments, "python{}.dll".format(python_version.replace(".", ""))), os.path.join(context["build_path"], "libs"))
    for f in glob(os.path.join(*path_segments, "libffi-*.dll".format(python_version.replace(".", "")))):
        shutil.copy(f, os.path.join(path_install, "bin"))
    shutil.copy(os.path.join(*path_segments, "python{}.pdb".format(python_version.replace(".", ""))), os.path.join(path_install, "pdb"))
    for f in glob(os.path.join(*path_segments, "_*.pdb".format(python_version.replace(".", "")))):
        shutil.copy(f, os.path.join(path_install, "pdb"))
    return True


if config.get('Appveyor_Build', True):
    python = Project("Python") \
        .depend(build.Execute(install)
                .depend(urldownload.URLDownload(
                    config.get('prebuilt_url') + "python-prebuilt-{}.7z"
                    .format(python_version + python_version_minor)).
                        set_destination("python-{}".format(python_version + python_version_minor))))
else:
    Project("libffi").depend(github.Source("python", "cpython-bin-deps", "libffi", shallowclone=True).set_destination("libffi"))

    python = Project("Python") \
        .depend(build.Execute(install)
                .depend(build.Execute(python_prepare)
                        .depend(PydCompiler()
                                .depend(msbuild.MSBuild("PCBuild/PCBuild.sln", "python,pythonw,python3dll,select,pyexpat,unicodedata,_queue,_bz2,_ssl",
                                                        project_PlatformToolset=config['vc_platformtoolset'],
                                                        reltarget="Release",
                                                        project_AdditionalParams=[
                                                            "/p:bz2Dir={}".format(os.path.join(build_path, "bzip2")),
                                                            "/p:zlibDir={}".format(os.path.join(build_path, "zlib-{}".format(config['zlib_version']))),
                                                            "/p:opensslIncludeDir={}".format(os.path.join(build_path, "openssl-{}".format(openssl_version), "include")),
                                                            "/p:opensslOutDir={}".format(os.path.join(build_path, "openssl-{}".format(openssl_version))),
                                                            "/p:libffiIncludeDir={}".format(os.path.join(build_path, "libffi", bitness(), "include")),
                                                            "/p:libffiOutDir={}".format(os.path.join(build_path, "libffi", bitness())),
                                                        ]
                                                        )
                                        .depend(build.Execute(patch_openssl_props)
                                                .depend(build.Run(upgrade_args, name="upgrade python project")
                                                        .depend(github.Source("python", "cpython", "v{}{}"
                                                                              .format(config['python_version'],
                                                                                      config['python_version_minor'])
                                                                              , shallowclone=True)
                                                        .set_destination("python-{}".format(python_version + python_version_minor))
                                                                .depend(sourceforge.Release("bzip2","bzip2-{0}.tar.gz"
                                                                                            .format(bzip2_version), tree_depth=1)
                                                                        .set_destination("bzip2")
                                                                        )
                                                                )
                                                        )
                                                )
                                        .depend("openssl")
                                        .depend("libffi")
                                        )
                                )
                        )
                )
