import pandas as pd

from .base import Strategy


class Xuan(Strategy):

    # 回測
    def backtest(self):
        self.name = 'Xuan'
        self.detail = '近10日最高價<近10日最低價*1.05及macd快線穿越慢線則多單進場,10%移動式停損'

        tmp_df = pd.DataFrame()
        tmp_df['high','low', 'close','volume'] = 0
        rolling_max = pd.DataFrame()
        rolling_min = pd.DataFrame()
        history_max = 0
        for i in range(0, len(self.stock)-1):
            NextTime = self.stock.iloc[i+1]['Date']
            NextOpen = self.stock.iloc[i+1]['open']
            ThisClose = self.stock.iloc[i]['close']
            ThisVolume = self.stock.iloc[i]['volume']
            LastMACD = self.MACD.iloc[i-1]['macd']
            LastMACD_MS = self.MACD.iloc[i-1]['macdsignal']
            ThisMACD = self.MACD.iloc[i]['macd']
            ThisMACD_MS = self.MACD.iloc[i]['macdsignal']
            
            # 把逐日資料塞進tmp_df
            tmp_df.loc[self.stock.iloc[i]['Date'], 'high'] = self.stock.iloc[i]['high']
            tmp_df.loc[self.stock.iloc[i]['Date'], 'low'] = self.stock.iloc[i]['low']
            tmp_df.loc[self.stock.iloc[i]['Date'], 'close'] = self.stock.iloc[i]['close']
            tmp_df.loc[self.stock.iloc[i]['Date'], 'volume'] = self.stock.iloc[i]['volume']

            # 移動取10日最高最低資料
            rolling_max = tmp_df[['high', 'low', 'close', 'volume']].rolling(10).max()
            rolling_min = tmp_df[['high', 'low', 'close', 'volume']].rolling(10).min()
            ten_avg_vol = tmp_df['volume'].rolling(10).mean()
            rolling_max.columns=['high(max)', 'low(max)', 'close(max)','volume(max)']
            rolling_min.columns=['high(min)', 'low(min)', 'close(min)','volume(min)']
            
            # 當日收盤價和成交量創10日新高
            Condition1 = ThisClose == rolling_max.iloc[i]['close(max)'] and ThisVolume == rolling_max.iloc[i]['volume(max)']
            # 10日以來最高價<10日以來最低價*1.05
            Condition2 = rolling_max.iloc[i]['high(max)'] < rolling_min.iloc[i]['low(min)'] * 1.05
            # 快線向上突破慢線
            Condition3 = LastMACD < LastMACD_MS and ThisMACD > ThisMACD_MS 
            # 快線向下跌破慢線
            Condition4 = LastMACD > LastMACD_MS and ThisMACD < ThisMACD_MS 

            # 判斷是否是交易日最後一天,是則強制全部平倉,不是則繼續如常判斷交易
            if not self.closePosition(i):
              # 判斷資產是否能負擔入場成本
                if self.enough(NextOpen):
                    # 當10日以來最高價<10日以來最低價*1.05,macd快線向上突破慢線 多單進場
                    if Condition2 and Condition3 and self.long_count == 0:
                        history_max = NextOpen
                        self.enter(NextTime, NextOpen, num=self.allInOut(NextOpen))
                # 快線向下跌破慢線 則allout
                if self.long_count > 0:
                    history_max = max(history_max, ThisClose)
                    if Condition4 or history_max * 0.9 >= ThisClose:
                        self.out(NextTime, NextOpen, num=self.long_count)

            self.countProfit(self.stock.iloc[i+1]['Date'])
 