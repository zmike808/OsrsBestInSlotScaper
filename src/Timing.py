import time


def timing_wrapper(timed_function):
    def wrap(*args, **kwargs):
        start_time = time.time()
        return_value = timed_function(*args, **kwargs)
        end_time = time.time()
        print('{:s} function took {:.3f} ms'.format(timed_function.__name__, (end_time - start_time) * 1000.0))
        return return_value
    return wrap
