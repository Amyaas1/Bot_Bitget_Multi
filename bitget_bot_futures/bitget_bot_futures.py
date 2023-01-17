#=============================
#	 IMPORTS NECESSAIRES
#=============================
from optparse import Values

import sys
path=sys.path[0]+'/'
#from numpy import NaN, float64, little_endian
sys.path.append(path+'utilities')
import pandas as pd
import time
import ccxt
from time import sleep
from utilities.perp_bitget import PerpBitget
from utilities.custom_indicators import CustomIndocators
from utilities.bilan import BilanSolde
from utilities.configuration_bot import ConfigBot
from utilities.get_infos_tokens import InfosTokens
from utilities.populate_data_exchange import DataExchange
from utilities.strats.populate_indicators import DataIndicators
from utilities.utilities_bot import UtilitiesBot
from utilities.take_profit import TakeProfit
from utilities.stop_lost import StopLost              

positionList=" "

#Démarage du bot
print('CCXT Version:', ccxt.__version__)
configuration = ConfigBot.get_var_config_bot(path)

if configuration['telegram_on'] == "True":
    message=" "
    from utilities.message_telegram import MessageTelegram
    import telegram_send
    
    
    
if configuration['debug'] == "True":
    print("************* Configuration des variables ****************")
    print(configuration)
    print("**********************************************************")

#choix de la class a importer suivant la strat choisi
if configuration['strat_active'] == "BOLLINGER":
    from utilities.strats.condition_bollinger import ConditionTrade
    
if configuration['telegram_on'] == "True":
    #Début du message Télégram
    message = MessageTelegram.addMessageComponent(message, f"{configuration['date_time']}\n{configuration['botname']} v{configuration['botnameversion']}")
    message = MessageTelegram.addMessageComponent(message, "===================\n")  


#Récupération de la liste des tokens et de leur infos
pairList = InfosTokens.get_infos_tokens(sys.path[0]+'/pair_list.json', configuration)

#Authentification sur l'exchange
bitget = PerpBitget(
		apiKey=configuration['apiKey'],
		secret=configuration['secret'],
        password=configuration['password']
	)

#si besoin d'une connexion mysql
if configuration['mysql_active'] == "True":
    from utilities.mysql_dashboard import MysqlDashboard
    mysql_dashboard  = MysqlDashboard(
		configuration
	)

# RECUPERE LE MONTANT TOTAL D'USD SUR LE SUBACCOUNT SPECIFIE
usd_balance = float(bitget.get_usdt_equity())
print("USD balance :", round(usd_balance, 2), configuration['stableCoin'])

# Collecte des Data de l'exchange
print("Collecte des Data de l'exchange")
if configuration['telegram_on'] == "True":
    dfList = DataExchange.get_data_exchange(pairList, configuration, bitget, telegram_send)
else:
    dfList = DataExchange.get_data_exchange(pairList, configuration, bitget, "")

# Collecte des indicateurs
print("Collecte des indicateurs")
dfList = DataIndicators.populate_indicator(configuration, dfList)



#print(openPositions)
#cette variable nous servira à la fin pour déterminer si on a fait des actions ou pas
#si la variable est toujours à 0 c'est qu'il n'y a eu aucun changement et qu'on ne prévient pas le bot telegram de nous notifier
changement=0

#==================================================
#          EXECUTION PRINCIPALE DU BOT : 
#==================================================
if configuration['telegram_on'] == "True":
    message = MessageTelegram.addMessageComponent(message, "Actions prises par le bot :\n")

#===================================
#  On execute la strat sur les différentes cryptos
#===================================

print("Execution de la Strat sur les Tokens")
openPositions = UtilitiesBot.get_open_position(bitget, configuration)


 
for coin in dfList:
    positions_data = bitget.get_open_position() 
    if configuration['debug'] == "True":
                print("Test sur : " + coin)
                
    
    try :
        openPositions = UtilitiesBot.get_open_position(bitget, configuration)
        pair=coin+"/"+configuration['stableCoin']+":"+configuration['stableCoin']
        
        position = [
                    {"side": d["side"], "size": d["contractSize"], "market_price":d["info"]["marketPrice"], "usd_size": float(d["contractSize"]) * float(d["info"]["marketPrice"]), "open_price": d["entryPrice"]}
                    for d in positions_data if d["symbol"] == pair
                    ]
        row = dfList[coin].iloc[-2]
       
        if len(position) > 0:
            position = position[0]
            
            print(f"Current position : {position}")
            
            if position["side"] == "long" and ConditionTrade.close_long(row, configuration):
                close_long_market_price = float(dfList[coin].iloc[-1]["close"])
                close_long_quantity = float(
                    bitget.convert_amount_to_precision(pair, position["size"])
                )
                exchange_close_long_quantity = close_long_quantity * close_long_market_price
                print(
                    f"Place Close Long Market Order: {close_long_quantity} {pair[:-5]} at the price of {close_long_market_price}$ ~{round(exchange_close_long_quantity, 2)}$"
                )
                if configuration['production'] == "True":
                    UtilitiesBot.cancel_order_open(bitget, configuration, pair)
                    time.sleep(int(configuration['delay_coin']))  
                    
                    bitget.place_market_order(pair, "sell", close_long_quantity, reduce=True)
                    if configuration['telegram_on'] == "True":
                        message = MessageTelegram.addMessageComponent(message, f"Place Close Long Market Order: {close_long_quantity} {pair[:-5]} at the price of {close_long_market_price}$ ~{round(exchange_close_long_quantity, 2)}$\n")
                    openPositions -= 1
                    #Ajout du log close long dans la db
                    if configuration['mysql_active'] == "True":
                        mysql_dashboard.log_close_long(close_long_quantity, coin, close_long_market_price)
                    #Fin de mysql
                    changement=changement+1

            elif position["side"] == "short" and ConditionTrade.close_short(row, configuration):
                close_short_market_price = float(dfList[coin].iloc[-1]["close"])
                close_short_quantity = float(
                    bitget.convert_amount_to_precision(pair, position["size"])
                )
                exchange_close_short_quantity = close_short_quantity * close_short_market_price
                print(
                    f"Place Close Short Market Order: {close_short_quantity} {pair[:-5]} at the price of {close_short_market_price}$ ~{round(exchange_close_short_quantity, 2)}$"
                )
                if configuration['production'] == "True":
                    UtilitiesBot.cancel_order_open(bitget, configuration, pair)
                    time.sleep(int(configuration['delay_coin']))  
                    
                    bitget.place_market_order(pair, "buy", close_short_quantity, reduce=True)
                    if configuration['telegram_on'] == "True":
                        message = MessageTelegram.addMessageComponent(message, f"Place Close Short Market Order: {close_short_quantity} {pair[:-5]} at the price of {close_short_market_price}$ ~{round(exchange_close_short_quantity, 2)}$\n")
                    openPositions -= 1
                    #Ajout du log close short dans la db
                    if configuration['mysql_active'] == "True":
                        mysql_dashboard.log_close_short(exchange_close_short_quantity, coin, close_short_market_price)
                    #Fin de mysql
                    changement=changement+1
                    
            else:
                if configuration['telegram_on'] == "True":
                    message = MessageTelegram.addMessageComponent(message, "On garde :\n")
                    message = MessageTelegram.addMessageComponent(message, "Position: " + str(coin) + " " +str(position["side"]) + " Qte: " + str(position["size"]) + " QteUsd: " + str(position["usd_size"]) + "$ Prix Achat: "+ str(position["open_price"]) + "$ Prix Actuel:"+ str(position["market_price"]) +  "$\n")
        
        else:
            if configuration['debug'] == "True":
                print("No active position for : " + coin)
              
            if ConditionTrade.open_long(row, configuration) and "long" in configuration['type']:
                
                if openPositions < int(configuration['maxOpenPosition']): 
                    long_market_price = float(dfList[coin].iloc[-1]["close"])
                    usdBalance = float(bitget.get_usdt_equity())
                    buyQuantityInUsd = usdBalance * 1/(int(configuration['maxOpenPosition'])-openPositions)
                    buyQuantityInUsd = 0.95 * buyQuantityInUsd 
                        
                    #if openPositions == int(configuration['maxOpenPosition']) - 1:
                    #    buyQuantityInUsd = 0.95 * buyQuantityInUsd
                        
                    long_quantity_in_usd = buyQuantityInUsd * int(configuration['leverage'])
                    long_quantity = float(bitget.convert_amount_to_precision(pair, float(
                        bitget.convert_amount_to_precision(pair, long_quantity_in_usd / long_market_price)
                    )))
                    exchange_long_quantity = long_quantity * long_market_price
                    print(
                        f"Place Open Long Market Order: {long_quantity} {pair[:-5]} at the price of {long_market_price}$ ~{round(exchange_long_quantity, 2)}$"
                    )
                    if configuration['production'] == "True":
                        bitget.place_market_order(pair, "buy", long_quantity, reduce=False)
                        if configuration['telegram_on'] == "True":
                            message = MessageTelegram.addMessageComponent(message, f"Place Open Long Market Order: {long_quantity} {pair[:-5]} at the price of {long_market_price}$ ~{round(exchange_long_quantity, 2)}$\n")
                        
                        #Ajout du log close short dans la db
                        if configuration['mysql_active'] == "True":
                            mysql_dashboard.log_open_long(long_quantity_in_usd, coin, long_market_price)
                        #Fin de mysql

                        if configuration['is_tp'] == "True":
                            message = TakeProfit.put_take_profit(bitget, configuration, message, "long", float(long_quantity), dfList, coin, pair)
                            
                        if configuration['is_sl'] == "True":
                            message = StopLost.put_stop_lost(bitget, configuration, message, "long", float(long_quantity), long_market_price, dfList, coin, pair)
                            
                        changement=changement+1
                else:
                    print("maximum de position ouverte")

            elif ConditionTrade.open_short(row, configuration) and "short" in configuration['type']:
                if openPositions < int(configuration['maxOpenPosition']): 
                    short_market_price = float(dfList[coin].iloc[-1]["close"])
                    usdBalance = float(bitget.get_usdt_equity())
                    buyQuantityInUsd = usdBalance * 1/(int(configuration['maxOpenPosition'])-openPositions)
                     
                    buyQuantityInUsd = 0.95 * buyQuantityInUsd   
                    #if openPositions == int(configuration['maxOpenPosition']) - 1:
                    #    buyQuantityInUsd = 0.95 * buyQuantityInUsd
                        
                    
                    short_quantity_in_usd = buyQuantityInUsd * int(configuration['leverage'])
                    short_quantity = float(bitget.convert_amount_to_precision(pair, float(
                        bitget.convert_amount_to_precision(pair, short_quantity_in_usd / short_market_price)
                    )))
                    exchange_short_quantity = short_quantity * short_market_price
                    print(
                        f"Place Open Short Market Order: {short_quantity} {pair[:-5]} at the price of {short_market_price}$ ~{round(exchange_short_quantity, 2)}$"
                    )
                    if configuration['production'] == "True":
                        bitget.place_market_order(pair, "sell", short_quantity, reduce=False)
                        if configuration['telegram_on'] == "True":
                            message = MessageTelegram.addMessageComponent(message, f"Place Open Short Market Order: {short_quantity} {pair[:-5]} at the price of {short_market_price}$ ~{round(exchange_short_quantity, 2)}$\n")
                        #Ajout du log close short dans la db
                        if configuration['mysql_active'] == "True":
                            mysql_dashboard.log_open_short(short_quantity_in_usd, coin, short_market_price)
                        #Fin de mysql
                
                    
                        if configuration['is_tp'] == "True":
                            message = TakeProfit.put_take_profit(bitget, configuration, message, "short", float(short_quantity), dfList, coin, pair)
                            
                        if configuration['is_sl'] == "True":
                            message = StopLost.put_stop_lost(bitget, configuration, message, "short", float(short_quantity), short_market_price, dfList, coin, pair)
                            
                        changement=changement+1
                
                else:
                    print("maximum de position ouverte")

            
    except Exception as e:
        print("ERROR : "+str(e))
    
        
        

usd_balance = float(bitget.get_usdt_equity())
print("USD balance :", round(usd_balance, 2), configuration['stableCoin'])
#print(totalBalanceInUsd)


#Récupération du solde en usdt
usdAmount = round(usd_balance, 2)

#Ajout du log Solde Wallet dans la db
if configuration['mysql_active'] == "True":
    mysql_dashboard.update_solde(usdAmount)
    



#============================================
#   Bilan et envoie Telegram
#============================================
if configuration['telegram_on'] == "True":
    BilanSolde.get_bilan(configuration, MessageTelegram, telegram_send, message, path+configuration['soldeFile'], usdAmount, configuration['todayJour'], configuration['todayMois'], configuration['todayAnnee'], configuration['todayHeure'], configuration['todayMinutes'], configuration['notifBilanDePerformance'], configuration['notifBilanEvolutionContinue'], float(configuration['totalInvestment']), configuration['alwaysNotifTelegram'], configuration['notifTelegramOnChangeOnly'], changement)
