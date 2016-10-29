# -*- encoding: utf8 -*-

'''
This system takes trading signals, and pass on to the trading application, and auto completes the trade
order confirmation needs to be disabled!!!
'''

import time
from PyEmailParser_ttc import emailOrderParser
from PyWinApi import tradingAPI

class TTC_autoTrader:
    def __init__(self):
        self.winapi = tradingAPI()
        
    def getOrderDetails(self):
        ep = emailOrderParser()
        return ep.getOrder()
    
    def orderProcess(self):
        orders = self.getOrderDetails()
        #orders = [('002755', 0, 10)]
        for stock, pct, price in orders:
            free_cash, _, total_value, _ = self.winapi.getAccDetails()
            if pct == 0: # sell off the stock
                self.winapi.clearStock(stock)
            else:
                self.winapi.adjustStock(stock, pct, price, free_cash, total_value)
            time.sleep(3) # pause 5 seconds after each order
            
if __name__ == '__main__':
    print("Auto Trading system started/自动交易系统运行中， 请开启同花顺网上交易系统5.0")
    ttc = TTC_autoTrader()
    while True:
        try:
            ttc.orderProcess()
        except:
            raise "order failed! please check!"
        time.sleep(60)