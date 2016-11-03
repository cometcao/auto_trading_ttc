# -*- encoding: utf8 -*-

'''
This system takes trading signals, and pass on to the trading application, and auto completes the trade
order confirmation needs to be disabled!!!
'''

import time
import traceback
from PyEmailParser_ttc import emailOrderParser
from PyWinApi import tradingAPI
from time import strftime
import threading

class TTC_autoTrader:
    def __init__(self):
        self.winapi = tradingAPI()
        
    def getOrderDetails(self):
        ep = emailOrderParser()
        return ep.getOrder()
    
    def orderProcess(self):
        #orders = self.getOrderDetails()
        orders = [('600689', 0, 1)]
        try:
            for stock, pct, price in orders:
                free_cash, _, total_value, _ = self.winapi.getAccDetails()
                if pct == 0: # sell off the stock
                    print ("trying to sell off {}".format(stock))
                    self.winapi.clearStock(stock)
                else:
                    allocated_value = pct / 100.0 * total_value
                    spendable_value = min(free_cash, allocated_value)
                    if spendable_value > 0:
                        amount = spendable_value // price
                        amount = amount - amount % 100 
                        print ("trying to adjust {} to {}%".format(stock, pct))
                        self.winapi.adjustStock(stock, price, amount)
                time.sleep(3) # pause 5 seconds after each order
        except:
            traceback.print_exc()
            raise "order failed! please check!"
            
if __name__ == '__main__':
    print("Auto Trading system started/自动交易系统运行中， 请开启同花顺网上交易系统5.0")
    ttc = TTC_autoTrader()
    while True:
        print(strftime("%Y-%m-%d %H:%M:%S"))
#         orderP = threading.Thread(target=ttc.orderProcess)
#         orderP.start()
#         orderP.join(10)
        ttc.orderProcess()
        time.sleep(180)