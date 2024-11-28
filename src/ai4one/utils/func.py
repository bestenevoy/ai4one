import inspect

def get_current_function_name():
    # Get the name of the currently running function
    return inspect.stack()[1].function
