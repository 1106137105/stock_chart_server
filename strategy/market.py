import yfinance as yf
import json

def TWII_0050(start, end):
    twii = yf.download('^TWII', start , end)
    _0050 = yf.download('0050.TW', start , end)
    _0050['Date'] = _0050.index.values
    start_date = _0050.iloc[0]['Date']
    market_roi = [[0], [0]]

    for i in range(1, len(_0050)):
        date = _0050.iloc[i]['Date']

        market_roi[1].append(round((_0050.loc[date]['Adj Close'] - _0050.loc[start_date]['Adj Close']) / _0050.loc[start_date]['Adj Close'], 2))

        try:
            market_roi[0].append(round((twii.loc[date]['Adj Close'] - twii.loc[start_date]['Adj Close']) / twii.loc[start_date]['Adj Close'], 2))
        except:
            market_roi[0].append(market_roi[-1])

    return json.dumps(market_roi)
