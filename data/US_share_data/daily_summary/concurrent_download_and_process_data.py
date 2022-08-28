from tqdm import tqdm
import pandas as pd
import os
import pickle
import json
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
from data_source_total import us_nasdaq_ticker_list, us_sp500_tickers, us_other_ticker_list

from data_processing.process_individual_US_get_cap_and_industry import US_data_get_cap_and_industry
# ---------------------------------------------------------------------------------------------------------------------


# pip.main(['install', 'pandas_datareader'])
# pip.main(['install', 'yahoo_fin'])
# pip.main(['install', 'requests_html'])
# pip.main(['install', 'html5lib'])

# import pandas_datareader.data as web


@timeit
def get_processed_data(which_market='us', auto_save=True):

    all_tickers = list(set(us_nasdaq_ticker_list + us_sp500_tickers + us_other_ticker_list))

    # SP500想办法解决一下
    # sp500_ticker_list = tickers_sp500()

    # 进行calculate_individual_stock_single_result第一轮concurrent处理，并将解决放入DataFrame中
    # with concurrent.futures.ProcessPoolExecutor(30) as executor:
    #     return_rate = pd.DataFrame(list(tqdm(executor.map(calculate_individual_stock_single_result, all_tickers),
    #                                          total=len(all_tickers))))
    #
    # # 进行第二次处理，加入market cap和industry
    #     return_cap_and_industry = pd.DataFrame(list(tqdm(executor.map(US_data_get_cap_and_industry, all_tickers),
    #                                                      total=len(all_tickers))), columns=['ticker',
    #                                                                                         'sector',
    #                                                                                         'market_cap',
    #                                                                                         'financialCurrency'])
    # # format: [('SDAC', 'Financial Services', 388987008), ('NWS', 'Communication Services', 10432429056)]

    with concurrent.futures.ProcessPoolExecutor(50) as executor:
        list(tqdm(executor.map(calculate_individual_stock_single_result, all_tickers), total=len(all_tickers)))
        list(tqdm(executor.map(US_data_get_cap_and_industry, all_tickers), total=len(all_tickers)))
    # format: [('SDAC', 'Financial Services', 388987008), ('NWS', 'Communication Services', 10432429056)]

    # 有一万多个文件夹，现在开始做成DataFrame
    basic_processed_data = pd.DataFrame()
    cap_industry_processed_data = pd.DataFrame()

    print('Process finished, now start read data and merge.')
    for ticker in tqdm(all_tickers):
        with open(os.path.join(os.getcwd(), 'temp_database_for_convenience', 'US_individual_stock_single_result',
                               f'{ticker}_without_cap_industry.json')) as f1:
            data1 = json.load(f1)
            basic_processed_data = basic_processed_data.append(pd.DataFrame(data1, index=[0]))
    for ticker in tqdm(all_tickers):
        with open(os.path.join(os.getcwd(), 'temp_database_for_convenience', 'US_individual_stock_single_result',
                               f'{ticker}_cap_industry.json')) as f2:
            data2 = json.load(f2)
            cap_industry_processed_data = cap_industry_processed_data.append(pd.DataFrame(data2, index=[0]))

    # 进行merge
    tickers_processed_result = basic_processed_data.merge(cap_industry_processed_data, left_on='ticker', right_on='symbol').drop(['symbol'], axis=1)
    tickers_processed_result = tickers_processed_result.drop_duplicates()

    if auto_save:
        file_name = os.path.join(os.getcwd(), 'temp_database_for_convenience',
                                 f'{which_market}_tickers_processed_result.pkl')
        tickers_processed_result.to_pickle(file_name)

    # 建议每次都保存一下到当前文件夹，然后再在别的地方用！也容易debug
    return tickers_processed_result


if __name__ == '__main__':
    # 建议在root下的__test中执行！因为有保存文件，所以在这里跑，路径会出问题！
    temp = get_processed_data()
