import time

from data.US_share_data.daily_summary.concurrent_download_and_process_data import US_get_processed_data

from functools import wraps
import time
from tools.time_decorator import timeit
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

from data_processing.process_individual_basic_data import calculate_individual_stock_single_result
from data_processing.process_individual_US_get_cap_and_industry import US_data_get_cap_and_industry
from data_source.data_source_total import us_common_total_ticker_list


if __name__ == '__main__':
    # US_get_processed_data(only_for_common_tickers=True, auto_save=True)
    print(calculate_individual_stock_single_result('AAPL'))
    # US_data_get_cap_and_industry('BABA')
    # print(us_common_total_ticker_list)
