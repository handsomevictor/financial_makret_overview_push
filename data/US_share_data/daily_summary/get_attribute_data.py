# Import packages
import yfinance as yf
import pandas as pd
from data_source_total import sp500_tickers_csv_url

import ssl
ssl._create_default_https_context = ssl._create_unverified_context  # ignore ssl certificate errors


# 3 columns: ['Symbol', 'Name', 'Sector']
sp500_tickers = pd.read_csv(sp500_tickers_csv_url)

