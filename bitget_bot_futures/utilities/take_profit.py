from message_telegram import MessageTelegram
import time

class TakeProfit():
    def put_take_profit(bitget, configuration, message, type_trade, quantity_total, dfList, coin, pair):
        if(int(configuration['nb_tp']) == 1):
            if(type_trade == "long"):
                quantity_tp_1 = float(quantity_total) / 2                                 
                pct_quantity_tp_1 = (quantity_tp_1 * 5) / 100 
                quantity_tp_1_final = quantity_tp_1 - pct_quantity_tp_1
            
                ActualPrice = float(dfList[coin].iloc[-1]["close"])
                tp1Price = float(bitget.convert_price_to_precision(pair, ActualPrice + float(configuration['tp_1']) * ActualPrice))
                tp1_long_quantity = quantity_tp_1_final * tp1Price
                    
                time.sleep(int(configuration['delay_coin']))                                
                bitget.place_limit_order(pair, "sell", quantity_tp_1_final, tp1Price, reduce=True)
                message = MessageTelegram.addMessageComponent(message, f"Place TP for 50% of the Long Limit Order: {quantity_tp_1_final} {pair[:-5]} at the price of {tp1Price}$ ~{round(tp1_long_quantity, 2)}$\n")
                            
                                        
            if(type_trade == "short"):
                quantity_tp_1 = float(quantity_total) / 2                                 
                pct_quantity_tp_1 = (quantity_tp_1 * 5) / 100 
                quantity_tp_1_final = quantity_tp_1 - pct_quantity_tp_1
                #print(quantity_tp_1_final)
                
                ActualPrice = float(dfList[coin].iloc[-1]["close"])
                tp1Price = float(bitget.convert_price_to_precision(pair, ActualPrice - float(configuration['tp_1']) * ActualPrice))
                tp1_short_quantity = quantity_tp_1_final * tp1Price
                
                time.sleep(int(configuration['delay_coin']))                                
                bitget.place_limit_order(pair, "buy", quantity_tp_1_final, tp1Price, reduce=True)
                message = MessageTelegram.addMessageComponent(message, f"Place TP for 50% of the Short Limit Order: {quantity_tp_1_final} {pair[:-5]} at the price of {tp1Price}$ ~{round(tp1_short_quantity, 2)}$\n")
            
            
        if(int(configuration['nb_tp']) == 2):
            if(type_trade == "long"):
                quantity_tp_2 = float(quantity_total) / 3                                 
                pct_quantity_tp_2 = (quantity_tp_2 * 5) / 100 
                quantity_tp_2_final = quantity_tp_2 - pct_quantity_tp_2
                #print(quantity_tp_2_final)
                
                ActualPrice = float(dfList[coin].iloc[-1]["close"])
                tp1Price = float(bitget.convert_price_to_precision(pair, ActualPrice + float(configuration['tp_1']) * ActualPrice))
                tp1_long_quantity = quantity_tp_2_final * tp1Price
                tp2Price = float(bitget.convert_price_to_precision(pair, ActualPrice + float(configuration['tp_2']) * ActualPrice))
                tp2_long_quantity = quantity_tp_2_final * tp2Price
                
                time.sleep(int(configuration['delay_coin']))
                bitget.place_limit_order(pair, "sell", quantity_tp_2_final, tp1Price, reduce=True)
                message = MessageTelegram.addMessageComponent(message, f"Place TP for 33% of the Long Limit Order: {quantity_tp_2_final} {pair[:-5]} at the price of {tp1Price}$ ~{round(tp1_long_quantity, 2)}$\n")
            
                time.sleep(int(configuration['delay_coin']))
                bitget.place_limit_order(pair, "sell", quantity_tp_2_final, tp2Price, reduce=True)
                message = MessageTelegram.addMessageComponent(message, f"Place TP for 66% of the Long Limit Order: {quantity_tp_2_final} {pair[:-5]} at the price of {tp2Price}$ ~{round(tp2_long_quantity, 2)}$\n")
        
            if(type_trade == "short"):
                quantity_tp_2 = float(quantity_total) / 3                                 
                pct_quantity_tp_2 = (quantity_tp_2 * 5) / 100 
                quantity_tp_2_final = quantity_tp_2 - pct_quantity_tp_2
                #print(quantity_tp_1_final)
                
                ActualPrice = float(dfList[coin].iloc[-1]["close"])
                tp1Price = float(bitget.convert_price_to_precision(pair, ActualPrice - float(configuration['tp_1']) * ActualPrice))
                tp1_short_quantity = quantity_tp_2_final * tp1Price
                
                tp2Price = float(bitget.convert_price_to_precision(pair, ActualPrice - float(configuration['tp_2']) * ActualPrice))
                tp2_short_quantity = quantity_tp_2_final * tp2Price
                
                time.sleep(int(configuration['delay_coin']))                                
                bitget.place_limit_order(pair, "buy", quantity_tp_2_final, tp1Price, reduce=True)
                message = MessageTelegram.addMessageComponent(message, f"Place TP for 33% of the Short Limit Order: {quantity_tp_2_final} {pair[:-5]} at the price of {tp1Price}$ ~{round(tp1_short_quantity, 2)}$\n")
            
                time.sleep(int(configuration['delay_coin']))                                
                bitget.place_limit_order(pair, "buy", quantity_tp_2_final, tp2Price, reduce=True)
                message = MessageTelegram.addMessageComponent(message, f"Place TP for 66% of the Short Limit Order: {quantity_tp_2_final} {pair[:-5]} at the price of {tp2Price}$ ~{round(tp2_short_quantity, 2)}$\n")
        
                
            
        return message
            