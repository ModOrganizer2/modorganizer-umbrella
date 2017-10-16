__author__ = 'Tannin'

import os

from config import config
from task import Task


class Retrieval(Task):
    def __init__(self):
        super(Retrieval, self).__init__()
        try:
            os.makedirs(config["paths"]["download"])
        except Exception, e:
            # ignore error, probably means the path already exists
            pass

    def fulfilled(self):
        super(Retrieval, self).fulfilled()

    def applies(self, parameters):
        return True

    @property
    def name(self):
        return

    def process(self, progress):
        return
