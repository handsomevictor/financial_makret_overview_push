# 输出这么几个参数：
# 1. 当天close price
# 2. 涨跌幅
# 3. 行业
# 4. ？财报时间？
# 5. 计算60天和30天的return，判断今天的是否在95%置信区间内！输出两个True or False,最后判断是在8%到92%的区间！
# 6. 判断是上涨，超级上涨，下跌，超级下跌，还是走平的趋势！方法：看均线：5，10，20，30，60得分为20，20，25，35，40分，5大于10则加20分，20小于
#    30则减20分，若一共大于80为超级上涨，30-80为上涨。分两个趋势，一个看30天的，一个看60天的！
#    -20到+20为平，以此类推

# 在判断trend是哪种类型时：bear & bull first method threshold - detailed information please refer to data_processing/market_trend_manually_set.py
# 有两种方法，详见下：
import os
import random
import json
import yfinance as yf
import numpy as np
import scipy.stats as stats
from collections import defaultdict
import pandas_datareader as web
import datetime
import platform
import pickle
# import gzip

import warnings
warnings.filterwarnings("ignore")

from data_processing.market_trend_manually_set import get_trend_bull_bear_threshold
from parameters import score_standard

platform_name = platform.system()


# For the output of p-value
def mean_confidence_interval(data, confidence=0.95):
    a = 1.0 * np.array(data)
    n = len(a)
    m, se = np.mean(a), scipy.stats.sem(a)
    h = se * scipy.stats.t.ppf((1 + confidence) / 2., n - 1)
    return m, m - h, m + h


def calculate_daily_return(data):
    try:
        data['change'] = data['Close'].pct_change()
        data['change'] = data['change'].fillna(0)
        daily_return = data['change'].iloc[-1]
        return daily_return, data['Close'].iloc[-1]
    except IndexError:
        return -1, -1


def calculate_n_days_return(data, n):
    # 需要翻转一下
    try:
        temp = data.iloc[::-1]
        return_n_days = (1 + temp.change).cumprod()[n - 1] - 1
        return return_n_days
    except IndexError:  # 有一些可能没有这么多数据
        return -1


def judge_daily_return_outlier(data):
    # 计算outlier daily return，这里不能用正态分布，因为算出来的值几乎每天都是outlier
    # 将所有return排序，取上下95%的位置
    try:
        lower_bound = np.quantile(data['change'].to_list(), 0.08)
        upper_bound = np.quantile(data['change'].to_list(), 0.92)

        if data['change'].iloc[-1] < lower_bound or data['change'].iloc[-1] > upper_bound:
            return True
        else:
            return False
    except IndexError:
        return -1


def calculate_p_value(data):
    # lower_bound, higher_bound = stats.t.interval(confidence=0.99,
    #                                              df=len(return_list) - 1,
    #                                              loc=np.mean(return_list),
    #                                              scale=stats.sem(return_list))
    return 0


def trend_result(score, trend_threshold, which_trend='30'):
    # 该函数用于判断trend - 两种MA方法均适用
    return 'VERY BULL' if score > trend_threshold[f'trend_{which_trend}']['very_bull'] \
        else 'BULL' if score > trend_threshold[f'trend_{which_trend}']['bull'] \
        else 'BEAR' if score < trend_threshold[f'trend_{which_trend}']['bear'] \
        else 'VERY BEAR' if score < trend_threshold[f'trend_{which_trend}']['very_bear'] \
        else 'FLAT'


def judge_trend_using_MA_first_method(data, score_standard):
    try:
        # 第一种：绝对boolean来判断trend
        MA_days = [5, 10, 20, 30, 40, 50, 60, 90, 120]
        MA5, MA10, MA20, MA30, MA40, MA50, MA60, MA90, MA120 = [data['Close'].rolling(window=i).mean()[-1] for i in
                                                                MA_days]

        status_trend_lambda = (lambda x: 1 if x else -1)
        scenario = [MA5 > MA10, MA10 > MA20, MA20 > MA30, MA30 > MA40, MA40 > MA50, MA50 > MA60, MA60 > MA90,
                    MA90 > MA120]
        scenario = [status_trend_lambda(i) for i in scenario]

        score_30_first_method = np.sum(np.array([*score_standard.values()][:-4]) * np.array(scenario[:-4]))
        score_60_first_method = np.sum(np.array([*score_standard.values()]) * np.array(scenario))

        # bear & bull first method threshold - detailed information please refer to data_processing/market_trend_manually_set.py
        trend_threshold_first_method = get_trend_bull_bear_threshold(score_list=list(score_standard.values()))
        return trend_result(score_30_first_method, trend_threshold_first_method, which_trend='30'), \
               trend_result(score_60_first_method, trend_threshold_first_method, which_trend='60')
    except IndexError:
        return 'not_available', 'not_available'


def judge_trend_using_MA_second_method(data, score_standard):
    try:
        # 用各个MA超出百分比乘上每个level的weights来做相对比较
        MA_days = [5, 10, 20, 30, 40, 50, 60, 90, 120]
        MA5, MA10, MA20, MA30, MA40, MA50, MA60, MA90, MA120 = [data['Close'].rolling(window=i).mean()[-1] for i in
                                                                MA_days]

        temp1 = [MA5, MA10, MA20, MA30, MA40, MA50, MA60, MA90]
        temp2 = [MA10, MA20, MA30, MA40, MA50, MA60, MA90, MA120]

        scenario2 = [(lambda x, y: x / y - 1)(i, j) for i, j in zip(temp1, temp2)]  # 计算超出的比例
        new_MA_weights = np.array(scenario2) * np.array(list(score_standard.values()))  # 计算新的各个MA的比重

        trend_threshold_second_method = get_trend_bull_bear_threshold(score_list=new_MA_weights)

        # 计算最终得分
        score_30_second_method = np.sum(np.array(list(score_standard.values())[:-4]) * np.array(scenario2[:-4]))
        score_60_second_method = np.sum(np.array(list(score_standard.values())) * np.array(scenario2))

        return trend_result(score_30_second_method, trend_threshold_second_method, which_trend='30'), \
               trend_result(score_60_second_method, trend_threshold_second_method, which_trend='60')
    except IndexError:
        return 'not_available', 'not_available'


def save_individual_processed_basic_res(ticker, features, platform_name):
    if platform_name == 'Linux':

        # 保存结果到temp_database中，因为一次执行一万多个太多了，所以直接每一个执行完直接保存
        file_dir = os.path.join(os.getcwd(), 'financial_makret_overview_push', 'temp_database_for_convenience',
                                'US_individual_stock_single_result')
    else:
        file_dir = os.path.join(os.getcwd(), 'temp_database_for_convenience', 'US_individual_stock_single_result')

    if not os.path.exists(file_dir):
        os.makedirs(file_dir)

    file_name = os.path.join(file_dir, f'{ticker}_without_cap_industry.json')

    if not os.path.exists(file_dir):
        os.makedirs(file_dir)

    with open(file_name, 'w') as fp:
        json.dump(features, fp, indent=4)
        print(f'Basic_data_{ticker} saved!')


def judge_if_individual_processed_already_exists(ticker, platform_name, file_kind='without_cap_industry'):
    if platform_name == 'Linux':
        file_dir = os.path.join(os.getcwd(), 'financial_makret_overview_push', 'temp_database_for_convenience',
                                'US_individual_stock_single_result')
    else:
        file_dir = os.path.join(os.getcwd(), 'temp_database_for_convenience', 'US_individual_stock_single_result')

    if not os.path.exists(file_dir):
        os.makedirs(file_dir)

    file_name = os.path.join(file_dir, f'{ticker}_{file_kind}.json')

    m_time = os.path.getmtime(file_name)
    dt_m = datetime.datetime.fromtimestamp(m_time)
    days_diff = (datetime.datetime.now() - dt_m).seconds / 3600
    if days_diff < 8:
        with open(file_name, 'rb') as f:
            try:
                basic_ticker_data = json.load(f)
                print(f'Basic {ticker} json file exists, data loaded!')
            except EOFError:  # EOFError: Ran out of input - means it is an empty file!
                print(f'Basic {ticker} json file exists, but is empty!')
                return False, None
        return True, basic_ticker_data
    else:
        return False, None


# 该函数主要目的为下载并保存个股的数据到本地
def calculate_individual_stock_single_result(ticker, save_as_json=True):
    platform_name = platform.system()
    # First judge whether the single processed basic result (modified less than 12 hours) is in the database, if true,
    # do nothing.
    res = judge_if_individual_processed_already_exists(ticker, platform_name)
    if res[0]:
        return res[1]
    print(f'Basic - {ticker} json file not exists, start downloading!')

    # ------------------------------------------------------------------------------------------------------------------
    # features指的是对于单个股票分析的方面：
    features = {
        'ticker': ticker,
        'close_price': -1,
        'daily_return': -1,
        'return_5_days': -1,
        'return_30_days': -1,
        'outlier_daily_return': -1,
        'data_p_value': -1,
        'trend_30_days_first_method': -1,
        'trend_60_days_first_method': -1,
        'trend_30_days_second_method': -1,
        'trend_60_days_second_method': -1,
    }

    # ------------------------------------------------------------------------------------------------------------------
    # 获取数据，如果没有数据，则返回default feature value
    try:
        data = yf.Ticker(ticker).history(period='120d', interval='1d')
    except IndexError:
        return features  # !!!!!!! 这里有很多项，所有项都要做到-1！

    # ------------------------------------------------------------------------------------------------------------------
    # 计算daily return
    features['daily_return'], features['close_price'] = calculate_daily_return(data)

    # ------------------------------------------------------------------------------------------------------------------
    # 计算5 days return和30 days return
    features['return_5_days'] = calculate_n_days_return(data, 5)
    features['return_30_days'] = calculate_n_days_return(data, 30)

    # ------------------------------------------------------------------------------------------------------------------
    # 计算boolean: if daily return is outlier
    features['outlier_daily_return'] = judge_daily_return_outlier(data)

    # ------------------------------------------------------------------------------------------------------------------
    # 计算p-value
    features['data_p_value'] = calculate_p_value(data)

    # ------------------------------------------------------------------------------------------------------------------
    # 计算trend - 2种方法：1：用boolean来做绝对比较；2：用各个MA超出百分比乘上每个level的weights来做相对比较
    # 第一种方法
    features['trend_30_days_first_method'], features['trend_60_days_first_method'] = judge_trend_using_MA_first_method(
        data, score_standard)
    # 第二种方法
    features['trend_30_days_second_method'], features[
        'trend_60_days_second_method'] = judge_trend_using_MA_second_method(data, score_standard)

    # 保存结果到temp_database中，因为一次执行一万多个太多了，所以直接每一个执行完直接保存
    if save_as_json:
        save_individual_processed_basic_res(ticker, features, platform_name)

    return features


if __name__ == '__main__':
    print(calculate_individual_stock_single_result('baba'))
