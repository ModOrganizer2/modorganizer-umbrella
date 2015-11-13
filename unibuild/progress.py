__author__ = 'Tannin'


class Progress(object):

    def __init__(self):
        self.__minimum = 0
        self.__maximum = 100
        self.__value = 0
        self.__job = ""
        self.__changeCallback = None

    @property
    def maximum(self):
        return self.__maximum

    @maximum.setter
    def maximum(self, new_value):
        self.__maximum = new_value

    @property
    def minimum(self):
        return self.__minimum

    @minimum.setter
    def minimum(self, new_value):
        self.__minimum = new_value

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, new_value):
        self.__value = new_value
        self.__call_callback()

    @property
    def job(self):
        return self.__job

    @job.setter
    def job(self, new_job):
        self.__job = new_job
        self.__call_callback()

    def __call_callback(self):
        if self.__changeCallback is not None:
            self.__changeCallback(self.__job, self.__value * 100 / self.__maximum)

    def finish(self):
        self.__changeCallback(self.__job, None)

    def set_change_callback(self, callback):
        self.__changeCallback = callback
