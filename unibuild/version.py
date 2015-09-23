__author__ = 'Tannin'


class Version(object):
    def __init__(self, version_string):
        self.__versionString = version_string

    def __eq__(self, other):
        return self.__versionString == other.__versionString

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        return self.__versionString < other.__versionString

    def __gt__(self, other):
        return self.__versionString > other.__versionString

    def __ge__(self, other):
        return self.__versionString >= other.__versionString

    def __le__(self, other):
        return self.__versionString <= other.__versionString