#=============================
#	 IMPORTS NECESSAIRES
#=============================
from optparse import Values
import sys
path_bot=sys.path[0]+'/'
#from numpy import NaN, float64, little_endian
sys.path.append(path_bot+'utilities')
from perp_bitget import PerpBitget
import telegram_send
import ta
import pandas as pd
import time
import ccxt
import datetime
import configparser
import json

from time import sleep
import math
#from custom_indicators import get_n_columns
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

bitget = PerpBitget(
		apiKey=apiKey,
		secret=secret,
        password=password
	)

#=====================
# CONFIGS PAR DEFAULT 
#=====================

timeframe=str(config['STRATEGIE']['timeframe'])
nbOfCandles=int(config['STRATEGIE']['nbOfCandles'])
stableCoin=str(config['PARAMETRES']['stableCoin'])
production = bool(config['PARAMETRES']['production'])
leverage = float(config['STRATEGIE']['leverage'])
delay_coin= int(config['PARAMETRES']['delay_coin'])
print("Timeframe utilisé :"+str(timeframe)+" chandelier :"+str(nbOfCandles) + " StableCoin:"+str(stableCoin) + " Leverage:" + str(leverage))




# HYPERPARAMETRES
#=================
type_config = str(config['HYPERPARAMETRES']['type'])

type = []
if type_config == "both":
    type = ["long", "short"]
if type_config == "long":
    type = ["long"]
if type_config == "short":
    type = ["short"]


bol_window = int(config['HYPERPARAMETRES']['bol_window'])
bol_std = float(config['HYPERPARAMETRES']['bol_std'])
min_bol_spread = int(config['HYPERPARAMETRES']['min_bol_spread'])
long_ma_window = int(config['HYPERPARAMETRES']['long_ma_window'])
maxOpenPosition = int(config['HYPERPARAMETRES']['maxOpenPosition'])

#=============================
# PARAMETRES DE NOTIFICATIONS
#=============================

notifTelegramOnChangeOnly=str(config['PARAMETRES']['notifTelegramOnChangeOnly'])
alwaysNotifTelegram = str(config['PARAMETRES']['alwaysNotifTelegram'])
notifBilanDePerformance=str(config['PARAMETRES']['notifBilanDePerformance'])
notifBilanEvolutionContinue=str(config['PARAMETRES']['notifBilanEvolutionContinue'])

#====================
# List Token
#====================
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
		
		df = bitget.get_more_last_historical_async(pair+":"+stableCoin, timeframe, nbOfCandles)
		dfList[pair.replace('/USDT','')] = df
	except :
		#Si on ne parvient à récupérer la paire à la première tentative (parfois l'api bitget est inaccessible) :
		#On attend X seconde(s) et on réessaye avec moins de bougies
		time.sleep(delay_coin)
		try :
			df = bitget.get_more_last_historical_async(pair+":"+stableCoin, timeframe, nbOfCandles-int(nbOfCandles*0.25))
			dfList[pair.replace('/USDT','')] = df
            
		except :
			time.sleep(delay_coin+1)
			try :
				df = bitget.get_more_last_historical_async(pair+":"+stableCoin, timeframe, nbOfCandles-int(nbOfCandles*0.50))
        
    
				dfList[pair.replace('/USDT','')] = df
			except :
				time.sleep(delay_coin+2)
				try : 
					df = bitget.get_more_last_historical_async(pair+":"+stableCoin, timeframe, nbOfCandles-int(nbOfCandles*0.75))
					dfList[pair.replace('/USDT','')] = df
				except :
					#Si au bout de la 3ème fois ça n'a vraiment pas fonctionné, on abandonne
					try :
						del dfList[pair+":"+stableCoin]
					except :
						pass
                    #Si ça ne fonctionne toujours pas, on abandonne cette paire
					pair_message = pair+":"+stableCoin
					telegram_send.send(messages=[f"{botname} : Impossible de récupérer les {nbOfCandles} dernières bougies de {pair_message} à 3 reprises, donc on n'utilisera pas cette paire durant cette execution."])
					print(f"Impossible de récupérer les 210 dernières bougies de {pair_message} à 2 reprises, on n'utilisera pas cette paire durant cette execution")
					pass
        

#===========================
# COLLECTE DES INDICATEURS
#===========================
print("COLLECTE DES INDICATEURS")
for coin in dfList:
    
    # -- Drop all columns we do not need --
    dfList[coin].drop(columns=dfList[coin].columns.difference(['open','high','low','close','volume']), inplace=True)

    dfList[coin].drop(columns=dfList[coin].columns.difference(['open','high','low','close','volume']), inplace=True)
    bol_band = ta.volatility.BollingerBands(close=dfList[coin]["close"], window=bol_window, window_dev=bol_std)
    dfList[coin]["lower_band"] = bol_band.bollinger_lband()
    dfList[coin]["higher_band"] = bol_band.bollinger_hband()
    dfList[coin]["ma_band"] = bol_band.bollinger_mavg()

    dfList[coin]['long_ma'] = ta.trend.sma_indicator(close=dfList[coin]['close'], window=long_ma_window)

    dfList[coin] = CustomIndocators.get_n_columns(dfList[coin], ["ma_band", "lower_band", "higher_band", "close"], 1)


#====================
# CONDITION LONG - SHORT
#====================
def open_long(row):
    if (
        row['n1_close'] < row['n1_higher_band'] 
        and (row['close'] > row['higher_band']) 
        and ((row['n1_higher_band'] - row['n1_lower_band']) / row['n1_lower_band'] > min_bol_spread)
        (row['close'] > row['long_ma'])
    ):
        return True
    else:
        return False

def close_long(row):
    if (row['close'] < row['ma_band']):
        return True
    else:
        return False

def open_short(row):
    if (
        row['n1_close'] > row['n1_lower_band'] 
        and (row['close'] < row['lower_band']) 
        and ((row['n1_higher_band'] - row['n1_lower_band']) / row['n1_lower_band'] > min_bol_spread)
        and (row['close'] < row['long_ma'])        
    ):
        return True
    else:
        return False

def close_short(row):
    if (row['close'] > row['ma_band']):
        return True
    else:
        return False




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
usd_balance = float(bitget.get_usdt_equity())
print("USD balance :", round(usd_balance, 2), stableCoin)



#cette variable nous servira à la fin pour déterminer si on a fait des actions ou pas
#si la variable est toujours à 0 c'est qu'il n'y a eu aucun changement et qu'on ne prévient pas le bot telegram de nous notifier
changement=0

#==================================================
#          EXECUTION PRINCIPALE DU BOT : 
#
#     
#==================================================

addMessageComponent("Actions prises par le bot :\n")



#===================================
#  On execute la strat sur les différentes cryptos
#===================================
def get_open_position():
    coinPositionList = []

    try :
        coinPositionList = bitget.get_open_position()
        time.sleep(delay_coin)
        #for t in coinPositionList:
        #    print(t)
    except Exception as e:
        print("ERROR : "+str(e))
    
    openPositions = len(coinPositionList)
    return openPositions

 
for coin in dfList:
    positions_data = bitget.get_open_position() 

    try :
        openPositions = get_open_position() 
        
        pair=coin+"/"+stableCoin+":"+stableCoin
        position = [
                    {"side": d["side"], "size": d["contractSize"], "market_price":d["info"]["marketPrice"], "usd_size": float(d["contractSize"]) * float(d["info"]["marketPrice"]), "open_price": d["entryPrice"]}
                    for d in positions_data if d["symbol"] == pair
                    ]
        
        row = dfList[coin].iloc[-2]
        
        if len(position) > 0:
            position = position[0]
            
            print(f"Current position : {position}")
            if position["side"] == "long" and close_long(row):
                close_long_market_price = float(dfList[coin].iloc[-1]["close"])
                close_long_quantity = float(
                    bitget.convert_amount_to_precision(pair, position["size"])
                )
                exchange_close_long_quantity = close_long_quantity * close_long_market_price
                print(
                    f"Place Close Long Market Order: {close_long_quantity} {pair[:-5]} at the price of {close_long_market_price}$ ~{round(exchange_close_long_quantity, 2)}$"
                )
                if production:
                    bitget.place_market_order(pair, "sell", close_long_quantity, reduce=True)
                    addMessageComponent(f"Place Close Long Market Order: {close_long_quantity} {pair[:-5]} at the price of {close_long_market_price}$ ~{round(exchange_close_long_quantity, 2)}$\n")
                    openPositions -= 1
                    
                    changement=changement+1

            elif position["side"] == "short" and close_short(row):
                close_short_market_price = float(dfList[coin].iloc[-1]["close"])
                close_short_quantity = float(
                    bitget.convert_amount_to_precision(pair, position["size"])
                )
                exchange_close_short_quantity = close_short_quantity * close_short_market_price
                print(
                    f"Place Close Short Market Order: {close_short_quantity} {pair[:-5]} at the price of {close_short_market_price}$ ~{round(exchange_close_short_quantity, 2)}$"
                )
                if production:
                    bitget.place_market_order(pair, "buy", close_short_quantity, reduce=True)
                    addMessageComponent(f"Place Close Short Market Order: {close_short_quantity} {pair[:-5]} at the price of {close_short_market_price}$ ~{round(exchange_close_short_quantity, 2)}$\n")
                    openPositions -= 1
                    
                    changement=changement+1
        
        else:
            print("No active position for : " + coin)
            if openPositions < maxOpenPosition:
                if open_long(row) and "long" in type:
                    
                    long_market_price = float(dfList[coin].iloc[-1]["close"])
                    usdBalance = float(bitget.get_usdt_equity())
                    buyQuantityInUsd = usdBalance * 1/(maxOpenPosition-openPositions)
                        
                    if openPositions == maxOpenPosition - 1:
                        buyQuantityInUsd = 0.95 * buyQuantityInUsd
                        
                    long_quantity_in_usd = buyQuantityInUsd * leverage
                    long_quantity = float(bitget.convert_amount_to_precision(pair, float(
                        bitget.convert_amount_to_precision(pair, long_quantity_in_usd / long_market_price)
                    )))
                    exchange_long_quantity = long_quantity * long_market_price
                    print(
                        f"Place Open Long Market Order: {long_quantity} {pair[:-5]} at the price of {long_market_price}$ ~{round(exchange_long_quantity, 2)}$"
                    )
                    if production:
                        bitget.place_market_order(pair, "buy", long_quantity, reduce=False)
                        addMessageComponent(f"Place Open Long Market Order: {long_quantity} {pair[:-5]} at the price of {long_market_price}$ ~{round(exchange_long_quantity, 2)}$\n")
                    
                        
                        changement=changement+1

                elif open_short(row) and "short" in type:
                    
                    short_market_price = float(dfList[coin].iloc[-1]["close"])
                    usdBalance = float(bitget.get_usdt_equity())
                    buyQuantityInUsd = usdBalance * 1/(maxOpenPosition-openPositions)
                        
                    if openPositions == maxOpenPosition - 1:
                        buyQuantityInUsd = 0.95 * buyQuantityInUsd
                        
                    
                    short_quantity_in_usd = buyQuantityInUsd * leverage
                    short_quantity = float(bitget.convert_amount_to_precision(pair, float(
                        bitget.convert_amount_to_precision(pair, short_quantity_in_usd / short_market_price)
                    )))
                    exchange_short_quantity = short_quantity * short_market_price
                    print(
                        f"Place Open Short Market Order: {short_quantity} {pair[:-5]} at the price of {short_market_price}$ ~{round(exchange_short_quantity, 2)}$"
                    )
                    if production:
                        bitget.place_market_order(pair, "sell", short_quantity, reduce=False)
                        addMessageComponent(f"Place Open Short Market Order: {short_quantity} {pair[:-5]} at the price of {short_market_price}$ ~{round(exchange_short_quantity, 2)}$\n")
                    
                        
                        changement=changement+1

            else:
                print("maximum de position ouverte")
    except Exception as e:
        print("ERROR : "+str(e))
    
        
        

usd_balance = float(bitget.get_usdt_equity())
print("USD balance :", round(usd_balance, 2), stableCoin)


usdAmount = round(usd_balance, 2)



#============================================
#   CODES NECESSAIRES POUR FAIRE DES BILANS
#    DE PERFORMANCES AU FIL DU TEMPS DANS
#   
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