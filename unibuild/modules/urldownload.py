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


from unibuild.retrieval import Retrieval
from config import config
import os
import sys
import logging
from urlparse import urlparse
import urllib2
import tarfile
import zipfile
import subprocess
import shutil
from unibuild.utility import ProgressFile
from unibuild.utility.context_objects import on_failure


class URLDownload(Retrieval):

    BLOCK_SIZE = 8192

    def __init__(self, url, tree_depth=0):
        super(URLDownload, self).__init__()
        self.__url = url
        self.__tree_depth = tree_depth
        self.__file_name = os.path.basename(urlparse(self.__url).path)

    @property
    def name(self):
        return "download {0}".format(self.__file_name)

    def set_destination(self, destination_name):
        name, ext = os.path.splitext(self.__file_name)
        if name.lower().endswith(".tar"):
            ext = ".tar" + ext

        self.__file_name = destination_name + ext
        return self

    def prepare(self):
        name, ext = os.path.splitext(self.__file_name)
        if name.lower().endswith(".tar"):
            name, e2 = os.path.splitext(name)

        if 'build_path' not in self._context:
            output_file_path = os.path.join(config['paths']['build'], name)
            self._context['build_path'] = output_file_path

    def process(self, progress):
        logging.info("processing download")
        output_file_path = self._context['build_path']
        archive_file_path = os.path.join(config['paths']['download'], self.__file_name)

        if os.path.isfile(output_file_path):
            logging.info("File already extracted: {0}".format(archive_file_path))
        else:
            if os.path.isfile(archive_file_path):
                logging.info("File already downloaded: {0}".format(archive_file_path))
            else:
                logging.info("File not yet downloaded: {0}".format(archive_file_path))
                self.download(archive_file_path, progress)
            progress.finish()

        if not self.extract(archive_file_path, output_file_path, progress):
            return False
        progress.finish()

        builddir = os.listdir(self._context["build_path"])
        if len(builddir) == 1:
            self._context["build_path"] = os.path.join(self._context["build_path"], builddir[0])
        return True

    def download(self, output_file_path, progress):
        logging.info("Downloading {} to {}".format(self.__url, output_file_path))
        progress.job = "Downloading"
        data = urllib2.urlopen(self.__url)
        with open(output_file_path, 'wb') as outfile:
            meta = data.info()
            length_str = meta.getheaders("Content-Length")
            if length_str:
                progress.maximum = int(length_str[0])
            else:
                progress.maximum = sys.maxint

            bytes_read = 0
            while True:
                block = data.read(URLDownload.BLOCK_SIZE)
                if not block:
                    break
                bytes_read += len(block)
                outfile.write(block)
                progress.value = bytes_read

    def extract(self, archive_file_path, output_file_path, progress):
        def progress_func(pos, size):
            progress.value = int(pos * 100 / size)

        logging.info("Extracting {0}".format(self.__url))

        progress.value = 0
        progress.job = "Extracting"
        output_file_path = u"\\\\?\\" + os.path.abspath(output_file_path)

        try:
            os.makedirs(output_file_path)
        except Exception:
            # doesn't matter if the directory already exists.
            pass

        with on_failure(lambda: shutil.rmtree(output_file_path)):
            filename, extension = os.path.splitext(self.__file_name)
            if extension == ".gz" or extension == ".tgz":
                archive_file = ProgressFile(archive_file_path, progress_func)
                with tarfile.open(fileobj=archive_file, mode='r:gz') as arch:
                    arch.extractall(output_file_path)
                archive_file.close()
            elif extension == ".bz2":
                archive_file = ProgressFile(archive_file_path, progress_func)
                with tarfile.open(fileobj=archive_file, mode='r:bz2') as arch:
                    arch.extractall(output_file_path)
                archive_file.close()
            elif extension == ".zip":
                archive_file = ProgressFile(archive_file_path, progress_func)
                with zipfile.ZipFile(archive_file) as arch:
                    arch.extractall(output_file_path)
                archive_file.close()
            elif extension == ".7z":
                proc = subprocess.Popen([config['paths']['7z'], "x", archive_file_path, "-o{}".format(output_file_path)])
                if proc.wait() != 0:
                    return False
            elif extension in [".exe", ".msi"]:
                # installers need to be handled by the caller
                return True
            else:
                logging.error("unsupported file extension {0}".format(extension))
                return False

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
