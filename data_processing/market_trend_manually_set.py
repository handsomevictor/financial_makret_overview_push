# 逻辑：设定好分数之后，通过穷举法找到所有可能，然后通过quantile，确定牛市熊市分界线，没有用到任何量化的方法

from collections import Counter
import random
import numpy as np


def random_ch():
    return random.choice([-1, 1])


def get_trend_bull_bear_threshold(score_list=None):
    """
    :param score_list: should be something like [30, 35, 40, 45, 40, 30, 25, 10], corresponding to MA5,
                       MA10, MA20, MA30, MA40, MA50, MA60 MA90 weights
    :return:
    """
    if score_list is None:
        score_list = [30, 50, 70, 45, 40, 30, 25, 10]

    temp_30 = []
    temp_60 = []

    for i in range(3000):
        temp_30.append(sum([random_ch() * score for score in score_list[:-4]]))
        temp_60.append(sum([random_ch() * score for score in score_list]))

    possible_score_30 = list(Counter(temp_30).keys())
    possible_score_60 = list(Counter(temp_60).keys())

    # 根据MA各个线的位置确定分数
    quantiles = [0.85, 0.65, 0.35, 0.15]
    very_bull_30, bull_30, bear_30, very_bear_30 = [np.quantile(possible_score_30, i) for i in quantiles]
    very_bull_60, bull_60, bear_60, very_bear_60 = [np.quantile(possible_score_60, i) for i in quantiles]

    return {'trend_30': {'very_bull': very_bull_30, 'bull': bull_30, 'bear': bear_30, 'very_bear': very_bear_30},
            'trend_60': {'very_bull': very_bull_60, 'bull': bull_60, 'bear': bear_60, 'very_bear': very_bear_60}}


if __name__ == '__main__':
    print(get_trend_bull_bear_threshold(score_list=None))
