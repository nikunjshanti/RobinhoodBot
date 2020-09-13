

def get_watchlist_symbols(r):
    """
    Returns: the symbol for each stock in your watchlist as a list of strings
    """
    my_list_names = []
    symbols = []
    watchlist = r.get_all_watchlists(info="results")
    if watchlist is not None:
        #print(json.dumps(watchlist))
        for list in watchlist:
            my_list_names.append(list['display_name'])
    for name in my_list_names:
        list = r.get_watchlist_by_name(name)
        for item in list['results']:
            #print(item)
            instrument_data = item
            symbol = instrument_data['symbol']
            symbols.append(symbol)
    return symbols