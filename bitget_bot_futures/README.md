# Bot_Bitget_Multi
Bot multi crypto - multi stratégies sur les futures de bitget

# Installation
```
git clone https://github.com/telecom4all/Bot_Bitget_Multi.git
cd bitget_bot_futures
```

# Utilisation d'un environnement virtuel
```
python3 -m venv .venv
source .venv/bin/activate
deactivate
```

# Installation des dépendances
```
pip install -r requirements.txt
```

# Exécution du bot
```
python bitget_bot_futures.py
```

# Exécution du bot toutes les heures
## Avec un environnement virtuel
Modifier ces 2 lignes dans le fichier start_bot.py avec votre path
```
source /path/.venv/bin/activate
python3 /path/bitget_bot_futures.py
```
Rajouter dans le crontab cette ligne
```
0 * * * * bash /path/start_bot.sh >> /path/bitget_bot_futures.log
```
## Sans environnement virtuel
Rajouter dans le crontab cette ligne
```
0 * * * * bash /path/bitget_bot_futures.py >> /path/bitget_bot_futures.log
```

# Configuration du bot
Tout se passe dans le fichier config-bot.cfg
```
[BITGET.AUTHENTIFICATION]
#indiquez ici vos clés API et password de bitget
apiKey =
secret =
password =

[SOLDE]
#Indiquez ici combien vous avez mis dUSD sur votre compte de votre poche au total
#Pensez à mettre à jour la somme lorsque vous avez ajouté à nouveau de largent
#Attention, indiquez le montant avec des . et surtout pas des ,
totalInvestment=16.0

[MYSQL]
#activé-desactivé
mysql_active=True
#hote
Mysqlhost=localhost
#user
Mysqluser=
#password
Mysqlpassword=
#base de données
Mysqldatabase=

[PARAMETRES]
#les paramètres généraux du bot
#nom du bot
botname=Bitget_Bot_futures_Multi
#bot version
botversion=1
#stable Coin
stableCoin=USDT
#production ou test
production=True
#debug
debug=True
#debug detail
debug_detail=True
#la strat active
#dans le but dans le futur de pouvoir rajouter des strat différentes
strat_active = BOLLINGER
#mettre le même nom qua cette ligne en bas du fichier
name_strat=BOLLINGER
#delai req coin sec
#pour éviter de se faire bloquer par lexchange car trop de requête
delay_coin = 1
#Si vous voulez recevoir une notif telegram à chaque exécution du bot,
telegram_on=True
#Autrement, vous ne recevrez une notification que si le bot fait un changement ou quil est 8h, 12h, 18h, 0h
alwaysNotifTelegram=true
#Envoie une notification uniquement lorsque le bot vend ou achète
#Autrement, vous ne recevrez une notification que si le bot fait un changement ou quil est 8h, 12h, 18h, 0h
notifTelegramOnChangeOnly=true
#Affiche les meilleures et pires performances dans la notif Telegram
notifBilanDePerformance=true
#Affiche la variation du solde heure par heure dans la notif Telegram
notifBilanEvolutionContinue=true

[STRATEGIE]
#les paramètre généraux des stratégies
timeframe = 1h
nbOfCandles = 1000
leverage = 1
is_tp = True
#si False le bot ne met pas de tp
nb_tp = 1
#1 ou 2
#(1 = 1 tp a 50% de la quantité total du trade)
#(2 = 1 tp a 33% de la quantité total du trade et 1 tp a 66% de la quantité total du trade)
tp_1=0.7
#pourcentage du tp1 (ici 7%)
tp_2=0.15
#pourcentage du tp2 (ici 15%)
is_sl=True
#si False pas de stop lost
sl=-0.10
#pourcentage du SL (ici 10%)
maxOpenPosition = 4
#Maximum de position ouverte en même temps sur votre compte
#soit long, soit short soit both
type = both
#both/long/short
#(long = que des trade en long)
#(short = que des trade en short)
#(both = trade short et long)

[FICHIER.HISTORIQUE]
#indiquer le chemin où se trouve le fichier historiques-soldes.dat
#example :
soldeFile=historiques-soldes.dat

[STRAT.BOLLINGER]
#stra bollinger band et les parameters
name_strat=BOLLINGER
bol_window=100
bol_std=2.25
min_bol_spread=0
long_ma_window=500
```

# Dans le futur on pourra rajouter des strat
Par exemple :
```
[STRAT.AUTRESTRAT]
#autre strat et les paramètres
name_strat=AUTRESTRAT
val1=100
val2=2.25
```

# Soutien
Ce code est disponible pour tous si vous voulez me "soutenir :-)" voici un lien d'affiliation Bitget : https://partner.bitget.com/bg/85MZE2

ou en cryptos :
- BTC --> 1CetuWt9PuppZ338MzBzQZSvtMW3NnpjMr
- ETH (Réseau ERC20) --> 0x18f71abd7c2ee05eab7292d8f34177e7a1b62236
- MATIC (Réseau Polygon) --> 0x18f71abd7c2ee05eab7292d8f34177e7a1b62236
- BNB (Réseau BSC BEP20) --> 0x18f71abd7c2ee05eab7292d8f34177e7a1b62236
- SOL --> AsLvBCG1fpmpaueTYBmU5JN5QKVkt9a1dLR44BAGUZbV

# Remerciements
Merci à titouannwtt pour son code duquel je me suis grandement inspiré !! : https://github.com/titouannwtt/bot-trading-advanced

Si vous voulez le soutenir :
- lien affiliation Binance : https://www.binance.me/fr/activity/referral/offers/claim?ref=CPA_00C08H2X8E
- dons cryptos :
  - Adresse BTC : 3GYhBgZMfgzqjYhVhc2w53oMcvZb4jfGfL
  - Adresse ETH (Réseau ERC20) : 0x43fC6F9B8b1CfBd83b52a1FD1de510effe0A49a7
  - Adresse SOL : 5QKaHfJWxAZ6sbU5QMb2e14yAAZ45iBH91SBgnheK26v