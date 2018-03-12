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
from glob import glob
import logging
import fnmatch
import os
import shutil
from subprocess import Popen

from config import config
from unibuild import Project
from unibuild.modules import build, github, Patch

transifex_version = config['transifex-client_version']
transifex_api = config['transifex_API']
transifex_client_binary = os.path.join(config["paths"]["build"],"transifex-client", "tx.py27.x64.exe")
qt_lrelease_binary = os.path.join(config["paths"]["qt_binary_install"], "bin","lrelease.exe")
transifex_minimum_percentage = config['transifex_minimum_percentage']
build_path = config["paths"]["build"]
install_path = config["paths"]["install"]
download_path = config["paths"]["download"]

def isnotEmpty(s):
    return bool(s and s.strip())

def translations_stage(context):
            dest_transifex = os.path.join(build_path, "transifex-translations")
            dest_client = os.path.join(build_path, "transifex-client")
            dest_translations = os.path.join(install_path, "bin", "translations")
            if not isnotEmpty(config['transifex_API']):
                logging.error("The transifex API key is not set in config.py, Please set it")
                return False
            if not os.path.exists(dest_transifex):
                os.makedirs(dest_transifex)
            if not os.path.exists(dest_client):
                os.makedirs(dest_client)
            if not os.path.exists(dest_translations):
                 os.makedirs(dest_translations)
            for f in glob(os.path.join(download_path, "tx.py27.x64.exe")):
                 shutil.copy(f, os.path.join(dest_client))
            return True

def GenerateFiles(path,data, c = 1):
            for i in glob(os.path.join(path, "*")):
                if os.path.isfile(i):
                    filepath, filename = os.path.split(i)
                    if filename.endswith(".ts"):
                        data.update({os.path.join(filepath,filename):os.path.join(install_path, "bin", "translations",os.path.basename(filepath).split(".")[-1] + "_" +  os.path.splitext(filename)[0] + ".qm")})
                elif os.path.isdir(i):
                    dirname = os.path.basename(i)
                    c+=1
                    GenerateFiles(i,data,c)
                    c-=1
            return data


class GenerateTranslations(build.Builder):
    def __init__(self):
        super(GenerateTranslations, self).__init__()

    @property
    def name(self):
        return "Generate Translations"

    def process(self, progress):
        soutpath = os.path.join(self._context["build_path"], "stdout.log")
        serrpath = os.path.join(self._context["build_path"], "stderr.log")
        with open(soutpath, "w") as sout:
            with open(serrpath, "w") as serr:
                data = {}
                data = GenerateFiles(self._context["build_path"],data)
                for i, o in data.items():
                    proc = Popen([qt_lrelease_binary, i,
                                "-qm",
                                 o],
                                cwd=self._context["build_path"],
                                shell=True,
                                stdout=sout, stderr=serr)
                    proc.communicate()
                    if proc.returncode != 0:
                        logging.error("failed to run pyqt configure.py (returncode %s), see %s and %s",
                                      proc.returncode, soutpath, serrpath)
                        return False
                return True


init_transifex_repo = build.Run("{} init --token={} --force --no-interactive"
                                .format(transifex_client_binary,transifex_api),
                                name="init transifex repository")

config_transifex_repo = build.Run("{} config mapping-remote https://www.transifex.com/tannin/mod-organizer/"
                                .format(transifex_client_binary),
                                name="config transifex repository")


pull_transifex_repo = build.Run("{} pull -a -f --minimum-perc={}"
                                .format(transifex_client_binary,transifex_minimum_percentage),
                                name="pull transifex repository")


Project("translations") \
    .depend(GenerateTranslations()
        .depend(pull_transifex_repo
            .depend(config_transifex_repo
                .depend(init_transifex_repo
                    .depend(build.Execute(translations_stage)
                        .depend(github.Release("transifex", "transifex-client", transifex_version, "tx.py27.x64", extension="exe")
                            .set_destination("transifex-translations")))))))
