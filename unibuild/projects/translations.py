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
from glob import glob
import logging
import fnmatch
import os
import shutil
from subprocess import Popen

from config import config
from unibuild import Project
from unibuild.modules import build, github, Patch
from unibuild.manager import TaskManager

transifex_version = config['transifex-client_version']
transifex_api = config['transifex_API']
transifex_client_binary = os.path.join(config["paths"]["build"],"transifex-client", "tx.py36.x64.exe")
qt_lrelease_binary = os.path.join(config["paths"]["qt_binary_install"], "bin","lrelease.exe")
transifex_minimum_percentage = config['transifex_minimum_percentage']
build_path = config["paths"]["build"]
install_path = config["paths"]["install"]
download_path = config["paths"]["download"]


def isnotEmpty(s):
    return bool(s and s.strip())


def transifex_environment():
    result = config['__Default_environment'].copy()
    result["TX_TOKEN"] = transifex_api
    return result


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
            for f in glob(os.path.join(download_path, "tx.py36.x64.exe")):
                 shutil.copy(f, os.path.join(dest_client))
            return True


def GenerateFiles(path,data, c = 1):
            for i in glob(os.path.join(path, "*")):
                if os.path.isfile(i):
                    filepath, filename = os.path.split(i)
                    if filename.endswith(".ts"):
                        dest_dir = os.path.join(install_path, "bin/resources", "translations")

                        # filepath is the directory that contains the .ts file
                        # in build/transifex-translations/translations, created
                        # by the transifex tool when pulling the translations
                        #
                        # for example, 'mod-organizer-2.game_enderal'

                        # filename is the name of the .ts file inside that
                        # directory
                        #
                        # for example, 'de.ts'


                        # the part after the dot, such as 'game_enderal'
                        project = os.path.basename(filepath).split(".")[-1]

                        # the name of the file without the extension, such as
                        # 'de'
                        lang = os.path.splitext(filename)[0]

                        # the filename of the qm file, such as
                        # 'game_enderal_de.qm'
                        qm = project + "_" + lang + ".qm"

                        src = os.path.join(filepath, filename)
                        srcs = [src]
                        dest = os.path.join(dest_dir, qm)

                        # if the task depends on gamebryo, add its .ts file
                        # so it gets merged with the one from this task
                        t = TaskManager().get_task("modorganizer-" + project)

                        if t is None:
                            # there's are case differences for some projects
                            t = TaskManager().get_task("modorganizer-" + project.lower())

                        if t is not None:
                            if t.depends_on("modorganizer-game_gamebryo"):
                                translations = os.path.join(build_path, "transifex-translations", "translations")
                                gamebryo_dir = os.path.join(translations, "mod-organizer-2.game_gamebryo")
                                gamebryo_ts = os.path.join(gamebryo_dir, filename)

                                # some translations might be missing
                                if os.path.exists(gamebryo_ts):
                                    srcs.append(gamebryo_ts)

                        data.update({dest: srcs})
                elif os.path.isdir(i):
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
                data = GenerateFiles(self._context["build_path"], data)
                for qm, srcs in list(data.items()):
                    args = []
                    args.append(qt_lrelease_binary)
                    args.extend(srcs)
                    args.append("-qm")
                    args.append(qm)

                    proc = Popen(args,
                                cwd=self._context["build_path"],
                                shell=True,
                                stdout=sout, stderr=serr)
                    proc.communicate()
                    if proc.returncode != 0:
                        logging.error("failed to run pyqt configure.py (returncode %s), see %s and %s",
                                      proc.returncode, soutpath, serrpath)
                        return False
                return True

    @staticmethod
    def _expiration():
        return config.get('repo_update_frequency', 60 * 60 * 24)  # default: one day


class PullTranslations(build.Builder):
    def __init__(self):
        super(PullTranslations, self).__init__()

    @property
    def name(self):
        return "Pull Translations"

    def process(self, progress):
        if "build_path" not in self._context:
            logging.error("source path not known for {},"
                          " are you missing a matching retrieval script?".format(self.name))

        soutpath = os.path.join(self._context["build_path"], "stdout.log")
        serrpath = os.path.join(self._context["build_path"], "stderr.log")
        with open(soutpath, "w") as sout:
            with open(serrpath, "w") as serr:
                environment = transifex_environment()
                cwd = str(self._context["build_path"])

                command = "{} config mapping-remote https://www.transifex.com/mod-organizer-2-team/mod-organizer-2/"\
                    .format(transifex_client_binary)
                sout.write("running {} in {}".format(command, cwd))
                proc = Popen(command,
                             env=environment,
                             cwd=cwd,
                             shell=True,
                             stdout=sout, stderr=serr)
                proc.communicate()
                if proc.returncode != 0:
                    logging.error("failed to run %s (returncode %s), see %s and %s",
                                  command, proc.returncode, soutpath, serrpath)
                    return False

                command = "{} pull -a -f --parallel --minimum-perc={}"\
                    .format(transifex_client_binary, transifex_minimum_percentage)
                sout.write("running {} in {}".format(command, cwd))
                proc = Popen(command,
                             env=environment,
                             cwd=cwd,
                             shell=True,
                             stdout=sout, stderr=serr)
                proc.communicate()
                if proc.returncode != 0:
                    logging.error("failed to run %s (returncode %s), see %s and %s",
                                  command, proc.returncode, soutpath, serrpath)
                    return False

        return True

    @staticmethod
    def _expiration():
        return config.get('repo_update_frequency', 60 * 60 * 24)  # default: one day


init_transifex_repo = build.Run("{} init --force --no-interactive"
                                .format(transifex_client_binary),
                                name="init transifex repository",
                                environment=transifex_environment())


def install_qt_translations(context):
    full_install_path = os.path.join(install_path, "bin/resources", "translations")
    qt_qm_path = os.path.join(config["paths"]["qt_binary_install"], "translations")
    translated_ts_path = os.path.join(build_path, "transifex-translations", "translations", "mod-organizer.organizer")
    for ts_file in glob(os.path.join(translated_ts_path, "*.ts")):
        language_code = os.path.splitext(os.path.basename(ts_file))[0]
        qt_qm = "qt_" + language_code + ".qm"
        if os.path.isfile(os.path.join(qt_qm_path, qt_qm)):
            shutil.copy(os.path.join(qt_qm_path, qt_qm), os.path.join(full_install_path, qt_qm))
        qtbase_qm = "qtbase_" + language_code + ".qm"
        if os.path.isfile(os.path.join(qt_qm_path, qtbase_qm)):
            shutil.copy(os.path.join(qt_qm_path, qtbase_qm), os.path.join(full_install_path, qtbase_qm))
    return True


Project("translations") \
    .depend(build.Execute(install_qt_translations)
        .depend(GenerateTranslations()
            .depend(PullTranslations()
                    .depend(init_transifex_repo
                        .depend(build.Execute(translations_stage)
                            .depend(github.Release("transifex", "transifex-client", transifex_version, "tx.py36.x64", extension="exe")
                                .set_destination("transifex-translations")))))))
