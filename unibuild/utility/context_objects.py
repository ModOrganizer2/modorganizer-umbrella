from contextlib import contextmanager


@contextmanager
def on_failure(func):
    """
    very generic context object generator that will run a parameterless lambda in case the
    wrapped code fails
    """
    try:
        yield
    except:
        func()
        raise

