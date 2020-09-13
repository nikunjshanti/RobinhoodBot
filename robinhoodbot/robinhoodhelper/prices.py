def currentprice(r, symbol):
    return r.get_latest_price([symbol])


def historicalprices(r, symbol, bounds="extended", interval="5minute", span="day"):
    return r.get_stock_historicals([symbol], interval=interval, span=span, bounds=bounds)

def calculatetradingrange(df):
    return float(df["high_price"]) - float(df["low_price"])


