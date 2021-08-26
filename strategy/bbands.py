# -*- coding: utf-8 -*-
"""
Created on Wed Aug 25 14:58:13 2021

@author: Hermit
"""
from .base import Strategy


class BB(Strategy):

    # 回測
    def backtest(self):
        self.name = '布林通道'
        self.detail = '藉由收盤價和布林通道上下線的關係判斷進出場'
        # 修改策略從這邊開始
        
        for i in range(0, len(self.stock)-1):
            
            NextTime = self.stock.iloc[i+1]['Date']
            NextOpen = self.stock.iloc[i+1]['open']
            LastClose, ThisClose = self.stock.iloc[i-1]['close'], self.stock.iloc[i]['close']
            LastBB, ThisBB = self.BBANDS.iloc[i-1], self.BBANDS.iloc[i]
            Condition1=(LastClose >= LastBB['upperband'] and ThisClose <= ThisBB['upperband'])
            Condition2=(LastClose <= LastBB['lowerband'] and ThisClose >= ThisBB['lowerband'])
            Condition3=(LastClose >= LastBB['middleband'] and ThisClose <= ThisBB['middleband'])
            Condition4=(LastClose <= LastBB['middleband'] and ThisClose >= ThisBB['middleband'])
            
            # 判斷是否是交易日最後一天,是則強制全部平倉,不是則繼續如常判斷交易
            if not self.closePosition(i):

                # 判斷資產是否能負擔入場成本
                if self.enough(NextOpen):

                    #多單進場(昨日收盤 >= 昨日BB上緣 且 今日收盤 <= 今日BB上緣)
                    if Condition1 and self.long_count == 0:
                        self.enter(NextTime, NextOpen, num=self.allInOut(NextOpen),BS='B')
                        
                    #空單進場(昨日收盤 >= 昨日BB下緣 且 今日收盤 <= 今日BB下緣)
                    elif Condition2 and (self.short_count == 0):
                        self.enter(NextTime, NextOpen, num=self.allInOut(NextOpen),BS='S')

                #多單出場(昨日收盤 >= 昨日BB中線 且 今日收盤 <= 今日BB中線)
                if self.long_count > 0:
                    if Condition3:
                        self.out(NextTime, NextOpen, num=self.long_count,BS='B')
                        
                #空單出場(昨日收盤 <= 昨日BB中線 且 今日收盤 >= 今日BB中線) 
                elif self.short_count > 0:
                    if Condition4:     
                        self.out(NextTime, NextOpen, num=self.short_count,BS='S')   
            
            self.countProfit(self.stock.iloc[i+1]['Date'])
