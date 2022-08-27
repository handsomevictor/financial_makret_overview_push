# All data sources:
import pandas as pd


# ---------------------------------------------------------------------------------------------------------------------
# US stock market ####################################### ticker data ##################################################
from tools.get_tickers.US.yahoo_fin.stock_info import tickers_nasdaq, tickers_other

us_nasdaq_ticker_list = tickers_nasdaq()
us_other_ticker_list = tickers_other()

# S&P 500 tickers:
us_sp500_tickers_csv_url = 'https://datahub.io/core/s-and-p-500-companies/r/constituents.csv'
us_sp500_tickers = pd.read_csv(us_sp500_tickers_csv_url)['Symbol'].to_list()
# sp500_tickers_parse_url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'


