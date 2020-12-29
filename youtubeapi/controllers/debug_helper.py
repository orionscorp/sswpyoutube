import time

'''
Every functions and variables here are only for debuggging purposes.
'''
class apicalls:
    API_CALLS_MADE_FUNCTION = 0
    API_CALLS_MADE_SESSION = 0

# Class to color the output of the terminal, untested on Windows or Mac.
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def st_time(func):
    """
        st decorator to calculate the total time of a func
    """

    def st_func(*args, **keyArgs):
        t1 = time.time()
        r = func(*args, **keyArgs)
        t2 = time.time()
        print (f"{bcolors.OKGREEN}Function=%s, Time=%s{bcolors.ENDC}" % (func.__name__, t2 - t1))
        print (f"{bcolors.OKGREEN}YouTube api calls made from this function=%s{bcolors.ENDC}" % apicalls.API_CALLS_MADE_FUNCTION)
        apicalls.API_CALLS_MADE_SESSION += apicalls.API_CALLS_MADE_FUNCTION
        apicalls.API_CALLS_MADE_FUNCTION = 0 # set it back to zero
        print (f"{bcolors.OKGREEN}YouTube api calls made during this session=%s{bcolors.ENDC}" % apicalls.API_CALLS_MADE_SESSION)
        return r

    return st_func