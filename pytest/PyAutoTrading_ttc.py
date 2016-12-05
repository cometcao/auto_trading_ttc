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
import logging
import sys



class TTC_autoTrader:
    def __init__(self):
        self._init_log()
        self.winapi = tradingAPI()
    
    def _init_log(self):
        self.root_log = logging.getLogger()
        self.root_log.setLevel(logging.INFO)
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s-%(name)s-%(levelname)s-%(message)s')
        ch.setFormatter(formatter)
        self.root_log.addHandler(ch)
        
    def _getOrderDetails(self):
        ep = emailOrderParser(self.root_log)
        return ep.getOrder()
    
    def orderProcess(self):
        orders = self._getOrderDetails()
        self.winapi.grabTradingApplication()
        try:
            for stock, pct, price in orders:
                if pct == 0: # sell off the stock
                    self.root_log.info("trying to sell off {}".format(stock))
                    self.winapi.clearStock(stock)
                else:
                    free_cash, _, total_value, _ = self.winapi.getAccDetails()
                    self.root_log.info("current cash: {} total value: {}".format(free_cash, total_value))
                    allocated_value = pct / 100.0 * total_value
                    spendable_value = min(free_cash, allocated_value)
                    if spendable_value > 0:
                        amount = spendable_value // price
                        amount = amount - amount % 100 
                        self.root_log.info("trying to adjust {} to {}% with amount {}".format(stock, pct, amount))
                        self.winapi.adjustStock(stock, price, amount)
                time.sleep(30) # pause 10 seconds after each order
        except:
            traceback.print_exc()
            raise "order failed! please check!"
            
if __name__ == '__main__':
    ttc = TTC_autoTrader()
    ttc.root_log.info("Auto Trading system started/自动交易系统运行中， 请开启同花顺网上交易系统5.0")
    while True:
        orderP = threading.Thread(target=ttc.orderProcess)
        orderP.start()
        orderP.join(60) 
        time.sleep(180)