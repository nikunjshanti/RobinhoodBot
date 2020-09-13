import robin_stocks as r

import yaml
import pandas as pd
import json, sys, getopt

from utils import dictlisthelper, stats, slack

import logging
#[%(threadName)-12.12s]
logFormatter = logging.Formatter("%(asctime)s [%(levelname)s]  %(message)s")
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

fileHandler = logging.FileHandler("{0}/{1}.log".format('.', 'robinbot'))
fileHandler.setFormatter(logFormatter)
log.addHandler(fileHandler)

consoleHandler = logging.StreamHandler(sys.stdout)
consoleHandler.setFormatter(logFormatter)
log.addHandler(consoleHandler)


from robinhoodhelper import watchlist, config, portfolio, holdings, prices, orders

#Log in to Robinhood
#Put your username and password in a config.py file in the same directory (see sample file)
login = r.login(config.rh_username, config.rh_password)


def main(stocksyaml, ignoreyaml):
    daytradesymbols = list()
    sybmolstoignore = list()
    for symbol in stocksyaml:
        daytradesymbols.append(symbol)

    for symbol in ignoreyaml:
        sybmolstoignore.append(symbol)

    #watchlist_symbols = watchlist.get_watchlist_symbols(r)
    #print(watchlist_symbols)
    portfolio_symbols = dictlisthelper.remove_listitems(portfolio.get_portfolio_symbols(r), sybmolstoignore)
    holdings_data = dictlisthelper.remove_entries_fromdict_usinglist(holdings.get_modified_holdings(r), sybmolstoignore)

    #print(holdings_data)
    #print(portfolio_symbols)

    holdingslist = list()
    holdingsdict = dictlisthelper.DefaultOrderedDict()
    stockdict = dictlisthelper.DefaultOrderedDict()

    stocktoanalyze = dictlisthelper.mergelist_remove_duplicates(daytradesymbols, portfolio_symbols)

    for stockssymbol in stocktoanalyze:
        currentprice = float(prices.currentprice(r, stockssymbol)[0])
        #print(f"{stockssymbol} : {currentprice}")
        stockdict[stockssymbol]["currentprice"] = currentprice

    dataframestocks = dictlisthelper.DefaultOrderedDict()

    for stockssymbol in stocktoanalyze:

        historyprice = prices.historicalprices(r, stockssymbol)
        stockssymboldf = pd.DataFrame(historyprice)

        dataframestocks[stockssymbol] = stockssymboldf
        highpricecol = stockssymboldf["high_price"]
        lowpricecol = stockssymboldf["low_price"]

        highpricemax = float(highpricecol.max())
        lowpricemin = float(lowpricecol.min())

        tradingrange = highpricemax - lowpricemin

        currentprice = stockdict[stockssymbol]["currentprice"]

        differencefromhigh = (highpricemax - currentprice) / currentprice
        differencefromlow = (lowpricemin - currentprice) / currentprice

        lastperiod = stockssymboldf.iloc[[-1]]

        stockdict[stockssymbol]["weightprice_last30"] =  float(stats.weighted_average(stockssymboldf.iloc[-6:], "close_price", "volume"))

        stockdict[stockssymbol]["lastperiod"]["highprice"] = float(lastperiod["high_price"])
        stockdict[stockssymbol]["lastperiod"]["lowprice"] = float(lastperiod["low_price"])
        stockdict[stockssymbol]["lastperiod"]["tradingrange"] = float(lastperiod["high_price"]) - float(lastperiod["low_price"])

        stockdict[stockssymbol]["highprice"] = highpricemax
        stockdict[stockssymbol]["lowprice"] = lowpricemin
        stockdict[stockssymbol]["tradingrange"] = tradingrange

        stockdict[stockssymbol]["diffromhigh"] = differencefromhigh
        stockdict[stockssymbol]["diffromlow"] = differencefromlow

        #print(f"{stockssymbol}\n{lastperiod}")
        #print(f"{stockssymbol} : Trading Range: -- {tradingrange}  High Price -- {highpricemax}  Low Price -- {lowpricemin}")

    log.info("HOLDINGS DATA")
    for symbol in holdings_data:
        holdingslist.append(symbol)
        holdingsdict[symbol] = holdings_data[symbol]
        log.info(f"{symbol} :  {json.dumps(holdings_data[symbol])}")

    log.info("STOCK INFO LIST")
    for symbol in stockdict:
        log.info(f"{symbol} :  {json.dumps(stockdict[symbol])}")

    itemstobuy = dictlisthelper.find_differences_in_list(stocktoanalyze, holdingslist)
    log.info(f"POTENTIONAL ITEMS TO BUY {itemstobuy}")

    open_orders_symbol_list = list()
    for stock in itemstobuy:
        #if the trading range is less 0.015 IE 1.5% potential to busy
        tradingpercentage = float(stockdict[stock]['lastperiod']['tradingrange'] / stockdict[stock]['currentprice'])
        #log.info(f"{stock} -- trading percentage == {tradingpercentage}")
        if tradingpercentage < 0.015 and tradingpercentage > 0.00001:
            #log.info(f"{stock} :  {json.dumps(stockdict[stock])}")
            if stockdict[stock]['currentprice'] > float(stockyaml[stock]["lowrange"]) \
                    and stockdict[stock]["currentprice"] < float(stockyaml[stock]['highrange']):
                orders.buy_limit(r, stock, stockyaml[stock]['quantity'], limitprice=stockdict[stock]['currentprice'],)
                msg = (f"{stock} -- PLACE ORDER at {stockdict[stock]['currentprice']} "
                       f"with Quantity {stockyaml[stock]['quantity']}")
                log.warning(msg)
                slack.post(text=msg)
                open_orders_symbol_list.append(stock)
                holdingslist.append(stock)

    open_orders = orders.open_orders(r)
    log.info(f"CHECK EXISTING ORDERS")
    for symbol in open_orders:
        openorder_forstock = open_orders[symbol]
        newlistprice = (stockdict[symbol]["currentprice"] + stockdict[symbol]["lastperiod"]["tradingrange"])
        log.debug(openorder_forstock)
        typeoforder = openorder_forstock['side']
        existingsellprice = float(openorder_forstock['price'])

        if typeoforder == 'buy':
            open_orders_symbol_list.append(symbol)
        elif typeoforder == 'sell':
            log.info(f"{symbol} -- {stockdict[symbol]['currentprice']} -- Existing Order -- {existingsellprice}, New Price??? {newlistprice}")
            #cancel existing order and place new order with new limit price
            if newlistprice < existingsellprice:
                if newlistprice < float(holdingsdict[symbol]["average_buy_price"]):
                    msg = (f"{symbol}, recommended to sell at loss : "
                           f" current price {stockdict[symbol]['currentprice']}"
                           f" new price {newlistprice} " 
                           f" existing purchase price {float(holdingsdict[symbol]['average_buy_price'])}"
                           f" loss {float(holdingsdict[symbol]['equity_change'])}"
                           )
                    slack.post(text=msg)
                    log.warning(msg)
                    open_orders_symbol_list.append(symbol)
                else:
                    cancel_order = orders.cancel_order(r, symbol)
                    log.info(cancel_order)
                    orders.sell_limit(r, symbol, quantity=holdingsdict[symbol]['quantity'], limitprice=newlistprice)
                    open_orders_symbol_list.append(symbol)
            else:
                open_orders_symbol_list.append(symbol)

    itemswithoutorder = dictlisthelper.find_differences_in_list(holdingslist, open_orders_symbol_list)

    log.info(f"Symbols no Orders -- {itemswithoutorder}")
    for symbol in itemswithoutorder:
        newlistprice = (stockdict[symbol]["currentprice"] + stockdict[symbol]["lastperiod"]["tradingrange"])
        sell_order = orders.sell_limit(r, symbol, quantity=holdingsdict[symbol]['quantity'], limitprice=newlistprice)
        msg = (f"{symbol}, Sell Order Placed : Execution price {newlistprice} "
               f"Quantity Sold: {holdingsdict[symbol]['quantity']} "
               f"Purchase Price:  {float(holdingsdict[symbol]['average_buy_price'])}")
        slack.post(text=msg)
        log.warning(msg)

    log.info(f"Stocks with Open Orders")
    open_orders = orders.open_orders(r)
    for symbol in open_orders:
        openorder_forstock = open_orders[symbol]
        log.info(f"{symbol} : {openorder_forstock['side']} :q: {openorder_forstock['quantity']}"
                 f", price: {openorder_forstock['price']}")



def loadyaml(filename):
    with open(filename, 'rb') as file:
        # The FullLoader parameter handles the conversion from YAML
        # scalar values to Python the dictionary format
        stocksyaml = yaml.load(file, Loader=yaml.FullLoader)

    return stocksyaml

if __name__ == '__main__':
    options, args = getopt.getopt(
        sys.argv[1:],
        'd:i:chobsn',
        ['daytrade=', 'ignorestock=', 'cancel', 'help', 'placeorders', 'buy', 'sell', 'slacknotify'])

    daytradeyamlfilename = None
    ignorestockyamlfilename = None
    cancelallorders = False
    for option_key, option_value in options:
        if option_key in ('-d', '-daytrade'):
            daytradeyamlfilename = option_value
        elif option_key in ('-i', '-ignorestock'):
            ignorestockyamlfilename = option_value
        elif option_key in ('-c', '-cancel'):
            cancelallorders = True
        elif option_key in ('-b', '-buy'):
            orders.placebuy = True
        elif option_key in ('-s', '-sell'):
            orders.placesell = True
            orders.placecancel = True
        elif option_key in ('-o', '-placeorders'):
            orders.placebuy = True
            orders.placesell = True
        elif option_key in ('-n', 'slacknotify'):
            slack.posttoslack = True
        elif option_key in ('-h', '-help'):
            print("python3 botforrobinhood.py -d daytradestaocks.yaml -i ignorestock.yaml")
            sys.exit()

    stockyaml = loadyaml(daytradeyamlfilename)
    ignoreyaml = loadyaml(ignorestockyamlfilename)

    if cancelallorders:
        log.warning("Cancelling all orders")
        r.cancel_all_stock_orders()
        sys.exit()
    else:
        main(stockyaml, ignoreyaml)




