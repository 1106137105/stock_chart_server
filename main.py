from fastapi import FastAPI
from talib.abstract import *
from fastapi.middleware.cors import CORSMiddleware

from strategy.basic import Basic
from strategy.lowerThanYear import LowerThanYear
from strategy.fomo import Fomo
from strategy.bbands import BB
from strategy.Xuan import Xuan
from strategy.market import TWII_0050

import uvicorn

app = FastAPI()

origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/{stock_no}/{start}/{end}")
def backtest(stock_no: str, start:str, end:str):
    # 全部策略
    strategies = [Basic, LowerThanYear, Fomo, BB, Xuan]
    results = []
    charts = []
    details = []

    # 選擇策略
    for i in range(0, len(strategies)):
        strategy = strategies[i](stock_no, start=start, end=end)
        strategy.backtest()
        results.append(strategy.GetKPI())
        charts.append(strategy.profit_json())
        details.append(strategy.detail)

    # 計算大盤和0050
    market = TWII_0050(start, end)

    # 回測開始 回傳資料
    date = strategy.date_json()
    return {"results": results, "charts": charts, "market": market, "date": date, "details": details}

if __name__ == '__main__':
    uvicorn.run(app='main:app', host="127.0.0.1", port=8000, reload=True, debug=True)