import os

from config import config
from unibuild.retrieval import Retrieval


class Repository(Retrieval):
    def __init__(self, url, branch):
        super(Repository, self).__init__()
        self._url = url
        self._branch = branch
        self._dir_name = os.path.basename(self._url)
        self._output_file_path = os.path.join(config["paths"]["build"], self._dir_name)

    @property
    def name(self):
        return "retrieve {0}".format(self._dir_name)
