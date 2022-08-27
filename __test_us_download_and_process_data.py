import time

from data.US_share_data.daily_summary.concurrent_process_data import get_processed_data

from functools import wraps
import time
from tools.time_decorator import timeit


@timeit
def trss():
    time.sleep(1)
    return 123


if __name__ == '__main__':
    # get_processed_data()
    a = trss()
    print(a)
