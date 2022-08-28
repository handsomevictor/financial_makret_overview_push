# All data sources:
import pandas as pd
import json
import os
from tqdm import tqdm
import pickle
import datetime

import warnings
warnings.filterwarnings("ignore")

import ssl
ssl._create_default_https_context = ssl._create_unverified_context


# ---------------------------------------------------------------------------------------------------------------------
# US stock market ####################################### ticker data ##################################################
from tools.get_tickers.US.yahoo_fin.stock_info import tickers_nasdaq, tickers_other

us_nasdaq_ticker_list = tickers_nasdaq()
us_other_ticker_list = tickers_other()

# S&P 500 tickers:
us_sp500_tickers_csv_url = 'https://datahub.io/core/s-and-p-500-companies/r/constituents.csv'
us_sp500_tickers = pd.read_csv(us_sp500_tickers_csv_url)['Symbol'].to_list()
# sp500_tickers_parse_url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'


# US stock market ####################################### ticker data ##################################################
# 定义一个常用US ticker，大大减少时间，在这些ticker执行完之后，再去执行其他的全部，分两次发邮件，第一个叫：major market move，第二个叫
# comprehensive market overview
def us_common_tickers(us_nasdaq_ticker_list, us_other_ticker_list, us_sp500_tickers):
    # 先判断是否已经下载了common tickers，如果有，直接读取并return，没有则重新读取上一次运行完之后的两万多个json文件提取common tickers！
    # 如果这个文件是5天前的，则重新下载！
    try:
        file_loc = os.path.join(os.getcwd(), 'temp_database_for_convenience', 'us_common_tickers.pkl')
        # 查看文件创建时间
        m_time = os.path.getmtime(file_loc)
        dt_m = datetime.datetime.fromtimestamp(m_time)
        days_diff = (datetime.datetime.now() - dt_m).days
        if days_diff < 3:
            with open(file_loc, 'rb') as f:
                common_tickers = pickle.load(f)
                print('Common tickers file exists, data loaded!')
            return common_tickers
        else:
            raise FileNotFoundError

    except FileNotFoundError:
        # 开始重新获取九千多个uncommon tickers的数据！
        print('Common tickers file expired or does not exists, common and uncommon tickers processed data redownloading!')

        # 重新下载uncommon文件！
        # 这里没有下载！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！

        file_name = os.path.join(os.getcwd(), 'temp_database_for_convenience', 'us_uncommon_tickers_processed_result.pkl')
        with open(file_name, 'rb') as f:
            tickers_processed_result = pickle.load(f)

        return tickers_processed_result.ticker.to_list()


us_common_total_ticker_list = us_common_tickers(us_nasdaq_ticker_list, us_other_ticker_list, us_sp500_tickers).ticker.to_list()

if __name__ == '__main__':
    print(us_common_total_ticker_list)
