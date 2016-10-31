# -*- encoding: utf8 -*-
'''
Created on 28 Oct 2016

@author: MetalInvest
'''
import poplib, email
import configparser
#import codecs

iniPath="autoTrading_ttc.ini"

class emailOrderParser(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        '''
        self.setupConfig()
        
    def setupConfig(self):
        config = configparser.ConfigParser()
        #config.read_file(codecs.open(iniPath, "r", "utf8"))
        config.read(iniPath)
        for i in range(5): # retry max 5 times
            try:
                emailCfg = config["EmailConfig"]
                self.pop_con = poplib.POP3_SSL(emailCfg["emailServer"], '995')
                #print (self.pop_con.getwelcome())
                self.pop_con.user(emailCfg["username"])#emailCfg["username"]
                self.pop_con.pass_(emailCfg["password"]) #emailCfg["password"]
                self.order_separator = emailCfg["order_separator"]
                self.stock_order_separator = emailCfg["stock_order_separator"]
            except:
                continue
            break
            
        
    def retrieveMsg(self):
        messages = [self.pop_con.retr(i) for i in range(1, len(self.pop_con.list()[1]) + 1)]
        # Concat message pieces:
        messages = [b"\n".join(mssg[1]) for mssg in messages]
        #Parse message intom an email object:
        messages = [email.message_from_bytes(mssg) for mssg in messages]
        self.pop_con.quit()
        return messages
    
    def getOrder(self):
        msgs = self.retrieveMsg()
        orders = []
        for m in msgs:
            orderString = m["subject"]
            if orderString:
                orders += self.parseOrder(orderString)
        return orders
            
    def parseOrder(self, sub_str):
        orders = []
        orderlist = sub_str.split(self.order_separator)
        for order in orderlist:
            trade = order.split(self.stock_order_separator)
            if len(trade) == 3:
                stock_code = trade[0]
                stock_pct = float(trade[1])
                stock_price = float(trade[2])
                if len(stock_code) == 6 and 0 <= stock_pct <= 100 and stock_price > 0:
                    print("received order {} for pct {} of price {}".format(stock_code, stock_pct, stock_price))
                    orders.append((stock_code, stock_pct, stock_price))
        return orders
    
# ep = emailOrderParser()
# ep.getOrder()