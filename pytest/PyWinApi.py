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
import logging

iniPath="autoTrading_ttc.ini"
class tradingAPI:
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self._setupConfig()
        self._grabTradingApplication()
    
    def _setupConfig(self):
        config = configparser.ConfigParser()
        config.read(iniPath)
        self.tradingCfg = config["TradingGUIIndexMap_THS"]

    def _grabTradingApplication(self):
        self.main_window = self._find_window(None, self.tradingCfg["main_window_label"])
        if not self.main_window:
            raise "Trading application not detected!!"
        self._getFocus()
#         self._set_foreground()
#         self._set_doubleTradeScreen()
        self.trading_window = findSpecifiedWindows(self.main_window, int(self.tradingCfg["double_trade_panel_child_number"]))
        if not self.trading_window:
            raise "Trading panel can't be located"   
        
    def _getFocus(self):
        #self.set_foreground()
        self._set_doubleTradeScreen()
        time.sleep(0.5)

    def getAccDetails(self):
        summary_window = findSpecifiedWindows(self.main_window, int(self.tradingCfg["summary_panel_child_number"]))
        free_cash = float(summary_window[int(self.tradingCfg["summary_free_cash_index"])][int(self.tradingCfg["summary_value_index"])]) # free cash
        port_value = float(summary_window[int(self.tradingCfg["summary_port_value_index"])][int(self.tradingCfg["summary_value_index"])]) # port value
        total_value = float(summary_window[int(self.tradingCfg["summary_total_value_index"])][int(self.tradingCfg["summary_value_index"])]) # total asset
        frozen_value = float(summary_window[int(self.tradingCfg["summary_frozen_value_index"])][int(self.tradingCfg["summary_value_index"])]) # frozen asset
        return free_cash, port_value, total_value, frozen_value
        
    def clearStock(self, stock):
        self._getFocus()
        self._setEditText(self.trading_window[int(self.tradingCfg["sell_stock_code_index"])][int(self.tradingCfg["order_value_index"])], stock)
        self._setComboBoxIndex(self.trading_window[int(self.tradingCfg["sell_order_type_index"])][int(self.tradingCfg["order_value_index"])], 1) 
        self._click(self.trading_window[int(self.tradingCfg["sell_order_input_price_index"])][int(self.tradingCfg["order_value_index"])]) # _click static to reflect the stock position
        self._clickButton(self.trading_window[int(self.tradingCfg["sell_button_index"])][int(self.tradingCfg["order_value_index"])])# sell button
        #self.set_background()
        
    def adjustStock(self, stock, price, amount):
        # for now we only have buy position from empty position
        order_index = 1
        if stock[0] == '6': #shang hai stock exchange code
            order_index = 2
        self._getFocus()
        self._setEditText(self.trading_window[int(self.tradingCfg["buy_stock_code_index"])][int(self.tradingCfg["order_value_index"])], stock)
        self._setComboBoxIndex(self.trading_window[int(self.tradingCfg["buy_order_type_index"])][int(self.tradingCfg["order_value_index"])], order_index)
        self._setEditText(self.trading_window[int(self.tradingCfg["buy_stock_amount_index"])][int(self.tradingCfg["order_value_index"])], str(amount)) # enter stock amount
        self._clickButton(self.trading_window[int(self.tradingCfg["buy_button_index"])][int(self.tradingCfg["order_value_index"])])# buy button
        #self.set_background()

    def findStockPosition(self, stock):
        self._setEditText(self.trading_window[int(self.tradingCfg["sell_stock_code_index "])][int(self.tradingCfg["order_value_index "])], stock)
        self._click(self.trading_window[15][0]) # click static to reflect the stock position
        posNum = int(self._getWindowText(self.trading_window[16][0]))
        
#################################################################################################  
        
    def _find_window(self, class_name, window_name = None):
        """find a window by its class_name"""
        return win32gui.FindWindow(class_name, window_name)

    def _window_enum_callback(self, hwnd, wildcard):
        '''Pass to win32gui.EnumWindows() to check all the opened windows'''
        if re.match(wildcard, str(win32gui.GetWindowText(hwnd))) != None:
            self.main_window = hwnd

    def _find_window_wildcard(self, wildcard):
        self.main_window = None
        win32gui.EnumWindows(self._window_enum_callback, wildcard)

    def _set_foreground(self):
        """put the window in the foreground"""
        focusWindow(self.main_window, win32con.SW_SHOWNORMAL)
        
    def _set_background(self):
        """put the window in the foreground"""
        focusWindow(self.main_window, win32con.SW_HIDE)
        
    def _set_doubleTradeScreen(self):
        sendKey(self.main_window, win32con.VK_F6)
        
    def _set_focus_buyScreen(self):
        sendKey(self.trading_window, win32con.VK_F1)

    def _set_focus_sellScreen(self):
        sendKey(self.trading_window, win32con.VK_F2)
        
    def _findChildWindows(self, hwnd):
        windows = []
        try:
            win32gui.EnumChildWindows(hwnd, self._windowEnumerationHandler, windows)
        except win32gui.error:
            # No child windows
            return
        return windows
    
    def _setEditText(self, hwnd, text):
        '''
        设置Edit控件的文本，这个只能是单行文本
        :param hwnd: Edit控件句柄
        :param text: 要设置的文本
        :return:
        '''
        self._click(hwnd)
        win32gui.SendMessage(hwnd, win32con.WM_SETTEXT, None, "")
        time.sleep(1)
        win32gui.SendMessage(hwnd, win32con.WM_SETTEXT, None, text)
        time.sleep(1.5)
#         win32gui.SendMessage(hwnd, win32con.WM_ACTIVATE, None, None)
        

    def _setComboBoxIndex(self, hwnd, index):
        win32gui.SendMessage(hwnd,win32con.CB_SETCURSEL,index,0)

    def _getWindowText(self, hwnd):
        return win32gui.GetWindowText(hwnd)

    def _clickButton(self, hwnd):
        '''Simulates a single mouse _click on a button
    
        Parameters
        ----------
        hwnd
            Window handle of the required button.
    
        Usage example::
    
            okButton = findControl(fontDialog,
                                   wantedClass="Button",
                                   wantedText="OK")
            _clickButton(okButton)
        '''
        clickButton(hwnd)


    def _click(self, hwnd):
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