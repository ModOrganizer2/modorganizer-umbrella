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

        output_file_path = os.path.join(config["paths"]["build"], name)
        self._context["build_path"] = output_file_path

    def process(self, progress):
        output_file_path = self._context["build_path"]
        archive_file_path = os.path.join(config["paths"]["download"], self.__file_name)

        if os.path.isdir(output_file_path):
            logging.info("File already extracted: {0}".format(output_file_path))
        else:
            if os.path.isfile(archive_file_path):
                logging.info("File already downloaded: {0}".format(archive_file_path))
            else:
                logging.info("File not yet downloaded: {0}".format(archive_file_path))
                self.download(archive_file_path, progress)

            self.extract(archive_file_path, output_file_path, progress)

        builddir = os.listdir(self._context["build_path"])
        if len(builddir) == 1:
            self._context["build_path"] = os.path.join(self._context["build_path"], builddir[0])
        return True

    def download(self, output_file_path, progress):
        logging.info("Downloading {} to {}".format(self.__url, output_file_path))
        data = urllib2.urlopen(self.__url)
        with open(output_file_path, 'wb') as outfile:
            meta = data.info()
            length_str = meta.getheaders("Content-Length")
            if length_str:
                progress.maximum = int(length_str[0]) * 2
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
        output_file_path = u"\\\\?\\" + os.path.abspath(output_file_path)

        logging.info("Extracting {0}".format(self.__url))

        os.makedirs(output_file_path)
        filename, extension = os.path.splitext(self.__file_name)
        print("{}".format(filename))
        if extension == ".gz":
            with tarfile.open(archive_file_path, 'r:gz') as arch:
                arch.extractall(output_file_path)
        elif extension == ".bz2":
            with tarfile.open(archive_file_path, 'r:bz2') as arch:
                arch.extractall(output_file_path)
        elif extension == ".zip":
            with zipfile.ZipFile(archive_file_path) as arch:
                arch.extractall(output_file_path)
        elif extension == ".7z":
            subprocess.call(["7za", "x", archive_file_path, "-o{}".format(output_file_path)])
        else:
            logging.error("unsupported file extension {0}".format(extension))

        for i in range(self.__tree_depth):
            sub_dirs = os.listdir(output_file_path)
            if len(sub_dirs) != 1:
                raise ValueError("unexpected archive structure,"
                                 " expected exactly one directory in {}".format(output_file_path))
            source_dir = os.path.join(output_file_path, sub_dirs[0])

            for src in os.listdir(source_dir):
                shutil.move(os.path.join(source_dir, src), output_file_path)

            shutil.rmtree(source_dir)
