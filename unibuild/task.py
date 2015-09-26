from manager import TaskManager
import os.path
import time
from config import config


class Task(object):
    class FailBehaviour:
        FAIL = 1
        CONTINUE = 2
        SKIP_PROJECT = 3

    def __init__(self):
        self.__dependencies = []
        self._context = None
        self.__fail_behaviour = Task.FailBehaviour.FAIL

    def name(self):
        return

    def settings(self):
        return {}

    @property
    def dependencies(self):
        return self.__dependencies

    @property
    def enabled(self):
        return True

    @enabled.setter
    def enabled(self, value):
        pass

    @property
    def fail_behaviour(self):
        return self.__fail_behaviour

    def set_fail_behaviour(self, behaviour):
        self.__fail_behaviour = behaviour
        return self

    @staticmethod
    def _expiration():
        return None

    def __success_path(self):
        task_name = self.name.replace("/", "_").replace("\\", "_")
        ctx_name = self._context.name if self._context else task_name
        return os.path.join(config["__build_base_path"], "progress",
                            "{}_complete_{}.txt".format(ctx_name, task_name))

    def already_processed(self):
        if not os.path.exists(self.__success_path()):
            return False

        expiration_duration = self._expiration()
        if expiration_duration:
            return os.path.getmtime(self.__success_path()) + expiration_duration > time.time()
        else:
            return True

    def mark_success(self):
        with open(self.__success_path(), "w"):
            pass

    def depend(self, task):
        if type(task) == str:
            task_obj = TaskManager().get_task(task)
            if task_obj is None:
                raise KeyError("unknown project \"{}\"".format(task))
            else:
                task = task_obj
        else:
            if self._context:
                task.set_context(self._context)
        self.__dependencies.append(task)
        return self

    def set_context(self, context):
        if not self._context:
            self._context = context
            for dep in self.__dependencies:
                dep.set_context(context)

    def applies(self, parameters):
        return

    def fulfilled(self):
        for dep in self.__dependencies:
            if not dep.fulfilled():
                return False
        return True

    def prepare(self):
        """
        initialize this task. At this point you can rely on required tasks to have run. This should be quick to
        complete but needs to initialize everything required by dependent tasks (globals, config, context).
        unlike progress, this is called if the task ran successfully already
        """
        pass

    def process(self, progress):
        pass
