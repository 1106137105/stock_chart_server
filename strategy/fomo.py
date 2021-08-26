import pandas as pd

from .base import Strategy


class Fomo(Strategy):

    # 回測
    def backtest(self):
        # 修改策略從這邊開始
        self.name = '增量上攻'
        self.detail = '價格及成交量創10日以來新高則進場,10%移動式停損'
        tmp_df = pd.DataFrame()
        tmp_df['close','volume'] = 0
        rolling_max = pd.DataFrame()
        rolling_min = pd.DataFrame()
        history_max = 0

        for i in range(0, len(self.stock)-1):
            NextTime = self.stock.iloc[i+1]['Date']
            NextOpen = self.stock.iloc[i+1]['open']
            ThisClose = self.stock.iloc[i]['close']
            ThisVolume = self.stock.iloc[i]['volume']
            
            tmp_df.loc[self.stock.iloc[i]['Date'], 'close'] = self.stock.iloc[i]['close']
            tmp_df.loc[self.stock.iloc[i]['Date'], 'volume'] = self.stock.iloc[i]['volume']
            rolling_max = tmp_df[['close', 'volume']].rolling(10).max()
            rolling_min = tmp_df[['close', 'volume']].rolling(3).min()
            rolling_max.columns=['close(max)','volume(max)']
            rolling_min.columns=['close(min)','volume(min)']

            enterCondition = ThisClose == rolling_max.iloc[i]['close(max)'] and ThisVolume == rolling_max.iloc[i]['volume(max)']
            outCondition = ThisClose == rolling_min.iloc[i]['close(min)'] and ThisVolume == rolling_min.iloc[i]['volume(min)']

            # 判斷是否是交易日最後一天,是則強制全部平倉,不是則繼續如常判斷交易
            if not self.closePosition(i):
              # 判斷資產是否能負擔入場成本
              if self.enough(NextOpen):
                # 如果今日收盤價成交量創10日以來新高則多單進場
                if enterCondition:
                  history_max = NextOpen
                  self.enter(NextTime, NextOpen, num=self.allInOut(NextOpen))

              # 如持有多單,以每日收盤價為基準,10%移動式停損
              if self.long_count > 0:
                history_max = max(history_max, ThisClose)
                if (history_max * 0.9 >= ThisClose) or outCondition:
                  self.out(NextTime, NextOpen, num=self.long_count)

            self.countProfit(self.stock.iloc[i+1]['Date'])
            