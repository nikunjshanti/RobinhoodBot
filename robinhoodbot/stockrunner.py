import robin_stocks as r
import logging
import yfinance as yf

logging.basicConfig(filename="stockrrunner.log", level=logging.DEBUG)


def get_portfolio_symbols():
    """
    Returns: the symbol for each stock in your portfolio as a list of strings
    """
    symbols = []
    holdings_data = r.get_open_stock_positions()
    for item in holdings_data:
        if not item:
            continue
        instrument_data = r.get_instrument_by_url(item.get('instrument'))
        symbol = instrument_data['symbol']
        symbols.append(symbol)
    return symbols

#Log in to Robinhood
#Put your username and password in a config.py file in the same directory (see sample file)

daytradesymbols = ['TECL']


#login = r.login(config.rh_username,config.rh_password)
#portfolio_symbols = get_portfolio_symbols()
#print("Current Portfolio: " + str(portfolio_symbols) + "\n")


# get stock info
#print(msft.info)

# get historical market data

from slack_webhook import Slack

slack = Slack(url='https://hooks.slack.com/services/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')



def main():
    daytradesymbols = ['AAPL']
    #hist = msft.history(period="1d", interval="1m", prepost=True)
    for stock in daytradesymbols:
        hist = yf.download(stock, period="1d", interval="1m", prepost=False)
        highprice = hist["High"]
        lowprice = hist["Low"]
        lastprice = hist.iloc[[-1]]
        currentprice = lastprice.iloc[0]['Close']

        highpricemax = highprice.max()
        lowpricemin = lowprice.min()

        slackmsg = ""
        tradingrange = highprice.max() - lowprice.min()
        msg = (f"Trading Range: {str(tradingrange)} ---- Current Price: {str(currentprice)}")
        slackmsg = slackmsg + msg + "\n"
        #slack.post(text=msg)
        logging.info(msg)
        msg = (f"High Price: {str(highpricemax)} ---- Low Price: {str(lowpricemin)} -----")
        slackmsg = slackmsg + msg + "\n"
        #slack.post(text=msg)
        logging.info(msg)

        differencefromhigh = (highprice.max() - currentprice) / currentprice
        differencefromlow = (lowprice.min() - currentprice) / currentprice

        msg = (f"Difference form high {str(differencefromhigh)} ---- Difference from Low {str(differencefromlow)}")
        slackmsg = slackmsg + msg + "\n"
        #slack.post(text=msg)
        logging.info(msg)

        #slack.post(text=slackmsg)

        differntfromlow = currentprice - lowprice.min()
        msg = f"Diff from Low {differntfromlow}"
        slackmsg = slackmsg + msg + "\n"
        logging.info(msg)



        if differencefromhigh > 0.010:
            if currentprice > lowprice:
                logging.info("buy")
            #and
        '''        
            attachments=[{
            "fallback": "Plan a vacation",
            "author_name": "Owner: rdesoto",
            "title": "Plan a vacation",
            "text": "I've been working too hard, it's time for a break.",
            "actions": [
                {
                    "name": "action",
                    "type": "button",
                    "text": "Complete this task",
                    "style": "",
                    "value": "complete"
                },
                {
                    "name": "tags_list",
                    "type": "select",
                    "text": "Add a tag...",
                    "data_source": "static",
                    "options": [
                        {
                            "text": "Launch Blocking",
                            "value": "launch-blocking"
                        },
                        {
                            "text": "Enhancement",
                            "value": "enhancement"
                        },
                        {
                            "text": "Bug",
                            "value": "bug"
                        }
                    ]
                }
            ]
        }])
        '''

        #buyprice = 1972
        #buypricepotential = (lowprice.min() - buyprice) / buyprice
        #print(buypricepotential)

if __name__ == '__main__':
    main()