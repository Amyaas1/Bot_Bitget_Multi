import ccxt
import pandas as pd
import time
import hmac
import base64
import hashlib
import bitget.spot.public_api as public
import bitget.spot.market_api as market
import bitget.spot.account_api as account
import bitget.spot.order_api as order
import json
import math

class SpotBitget():
    def __init__(self, apiKey=None, secret=None, password=None, EnableRateLimit=True):
        bitgetAuthObject = {
            "apiKey": apiKey,
            "secret": secret,
            "password": password,
            'options': {
                'defaultType': 'spot',
                'createMarketBuyOrderRequiresPrice': 'false'
            },
            'nonce': lambda: int(time.time() * 1000)
            #"EnableRateLimit": True,
       }
        if bitgetAuthObject['secret'] == None:
            self._auth = False
            self._session = ccxt.bitget()
        else:
            self._auth = True
            self._session = ccxt.bitget(bitgetAuthObject)
        self.market = self._session.load_markets()
        
       # orderApi = order.OrderApi(apiKey, secret, password, use_server_time=False, first=False)
       # result = orderApi.orders(symbol='ethusdt_spbl', price='1213.42', quantity='0.00580000', side='sell', orderType='market', force='normal', clientOrderId='')
       # print(result)
           
           
        #orderApi = order.OrderApi(apiKey, secret, password, use_server_time=False, first=False)
        #result = orderApi.history(symbol='btcusdt_spbl')
        #print(result)
        #self._session.verbose = True

        #print(self._session.has)
        
        #print(self._session.account())
        #if 'signIn' in self._session:
        #    self._session.sign()
        

        #print(self._session.requiredCredentials)
        #self._session.check_required_credentials() 
       
        #orderApi = order.OrderApi(apiKey, secret, password, use_server_time=False, first=False)
        #print(orderApi)
        
        #publicApi = public.PublicApi(apiKey, secret, password, use_server_time=True, first=False);
        #result = publicApi.currencies()
        #print(result)
    
        #accountApi = account.AccountApi(apiKey, secret, password, use_server_time=False, first=False)
        #result = accountApi.assets()
        #print(result)
        #result = accountApi.bills()
        #print(result)

    


    def authentication_required(fn):
        """Annotation for methods that require auth."""
        def wrapped(self, *args, **kwargs):
            if not self._auth:
                print("You must be authenticated to use this method", fn)
                exit()
            else:
                return fn(self, *args, **kwargs)
        return wrapped

    def get_historical_since(self, symbol, timeframe, startDate):
        try:
            tempData = self._session.fetch_ohlcv(symbol, timeframe, int(
                time.time()*1000)-1209600000, limit=1000)
            dtemp = pd.DataFrame(tempData)
            timeInter = int(dtemp.iloc[-1][0] - dtemp.iloc[-2][0])
        except:
            return None

        finished = False
        start = False
        allDf = []
        startDate = self._session.parse8601(startDate)
        while(start == False):
            try:
                tempData = self._session.fetch_ohlcv(
                    symbol, timeframe, startDate, limit=1000)
                dtemp = pd.DataFrame(tempData)
                timeInter = int(dtemp.iloc[-1][0] - dtemp.iloc[-2][0])
                nextTime = int(dtemp.iloc[-1][0] + timeInter)
                allDf.append(dtemp)
                start = True
            except:
                startDate = startDate + 1209600000*2

        if dtemp.shape[0] < 1:
            finished = True
        while(finished == False):
            try:
                tempData = self._session.fetch_ohlcv(
                    symbol, timeframe, nextTime, limit=1000)
                dtemp = pd.DataFrame(tempData)
                nextTime = int(dtemp.iloc[-1][0] + timeInter)
                allDf.append(dtemp)
                # print(dtemp.iloc[-1][0])
                if dtemp.shape[0] < 1:
                    finished = True
            except:
                finished = True
        result = pd.concat(allDf, ignore_index=True, sort=False)
        result = result.rename(
            columns={0: 'timestamp', 1: 'open', 2: 'high', 3: 'low', 4: 'close', 5: 'volume'})
        result = result.set_index(result['timestamp'])
        result.index = pd.to_datetime(result.index, unit='ms')
        del result['timestamp']
        return result

    def get_last_historical(self, symbol, timeframe, limit):
        result = pd.DataFrame(data=self._session.fetch_ohlcv(
            symbol, timeframe, None, limit=limit))
        result = result.rename(
            columns={0: 'timestamp', 1: 'open', 2: 'high', 3: 'low', 4: 'close', 5: 'volume'})
        result = result.set_index(result['timestamp'])
        result.index = pd.to_datetime(result.index, unit='ms')
        del result['timestamp']
        return result

    def get_bid_ask_price(self, symbol):
        try:
            ticker = self._session.fetchTicker(symbol)
            #print(ticker)
        except BaseException as err:
            print("An error occured", err)
            exit()
        return {"bid":ticker["bid"],"ask":ticker["ask"]}

    def get_min_order_amount(self, symbol):
        return self._session.markets_by_id[symbol]['limits']['amount']['min']

    def convert_amount_to_precision(self, symbol, amount):
        return self._session.amount_to_precision(symbol, amount)

    def convert_price_to_precision(self, symbol, price):
        return self._session.price_to_precision(symbol, price)

    @authentication_required
    def get_all_balance(self):
        try:
            allBalance = self._session.fetchBalance()
        except BaseException as err:
            print("An error occured", err)
            exit()
        return allBalance['total']
    
    
    def checkIfIsInAllbalance(self, pairList_coin, coinName):
        for coin in pairList_coin:
            if coin == coinName:
                return True
                pass
            
        
    def sommeCrypto(self, list, fiat):
        somme=0.0
        for key,value in list.items():
            if key != fiat:
                somme=float(float(somme)+float(value))
        return somme        

                
                
                    
    @authentication_required
    def get_all_balance_in_usd(self, pairList_coin):
        try:
            allBalance = self._session.fetchBalance()
            allBalance = allBalance['total']
            for coin in allBalance:
                if (coin != 'USDT') and (self.checkIfIsInAllbalance(pairList_coin, coin) == True):
                    try:
                        #print("total: "+str())
                        total = self.get_balance_of_one_coin(coin+'/USDT')
                        ticker = self._session.fetchTicker(coin+'/USDT')
                        price = ticker['last']
                        allBalance[coin] = float(total) * float(price)
                    except:
                        pass
                        print("Cannot get price of",coin+'/USDT')
        except BaseException as err:
            print("An error occured", err)
            exit()
        return allBalance

    @authentication_required
    def get_balance_of_one_coin(self, coin):
        try:
            allBalance = self._session.fetchBalance()
            
            for coinin in allBalance['info']:
                #print(str(coinin['coinName']+'/USDT') + ' : ' + str(coin))
                retour=0.0
                if str(coinin['coinName']+'/USDT') == str(coin):
                    frozen = coinin['frozen']
                    lock = coinin['lock']
                    available = coinin['available']
                    total = float(frozen) + float(lock) + float(available)
                    #print(" Coin:"+coinin['coinName']+ " Total:" + str(total))
                    #retour = total
                    return total
                
              
            
        except BaseException as err:
            print("An error occured", err)
            exit()
        #try:
            
           # allBalanceTotal = allBalance['total'][coin]
        #    print("retour2:"+str(retour))
        #    return retour
        #except:
        #    return 0

    @authentication_required
    def get_balance_of_one_coin_usd(self, coin):
        try:
            allBalance = self._session.fetchBalance()
        except BaseException as err:
            print("An error occured", err)
            exit()
        try:
            return allBalance['total'][coin]
        except:
            return 0

    def pre_hash(timestamp, method, request_path, body):
        return str(timestamp) + str.upper(method) + request_path + body
    
    def sign(message, secret_key):
        mac = hmac.new(bytes(secret_key, encoding='utf8'), bytes(message, encoding='utf-8'), digestmod='sha256')
        d = mac.digest()
        return base64.b64encode(d)
    
    @authentication_required
    def place_market_order(self, symbol, side, amount, price):
        orderType="market"
        try:
             
           # orderApi = order.OrderApi(apiKey, secret, password, use_server_time=False, first=False)
            #result = orderApi.orders(symbol=coin.lower()+'usdt_spbl', price=price, quantity=montant, side=side, orderType=orderType, force='normal', clientOrderId='')
           # print(result)
            result='Symbol: '+str(symbol)+' Side: '+str(side)+' Amount: '+str(amount)+' Price: '+str(price)+' Precision: '+str(self.convert_amount_to_precision(symbol, amount))
            print(result)
            
            return self._session.createOrder(
            #    #'client_order_id': ,
                symbol, 
                'market', 
                side, 
                self.convert_amount_to_precision(symbol, amount), 
                self.convert_price_to_precision(symbol, price),
            #    params
                )
        except BaseException as err:
            print("An error occured", err)
            exit()

    @authentication_required
    def place_limit_order(self, symbol, side, amount, price):
        print('Symbol:'+str(symbol)+' Side:'+str(side)+' Amount:'+str(amount)+' buyPrice'+str(price)+' Pricision:'+str(self.convert_amount_to_precision(symbol, amount)))
        try:
            return self._session.createOrder(
                symbol, 
                'limit', 
                side, 
                self.convert_amount_to_precision(symbol, amount), 
                self.convert_price_to_precision(symbol, price)
                )
        except BaseException as err:
            print("An error occured", err)
            exit()

    @authentication_required
    def place_market_stop_loss(self, symbol, amount, price):
        params = {
        'stopPrice': self.convert_price_to_precision(symbol, price),  # your stop price
        }
        try:
            return self._session.createOrder(
                symbol, 
                'stop', 
                'sell', 
                self.convert_amount_to_precision(symbol, amount), 
                None,
                params
                )
        except BaseException as err:
            print("An error occured", err)
            exit()

    @authentication_required
    def cancel_all_open_order(self, symbol):
        try:
            #print(symbol)
            open_order=self._session.fetch_open_orders(symbol)
            #print(open_order)
            try:
                for order in open_order:
                    self._session.cancel_order(order['id'],symbol)
                return True    
            except BaseException as err:
                print("An error occured", err)
                return False            
                
        except BaseException as err:
            print("An error occured", err)
            exit()

    @authentication_required
    def cancel_order_by_id(self, id):
        try:
            return self._session.cancel_order(id)
        except BaseException as err:
            print("An error occured", err)
            exit()

    @authentication_required
    def get_open_order(self):
        try:
            return self._session.fetchOpenOrders()
        except BaseException as err:
            print("An error occured", err)
            exit()

    @authentication_required
    def get_open_stop_order(self):
        params = {
            'type':'stop'
        }
        try:
            return self._session.fetchOpenOrders(None,None,None,params)
        except BaseException as err:
            print("An error occured", err)
            exit()

    @authentication_required
    def get_my_trades(self, symbol=None, since=None, limit=1):
        try:
            return self._session.fetch_my_trades(symbol, since, limit)
        except BaseException as err:
            print("An error occured", err)
            exit()