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
import os
import shutil
import subprocess
import tarfile

from config import config
from unibuild.retrieval import Retrieval
from unibuild.utility import ProgressFile
from unibuild.utility.context_objects import on_failure

logging.getLogger("requests").setLevel(logging.WARNING)

class PIPDownload(Retrieval):

    def __init__(self, package, version, tree_depth=0, name=None, clean=True):
        super(PIPDownload, self).__init__()
        self.__package = package
        self.__version = version
        self.__tree_depth = tree_depth
        self.__clean = clean
        self.__file_path = os.path.join(config['paths']['download'], "{}-{}.tar.gz".format(package, version))
        self.__name = "{}-{}".format(package, version) if name is None else name

    @property
    def name(self):
        if self.__name is None:
            return "download {0}".format(self.__file_name)
        return "download {0}".format(self.__name)

    @name.setter
    def name(self, value):
        self.__name = value

    @property
    def package(self):
        return self.__package

    @package.setter
    def package(self, value):
        self.__package = value

    @property
    def version(self):
        return self.__version

    @version.setter
    def version(self, value):
        self.__version = value

    def prepare(self):
        if 'build_path' not in self._context:
            output_file_path = os.path.join(config['paths']['build'], "{}-{}".format(self.__package, self.__version))
            self._context['build_path'] = output_file_path

    def process(self, progress):
        logging.info("processing download")
        output_file_path = self._context['build_path']
        #archive_file_path = os.path.join(config['paths']['download'], self.__file_name)

        if os.path.isfile(output_file_path):
            logging.info("File already extracted: %s", self.__file_path)
        else:
            if os.path.isfile(self.__file_path):
                logging.info("File already downloaded: %s", self.__file_path)
            else:
                logging.info("File not yet downloaded: %s", self.__file_path)
                self.download(output_file_path, progress)
            progress.finish()

        if not self.extract(self.__file_path, output_file_path, progress):
            return False
        progress.finish()

        builddir = os.listdir(self._context["build_path"])
        if len(builddir) == 1:
            self._context["build_path"] = os.path.join(self._context["build_path"], builddir[0])
        return True

    def download(self, output_file_path, progress):
        logging.info("Downloading {}-{} to {}".format(self.__package, self.__version, output_file_path))
        #progress.job = "Downloading"
        subprocess.check_call(["python", "-m", "pip", "download", "--no-binary=:all:", "--no-deps", "-d", "{}".format(config['paths']['download']), "{}=={}".format(self.__package, self.__version)])

    def extract(self, archive_file_path, output_file_path, progress):
        def progress_func(pos, size):
            progress.value = int(pos * 100 / size)

        try:
            os.makedirs(output_file_path)
        except Exception:
            # it does matter if the directory already exists otherwise downloads with tree_depth will fail if the are
            # extracted a second time on a dirty build environment
            sub_dirs = os.listdir(output_file_path)
            if not len(sub_dirs) == 0 and self.__clean:
                logging.info("Cleaning {}".format(output_file_path))
                for ls in sub_dirs:
                    try:
                        shutil.rmtree(os.path.join(output_file_path, ls))
                    except Exception:
                        os.remove(os.path.join(output_file_path, ls))

        logging.info("Extracting {}".format(self.__file_path))
        output_file_path = "\\\\?\\" + os.path.abspath(output_file_path)

        def extractProgress():
            progress.value = 0
            progress.job = "Extracting"

        with on_failure(lambda: shutil.rmtree(output_file_path)):
            extractProgress()
            archive_file = ProgressFile(archive_file_path, progress_func)
            with tarfile.open(fileobj=archive_file, mode='r:gz') as arch:
                def is_within_directory(directory, target):
                    
                    abs_directory = os.path.abspath(directory)
                    abs_target = os.path.abspath(target)
                
                    prefix = os.path.commonprefix([abs_directory, abs_target])
                    
                    return prefix == abs_directory
                
                def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
                
                    for member in tar.getmembers():
                        member_path = os.path.join(path, member.name)
                        if not is_within_directory(path, member_path):
                            raise Exception("Attempted Path Traversal in Tar File")
                
                    tar.extractall(path, members, numeric_owner=numeric_owner) 
                    
                
                safe_extract(arch, output_file_path)
            archive_file.close()

            for i in range(self.__tree_depth):
                sub_dirs = os.listdir(output_file_path)
                if len(sub_dirs) != 1:
                    raise ValueError("unexpected archive structure,"
                                     " expected exactly one directory in {}".format(output_file_path))
                source_dir = os.path.join(output_file_path, sub_dirs[0])

                for src in os.listdir(source_dir):
                    shutil.move(os.path.join(source_dir, src), output_file_path)

                shutil.rmtree(source_dir)
        return True
