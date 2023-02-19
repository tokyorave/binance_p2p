import pandas as pd
import requests
from pprint import pprint


bankAmount = 235696  # Specify bank amount

#Получаем цену актива в USDT

def get_pricesUSDT(urlsUSDT):
    pricesUSDT = []
    for url in urlsUSDT:
        response = requests.get(url)
        data = response.json()
        pricesUSDT.append("{:.2f}".format(float(data['price'])))
    return pricesUSDT

urlsUSDT = [
    'https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT',
    'https://api.binance.com/api/v3/ticker/price?symbol=ETHUSDT',
    'https://api.binance.com/api/v3/ticker/price?symbol=BNBUSDT'
]

pricesUSDT = get_pricesUSDT(urlsUSDT)
pricesUSDT = [float(price) for price in pricesUSDT]

def get_pricesBTC(urlsBTC):
    pricesBTC = []
    for url in urlsBTC:
        response = requests.get(url)
        data = response.json()
        pricesBTC.append("{:.6f}".format(float(data['price'])))
    return pricesBTC

urlsBTC = [
    'https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT',
    'https://api.binance.com/api/v3/ticker/price?symbol=ETHBTC',
    'https://api.binance.com/api/v3/ticker/price?symbol=BNBBTC'
]

pricesBTC = get_pricesBTC(urlsBTC)
pricesBTC = [float(price) for price in pricesBTC]

assets = ["USDT", "BTC", "ETH", "BNB"]

def get_c2c_orders(asset, bankAmount):
    """Sends a POST request with input data and returns a list of orders"""
    url = 'https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search'
    order_url = 'https://p2p.binance.com/en/advertiserDetail?advertiserNo='
    headers = {'content-type': 'application/json'}
    rows = 1  # Number of rows per page
    page = 1  # Starting page
    orders = []  # List of orders

    while page <= 1:  # Loop through pages until there is no more data
        json_data = {
            "page": page,
            "rows": rows,
            "asset": asset,
            "fiat": "RUB",
            "payTypes": ["TinkoffNew", "RaiffeisenBank", "RosBankNew"],
            "tradeType": "BUY",
            "transAmount": bankAmount
        }
        response = requests.post(url, headers=headers, json=json_data)
        response.raise_for_status()
        data = response.json()

        if not data['data']:
            break

        for order in data['data']:
            orders.append([
                order['advertiser']['nickName'],
                order['advertiser']['monthOrderCount'],
                order['advertiser']['monthFinishRate'],
                order['adv']['price'],
                order['adv']['fiatUnit'],
                order['adv']['tradableQuantity'],
                order['adv']['asset'],
                order['adv']['minSingleTransAmount'],
                order['adv']['dynamicMaxSingleTransAmount'],
                order['adv']['tradeMethods'][0]['tradeMethodName'],
                order['advertiser']['userNo'],
                order_url + str(order['advertiser']['userNo'])
            ])

        page += 1

    return orders

def main():

    fiatEnterPoints = []
    fiatExitPoints = []
    coinVolume = []

    for asset in assets:
        orders = get_c2c_orders(asset, bankAmount)
        buy_list = pd.DataFrame(orders, columns=[
            'Имя', 'Кол-во ордеров', 'Выполненых', 'Цена', 'Фиат', 'Доступно', 'Актив',
            'Минимум', 'Максимум', 'Тип оплаты', 'Номер объявления', 'Ссылка'
        ])
        
        fiatEnterPoints += buy_list['Цена'].astype(float).tolist()

        orders = get_c2c_orders(asset, 0)
        sell_list = pd.DataFrame(orders, columns=[
            'Имя', 'Кол-во ордеров', 'Выполненых', 'Цена', 'Фиат', 'Доступно', 'Актив',
            'Минимум', 'Максимум', 'Тип оплаты', 'Номер объявления', 'Ссылка'
        ])

        fiatExitPoints += sell_list['Цена'].astype(float).tolist()

    # Loop through fiatEnterPoints and calculate coinValue for each point
    for i in range(len(fiatEnterPoints)):
        coinVolume.append(bankAmount / fiatEnterPoints[i])
    print(ascii(coinVolume))



    # Print the fiatExitPoints after the loop
    fiatExitValue = []
    for i in range(len(coinVolume)):
        for j in range(len(fiatExitPoints)):
            fiatExitValue.append(coinVolume[i] * fiatExitPoints[j])
    print(ascii(fiatExitPoints))

    potentialProfitUSDT = []
    bankProfitUSDT = []

    #Calculate potential profit for USDT enter point
    for i in range(len(pricesUSDT)):
        bankProfitUSDT.append(coinVolume[0] / pricesUSDT[i] * fiatExitPoints [i+1])
        potentialProfitUSDT.append(bankProfitUSDT[i] - bankAmount)
        if potentialProfitUSDT[i] > 0:
            print('='.center(80, '='))
            print("Объем монеты " + str(coinVolume[0]) + " Цена в USDT " + str(pricesUSDT[i]) + " Цена на P2P " + str(fiatExitPoints[i+1]))
            print("Покупаем USDT на P2P по " + str(fiatEnterPoints[0]) + " руб. " + " USDT => " + assets[i+1] + " Profit = " + str(potentialProfitUSDT[i]) + " Bank = " + str(bankProfitUSDT[i]))
        

    potentialProfitBTC = []
    bankProfitBTC = []

    #fiatExitPoints
    #0 - USDT
    #1 - BTC
    #2 - ETH
    #3 - BNB



    #Calculate potential profit for BTC enter point
    j=0
    for i in range(len(pricesBTC) + 1):
        if i != 1:
            if pricesBTC[j] < 1:
                bankProfitBTC.append(coinVolume[1] / pricesBTC[j] * fiatExitPoints [i])
                potentialProfitBTC.append(bankProfitBTC[j] - bankAmount)
            else:
                bankProfitBTC.append(coinVolume[1] * pricesBTC[j] * fiatExitPoints [i])
                potentialProfitBTC.append(bankProfitBTC[j] - bankAmount)
            if potentialProfitBTC[j] > 0:
                print('='.center(80, '='))
                print("Покупаем BTC на P2P по " + str(fiatEnterPoints[1]) + " руб. " + "BTC => " + assets[i] + " Profit = " + str(potentialProfitBTC[j]) + " Bank = " + str(bankProfitBTC[j]))
            j = j+1

    #Calculate potential profit for ETH enter point
    j=0
    for i in range(len(pricesBTC) + 1):
        if i != 2:
            if pricesBTC[j] < 1:
                bankProfitBTC.append(coinVolume[1] / pricesBTC[j] * fiatExitPoints [i])
                potentialProfitBTC.append(bankProfitBTC[j] - bankAmount)
            else:
                bankProfitBTC.append(coinVolume[1] * pricesBTC[j] * fiatExitPoints [i])
                potentialProfitBTC.append(bankProfitBTC[j] - bankAmount)
            if potentialProfitBTC[j] > 0:
                print('='.center(80, '='))
                print("Покупаем ETH на P2P по " + str(fiatEnterPoints[2]) + " руб. " + "ETH => " + assets[i] + " Profit = " + str(potentialProfitBTC[j]) + " Bank = " + str(bankProfitBTC[j]))
            j = j+1

    #Calculate potential profit for BNB enter point
    j=0
    for i in range(len(pricesBTC) + 1):
        if i != 3:
            if pricesBTC[j] < 1:
                bankProfitBTC.append(coinVolume[1] / pricesBTC[j] * fiatExitPoints [i])
                potentialProfitBTC.append(bankProfitBTC[j] - bankAmount)
            else:
                bankProfitBTC.append(coinVolume[1] * pricesBTC[j] * fiatExitPoints [i])
                potentialProfitBTC.append(bankProfitBTC[j] - bankAmount)

            if potentialProfitBTC[j] > 0:
                print('='.center(80, '='))
                print("Покупаем BNB на P2P по " + str(fiatEnterPoints[3]) + " руб. " + "BNB => " + assets[i] + " Profit = " + str(potentialProfitBTC[j]) + " Bank = " + str(bankProfitBTC[j]))
            j = j+1

if __name__ == '__main__':
    main()
