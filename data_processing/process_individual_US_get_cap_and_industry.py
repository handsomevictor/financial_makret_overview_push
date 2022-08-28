# Only run once, and save the dict to pickle file
# sharesOutstanding 是总股本！换手率用volume/sharesOutstanding！
# 本文件每周只执行一次！把结果保存到temp_convenience_database root中！


import yfinance as yf
import pandas as pd
import os
import json
import platform
import warnings

warnings.filterwarnings("ignore")

from data_processing.process_individual_basic_data import judge_if_individual_processed_already_exists


def save_as_json_func(ticker, data):
    # 保存结果到temp_database中，因为一次执行一万多个太多了，所以直接每一个执行完直接保存
    if platform.system() == 'Linux':
        file_dir = os.path.join(os.getcwd(), 'financial_makret_overview_push', 'temp_database_for_convenience',
                                'US_individual_stock_single_result')
    else:
        file_dir = os.path.join(os.getcwd(), 'temp_database_for_convenience', 'US_individual_stock_single_result')

    file_name = os.path.join(file_dir, f'{ticker}_cap_industry.json')

    if not os.path.exists(file_dir):
        os.makedirs(file_dir)

    with open(file_name, 'w') as fp:
        json.dump(data, fp, indent=4)


# 该函数主要目的为下载并保存个股的数据到本地
def US_data_get_cap_and_industry(ticker, save_as_json=True):
    platform_name = platform.system()
    # 先判断是否再8个小时内已经下载过改数据
    res = judge_if_individual_processed_already_exists(ticker, platform_name, basic_or_cap='Cap_industry',
                                                       file_kind='cap_industry')
    if res[0]:
        return res[1]
    print(f'Cap Industry - {ticker} json file not exists, start downloading!')

    try:
        dhr = yf.Ticker(ticker)
        info = dhr.info
        result = dict((key, value) for key, value in info.items() if
                      key in ['symbol', 'sector', 'marketCap', 'financialCurrency'])

    except KeyError:  # doesn't exist in yahoo finance
        result = {
            'symbol': ticker,
            'sector': -1,
            'marketCap': -1,
            'financialCurrency': -1
        }

    if save_as_json:
        save_as_json_func(ticker=ticker, data=result)
        print(f'Cap_and_industry_{ticker} saved!')
    return result


if __name__ == '__main__':
    print(US_data_get_cap_and_industry('BABA'))

# 'financialCurrency'
