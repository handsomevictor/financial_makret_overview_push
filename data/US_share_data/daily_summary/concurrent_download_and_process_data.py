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


@timeit
# 先运行完common tickers，都计算完了，再去搞别的！不然实在太慢了！
def US_get_processed_data(which_market='us', only_for_common_tickers=True, auto_save=True):
    if only_for_common_tickers:
        all_tickers = us_common_total_ticker_list
    else:
        # 此时指的是除了common以外的tickers，这里绝大绝大部分都是已经delisted的，跑完主要程序之后再跑这个就行！
        temp = list(set(us_nasdaq_ticker_list + us_sp500_tickers + us_other_ticker_list))
        all_tickers = [i for i in temp if i not in us_common_total_ticker_list]

    with concurrent.futures.ProcessPoolExecutor(50) as executor:
        # 进行calculate_individual_stock_single_result第一轮concurrent处理，并将解决放入DataFrame中
        list(tqdm(executor.map(calculate_individual_stock_single_result, all_tickers), total=len(all_tickers)))
        # 进行第二次处理，加入market cap和industry
        list(tqdm(executor.map(US_data_get_cap_and_industry, all_tickers), total=len(all_tickers)))
        # format: [('SDAC', 'Financial Services', 388987008), ('NWS', 'Communication Services', 10432429056)]

    # 有一万多个文件夹，现在开始做成DataFrame
    basic_processed_data = pd.DataFrame()
    cap_industry_processed_data = pd.DataFrame()

    print('Process finished, now start read data and merge.')
    platform_name = platform.system()

    for ticker in tqdm(all_tickers):
        if platform_name == 'Linux':
            file_name = os.path.join(os.getcwd(), 'financial_makret_overview_push', 'temp_database_for_convenience',
                                     'US_individual_stock_single_result', f'{ticker}_without_cap_industry.json')
        else:
            file_name = os.path.join(os.getcwd(), 'temp_database_for_convenience', 'US_individual_stock_single_result',
                                     f'{ticker}_without_cap_industry.json')

        with open(file_name) as f1:
            data1 = json.load(f1)
            basic_processed_data = basic_processed_data.append(pd.DataFrame(data1, index=[0]))

    for ticker in tqdm(all_tickers):
        if platform_name == 'Linux':
            file_name = os.path.join(os.getcwd(), 'financial_makret_overview_push', 'temp_database_for_convenience',
                                     'US_individual_stock_single_result', f'{ticker}_cap_industry.json')
        else:
            file_name = os.path.join(os.getcwd(), 'temp_database_for_convenience', 'US_individual_stock_single_result',
                                     f'{ticker}_cap_industry.json')

        with open(file_name) as f2:
            data2 = json.load(f2)
            cap_industry_processed_data = cap_industry_processed_data.append(pd.DataFrame(data2, index=[0]))

    # 进行merge
    tickers_processed_result = basic_processed_data.merge(cap_industry_processed_data, left_on='ticker',
                                                          right_on='symbol').drop(['symbol'], axis=1)
    tickers_processed_result = tickers_processed_result.drop_duplicates()

    if auto_save:
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

    # 建议每次都保存一下到当前文件夹，然后再在别的地方用！也容易debug
    return tickers_processed_result


if __name__ == '__main__':
    # 建议在root下的__test中执行！因为有保存文件，所以在这里跑，路径会出问题！
    temp = US_get_processed_data()
