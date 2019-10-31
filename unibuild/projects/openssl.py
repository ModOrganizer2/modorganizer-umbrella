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
import logging
import os.path
import shutil
import time
from subprocess import Popen
from glob import glob

from config import config
from unibuild import Project
from unibuild.modules import build,  Patch, urldownload
from unibuild.projects import nasm

# currently binary installation only
openssl_version = config['openssl_version']
nasm_version = config['nasm_version']
build_path = config["paths"]["build"]
install_path = config["paths"]["install"]
openssl_path = os.path.join(build_path, "openssl-{}".format(openssl_version))

# installation happens concurrently in separate process.  We need to wait for all relevant files to exist,
# and can determine failure only by timeout
timeout = 15  # seconds


def bitness():
    return "64" if config['architecture'] == "x86_64" else "32"

def bitness_suffix():
    return "-x64" if config['architecture'] == "x86_64" else ""


filename = "openssl-{}.tar.gz".format(openssl_version)
url = "https://www.openssl.org/source/{}".format(filename)


def openssl_environment():
    result = config['__environment'].copy()
    result['Path'] += ";" + os.path.join(build_path, "nasm-{}-win{}".format(nasm_version, bitness(), nasm_version, bitness()))
    result['CL'] = "/MP"
    return result


def openssl_stage(context):
    if not config['Appveyor_Build']:
        shutil.copy(os.path.join(openssl_path, "ms", "applink.c"), os.path.join(openssl_path, "include"))
    final_path = os.path.join(openssl_path, "build")
    dest_bin = os.path.join(install_path, "bin")
    dest_lib = os.path.join(install_path, "libs")
    dest_pdb = os.path.join(install_path, "pdb")
    if not os.path.exists(dest_bin):
        os.makedirs(dest_bin)
    if not os.path.exists(os.path.join(dest_bin, "dlls")):
        os.mkdir(os.path.join(dest_bin, "dlls"))
    if not os.path.exists(dest_lib):
        os.makedirs(dest_lib)
    if not os.path.exists(dest_pdb):
        os.makedirs(dest_pdb)
    for f in glob(os.path.join(final_path, "bin", "libcrypto-1_1{}.dll".format(bitness_suffix()))):
         shutil.copy(f, os.path.join(dest_bin, "libcrypto-1_1{}.dll".format(bitness_suffix())))
         shutil.copy(f, os.path.join(dest_bin, "dlls", "libcrypto-1_1{}.dll".format(bitness_suffix())))
    for f in glob(os.path.join(final_path, "bin", "libssl-1_1{}.dll".format(bitness_suffix()))):
         shutil.copy(f, os.path.join(dest_bin, "libssl-1_1{}.dll".format(bitness_suffix())))
         shutil.copy(f, os.path.join(dest_bin, "dlls", "libssl-1_1{}.dll".format(bitness_suffix())))
    for f in glob(os.path.join(final_path,"bin", "libcrypto-1_1{}.pdb".format(bitness_suffix()))):
        shutil.copy(f, os.path.join(dest_pdb, "libcrypto-1_1{}.pdb".format(bitness_suffix())))
    for f in glob(os.path.join(final_path,"bin", "libssl-1_1{}.pdb".format(bitness_suffix()))):
        shutil.copy(f, os.path.join(dest_pdb, "libssl-1_1{}.pdb".format(bitness_suffix())))
    for f in glob(os.path.join(final_path, "lib", "libcrypto.lib")):
        shutil.copy(f, os.path.join(dest_lib, "libcrypto.lib"))
    for f in glob(os.path.join(final_path, "lib", "libssl.lib")):
        shutil.copy(f, os.path.join(dest_lib, "libssl.lib"))
    return True


OpenSSL_Install = build.Run(r"nmake install",
                      environment=openssl_environment(),
                      name="Install OpenSSL",
                      working_directory=lambda: os.path.join(openssl_path))

OpenSSL_Build = build.Run(r"nmake",
                      environment=openssl_environment(),
                      name="Building OpenSSL",
                      working_directory=lambda: os.path.join(openssl_path))


Configure_openssl = build.Run(r"{} Configure --openssldir={} --prefix={} VC-WIN{}A".format(config['paths']['perl'],
                                                                              os.path.join(openssl_path, "build"),
                                                                              os.path.join(openssl_path, "build"),
                                                                               bitness()),
                      environment=openssl_environment(),
                      name="Configure OpenSSL",
                      working_directory=lambda: os.path.join(openssl_path))


if config['Appveyor_Build']:
    openssl = Project("openssl") \
        .depend(build.Execute(openssl_stage)
                .depend(urldownload.URLDownload(config.get('prebuilt_url') + "openssl-prebuilt-{}.7z"
                                                .format(openssl_version))
                .set_destination("openssl-{}".format(openssl_version))))
else:
    openssl = Project("openssl") \
        .depend(build.Execute(openssl_stage)
            .depend(OpenSSL_Install
                .depend(OpenSSL_Build
                        .depend(Configure_openssl
                            .depend(urldownload.URLDownload(url, tree_depth=1)
                                .depend("nasm"))))))
