import os
import yfinance as yf
import pandas as pd
import numpy as np
from tqdm import tqdm
# from get_all_tickers import get_tickers as gt
import lxml
import html5lib
import pickle
import concurrent.futures
from data.US_share_data.daily_summary.process_individual_data import calculate_single_result
from tools.get_tickers.US.yahoo_fin.stock_info import get_data, tickers_sp500, tickers_nasdaq, \
    tickers_other, get_quote_table


import warnings
warnings.filterwarnings('ignore')

import pip
# pip.main(['install', 'pandas_datareader'])
# pip.main(['install', 'yahoo_fin'])
# pip.main(['install', 'requests_html'])
# pip.main(['install', 'html5lib'])

# import pandas_datareader.data as web


def get_processed_data():
    nasdaq_ticker_list = tickers_nasdaq()

    # SP500想办法解决一下
    # sp500_ticker_list = tickers_sp500()
    other_ticker_list = tickers_other()

    with concurrent.futures.ProcessPoolExecutor(200) as executor:
        return_rate = list(tqdm(executor.map(calculate_single_result, nasdaq_ticker_list), total=len(nasdaq_ticker_list)))

    # loc = os.path.join(os.getcwd(), 'nasdaq_return_test.pkl')
    #
    # with open(loc, 'wb') as fp:
    #     pickle.dump(dict(zip(nasdaq_ticker_list, return_rate)), fp)
    return return_rate


if __name__ == '__main__':
    print(get_processed_data())
