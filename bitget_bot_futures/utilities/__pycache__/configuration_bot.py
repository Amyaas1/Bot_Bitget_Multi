import configparser
import datetime

class ConfigBot():
    def get_var_config_bot(path_bot):
        #===================================
        # INITIALISATION DES CONFIGURATIONS
        #===================================

        config = configparser.ConfigParser()
        now = datetime.datetime.now()
        config.read(path_bot+'config-bot.cfg')
        botname = str(config['PARAMETRES']['botname'])
        botnameversion = str(config['PARAMETRES']['botversion'])
        totalInvestment = float(config['SOLDE']['totalInvestment'])
        print(f"========================\n{botname} v{botnameversion} - "+str(datetime.datetime.now()))
        print("Sections recupérées dans le fichier de configuration: "+str(config.sections()))
        
        configutation = {}
        #=====================
        # CONFIGS PAR DEFAULT 
        #=====================
        timeframe=str(config['STRATEGIE']['timeframe'])
        nbOfCandles=int(config['STRATEGIE']['nbOfCandles'])
        stableCoin=str(config['PARAMETRES']['stableCoin'])
        production = bool(config['PARAMETRES']['production'])
        leverage = float(config['STRATEGIE']['leverage'])
        delay_coin= int(config['PARAMETRES']['delay_coin'])

        is_tp = str(config['STRATEGIE']['is_tp'])
        nb_tp = int(config['STRATEGIE']['nb_tp'])
        tp_1 = str(config['STRATEGIE']['tp_1'])
        tp_2 = str(config['STRATEGIE']['tp_2'])

        print("Timeframe utilisé :"+str(timeframe)+" chandelier :"+str(nbOfCandles) + " StableCoin:"+str(stableCoin) + " Leverage:" + str(leverage))


        #=============================
        # PARAMETRES DE NOTIFICATIONS
        #=============================

        notifTelegramOnChangeOnly=str(config['PARAMETRES']['notifTelegramOnChangeOnly'])
        alwaysNotifTelegram = str(config['PARAMETRES']['alwaysNotifTelegram'])
        notifBilanDePerformance=str(config['PARAMETRES']['notifBilanDePerformance'])
        notifBilanEvolutionContinue=str(config['PARAMETRES']['notifBilanEvolutionContinue'])

        #=================
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
        #	AUTHENTIFICATION PART
        #=============================
        apiKey=str(config['BITGET.AUTHENTIFICATION']['apiKey'])
        secret=str(config['BITGET.AUTHENTIFICATION']['secret'])
        password=str(config['BITGET.AUTHENTIFICATION']['password'])
        
        #################################################################
        #si besoin d'une connexion mysql
        #################################################################

        mysql_active=str(config['MYSQL']['mysql_active'])
        host_mysql=str(config['MYSQL']['host'])
        user_mysql=str(config['MYSQL']['user'])
        password_mysql=str(config['MYSQL']['password'])
        database_mysql=str(config['MYSQL']['database'])
        
        
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