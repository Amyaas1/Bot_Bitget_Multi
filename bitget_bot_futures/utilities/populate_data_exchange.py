import time


class DataExchange():
    def get_data_exchange(pairList, configuration, bitget, telegram_send):
        dfList = {}
        for pair in pairList:
            if configuration['debug'] == "True":
                print("Get Data for : " + pair)
            #On essaie de récupérer toutes les bougies sur l'API bitget
            try :
                
                df = bitget.get_more_last_historical_async(pair+":"+configuration['stableCoin'], configuration['timeframe'], int(configuration['nbOfCandles']))
                dfList[pair.replace('/USDT','')] = df
            except :
                #Si on ne parvient à récupérer la paire à la première tentative (parfois l'api bitget est inaccessible) :
                #On attend X seconde(s) et on réessaye avec moins de bougies
                time.sleep(int(configuration['delay_coin']))
                try :
                    df = bitget.get_more_last_historical_async(pair+":"+configuration['stableCoin'], configuration['timeframe'], int(configuration['nbOfCandles'])-int(configuration['nbOfCandles']*0.25))
                    dfList[pair.replace('/USDT','')] = df
                    
                except :
                    time.sleep(int(configuration['delay_coin'])+1)
                    try :
                        df = bitget.get_more_last_historical_async(pair+":"+configuration['stableCoin'], configuration['timeframe'], int(configuration['nbOfCandles'])-int(configuration['nbOfCandles']*0.50))
                
            
                        dfList[pair.replace('/USDT','')] = df
                    except :
                        time.sleep(int(configuration['delay_coin'])+2)
                        try : 
                            df = bitget.get_more_last_historical_async(pair+":"+configuration['stableCoin'], configuration['timeframe'], int(configuration['nbOfCandles'])-int(configuration['nbOfCandles']*0.75))
                            dfList[pair.replace('/USDT','')] = df
                        except :
                            #Si au bout de la 3ème fois ça n'a vraiment pas fonctionné, on abandonne
                            try :
                                del dfList[pair+":"+configuration['stableCoin']]
                            except :
                                pass
                            #Si ça ne fonctionne toujours pas, on abandonne cette paire
                            pair_message = pair+":"+configuration['stableCoin']

            
                            if configuration['telegram_on'] == "True":
                                telegram_send.send(messages=[f"{configuration['botname']} : Impossible de récupérer les {configuration['nbOfCandles']} dernières bougies de {pair_message} à 3 reprises, donc on n'utilisera pas cette paire durant cette execution."])
            
                            print(f"Impossible de récupérer les 210 dernières bougies de {pair_message} à 2 reprises, on n'utilisera pas cette paire durant cette execution")
                            pass
        return dfList