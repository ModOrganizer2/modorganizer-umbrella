__author__ = 'Tannin'

from project import Project


class Dependency(Project):
    def __init__(self, name):
        super(Dependency, self).__init__(name)

    def applies(self, parameters):
        return True

    def version_eq(self, version):
        return self
