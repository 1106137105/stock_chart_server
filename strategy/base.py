from talib.abstract import *
import yfinance as yf
import numpy as np

class Strategy:

    def __init__(self, stock_no, detail="暫無描述", name="default", start="2017-01-01", end="2021-01-01", capital=5000000, rsi=10):
        self.name = name
        self.stock_no = stock_no
        self.start = start
        self.end = end
        self.capital = capital # 資金
        self.start_capital = capital # 起始資金
        self.detail = detail # 策略描述

        self.long_count = 0   # 持有多單數量
        self.short_count = 0  # 持有空單數量
        
        self.ProfitList = []  # 損益表
        self.buyCount = 0 # 買進次數

        self.stock = yf.download(stock_no, self.start, self.end).round(2)
        self.stock.columns = ['open', 'high', 'low', 'close', 'adj.close', 'volume']

        self.stock['Date'] = self.stock.index.values
        self.stock['RSI'] = RSI( self.stock , rsi )
        self.stock['Profit'] = np.zeros(len(self.stock)) # 累計損益

        self.MACD = MACD(self.stock)
        self.BBANDS = BBANDS(self.stock, timeperiod=20)
        self.KD = STOCH(self.stock, fastk_period = 9,slowk_period=3,slowd_period=3)

        # 進場
        self.OrderTime = None
        self.OrderPrice = None

        # 出場
        self.CoverTime = None
        self.CoverPrice = None
    
    def getMA(self, ma):
        name = f'{ma}MA'
        self.stock[name] = SMA(self.stock, ma)
    
    def enough(self, price):
        return self.capital > (price * 1000)
    
    def closePosition(self, i):
        NextTime = self.stock.iloc[i+1]['Date']
        NextOpen = self.stock.iloc[i+1]['open']

        if i == (len(self.stock)-2) and (self.long_count > 0 or self.short_count > 0):
            self.out(NextTime, NextOpen, num=self.long_count)
            return True
        return False

    # 進場
    def enter(self, NextTime, NextOpen, num=1, BS='B'):
        self.OrderTime = NextTime
        self.OrderPrice = NextOpen
        self.buyCount += 1

        # 進場成本
        self.capital -= (num * NextOpen * 1000)

        # 進場數量
        if BS == 'B':
            self.long_count += num
        elif BS == 'S':
            self.short_count += num

        # print('enter', self.OrderPrice, self.long_count, self.capital)

    # 出場
    def out(self, NextTime, NextOpen, num=1, BS='B'):
        self.CoverTime = NextTime
        self.CoverPrice = NextOpen

        if BS == "B":
            Profit = (self.CoverPrice - self.OrderPrice) * num
            self.long_count -= num
        elif BS == "S":
            Profit = (self.OrderPrice - self.CoverPrice) * num
            self.short_count -= num

        self.capital += self.CoverPrice * num * 1000
        self.ProfitList.append( Profit * 1000 )
        # print('out', self.CoverPrice, self.long_count, self.capital)
    
    def countProfit(self, date):
        self.stock.loc[date, 'Profit'] = round(sum(np.array(self.ProfitList)) / self.start_capital, 2)
    
    def allInOut(self, price):
        return self.capital // (price * 1000)

    def profit_json(self):
        return self.stock['Profit'].tolist()
    
    def date_json(self):
        return self.stock['Date'].to_json(orient="records")
    
    # 計算績效 (回傳值)
    def GetKPI(self):
        # 將 List 轉為 numpy array 格式
        ProfitList = np.array(self.ProfitList)
        result = {}
        result['策略名稱'] = self.name

        # 進場次數
        result['進場次數'] = self.buyCount

        # 交易次數
        TotalNum = len(ProfitList)
        result['出場次數'] = TotalNum

        # 總損益
        TotalProfit = sum(ProfitList)
        result['總損益'] = round(TotalProfit, 2)

        # 報酬率
        ROI = round((TotalProfit/self.start_capital)* 100, 2) 
        result['報酬率'] = f'{ROI}%'

        # 平均損益
        if TotalNum == 0:
            AvgProfit = None
        else:
            AvgProfit = round( TotalProfit / TotalNum , 2 )
        result['平均損益'] = AvgProfit

        # 總勝率
        Win = [ i for i in ProfitList if i > 0 ]   # 獲利的部分
        Loss = [ i for i in ProfitList if i < 0 ]  # 虧損的部分
        if TotalNum == 0:
            WinRate = None
        else:
            WinRate = round( len(Win) / TotalNum * 100 , 2 )
        result['總勝率'] = f'{WinRate} %'

        # 平均獲利
        if len(Win) == 0:
            AvgWin = None
        else:
            AvgWin = round( np.mean(Win) , 2 )
        result['平均獲利'] = AvgWin

        # 平均虧損
        if len(Loss) == 0:
            AvgLoss = None
        else:
            AvgLoss = round( np.mean(Loss) , 2 )
        result['平均虧損'] = AvgLoss

        # 獲利因子
        if sum(Loss) == 0:
            ProfitFactor = None
        else:
            ProfitFactor = round( sum(Win) / abs(sum(Loss)) , 2 )
        result['獲利因子'] = ProfitFactor

        # 賺賠比率
        if AvgLoss == 0 or AvgWin == None or AvgLoss == None:
            WinLossRate = None
        else:
            WinLossRate = round( AvgWin / abs(AvgLoss) , 2 )
        result['賺賠比率'] = WinLossRate

        # 最大連續虧損
        MaxLoss = 0
        ConLoss = 0
        for i in ProfitList:
            if i < 0:
                ConLoss += i
            else:
                ConLoss = 0
            MaxLoss = min(MaxLoss,ConLoss)
        result['最大連續虧損'] = round(abs(MaxLoss), 2)

        # 最大資金回落
        MaxCapital = 0
        Capital = 0
        MDD = 0
        DD = 0
        for i in ProfitList:
            Capital += i
            MaxCapital = max(MaxCapital,Capital)
            DD = MaxCapital - Capital
            MDD = max(MDD,DD)
        # print('最大資金回落:',abs(MDD))
        result['最大資金回落'] = round(abs(MDD), 2)

        return result
 