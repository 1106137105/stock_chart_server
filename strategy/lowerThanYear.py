from .base import Strategy

class LowerThanYear(Strategy):

    def backtest(self):
        self.name="低於年線買入"
        self.detail = "此策略只要當日低於年線就買進一張, 最後一天平倉"

        self.getMA(240)

        for i in range(240, len(self.stock)-1):
            NextTime = self.stock.iloc[i+1]['Date']
            NextOpen = self.stock.iloc[i+1]['open']
            ThisMA = self.stock.iloc[i]['240MA']
            ThisClose = self.stock.iloc[i]['close']

            if not self.closePosition(i):

                if  self.enough(NextOpen):
                    Condition1 = ThisMA > ThisClose
                    if Condition1:
                        self.enter(NextTime, NextOpen, num=1)
            
            self.countProfit(self.stock.iloc[i+1]['Date'])
