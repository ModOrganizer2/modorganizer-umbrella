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
from unibuild.modules import urldownload, build
from config import config
from subprocess import Popen
import os
import logging
import time


# currently binary installation only


openssl_version = "1.0.2e"


def bitness():
    return "64" if config['architecture'] == "x86_64" else "32"

filename = "Win{}OpenSSL-{}.exe".format(bitness(), openssl_version.replace(".", "_"))

url = "https://slproweb.com/download/{}".format(filename)

def build_func(context):
    proc = Popen([os.path.join(config['paths']['download'], filename),
                  "/VERYSILENT", "/DIR={}".format(context['build_path'])],
                 cwd=config['paths']['download'],
                 env=config['__environment'])
    proc.communicate()
    if proc.returncode != 0:
        logging.error("failed to run installer (returncode %s)",
                      proc.returncode)
        return False
    # TODO: installation happens concurrently in separate process. Wait for all relevant files to exist?
    return True


openssl = Project("openssl")\
    .depend(build.Execute(build_func)
            .depend(urldownload.URLDownload(url))
            )

