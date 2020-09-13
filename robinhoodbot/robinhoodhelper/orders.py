from utils import dictlisthelper
from utils import print as printcmdoptions
import json

placebuy = False
placesell = False
placecancel = False

def buy_limit(r, symbol, quantity, limitprice, timeInForce="gfd", extendedHours="True"):
    if placebuy:
        return r.order_buy_limit(symbol, quantity, limitprice, timeInForce, extendedHours)
    else:
        pass

def sell_limit(r, symbol, quantity, limitprice, timeInForce="gfd", extendedHours="True"):
    if placesell:
        return r.order_sell_limit(symbol, quantity, limitprice, timeInForce, extendedHours)
    else:
        pass


def open_orders(r):
    openorderlistbysymbol = dictlisthelper.DefaultOrderedDict()

    printcmdoptions.blockPrint()
    open_orders_list = r.get_all_open_stock_orders()
    printcmdoptions.enablePrint()

    for order in open_orders_list:
        instrumenturl = order['instrument']
        instrumentdata = r.stocks.get_instrument_by_url(instrumenturl)

        openorderlistbysymbol[instrumentdata['symbol']] = order

    return openorderlistbysymbol

def cancel_order(r, symbol):
    openorderlistbysymbol = open_orders(r)

    try:
        openorder = openorderlistbysymbol[symbol]
        if len(openorder["id"]) > 1 and placecancel:
            cancelorder = r.orders.cancel_stock_order(openorder["id"])
            return cancelorder
    except KeyError:
        print("Order not found for symbol" + symbol)

