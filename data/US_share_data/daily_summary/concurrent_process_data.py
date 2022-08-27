from tqdm import tqdm
import pandas as pd
import time
import os
import pickle
import warnings
warnings.filterwarnings('ignore')

# from get_all_tickers import get_tickers as gt
import concurrent.futures
from data_processing.process_individual_data import calculate_individual_stock_single_result
from tools.time_decorator import timeit

# ---------------------------------------------------------------------------------------------------------------------
# nasdaq & other company list
from tools.get_tickers.US.yahoo_fin.stock_info import tickers_nasdaq, \
    tickers_other
from data_source_url_total import sp500_tickers_csv_url
from data_processing.individual_US_get_cap_and_industry import US_data_get_cap_and_industry
# ---------------------------------------------------------------------------------------------------------------------


# pip.main(['install', 'pandas_datareader'])
# pip.main(['install', 'yahoo_fin'])
# pip.main(['install', 'requests_html'])
# pip.main(['install', 'html5lib'])

# import pandas_datareader.data as web


@timeit
def get_processed_data(which_market='us', auto_save=True):
    start = time.time()

    nasdaq_ticker_list = tickers_nasdaq()
    sp500_tickers = pd.read_csv(sp500_tickers_csv_url)['Symbol'].to_list()
    other_ticker_list = tickers_other()
    all_tickers = list(set(sp500_tickers + nasdaq_ticker_list + other_ticker_list))

    # SP500想办法解决一下
    # sp500_ticker_list = tickers_sp500()

    # 进行calculate_individual_stock_single_result第一轮concurrent处理，并将解决放入DataFrame中
    with concurrent.futures.ProcessPoolExecutor(200) as executor:
        return_rate = pd.DataFrame(list(tqdm(executor.map(calculate_individual_stock_single_result, all_tickers),
                                             total=len(all_tickers))))

    # 进行第二次处理，加入market cap和industry
    with concurrent.futures.ProcessPoolExecutor(200) as executor:
        return_cap_and_industry = pd.DataFrame(list(tqdm(executor.map(US_data_get_cap_and_industry, all_tickers), total=len(all_tickers))),
                                               columns=['ticker', 'sector', 'market_cap', 'financialCurrency'])
    # format: [('SDAC', 'Financial Services', 388987008), ('NWS', 'Communication Services', 10432429056)]

    # 进行merge
    tickers_processed_result = return_rate.merge(return_cap_and_industry, on='ticker')

    end = time.time()
    print('Time used: {}'.format(end - start))

    if auto_save:
        file_name = os.path.join(os.getcwd(), 'temp_data_csv_for_convenience', f'tickers_processed_result_of_{which_market}.pkl')
        temp.to_pickle(file_name, index=False)

    # 建议每次都保存一下到当前文件夹，然后再在别的地方用！也容易debug
    return tickers_processed_result


if __name__ == '__main__':
    # 建议在root下的__test中执行！因为有保存文件，所以在这里跑，路径会出问题！
    temp = get_processed_data()
