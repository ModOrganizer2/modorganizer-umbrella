__author__ = 'Tannin'


from task import Task


class Builder(Task):

    def __init__(self):
        super(Builder, self).__init__()

    def applies(self, parameters):
        return True

    def name(self):
        return

    def process(self, progress):
        return
