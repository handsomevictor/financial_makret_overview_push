from tqdm import tqdm
import concurrent.futures
import pandas as pd

# nasdaq & other company list
from tools.get_tickers.US.yahoo_fin.stock_info import tickers_nasdaq, tickers_other, tickers_dow
from data_source_url_total import sp500_tickers_csv_url
from data_processing.individual_US_get_cap_and_industry import US_data_get_cap_and_industry

import ssl
ssl._create_default_https_context = ssl._create_unverified_context  # ignore ssl certificate errors

import warnings
warnings.filterwarnings('ignore')


sp500_tickers = pd.read_csv(sp500_tickers_csv_url)['Symbol'].to_list()
nasdaq_ticker_list = tickers_nasdaq()
# dow_jones_ticker_list = tickers_dow()


def get_US_ticker_cap_and_industry(features=None):  # update features
    # return format: [('SDAC', 'Financial Services', 388987008), ('NWS', 'Communication Services', 10432429056)]
    all_tickers = list(set(sp500_tickers + nasdaq_ticker_list))[:10]

    with concurrent.futures.ProcessPoolExecutor(200) as executor:
        return_cap_and_industry = list(tqdm(executor.map(US_data_get_cap_and_industry, all_tickers), total=len(all_tickers)))

    return return_cap_and_industry


if __name__ == '__main__':
    print(pd.DataFrame(get_US_ticker_cap_and_industry()))
    pass
