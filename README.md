# auto_trading_ttc [同花顺下单外挂]

可以修改配置文件支持其他下单程序， 对应的邮件分析系统是扫描新邮件检索下单信号。 通常来说外挂下单应该是你所需要的， 请随意使用。 不用谢， 叫我雷锋

The content of file autoTrading_ttc.ini below

[TradingGUIIndexMap_THS]
main_window_label = 网上股票交易系统5.0
main_window_class = Afx:400000:b:10003:6:10a027b
double_trade_panel_child_number = 73
summary_panel_child_number = 21
order_value_index = 0
buy_stock_code_index = 2
buy_order_type_index = 4
buy_order_price_index = 5
buy_stock_amount_index = 7
buy_button_index = 8
sell_stock_code_index = 11
sell_order_type_index = 13
sell_order_price_index = 14
sell_order_input_price_index = 15
sell_stock_amount_index = 16
sell_button_index = 17
summary_value_index = 1
summary_free_cash_index = 4
summary_port_value_index = 5
summary_total_value_index = 6
summary_frozen_value_index = 8

[EmailConfig]
emailServer = XXXX
username = XXXX
password = XXXX
order_separator = #
stock_order_separator = :
