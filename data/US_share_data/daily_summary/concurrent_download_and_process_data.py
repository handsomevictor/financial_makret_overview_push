from tqdm import tqdm
import pandas as pd
import os
import pickle
import json
import platform
import warnings

warnings.filterwarnings('ignore')

# from get_all_tickers import get_tickers as gt
import concurrent.futures
from data_processing.process_individual_basic_data import calculate_individual_stock_single_result
from tools.time_decorator import timeit
from urllib.error import HTTPError

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

# ---------------------------------------------------------------------------------------------------------------------
# US ticker list
from data_source.data_source_total import us_nasdaq_ticker_list, us_sp500_tickers, us_other_ticker_list, \
    us_common_total_ticker_list

from data_processing.process_individual_US_get_cap_and_industry import US_data_get_cap_and_industry


# ---------------------------------------------------------------------------------------------------------------------


# pip.main(['install', 'pandas_datareader'])
# pip.main(['install', 'yahoo_fin'])
# pip.main(['install', 'requests_html'])
# pip.main(['install', 'html5lib'])

# import pandas_datareader.data as web


def read_and_merge_individual_processed_stock_from_local(all_tickers, platform_name, file_kind):
    processed_data = pd.DataFrame()
    for ticker in tqdm(all_tickers):
        if platform_name == 'Linux':
            file_name = os.path.join(os.getcwd(), 'financial_makret_overview_push', 'temp_database_for_convenience',
                                     'US_individual_stock_single_result', f'{ticker}_{file_kind}.json')
        else:
            file_name = os.path.join(os.getcwd(), 'temp_database_for_convenience', 'US_individual_stock_single_result',
                                     f'{ticker}_{file_kind}.json')

        with open(file_name) as f:
            # The file might be None, empty files seems can't be loaded.
            try:
                data = json.load(f)
                processed_data = processed_data.append(pd.DataFrame(data, index=[0]))
            except json.decoder.JSONDecodeError:
                print(f'JSONDecodeError on file {ticker}_{file_kind}.json!')
                continue
    return processed_data


def auto_save_all_processed_stock_to_local(only_for_common_tickers, which_market, platform_name, tickers_processed_result):
    if only_for_common_tickers:
        if platform_name == 'Linux':
            file_name = os.path.join(os.getcwd(), 'financial_makret_overview_push', 'temp_database_for_convenience',
                                     f'{which_market}_common_tickers_processed_result.pkl')
        else:
            file_name = os.path.join(os.getcwd(), 'temp_database_for_convenience',
                                     f'{which_market}_common_tickers_processed_result.pkl')
    else:
        if platform_name == 'Linux':
            file_name = os.path.join(os.getcwd(), 'financial_makret_overview_push', 'temp_database_for_convenience',
                                     f'{which_market}_uncommon_tickers_processed_result.pkl')
        else:
            file_name = os.path.join(os.getcwd(), 'temp_database_for_convenience',
                                     f'{which_market}_uncommon_tickers_processed_result.pkl')

    tickers_processed_result.to_pickle(file_name)
    print(f'{which_market} tickers processed result saved to {file_name}')


@timeit
# ????????????common tickers???????????????????????????????????????????????????????????????
def US_get_processed_data(which_market='us', only_for_common_tickers=True, auto_save=True):
    platform_name = platform.system()

    if only_for_common_tickers:
        all_tickers = us_common_total_ticker_list
    else:
        # ?????????????????????common?????????tickers???????????????????????????????????????delisted???????????????????????????????????????????????????
        temp = list(set(us_nasdaq_ticker_list + us_sp500_tickers + us_other_ticker_list))
        all_tickers = [i for i in temp if i not in us_common_total_ticker_list]

    # ------------------------------------------------------------------------------------------------------------------
    # Start downloading information (basic and cap_industry) and save those individual files to local
    # In case of Network Error: run twice
    for _ in range(1):
        print(f'{_+1} time trying downloading or reading basic json individual files.')
        try:
            with concurrent.futures.ProcessPoolExecutor(50) as executor:
                # ??????calculate_individual_stock_single_result?????????concurrent???????????????????????????DataFrame???
                list(tqdm(executor.map(calculate_individual_stock_single_result, all_tickers), total=len(all_tickers)))
        except HTTPError:
            print('Network Error on basic individual files, please try again!')
            continue

    for _ in range(1):
        print(f'{_ + 1} time trying downloading or reading cap industry json individual files.')
        try:
            with concurrent.futures.ProcessPoolExecutor(50) as executor:
                # ??????????????????????????????market cap???industry
                list(tqdm(executor.map(US_data_get_cap_and_industry, all_tickers), total=len(all_tickers)))
                # format: [('SDAC', 'Financial Services', 388987008), ('NWS', 'Communication Services', 10432429056)]
        except HTTPError:
            print('Network Error on cap industry individual files, please try again!')
            continue

    # ------------------------------------------------------------------------------------------------------------------
    # Starting reading all those files (either 3K or 9K)
    # ???????????????json???????????????????????????DataFrame
    print('Process finished, now start read data and merge.')
    basic_processed_data = read_and_merge_individual_processed_stock_from_local(all_tickers, platform_name,
                                                                                file_kind='without_cap_industry')
    cap_industry_processed_data = read_and_merge_individual_processed_stock_from_local(all_tickers, platform_name,
                                                                                       file_kind='cap_industry')

    # ??????info??????merge
    tickers_processed_result = basic_processed_data.merge(cap_industry_processed_data, left_on='ticker',
                                                          right_on='symbol').drop(['symbol'], axis=1)
    tickers_processed_result = tickers_processed_result.drop_duplicates()

    # ------------------------------------------------------------------------------------------------------------------
    # Start saving all processed data
    if auto_save:
        # function is above
        auto_save_all_processed_stock_to_local(only_for_common_tickers, which_market, platform_name, tickers_processed_result)

    # ???????????????????????????????????????????????????????????????????????????????????????debug
    return tickers_processed_result


if __name__ == '__main__':
    # ?????????root??????__test??????????????????????????????????????????????????????????????????????????????
    temp = US_get_processed_data()
