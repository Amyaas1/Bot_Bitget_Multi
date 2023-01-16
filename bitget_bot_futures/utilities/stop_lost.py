from message_telegram import MessageTelegram
import time

class StopLost():
        
    def put_stop_lost(bitget, configuration, message, type_trade, quantity, price, dfList, coin, pair):
        if(type_trade == "long"):
            print("test long")
            pct_sl = float(configuration['sl'])
            pct = (price * pct_sl)
            trigger_price = price - pct
            limit_price = price - pct
            #symbol, side, amount, trigger_price, limit_price
            time.sleep(int(configuration['delay_coin'])) 
            print(
                        f"Place Stop Lost Long Limit Order: {quantity} {pair[:-5]} at the price of {price}$ ~{round(quantity, 2)}$"
                    )
            
            bitget.place_limit_order(pair, "buy", quantity, trigger_price, reduce=False)
            message = MessageTelegram.addMessageComponent(message, f"Place SL for the Long Limit Order: {quantity} {pair[:-5]} at the price of {trigger_price}$ ~{round(quantity, 2)}$\n")
                    
                                    
        if(type_trade == "short"):
            
            pct_sl = float(configuration['sl'])
            pct = (price * pct_sl)
            trigger_price = price + pct
            limit_price = trigger_price + 0.1
            
            time.sleep(int(configuration['delay_coin'])) 
            #symbol, side, amount, trigger_price, limit_price
            print(
                        f"Place Stop Lost Short Limit Order: {quantity} {pair[:-5]} at the price of {price}$ ~{round(quantity, 2)}$"
                    )
           
            bitget.place_limit_order(pair, "sell", quantity, trigger_price, reduce=False)
            
            message = MessageTelegram.addMessageComponent(message, f"Place SL for the Short Limit Order: {quantity} {pair[:-5]} at the price of {trigger_price}$ ~{round(quantity, 2)}$\n")
             
        return message
            