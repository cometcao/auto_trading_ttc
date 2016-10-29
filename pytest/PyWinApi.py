# -*- encoding: utf8 -*-
'''
Created on 29 Oct 2016

@author: MetalInvest
'''
import time
import struct
import win32api
import win32gui
import win32con
from winguiauto import *
import re
import configparser


iniPath="autoTrading_ttc.ini"
class tradingAPI:
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.setupConfig()
        self.grabTradingApplication()
    
    def setupConfig(self):
        config = configparser.ConfigParser()
        config.read(iniPath)
        self.tradingCfg = config["TradingGUIIndexMap_THS"]

    def grabTradingApplication(self):
        self.main_window = self.find_window(None, self.tradingCfg["main_window_label"])
        if not self.main_window:
            raise "Trading application not detected!!"
        self.trading_window = findSpecifiedWindows(self.main_window, int(self.tradingCfg["double_trade_panel_child_number"]))
        if not self.trading_window:
            raise "Trading panel can't be located"   
        focusWindow(self.main_window, win32con.SW_SHOWDEFAULT)     

    def getAccDetails(self):
        summary_window = findSpecifiedWindows(self.main_window, int(self.tradingCfg["summary_panel_child_number"]))
        free_cash = float(summary_window[int(self.tradingCfg["summary_free_cash_index"])][int(self.tradingCfg["summary_value_index"])]) # free cash
        port_value = float(summary_window[int(self.tradingCfg["summary_port_value_index"])][int(self.tradingCfg["summary_value_index"])]) # port value
        total_value = float(summary_window[int(self.tradingCfg["summary_total_value_index"])][int(self.tradingCfg["summary_value_index"])]) # total asset
        frozen_value = float(summary_window[int(self.tradingCfg["summary_frozen_value_index"])][int(self.tradingCfg["summary_value_index"])]) # frozen asset
        return free_cash, port_value, total_value, frozen_value
        
    def clearStock(self, stock):
        self.setEditText(self.trading_window[int(self.tradingCfg["sell_stock_code_index"])][int(self.tradingCfg["order_value_index"])], stock)
        self.setComboBoxIndex(self.trading_window[int(self.tradingCfg["sell_order_type_index"])][int(self.tradingCfg["order_value_index"])], 1) 
        self.click(self.trading_window[int(self.tradingCfg["sell_order_input_price_index"])][int(self.tradingCfg["order_value_index"])]) # click static to reflect the stock position
        self.winapi.click(self.trading_window[int(self.tradingCfg["sell_button_index"])][int(self.tradingCfg["order_value_index"])])# sell button
        
    def adjustStock(self, stock, pct, price, cash, tol):
        # for now we only have buy position from empty position
        #self.findStockPosition(stock) # this can't be easily achieved for now
        allocated_value = pct / 100.0 * tol
        spendable_value = min(cash, allocated_value)
        if spendable_value > 3000:
            amount = spendable_value // price
            amount = amount - amount % 100 
            self.setEditText(self.trading_window[2][0], stock)
            self.setComboBoxIndex(self.trading_window[4][0], 1)
            self.setEditText(self.trading_window[7][0], str(amount)) # enter stock amount
            self.click(self.trading_window[8][0])# buy button

    def findStockPosition(self, stock):
        self.setEditText(self.trading_window[int(self.tradingCfg["sell_stock_code_index "])][int(self.tradingCfg["order_value_index "])], stock)
        self.click(self.trading_window[15][0]) # click static to reflect the stock position
        posNum = int(self.getWindowText(self.trading_window[16][0]))
        
#################################################################################################  
        
    def find_window(self, class_name, window_name = None):
        """find a window by its class_name"""
        return win32gui.FindWindow(class_name, window_name)

    def _window_enum_callback(self, hwnd, wildcard):
        '''Pass to win32gui.EnumWindows() to check all the opened windows'''
        if re.match(wildcard, str(win32gui.GetWindowText(hwnd))) != None:
            self._handle = hwnd

    def find_window_wildcard(self, wildcard):
        self._handle = None
        win32gui.EnumWindows(self._window_enum_callback, wildcard)

    def set_foreground(self):
        """put the window in the foreground"""
        focusWindow(self._handle, win32con.SW_SHOWDEFAULT)
        
    def set_doubleTradeScreen(self):
        sendKey(self._handle, win32con.VK_F6)
        
    def findChildWindows(self, hwnd):
        windows = []
        try:
            win32gui.EnumChildWindows(hwnd, self._windowEnumerationHandler, windows)
        except win32gui.error:
            # No child windows
            return
        return windows
    
    def setEditText(self, hwnd, text):
        '''
        设置Edit控件的文本，这个只能是单行文本
        :param hwnd: Edit控件句柄
        :param text: 要设置的文本
        :return:
        '''
        win32gui.SendMessage(hwnd, win32con.WM_SETTEXT, None, text)

    def setComboBoxIndex(self, hwnd, index):
        win32gui.SendMessage(hwnd,win32con.CB_SETCURSEL,index,0)

    def getWindowText(self, hwnd):
        return win32gui.GetWindowText(hwnd)

    def clickButton(self, hwnd):
        '''Simulates a single mouse click on a button
    
        Parameters
        ----------
        hwnd
            Window handle of the required button.
    
        Usage example::
    
            okButton = findControl(fontDialog,
                                   wantedClass="Button",
                                   wantedText="OK")
            clickButton(okButton)
        '''
        clickButton(hwnd)


    def click(self, hwnd):
        '''
        模拟鼠标左键单击
        :param hwnd: 要单击的控件、窗体句柄
        :return:
        '''
        time.sleep(0.3)
        win32gui.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, None, None)
        time.sleep(.2)
        win32gui.PostMessage(hwnd, win32con.WM_LBUTTONUP, None, None)
        time.sleep(0.3)