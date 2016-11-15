# -*- encoding: utf8 -*-
'''
Created on 28 Oct 2016

@author: MetalInvest
'''
import poplib, email
import configparser
import time

import feedparser
import urllib.request
import logging

#import codecs

iniPath="autoTrading_ttc.ini"

class emailOrderParser(object):
    '''
    classdocs
    '''

    def __init__(self, root_log):
        '''
        '''
        self.root_log = root_log
        self.config = configparser.ConfigParser()
        self.config.read(iniPath)
        
    def _setupConfig(self):
        emailCfg = self.config["EmailConfig"]
        self.pop_con = poplib.POP3_SSL(emailCfg["emailServer"], port='995', timeout=5)
        #print (self.pop_con.getwelcome())
        self.pop_con.user(emailCfg["username"])#emailCfg["username"]
        self.pop_con.pass_(emailCfg["password"]) #emailCfg["password"]
        self.order_separator = emailCfg["order_separator"]
        self.stock_order_separator = emailCfg["stock_order_separator"]
        
    def _retrieveMsg(self):
        for i in range(5): # retry max 5 times
            try:
                self._setupConfig()
                messages = [self.pop_con.retr(i) for i in range(1, len(self.pop_con.list()[1]) + 1)]
                # Concat message pieces:
                messages = [b"\n".join(mssg[1]) for mssg in messages]
                #Parse message intom an email object:
                messages = [email.message_from_bytes(mssg) for mssg in messages]
                self.pop_con.quit()
                self.root_log.info("number of message received:{}".format(len(messages)))
                return messages
            except:
                self.root_log.error("failed to connect to read email! retrying...")
                time.sleep(0.5)
                continue
        return []
    
    def _retrieveMsg_v2(self):
        emailCfg = self.config["EmailConfig"]
        auth_handler = urllib.request.HTTPBasicAuthHandler()
        auth_handler.add_password(
            realm='mail.google.com',
            uri='https://mail.google.com',
            user='%s@gmail.com' % emailCfg["username"],
            passwd=emailCfg["password"]
        )
        opener = urllib.request.build_opener(auth_handler)
        urllib.request.install_opener(opener)
        feed = urllib.request.urlopen('https://mail.google.com/mail/feed/atom')        
        d = feedparser.parse(feed)
        print(d)
    
    def getOrder(self):
        msgs = self._retrieveMsg()
        orders = []
        for m in msgs:
            orderString = m["subject"]
            if orderString:
                orders += self._parseOrder(orderString)
        orders.sort(key=lambda tup: tup[1])
        return orders
            
    def _parseOrder(self, sub_str):
        orders = []
        orderlist = sub_str.split(self.order_separator)
        for order in orderlist:
            trade = order.split(self.stock_order_separator)
            if len(trade) == 3:
                stock_code = trade[0]
                stock_pct = float(trade[1])
                stock_price = float(trade[2])
                if len(stock_code) == 6 and 0 <= stock_pct <= 100 and stock_price >= 0:
                    self.root_log.info("received order {} for {}% of portfolio at price {}".format(stock_code, stock_pct, stock_price))
                    orders.append((stock_code, stock_pct, stock_price))
        return orders
#     
# ep = emailOrderParser()
# ep._retrieveMsg_v2()