from message_telegram import MessageTelegram
import time

class StopLost():
    #def place_limit_stop_loss(self, symbol, side, amount, trigger_price, price, reduce=False):
    
    def put_stop_lost(bitget, configuration, message, type_trade, quantity, price, dfList, coin, pair):
        if(type_trade == "long"):
            
            pct_sl = float(configuration['sl'])
            pct = (price * pct_sl)
            trigger_price = price - pct
            
            time.sleep(int(configuration['delay_coin'])) 
            #bitget.place_limit_stop_loss(pair, "sell", quantity, trigger_price, price, reduce=False)
            bitget.place_limit_order(pair, "sell", quantity, trigger_price, reduce=False)
            
            message = MessageTelegram.addMessageComponent(message, f"Place SL for the Long Limit Order: {quantity} {pair[:-5]} at the price of {trigger_price}$ ~{round(quantity, 2)}$\n")
                    
                                    
        if(type_trade == "short"):
            
            pct_sl = float(configuration['sl'])
            pct = (price * pct_sl)
            trigger_price = price + pct
            
            time.sleep(int(configuration['delay_coin'])) 
            #bitget.place_limit_stop_loss(pair, "buy", quantity, trigger_price, price, reduce=False)
            bitget.place_limit_order(pair, "buy", quantity, trigger_price, reduce=False)
            
            message = MessageTelegram.addMessageComponent(message, f"Place SL for the Short Limit Order: {quantity} {pair[:-5]} at the price of {trigger_price}$ ~{round(quantity, 2)}$\n")
             
        return message
            