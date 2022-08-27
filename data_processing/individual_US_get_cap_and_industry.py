# Only run once, and save the dict to pickle file

import yfinance as yf
import pandas as pd


def US_data_get_cap_and_industry(ticker):
    try:
        dhr = yf.Ticker(ticker)
        info = dhr.info
        return ticker, info['sector'], info['marketCap'], info['financialCurrency']
    except KeyError:  # doesn't exist in yahoo finance
        return ticker, -1, -1, -1


if __name__ == '__main__':
    print(US_data_get_cap_and_industry('AAPL'))

# 'financialCurrency'
