import numpy as np
#Safe divide by zero division function
def safe_division(n, d):
    return n / d if d else 0

def weighted_average(df, pricecolumn, volume):
    weights = 0
    prices = 0

    for index, row in df.iterrows():
        weights = weights + float(row[volume])
        weightprice = float(row[volume]) * float(row[pricecolumn])
        prices = prices + weightprice

    return safe_division(prices , weights)


