import time

from data.US_share_data.daily_summary.concurrent_download_and_process_data import get_processed_data

from functools import wraps
import time
from tools.time_decorator import timeit
import ssl
ssl._create_default_https_context = ssl._create_unverified_context


@timeit
def trss():
    time.sleep(1)
    return 123


if __name__ == '__main__':
    get_processed_data(auto_save=True)
