from .base import Strategy

class Basic(Strategy):

    def backtest(self):
        self.name = "突破五日線"
        self.detail = "此策略只要穿越5日線就將全部資金ALL IN, 並設立移動式停利停損5%出場 ALL OUT, 最後一天平倉"

        self.getMA(5)
        history_max = 0

        for i in range(5, len(self.stock)-1):
            NextTime = self.stock.iloc[i+1]['Date']
            NextOpen = self.stock.iloc[i+1]['open']
            ThisMA = self.stock.iloc[i]['5MA']
            ThisClose = self.stock.iloc[i]['close']
            LastMA = self.stock.iloc[i-1]['5MA']
            LastClose = self.stock.iloc[i-1]['close']
            bought = False

            if not self.closePosition(i):
                # 最後一天平倉

                if self.enough(NextOpen):
                    # 超越5日線後 All in
                    Condition1 = LastClose <= LastMA
                    Condition2 = ThisClose > ThisMA
                    if Condition1 and Condition2:
                        history_max = NextOpen
                        self.enter(NextTime, NextOpen, num=self.allInOut(NextOpen))
                        bought = True

                if self.long_count > 0 and not bought:
                    history_max = max(history_max, ThisClose)
                    Condition1 = (history_max * 0.95) >= ThisClose # 5%移動式停損
                    if Condition1:
                        history_max = 0
                        self.out(NextTime, NextOpen, num=self.long_count)
            
            self.countProfit(self.stock.iloc[i+1]['Date'])