import time

class UtilitiesBot():
    def get_open_position(bitget, configuration):
        coinPositionList = []

        try :
            coinPositionList = bitget.get_open_position()
            time.sleep(int(configuration['delay_coin']))
            #for t in coinPositionList:
            #    print(t)
        except Exception as e:
            print("ERROR : "+str(e))
        
        openPositions = len(coinPositionList)
        return openPositions
    
    def cancel_order_open(bitget, configuration, pair):
        open_order =  bitget.get_open_order(pair)
        if len(open_order) > 0:
            for order in open_order:
                bitget.cancel_order_by_id(order['info']['orderId'], pair)
        