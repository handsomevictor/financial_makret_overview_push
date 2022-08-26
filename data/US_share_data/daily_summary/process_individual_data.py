# 输出这么几个参数：
# 1. 当天close price
# 2. 涨跌幅
# 3. 行业
# 4. ？财报时间？
# 5. 计算60天和30天的return，判断今天的是否在95%置信区间内！输出两个True or False
# 6. 判断是上涨，超级上涨，下跌，超级下跌，还是走平的趋势！方法：看均线：5，10，20，30，60得分为20，20，25，35，40分，5大于10则加20分，20小于30则减20分，若一共大于80为超级上涨，30-80为上涨，
#    -20到+20为平，以此类推

import yfinance as yf


def calculate_single_result(ticker):
    try:
        data = yf.Ticker(ticker).history(period='60d', interval='1d')
        data['change'] = data['Close'].pct_change()
        data['change'] = data['change'].fillna(0)
        return ticker, data.change.to_list()[-1]
    except IndexError:
        return ticker, -1


if __name__ == '__main__':
    print(calculate_single_result('tsla'))
