#=============================
#	 IMPORTS NECESSAIRES
#=============================
from optparse import Values
import sys
path_bot=sys.path[0]+'/'
from constantly import ValueConstant
from numpy import NaN, float64, little_endian
sys.path.append(path_bot+'utilities')
from spot_bitget import SpotBitget
import telegram_send
import ta
import pandas as pd
import time
import ccxt
import datetime
import configparser
import json
#import mysql.connector
from time import sleep
import math
from custom_indicators import CustomIndocators

f = open(sys.path[0]+'/pair_list.json',)
pairJson = json.load(f)
f.close()
pairList_coin = pairJson['bigwill']
#print(pairList_coin)

path=path_bot

print('CCXT Version:', ccxt.__version__)
#===================================
# INITIALISATION DES CONFIGURATIONS
#===================================

config = configparser.ConfigParser()
now = datetime.datetime.now()
config.read(path_bot+'config-bot.cfg')
botname = str(config['PARAMETRES']['botname'])
botnameversion = str(config['PARAMETRES']['botversion'])
print(f"========================\n{botname} v{botnameversion} - "+str(datetime.datetime.now()))
print("Sections recupérées dans le fichier de configuration: "+str(config.sections()))

#=============================
#	AUTHENTIFICATION PART
#=============================
apiKey=str(config['BITGET.AUTHENTIFICATION']['apiKey'])
secret=str(config['BITGET.AUTHENTIFICATION']['secret'])
password=str(config['BITGET.AUTHENTIFICATION']['password'])

bitget = SpotBitget(
		apiKey=apiKey,
		secret=secret,
        password=password,
		EnableRateLimit=True
	)

#=====================
# CONFIGS PAR DEFAULT 
#=====================

timeframe=str(config['STRATEGIE']['timeframe'])
nbOfCandles=int(config['STRATEGIE']['nbOfCandles'])
stableCoin=str(config['PARAMETRES']['stableCoin'])
print("Timeframe utilisé :"+str(timeframe)+" chandelier :"+str(nbOfCandles) + " StableCoin:"+str(stableCoin))



#################################################################
#si besoin d'une connexion mysql
#################################################################

mysql_active=str(config['MYSQL']['mysql_active'])
host_mysql=str(config['MYSQL']['host'])
user_mysql=str(config['MYSQL']['user'])
password_mysql=str(config['MYSQL']['password'])
database_mysql=str(config['MYSQL']['database'])
#ID connexion SQL commenter si pas utilisé
#if bool(mysql_active) == True:
#    mydb = mysql.connector.connect(
#        host=str(host_mysql),
#        user=str(user_mysql),
#        password=str(password_mysql),
#        database=str(database_mysql)
#    )
#    mycursor = mydb.cursor()

#print(mycursor)
#################################################################
#AJOUTER ET REMPLIR CETTE PARTIE AVANT LES INDICATORS VARIABLE
#################################################################

#=============
# INDICATEURS
#=============
aoParam1=int(config['INDICATORS']['aoParam1'])
aoParam2=int(config['INDICATORS']['aoParam2'])
stochWindow=int(config['INDICATORS']['stochWindow'])
willWindow=int(config['INDICATORS']['willWindow'])

#=================
# HYPERPARAMETRES
#=================
maxOpenPosition = int(config['HYPERPARAMETRES']['maxOpenPosition'])
stochOverBought = float(config['HYPERPARAMETRES']['stochOverBought'])
stochOverSold = float(config['HYPERPARAMETRES']['stochOverSold'])
willOverSold = float(config['HYPERPARAMETRES']['willOverSold'])
willOverBought = float(config['HYPERPARAMETRES']['willOverBought'])
TpPct = float(config['HYPERPARAMETRES']['TpPct'])


#TRIX
trixLength = int(config['HYPERPARAMETRES']['trixLength'])
trixSignal = int(config['HYPERPARAMETRES']['trixSignal'])

#=============================
# PARAMETRES DE NOTIFICATIONS
#=============================

notifTelegramOnChangeOnly=str(config['PARAMETRES']['notifTelegramOnChangeOnly'])
alwaysNotifTelegram = str(config['PARAMETRES']['alwaysNotifTelegram'])
notifBilanDePerformance=str(config['PARAMETRES']['notifBilanDePerformance'])
notifBilanEvolutionContinue=str(config['PARAMETRES']['notifBilanEvolutionContinue'])

#====================
# COLLECTE DES PRIX
#====================
usdBalance=bitget.get_balance_of_one_coin_usd(stableCoin)
coinInUsd = bitget.get_all_balance_in_usd(pairList_coin)
sommeCryptos=bitget.sommeCrypto(coinInUsd, stableCoin)
totalBalanceInUsd = usdBalance + sommeCryptos
print("Wallet : "+str(usdBalance)+" "+stableCoin)   
print("Cryptos : "+str(sommeCryptos)+" "+stableCoin+" de Cryptos")  
print("Total : "+str(totalBalanceInUsd)+" "+ stableCoin)   





pairList=[]
for pair in pairList_coin:
    pairList.append(pair+'/'+stableCoin) 
print("************* Pair List *************")
print(pairList)
print("*************************************")

dfList = {}

for pair in pairList:
	#On essaie de récupérer toutes les bougies sur l'API bitget
	try :
		df = bitget.get_last_historical(pair, timeframe, nbOfCandles)
		dfList[pair.replace('/USDT','')] = df
	except :
		#Si on ne parvient à récupérer la paire à la première tentative (parfois l'api bitget est inaccessible) :
		#On attend X seconde(s) et on réessaye avec moins de bougies
		time.sleep(1)
		try :
			df = bitget.get_last_historical(pair, timeframe, nbOfCandles-int(nbOfCandles*0.25))
			dfList[pair.replace('/USDT','')] = df
            
		except :
			time.sleep(2)
			try :
				df = bitget.get_last_historical(pair, timeframe, nbOfCandles-int(nbOfCandles*0.50))
				dfList[pair.replace('/USDT','')] = df
			except :
				time.sleep(3)
				try : 
					df = bitget.get_last_historical(pair, timeframe, nbOfCandles-int(nbOfCandles*0.75))
					dfList[pair.replace('/USDT','')] = df
				except :
					#Si au bout de la 3ème fois ça n'a vraiment pas fonctionné, on abandonne
					try :
						del dfList[pair]
					except :
						pass
					#Si ça ne fonctionne toujours pas, on abandonne cette paire
					telegram_send.send(messages=[f"{botname} : Impossible de récupérer les {nbOfCandles} dernières bougies de {pair} à 3 reprises, donc on n'utilisera pas cette paire durant cette execution."])
					print(f"Impossible de récupérer les 210 dernières bougies de {pair} à 2 reprises, on n'utilisera pas cette paire durant cette execution")
					pass
        

#===========================
# COLLECTE DES INDICATEURS
#===========================

for coin in dfList:
    # -- Drop all columns we do not need --
    dfList[coin].drop(columns=dfList[coin].columns.difference(['open','high','low','close','volume']), inplace=True)

    # -- Indicators, you can edit every value --
    dfList[coin]['AO']= CustomIndocators.awesome_oscillator(dfList[coin], aoParam1, aoParam2) 
    #ta.momentum.awesome_oscillator(dfList[coin]['high'],dfList[coin]['low'],window1=aoParam1,window2=aoParam2, fillna=True)
    
    
    #---------------------------
    # indicateurs de tendance
    #---------------------------
    # EMA
    #EMA 7
    dfList[coin]['EMA7']=CustomIndocators.ema(dfList[coin]['close'], 7)
    #EMA 30
    dfList[coin]['EMA30']=CustomIndocators.ema(dfList[coin]['close'], 30)
    #EMA 150 
    dfList[coin]['EMA150']=CustomIndocators.ema(dfList[coin]['close'], 150)
    #EMA 100
    dfList[coin]['EMA100']=CustomIndocators.ema(dfList[coin]['close'], 100)
    #EMA 200
    dfList[coin]['EMA200']=CustomIndocators.ema(dfList[coin]['close'], 200)
    #EMA 28
    dfList[coin]['EMA28']=CustomIndocators.ema(dfList[coin]['close'], 28)
    #EMA 48
    dfList[coin]['EMA48']=CustomIndocators.ema(dfList[coin]['close'], 48)
    #EMA 50
    dfList[coin]['EMA50']=CustomIndocators.ema(dfList[coin]['close'], 50)
 
    # SMA
    dfList[coin]['sma7']=CustomIndocators.sma(dfList[coin]['close'], 7)
     
    # --- TRIX Indicator
    #dfList[coin]['TRIX'] -- dfList[coin]['TRIX_PCT'] -- dfList[coin]['TRIX_SIGNAL'] -- dfList[coin]['TRIX_HISTO']
    dfList[coin]=CustomIndocators.trixIndicator(dfList[coin], trixLength,trixSignal)
    
    # --- Ichimocu
    #dfList[coin]['SSA'] -- dfList[coin]['SSB'] -- dfList[coin]['kijun'] -- dfList[coin]['tenkan'] -- dfList[coin]['ssa'] -- dfList[coin]['ssb'] -- dfList[coin]['ssa25'] --dfList[coin]['ssb25'] -- dfList[coin]['ssa52'] -- dfList[coin]['ssb52'] - dfList[coin]['close25'] -- dfList[coin]['close1']
    dfList[coin]=CustomIndocators.ichimoku(dfList[coin])
    
    # --- MACD
    #dfList[coin]['macd'] -- dfList[coin]['macd_signal'] -- dfList[coin]['macd_histo']
    dfList[coin]=CustomIndocators.macdIndicator(dfList[coin])
    
    # --- Awesome Oscillator
    dfList[coin]['awesome_oscilllator'] = CustomIndocators.awesome_oscillator(dfList[coin], aoParam1, aoParam2)

    # ADX Attention erreur dans le code de l'indicateur 
    #dfList[coin]['adx'] = CustomIndocators.adx(dfList[coin])

    # Fear and Greed 
    dfList[coin]["fear_greed"] = CustomIndocators.fear_and_greed(dfList[coin]["close"])

    #---------------------------
    # oscillateurs
    #---------------------------
    # --- STOCK_RSI Indicator
    dfList[coin]['STOCH_RSI'] = CustomIndocators.stoch_rsi(dfList[coin], stochWindow)
    
    # --- Stochastic
    #dfList[coin]['stochastic'] -- dfList[coin]['stoch_signal']
    dfList[coin]=CustomIndocators.stochastic(dfList[coin])
    
    # --- William R Indicator
    #dfList[coin]['WillR'] -- dfList[coin]['max_21'] -- dfList[coin]['min_21'] -- dfList[coin]['william_r'] -- dfList[coin]['emaw']
    dfList[coin]=CustomIndocators.william_r(df, willWindow)
    
    # CCI
    #dfList[coin]['hlc3'] -- dfList[coin]['sma_cci'] -- dfList[coin]['mad'] -- dfList[coin]['cci']
    dfList[coin]=CustomIndocators.cci(df)

    # PPO
    #df['ppo'] -- df['ppo_signal'] -- df['ppo_histo']
    dfList[coin]=CustomIndocators.ppo(df)
    
    # PVO
    #df['pvo'] -- df['pvo_signal'] -- df['pvo_histo']
    dfList[coin]=CustomIndocators.pvo(df)
    
    # Aroon
    #dfList[coin]['aroon_up'] -- dfList[coin]['aroon_dow']
    dfList[coin]=CustomIndocators.aroon(df)
    
    #---------------------------
    # volatilité/volume
    #---------------------------
    # Kaufman ou KAMA
    dfList[coin]["kama"] = CustomIndocators.kama(df)

    # ATR
    dfList[coin]["atr"] = CustomIndocators.atr(df, 2)

    # Les bandes de Bollingers
    #dfList[coin]["bol_high"] -- dfList[coin]["bol_low"] -- dfList[coin]["bol_medium"] -- dfList[coin]["bol_gap"]
    # Return binaire 0 ou 1 
    #dfList[coin]["bol_higher"] -- dfList[coin]["bol_lower"] 
    dfList[coin]=CustomIndocators.bollingers(df)


    # Le canal de Donchian
    #dfList[coin]["don_high"] -- dfList[coin]["don_low"] -- dfList[coin]["don_medium"] =
    dfList[coin]=CustomIndocators.donchian(df)


    # Le canal de Keltner 
    #dfList[coin]["kel_high"] -- dfList[coin]["kel_low"] -- dfList[coin]["kel_medium"]
    # Return binaire 0 ou 1 
    #dfList[coin]["kel_higher"] -- dfList[coin]["kel_lower"]
    dfList[coin]=CustomIndocators.keltner(df)
    
    # Chopiness
    dfList[coin]["chop"] = CustomIndocators.chop(dfList[coin]['high'], dfList[coin]['low'], dfList[coin]['close'], window=14)
    
    # ADI Indicator
    dfList[coin]["adi"] = CustomIndocators.adi(df)
   
    # Force Index
    dfList[coin]["fi"] = CustomIndocators.fi_indicator(df)

    #Volume anomaly
    # Récupération des valeurs
    dfList[coin]["volume_anomaly"] = CustomIndocators.volume_anomality(dfList[coin], volume_window=10)
    
    
    




#=======================================
#  CONDITIONS NECESSAIRES POUR L'ACHAT
#=======================================
#Ici on se base sur la stratégie du BigWill
def buyCondition(row, previousRow=None):
    #print("row['AO']:"+str(row['AO']))
    #print("row['STOCH_RSI']:"+str(row['STOCH_RSI']))
    #print("row['WillR']:"+str(row['WillR']))
    #print("row['EMA100']:"+str(row['EMA100']))
    #print("row['EMA200']:"+str(row['EMA200']))
    #print("++++++++++++++++++++++++")
    if (
        row['AO'] >= 0
        and previousRow['AO'] > row['AO']
        and row['WillR'] < willOverSold
        and row['EMA100'] > row['EMA200']
    ):
        return True
    else:
        #A MODIFIER
        return False
        #return True

#=======================================
# CONDITIONS NECESSAIRES POUR LA VENTE
#=======================================
#Ici on se base sur la stratégie du BigWill
def sellCondition(row, previousRow=None):
    
    #print("row['AO']:"+str(row['AO']))
    #print("row['STOCH_RSI']:"+str(row['STOCH_RSI']))
    #print("row['WillR']:"+str(row['WillR']))
    #print("++++++++++++++++++++++++")
    if (
        (row['AO'] < 0
        and row['STOCH_RSI'] > stochOverSold)
        or row['WillR'] > willOverBought
    ):
        return True
    else:
        return False
        #return True

#=========================================================================================
#  PERMET D'AJOUTER DES ELEMENTS DE TEXTE AU MESSAGE FINAL QUI SERA ENVOYE SUR Telegram
#=========================================================================================

message=" "
def addMessageComponent(string):
    global message
    message=message+"\n"+string

positionList=" "
def addPosition(string):
    global positionList
    positionList=positionList+", "+string
        
#===================================
#  RECUPERE LA DATE EXACTE DU JOUR
#===================================

date = datetime.datetime.now()
todayJour=date.day
todayMois=date.month
todayAnnee=date.year
todayHeure=date.hour
todayMinutes=date.minute
separateDate = str(date).split(".")
date = str(separateDate[0])
heureComplète = str(separateDate[1])

addMessageComponent(f"{date}\n{botname} v{botnameversion}")
addMessageComponent("===================\n")

#==============================================================
# RECUPERE LE MONTANT TOTAL D'USD SUR LE SUBACCOUNT SPECIFIE
#==============================================================
coinBalance = bitget.get_all_balance()
#print(coinBalance)
coinInUsd = bitget.get_all_balance_in_usd(pairList_coin)
#print(coinInUsd)
usdBalance = bitget.get_balance_of_one_coin_usd('USDT')
#print(usdBalance)
del coinBalance['USDT']
del coinInUsd['USDT']
totalBalanceInUsd = usdBalance + sum(coinInUsd.values())
#print(totalBalanceInUsd)

coinPositionList = []
for coin in coinInUsd:
    
    if coinInUsd[coin] > 0.05 * totalBalanceInUsd:
        #print("Coin:"+coin + " coinInUsd[coin]:"+str(coinInUsd[coin]))
        coinPositionList.append(coin)
openPositions = len(coinPositionList)


#print(openPositions)
#cette variable nous servira à la fin pour déterminer si on a fait des actions ou pas
#si la variable est toujours à 0 c'est qu'il n'y a eu aucun changement et qu'on ne prévient pas le bot telegram de nous notifier
changement=0

#==================================================
#          EXECUTION PRINCIPALE DU BOT : 
#
# • VERIFIE NOS POSITIONS OUVERTES ET DETERMINE :
#     • Si on doit les fermer
#     • Si on doit les garder
# • VERIFIE SI IL Y A DES OPPORTUNITEES DE POSITIONS A OUVRIR
#
#       Codé par l'Architecte  - 20/03/2022
#==================================================

addMessageComponent("Actions prises par le bot :\n")

# Test si coin dans la liste
def checkIfIsInCoinList(coin):
    retour=False
    for coinInList in pairList_coin:
        if coinInList==coin:
            retour=True
            
    #print(str(retour)+' '+coin)
    return retour

# On vérifie si on a des cryptos actuellement achetés 
for coin in coinPositionList:
    #print(coin)
    if checkIfIsInCoinList(coin) == True:
        #On vérifie si c'est le moment de les vendre ou pas
        #print("++++++++++++++++++++++++")
        #print(coin)
        if sellCondition(dfList[coin].iloc[-2], dfList[coin].iloc[-3]) == True:
            #print("SELL")
            openPositions -= 1
            changement=changement+1
            symbol = coin+'/USDT'
            #print("symbol:"+str(symbol))
            sellPrice = float(bitget.convert_price_to_precision(symbol, bitget.get_bid_ask_price(symbol)['ask'])) 
            #print("buyPrice:"+str(sellPrice))
            cancel = bitget.cancel_all_open_order(symbol)
            #print("cancel="+str(cancel))
            time.sleep(1)
            coinBalance = bitget.get_all_balance()
            del coinBalance['USDT']
                       
            sell = bitget.place_market_order(symbol,'sell',coinBalance[coin],sellPrice)
            
            print("Vente", coinBalance[coin], coin, sell)
            #Ajout du log SELL dans la db
            if bool(mysql_active) == True:
                sql = "INSERT INTO big_will_orderBook (type, amount, symbol, price) VALUES (%s, %s, %s, %s)"
                val = ("1", coinBalance[coin], symbol, sellPrice)
                #mycursor.execute(sql, val)
                #mydb.commit()
            #Fin de mysql
                
            addMessageComponent(f"Vente :\n • {coinBalance[coin]} de {coin}\n • Prix actuel {sellPrice} $\n")
            print("********************************************")
            print("********************************************")
        else:
            print("On garde")
            symbol = coin+'/USDT'
            sellPrice = float(bitget.convert_price_to_precision(symbol, bitget.get_bid_ask_price(symbol)['ask'])) 
            addMessageComponent(f"On garde :\n •  {coin}\n • Prix actuel {sellPrice}\n")
        time.sleep(1)
#On vérifie si on peut acheter
if openPositions < maxOpenPosition:
    for coin in dfList:
        if coin not in coinPositionList:
            #print("++++++++++++++++++++++++")
            #print(coin)
            #On vérifie si il y a des choses intéressantes
            if buyCondition(dfList[coin].iloc[-2], dfList[coin].iloc[-3]) == True and openPositions < maxOpenPosition:
                #print("BUY")
                time.sleep(1)
                changement=changement+1
                usdBalance = bitget.get_balance_of_one_coin_usd('USDT')
                symbol = coin+'/USDT'
                buyPrice = float(bitget.convert_price_to_precision(symbol, bitget.get_bid_ask_price(symbol)['ask'])) 
                tpPrice = float(bitget.convert_price_to_precision(symbol, buyPrice + TpPct * buyPrice))
                buyQuantityInUsd = usdBalance * 1/(maxOpenPosition-openPositions)
                
                if openPositions == maxOpenPosition - 1:
                    buyQuantityInUsd = 0.95 * buyQuantityInUsd

                buyAmount = bitget.convert_amount_to_precision(symbol, buyQuantityInUsd/buyPrice)
                
                buy = bitget.place_market_order(symbol,'buy',buyAmount,buyPrice)
                time.sleep(2)
                print(buy)
                
                #Ajout du log BUY dans la db
                if bool(mysql_active) == True:
                    sql = "INSERT INTO big_will_orderBook (type, amount, symbol, price) VALUES (%s, %s, %s, %s)"
                    val = ("2", buyAmount, symbol, buyPrice)
                    #mycursor.execute(sql, val)
                    #mydb.commit()
                #Fin de mysql
                print("********************************************")
                #print("place TP")
                buyAmount2 = bitget.get_balance_of_one_coin(coin)
                #time.sleep(2)
                #tp = bitget.place_limit_order(symbol,'sell',str(float(buyAmount)/2),tpPrice)
                #try:
                #    tp["id"]
                #except:
                    #time.sleep(2)
                    #buyAmount2 = bitget.get_balance_of_one_coin(coin)
                #    time.sleep(4)
                #    tp = bitget.place_limit_order(symbol,'sell',str(float(buyAmount)/2),tpPrice)
                #    pass
                #print(tp)
                #print("********************************************")
                addMessageComponent(f"Achat :\n • {coin}\n • Prix actuel {buyPrice}\n • Quantité {buyAmount}\n")
                #addMessageComponent(f"Place : {str(float(buyAmount)/2)} {coin} TP à {tpPrice} $\n")
                print("Achat",buyAmount,coin,'at',buyPrice,buy)
                #print("Place",buyAmount,coin,"TP at",tpPrice, tp)

                openPositions += 1
                print("********************************************")
                print("********************************************")


#usdAmount = totalBalanceInUsd
coinBalance = bitget.get_all_balance()
#print(coinBalance)
coinInUsd = bitget.get_all_balance_in_usd(pairList_coin)
#print(coinInUsd)
usdBalance = bitget.get_balance_of_one_coin_usd('USDT')
#print(usdBalance)
del coinBalance['USDT']
del coinInUsd['USDT']
totalBalanceInUsd = usdBalance + sum(coinInUsd.values())
#print(totalBalanceInUsd)

usdAmount = totalBalanceInUsd
#print(usdAmount)

#Ajout du log Solde Wallet dans la db
if bool(mysql_active) == True:
    now_recap = datetime.datetime.now()
    date_recap = now_recap.strftime("%Y-%m-%d")
    #mycursor.execute("INSERT INTO big_will (date, wallet) VALUES (%s, %s)", (date_recap, usdAmount))
    #mydb.commit()
    #mydb.close()

#============================================
#   CODES NECESSAIRES POUR FAIRE DES BILANS
#    DE PERFORMANCES AU FIL DU TEMPS DANS
#       LA NOTIFICATION TELEGRAM FINALE
#        Codé par Mouton - 05/04/2022
#============================================

#usdAmount = bitget.get_balance_of_one_coin_usd('USDT')
soldeMaxAnnee=usdAmount
soldeMaxMois=usdAmount
soldeMaxJour=usdAmount
soldeMinAnnee=usdAmount
soldeMinMois=usdAmount
soldeMinJour=usdAmount

jourMinAnnee=moisMinAnnee=anneeMinAnnee=heureMinAnnee=0
jourMinMois=moisMinMois=anneeMinMois=heureMinMois=0
jourMinJour=moisMinJour=anneeMinJour=heureMinJour=0

jourMaxAnnee=moisMaxAnnee=anneeMaxAnnee=heureMaxAnnee=0
jourMaxMois=moisMaxMois=anneeMaxMois=heureMaxMois=0
jourMaxJour=moisMaxJour=anneeMaxJour=heureMaxJour=0

print(f"Solde du compte => {usdAmount} $")

#Récupérations des anciennes données dans le fichier historiques-soldes.dat
try :
    with open(path_bot+str(config['FICHIER.HISTORIQUE']['soldeFile']), "r") as f:
        for line in f:
            if "#" in line:
                # on saute la ligne
                continue
            try :
                data = line.split()
                jour=int(data[0])
                mois=int(data[1])
                annee=int(data[2])
                heure=int(data[3])
                minutes=int(data[4])
                solde=float(data[5])
                
                
                #permet de trouver le jour où vous avez eu le plus petit solde cette année
                if(soldeMinAnnee>solde and annee==todayAnnee):
                    soldeMinAnnee=solde
                    jourMinAnnee=jour
                    moisMinAnnee=mois
                    anneeMinAnnee=annee
                    heureMinAnnee=heure
                    
                #permet de trouver le jour où vous avez eu le plus petit solde ce mois-ci
                if(soldeMinMois>solde and annee==todayAnnee and mois==todayMois):
                    soldeMinMois=solde
                    jourMinMois=jour
                    moisMinMois=mois
                    anneeMinMois=annee
                    heureMinMois=heure    
                    
                #permet de trouver l'heure où vous avez eu le plus petit solde aujourd'hui
                if(soldeMinJour>solde and annee==todayAnnee and mois==todayMois and jour==todayJour):
                    soldeMinJour=solde
                    jourMinJour=jour
                    moisMinJour=mois
                    anneeMinJour=annee
                    heureMinJour=heure

				#permet de trouver le jour où vous avez eu le plus gros solde cette année
                if(soldeMaxAnnee<solde and annee==todayAnnee):
                    soldeMaxAnnee=solde
                    jourMaxAnnee=jour
                    moisMaxAnnee=mois
                    anneeMaxAnnee=annee
                    heureMaxAnnee=heure
                
                #permet de trouver le jour où vous avez eu le plus gros solde ce mois-ci
                if(soldeMaxMois<solde and annee==todayAnnee and mois==todayMois):
                    soldeMaxMois=solde
                    jourMaxMois=jour
                    moisMaxMois=mois
                    anneeMaxMois=annee
                    heureMaxMois=heure
    
                #permet de trouver l'heure où vous avez eu le plus gros solde aujourd'hui
                if(soldeMaxJour<solde and annee==todayAnnee and mois==todayMois and jour==todayJour):
                    soldeMaxJour=solde
                    jourMaxJour=jour
                    moisMaxJour=mois
                    anneeMaxJour=annee
                    heureMaxJour=heure
      
                #permet de trouver le solde de 6 heures auparavant
                if(todayHeure<=6):
                    if ((todayJour-1==jour) and (todayMois==mois) and (todayAnnee==annee)) :
                        if((24-(6-todayHeure)==heure)):
                            solde6heures=solde
                    elif (todayJour==1 and ((todayMois-1==mois) and (todayAnnee==annee)) or ((todayMois==1) and (todayAnnee-1==annee) and (jour==31))) :
                        if((24-(6-todayHeure)==heure)):
                            solde6heures=solde
                elif ( (todayHeure-6==heure) and (todayJour==jour) and (todayMois==mois) and (todayAnnee==annee) ) :
                    solde6heures=solde
                    
                #permet de trouver le solde de 12 heures auparavant
                if(todayHeure<=12):
                    if ((todayJour-1==jour) and (todayMois==mois) and (todayAnnee==annee)) :
                        if((24-(12-todayHeure)==heure)):
                            solde12heures=solde
                        elif (todayJour==1 and ((todayMois-1==mois) and (todayAnnee==annee)) or ((todayMois==1) and (todayAnnee-1==annee) and (jour==31))) :
                            if((24-(12-todayHeure)==heure)):
                                solde12heures=solde
                elif ( (todayHeure-12==heure) and (todayJour==jour) and (todayMois==mois) and (todayAnnee==annee) ) :
                    solde12heures=solde   
                
                #permet de trouver le solde de 1 jours auparavant
                if(todayJour<=1):
                    if ((todayMois-1==mois) and (todayAnnee==annee)) or ((todayMois==1 and mois==12) and (todayAnnee-1==annee)) :
                        if (mois==1 or mois==3 or mois==5 or mois==7 or mois==8 or mois==10 or mois==12) :
                            if((31-todayJour+1==jour)):
                                solde1jours=solde
                            else :
                                if((30-todayJour+1==jour)):
                                    solde1jours=solde
                elif ( (todayJour-1==jour) and (todayMois==mois) and (todayAnnee==annee) ) :
                    solde1jours=solde 
                    
                #permet de trouver le solde de 3 jours auparavant
                if(todayJour<=3):
                    if ((todayMois-1==mois) and (todayAnnee==annee)) or ((todayMois==1 and mois==12) and (todayAnnee-1==annee)) :
                        if (mois==1 or mois==3 or mois==5 or mois==7 or mois==8 or mois==10 or mois==12) :
                            if((31-todayJour+3==jour)):
                                 solde3jours=solde
                        else :
                            if((30-todayJour+3==jour)):
                                solde3jours=solde
                elif ( (todayJour-3==jour) and (todayMois==mois) and (todayAnnee==annee) ) :
                    solde3jours=solde                
                    
                #permet de trouver le solde de 7 jours auparavant
                if(todayJour<=7):
                    if ((todayMois-1==mois) and (todayAnnee==annee)) or ((todayMois==1 and mois==12) and (todayAnnee-1==annee)) :
                        if (mois==1 or mois==3 or mois==5 or mois==7 or mois==8 or mois==10 or mois==12) :
                            if((31-todayJour+7==jour)):
                                solde7jours=solde
                        else :
                            if((30--todayJour+7==jour)):
                                solde7jours=solde
                elif ( (todayJour-7==jour) and (todayMois==mois) and (todayAnnee==annee) ) :
                    solde7jours=solde
                
                #permet de trouver le solde de 14 jours auparavant
                if(todayJour<=14):
                    if ((todayMois-1==mois) and (todayAnnee==annee)) or ((todayMois==1 and mois==12) and (todayAnnee-1==annee)) :
                        if (mois==1 or mois==3 or mois==5 or mois==14 or mois==8 or mois==10 or mois==12) :
                            if((31-todayJour+14==jour)):
                                solde14jours=solde
                        else :
                            if((30-todayJour+14==jour)):
                                solde14jours=solde
                elif ( (todayJour-14==jour) and (todayMois==mois) and (todayAnnee==annee) ) :
                    solde14jours=solde                    
                    
                #permet de trouver le solde de 1 mois auparavant
                if(todayMois==1 and mois==12 and annee==todayAnnee-1 and todayJour==jour) :
                    solde1mois=solde
                elif(todayMois-1==mois and annee==todayAnnee and todayJour==jour) :
                    solde1mois=solde
                    
                #permet de trouver le solde de 2 mois auparavant
                if(todayMois==1 and mois==11 and annee==todayAnnee-1 and todayJour==jour) :
                    solde2mois=solde
                if(todayMois==2 and mois==12 and annee==todayAnnee-1 and todayJour==jour) :
                    solde2mois=solde
                elif(todayMois-2==mois and annee==todayAnnee and todayJour==jour) :
                    solde2mois=solde
                    
                if 'solde' in locals():
                    soldeLastExec=solde
                else:
                    soldeLastExec=usdAmount    


      
            except :
            	pass
except :
    print(f"WARNING : Le fichier {path_bot+str(config['FICHIER.HISTORIQUE']['soldeFile'])} est introuvable, il va être créé.")

#==================================================
#  Enregistrement du solde dans le fichier .dat
#==================================================

todaySolde=usdAmount
with open(path_bot+str(config['FICHIER.HISTORIQUE']['soldeFile']), "a") as f:
    f.write(f"{todayJour} {todayMois} {todayAnnee} {todayHeure} {todayMinutes} {todaySolde} \n")
    
    
#=======================================================
#  Affiche le bilan de perf dans le message telegram
#=======================================================

if notifBilanDePerformance=="true" :
    addMessageComponent("\n===================\n")
    addMessageComponent("Bilan de performance :")
    if 'soldeMaxJour' in locals():
        soldeMaxJour=round(soldeMaxJour,3)
        addMessageComponent(f" - Best solde aujourd'hui : {soldeMaxJour}$ à {heureMaxJour}h")
    if 'soldeMaxMois' in locals():
        soldeMaxMois=round(soldeMaxMois,3)
        addMessageComponent(f" - Best solde ce mois-ci : {soldeMaxMois}$ le {jourMaxMois}/{moisMaxMois} à {heureMaxMois}h")
    if 'soldeMaxAnnee' in locals():
        soldeMaxAnnee=round(soldeMaxAnnee,3)
        addMessageComponent(f" - Best solde cette année : {soldeMaxAnnee}$ le {jourMaxAnnee}/{moisMaxAnnee}/{anneeMaxAnnee} à {heureMaxAnnee}h")
        
    addMessageComponent(" ")

    if 'soldeMinJour' in locals():
        soldeMinJour=round(soldeMinJour,3)
        addMessageComponent(f" - Pire solde aujourd'hui : {soldeMinJour}$ à {heureMinJour}h")
    if 'soldeMinMois' in locals():
        soldeMinMois=round(soldeMinMois,3)
        addMessageComponent(f" - Pire solde ce mois-ci : {soldeMinMois}$ le {jourMinMois}/{moisMinMois} à {heureMinMois}h")
    if 'soldeMinAnnee' in locals():
        soldeMinAnnee=round(soldeMinAnnee,3)
        addMessageComponent(f" - Pire solde cette année : {soldeMinAnnee}$ le {jourMinAnnee}/{moisMinMois}/{anneeMinAnnee} à {heureMinAnnee}h")


#=================================================================
#  Affiche le bilan d'évolution continue dans le message telegram
#=================================================================

if notifBilanEvolutionContinue=="true" :
    addMessageComponent("\n===================\n")
    addMessageComponent("Bilan d'évolution continue :")
    if 'soldeLastExec' in locals():
        bonus=100*(todaySolde-soldeLastExec)/soldeLastExec 
        gain=bonus/100*soldeLastExec
        bonus=round(bonus,3)
        gain=round(gain,5)
        soldeLastExecRounded=round(soldeLastExec,3)
        if gain<0 :
            addMessageComponent(f" - Dernière execution du bot : {bonus}% ({soldeLastExecRounded}$ {gain}$)")
        else :
            addMessageComponent(f" - Dernière execution du bot : +{bonus}% ({soldeLastExecRounded}$ +{gain}$)")
    if 'solde6heures' in locals():
        bonus=100*(todaySolde-solde6heures)/solde6heures 
        gain=round(bonus/100*todaySolde,2)
        bonus=round(bonus,3)
        gain=round(gain,5)
        solde6heures=round(solde6heures,3)
        if gain<0 :
            addMessageComponent(f" - il y a 6h : {bonus}% ({solde6heures}$ {gain}$)")
        else :
            addMessageComponent(f" - il y a 6h : +{bonus}% ({solde6heures}$ +{gain}$)")
    if 'solde12heures' in locals():
        bonus=100*(todaySolde-solde12heures)/solde12heures 
        gain=round(bonus/100*todaySolde,2)
        bonus=round(bonus,3)
        gain=round(gain,5)
        solde12heures=round(solde12heures,3)
        if gain<0 :
            addMessageComponent(f" - il y a 12h : {bonus}% ({solde12heures}${gain}$)")
        else :
            addMessageComponent(f" - il y a 12h : +{bonus}% ({solde12heures}$ +{gain}$)")
    if 'solde1jours' in locals():
        bonus=100*(todaySolde-solde1jours)/solde1jours
        gain=round(bonus/100*todaySolde,2)
        bonus=round(bonus,3)
        gain=round(gain,5)
        solde1jours=round(solde1jours,5)
        if gain<0 :
            addMessageComponent(f" - il y a 1j : {bonus}% ({solde1jours}$ {gain}$)")
        else :
            addMessageComponent(f" - il y a 1j : +{bonus}% ({solde1jours}$ +{gain}$)")
    if 'solde3jours' in locals():
        bonus=100*(todaySolde-solde3jours)/solde3jours
        gain=round(bonus/100*todaySolde,2)
        bonus=round(bonus,3)
        gain=round(gain,5)
        solde3jours=round(solde3jours,3)
        if gain<0 :
            addMessageComponent(f" - il y a 3j : {bonus}% ({solde3jours}$ {gain}$)")
        else :
            addMessageComponent(f" - il y a 3j : +{bonus}% ({solde3jours}$ +{gain}$)")
    if 'solde7jours' in locals():
        bonus=100*(todaySolde-solde7jours)/solde7jours
        gain=round(bonus/100*todaySolde,2)
        bonus=round(bonus,3)
        gain=round(gain,5)
        solde7jours=round(solde7jours,3)
        if gain<0 :
            addMessageComponent(f" - il y a 7j : {bonus}% ({solde7jours}$ {gain}$)")
        else :
            addMessageComponent(f" - il y a 7j : +{bonus}% ({solde7jours}$ +{gain}$)")
    if 'solde14jours' in locals():
        bonus=100*(todaySolde-solde14jours)/solde14jours
        gain=round(bonus/100*todaySolde,2)
        bonus=round(bonus,3)
        gain=round(gain,5)
        solde14jours=round(solde14jours,3)
        if gain<0 :
            addMessageComponent(f" - il y a 14j : {bonus}% ({solde14jours}$ {gain}$)")
        else :
            addMessageComponent(f" - il y a 14j : +{bonus}% ({solde14jours}$ +{gain}$)")
    if 'solde1mois' in locals():
        bonus=100*(todaySolde-solde1mois)/solde1mois
        gain=round(bonus/100*todaySolde,2)
        bonus=round(bonus,3)
        gain=round(gain,5)
        solde1mois=round(solde1mois,3)
        if gain<0 :
            addMessageComponent(f" - il y a 1 mois : {bonus}% ({solde1mois}$ {gain}$)")
        else :
            addMessageComponent(f" - il y a 1 mois : +{bonus}% ({solde1mois}$ +{gain}$)")
    if 'solde2mois' in locals():
        bonus=100*(todaySolde-solde2mois)/solde2mois
        gain=round(bonus/100*todaySolde,2)
        bonus=round(bonus,3)
        gain=round(gain,5)
        solde2mois=round(solde2mois,3)
        if gain<0 :
            addMessageComponent(f" - il y a 2 mois : {bonus}% ({solde2mois}$ {gain}$)")
        else :
            addMessageComponent(f" - il y a 2 mois : +{bonus}% ({solde2mois}$ +{gain}$)")

totalInvestment = float(config['SOLDE']['totalInvestment'])
bonus=100*(todaySolde-totalInvestment)/totalInvestment
gain=round((bonus/100)*totalInvestment,3)
bonus=round(bonus,3)
totalInvestment=round(totalInvestment,5)
addMessageComponent("\n===================\n")
addMessageComponent(f"INVESTISSEMENT INITIAL => {totalInvestment}$")
if gain<0 :
    addMessageComponent(f"PERTE TOTAL => {gain} $ ({bonus}%)\n")
else :
    addMessageComponent(f"GAIN TOTAL => +{gain} $ (+{bonus}%)\n")
addMessageComponent(f"SOLDE TOTAL => {usdAmount}$")
addMessageComponent(f"N'hésitez pas à me soutenir pour le travail du bot :\n • Adresse BTC : 3BkDUUjguk1aj2oo8QyN3CnyaLwuoY4ZBy\n • Adresse ETH (Réseau ERC20) : 0x5c2eabcb75b6138bdfe39fd9a0dae0716c6426bc\n • Adresse SOL : 2jdYFuHMGzpc7njdaFjMEeFaXb3dhWcZDf6zhtGvwPLJ\n")

message = message.replace(' , ',' ')
message = message.replace('-USDT','')

#======================================================
#  Se base sur les configurations pour déterminer s'il  
#  faut vous envoyer une notification telegram ou non
#======================================================


#Si on a activé de toujours recevoir la notification telegram
if alwaysNotifTelegram=='true':
    telegram_send.send(messages=[f"{message}"])
elif notifTelegramOnChangeOnly=='true' and changement>0 :
    telegram_send.send(messages=[f"{message}"])
else :
    print("Aucune information n'a été envoyé à Telegram")
    
print("...................................................")
print("...................................................")