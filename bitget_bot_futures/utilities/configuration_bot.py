import json
import configparser
import datetime

class ConfigBot():
    def get_var_config_bot(path_bot):
        # Initialisation de la variable de retour
        config_data = {}
        
        # Lecture du fichier de configuration
        config = configparser.ConfigParser()
        now = datetime.datetime.now()
        config.read(path_bot+'config-bot.cfg')
        
        # Récupération des sections du fichier de configuration
        sections = config.sections()
        config_data['sections'] = sections
        
        # Récupération des paramètres généraux
        botname = str(config['PARAMETRES']['botname'])
        botnameversion = str(config['PARAMETRES']['botversion'])
        totalInvestment = str(config['SOLDE']['totalInvestment'])
        stableCoin = str(config['PARAMETRES']['stableCoin'])
        production = str(config['PARAMETRES']['production'])
        leverage = str(config['STRATEGIE']['leverage'])
        delay_coin = str(config['PARAMETRES']['delay_coin'])
        soldeFile = str(config['FICHIER.HISTORIQUE']['soldeFile'])
        strat_active = str(config['PARAMETRES']['strat_active'])
        debug = str(config['PARAMETRES']['debug'])
        debug_detail = str(config['PARAMETRES']['debug_detail'])
        
        
        # Mise à jour de la variable de retour
        config_data.update({
            'botname': botname,
            'botnameversion': botnameversion,
            'totalInvestment': totalInvestment,
            'stableCoin': stableCoin,
            'production': production,
            'leverage': leverage,
            'delay_coin': delay_coin,
            'soldeFile': soldeFile,
            'strat_active':strat_active,
            'debug': debug,
            'debug_detail': debug_detail
        })
        
        
        # Récupération des paramètres de généraux de la stratégie
        timeframe = str(config['STRATEGIE']['timeframe'])
        nbOfCandles = str(config['STRATEGIE']['nbOfCandles'])
        is_tp = str(config['STRATEGIE']['is_tp'])
        nb_tp = str(config['STRATEGIE']['nb_tp'])
        tp_1 = str(config['STRATEGIE']['tp_1'])
        tp_2 = str(config['STRATEGIE']['tp_2'])
        maxOpenPosition = str(config['STRATEGIE']['maxOpenPosition'])
        type_config = config['STRATEGIE']['type']
        is_sl = str(config['STRATEGIE']['is_sl'])
        sl = str(config['STRATEGIE']['sl'])

        if type_config == "both":
            type = ["long", "short"]
        elif type_config == "long":
            type = ["long"]
        elif type_config == "short":
            type = ["short"]
            
        # Mise à jour de la variable de retour
        config_data.update({
            'timeframe': timeframe,
            'nbOfCandles': nbOfCandles,
            'is_tp': is_tp,
            'nb_tp': nb_tp,
            'tp_1': tp_1,
            'tp_2': tp_2,
            'type': type,
            'is_sl': is_sl,
            'sl': sl,
            'maxOpenPosition': maxOpenPosition
        })
        
        # Récupération des paramètres de notification
        telegram_on = str(config['PARAMETRES']['telegram_on'])
        notifTelegramOnChangeOnly = str(config['PARAMETRES']['notifTelegramOnChangeOnly'])
        alwaysNotifTelegram = str(config['PARAMETRES']['alwaysNotifTelegram'])
        notifBilanDePerformance = str(config['PARAMETRES']['notifBilanDePerformance'])
        notifBilanEvolutionContinue = str(config['PARAMETRES']['notifBilanEvolutionContinue'])
        
        # Mise à jour de la variable de retour
        config_data.update({
            'telegram_on': telegram_on,
            'notifTelegramOnChangeOnly': notifTelegramOnChangeOnly,
            'alwaysNotifTelegram': alwaysNotifTelegram,
            'notifBilanDePerformance': notifBilanDePerformance,
            'notifBilanEvolutionContinue': notifBilanEvolutionContinue
        })

        # Récupération des parametre de stratégie
        if strat_active == "BOLLINGER":
            name_strat = str(config['STRAT.BOLLINGER']['name_strat'])
            bol_window = str(config['STRAT.BOLLINGER']['bol_window'])
            bol_std = str(config['STRAT.BOLLINGER']['bol_std'])
            min_bol_spread = str(config['STRAT.BOLLINGER']['min_bol_spread'])
            long_ma_window = str(config['STRAT.BOLLINGER']['long_ma_window'])
            

            # Mise à jour de la variable de retour
            config_data.update({
                'bol_window': bol_window,
                'bol_std': bol_std,
                'min_bol_spread': min_bol_spread,
                'long_ma_window': long_ma_window,
                'name_strat' : name_strat
            })


        # Récupération des informations d'authentification
        apiKey = str(config['BITGET.AUTHENTIFICATION']['apiKey'])
        secret = str(config['BITGET.AUTHENTIFICATION']['secret'])
        password = str(config['BITGET.AUTHENTIFICATION']['password'])

        # Mise à jour de la variable de retour
        config_data.update({
            'apiKey': apiKey,
            'secret': secret,
            'password': password
        })

        
        # Récupération des informations de date
        date = datetime.datetime.now()
        todayJour=date.day
        todayMois=date.month
        todayAnnee=date.year
        todayHeure=date.hour
        todayMinutes=date.minute
        separateDate = str(date).split(".")
        date = str(separateDate[0])
        heureComplète = str(separateDate[1])
        
        # Mise à jour de la variable de retour
        config_data.update({
            'date_time': date,
            'todayJour': todayJour,
            'todayMois': todayMois,
            'todayAnnee': todayAnnee,
            'todayHeure': todayHeure,
            'todayMinutes': todayMinutes,
            'heureComplète': heureComplète
        })
        
        # Si nécessaire, récupération des informations de connexion à une base de données MySQL
        mysql_active = str(config['MYSQL']['mysql_active'])

        if mysql_active == "True":
            mysql_host = str(config['MYSQL']['host'])
            mysql_database = str(config['MYSQL']['database'])
            mysql_user = str(config['MYSQL']['user'])
            mysql_password = str(config['MYSQL']['password'])
            
            # Mise à jour de la variable de retour
            config_data.update({
                'mysql_active': mysql_active,
                'mysql_host': mysql_host,
                'mysql_database': mysql_database,
                'mysql_user': mysql_user,
                'mysql_password': mysql_password
            })
        else:
            # Mise à jour de la variable de retour
            config_data.update({
                'mysql_active': mysql_active
            })

        # Conversion de la variable de retour en chaîne de caractères JSON
        #config_data_json = json.dumps(config_data)

        return config_data

        