import os
import sys
sys.path.append(sys.path[0]+'/utilities')
from spot_bitget import SpotBitget
import json
import mysql.connector
from datetime import datetime
import configparser
from numpy import *
 
config = configparser.ConfigParser()
now = datetime.now()

config.read(sys.path[0]+'/config-bot.cfg')

stableCoin=str(config['PARAMETRES']['stableCoin'])
botname = str(config['PARAMETRES']['botname'])
botnameversion = str(config['PARAMETRES']['botversion'])
print(f"========================\nRécap pour le bot : {botname} v{botnameversion} - "+str(datetime.now()) + ' Fiat: ' + str(stableCoin))
print("Sections recupérées dans le fichier de configuration: "+str(config.sections()))



#config Mysql
host_mysql=str(config['MYSQL']['host'])
user_mysql=str(config['MYSQL']['user'])
password_mysql=str(config['MYSQL']['password'])
database_mysql=str(config['MYSQL']['database'])



now = datetime.now()
date = now.strftime("%Y-%m-%d")

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


f = open(sys.path[0]+'/pair_list.json',)
pairJson = json.load(f)
f.close()
pairList_coin = pairJson['bigwill']


pairList=[]
for pair in pairList_coin:
    pairList.append(pair+'/'+stableCoin) 
print("************* Pair List *************")
print(pairList)
print("*************************************")


#usdAmount = totalBalanceInUsd
coinBalance = bitget.get_all_balance()
#print(coinBalance)
coinInUsd = bitget.get_all_balance_in_usd(pairList_coin)
#print(coinInUsd)
usdBalance = bitget.get_balance_of_one_coin_usd('USDT')
#print(usdBalance)
del coinBalance['USDT']
del coinInUsd['USDT']
somme = bitget.sommeCrypto(coinInUsd, stableCoin)

totalBalanceInUsd = usdBalance + somme
print(totalBalanceInUsd)

mydb = mysql.connector.connect(
        host=str(host_mysql),
        user=str(user_mysql),
        password=str(password_mysql),
        database=str(database_mysql)
    )
mycursor = mydb.cursor()

mycursor.execute("INSERT INTO big_will (date, wallet) VALUES (%s, %s)", (date, totalBalanceInUsd))
mydb.commit()
mydb.close()
