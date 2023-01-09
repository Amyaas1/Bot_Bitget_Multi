

class BilanSolde():
    
    
    #============================================
    #   CODES NECESSAIRES POUR FAIRE DES BILANS
    #    DE PERFORMANCES AU FIL DU TEMPS DANS
    #       LA NOTIFICATION TELEGRAM FINALE
    #============================================
    def get_bilan(configuration, MessageTelegram, telegram_send, message, fichier_dat, usdAmount, todayJour, todayMois, todayAnnee, todayHeure, todayMinutes, notifBilanDePerformance, notifBilanEvolutionContinue, totalInvestment, alwaysNotifTelegram, notifTelegramOnChangeOnly, changement):
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
            with open(fichier_dat, "r") as f:
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
            print(f"WARNING : Le fichier {fichier_dat} est introuvable, il va être créé.")

        #==================================================
        #  Enregistrement du solde dans le fichier .dat
        #==================================================

        todaySolde=usdAmount
        with open(fichier_dat, "a") as f:
            f.write(f"{todayJour} {todayMois} {todayAnnee} {todayHeure} {todayMinutes} {todaySolde} \n")
            
        
        
        
        #=======================================================
        #  Affiche le bilan de perf dans le message telegram
        #=======================================================

        if notifBilanDePerformance=="true" :
            message = MessageTelegram.addMessageComponent(message, "\n===================\n")
            message = MessageTelegram.addMessageComponent(message, "Bilan de performance :")
            if 'soldeMaxJour' in locals():
                soldeMaxJour=round(soldeMaxJour,3)
                message = MessageTelegram.addMessageComponent(message, f" - Best solde aujourd'hui : {soldeMaxJour}$ à {heureMaxJour}h")
            if 'soldeMaxMois' in locals():
                soldeMaxMois=round(soldeMaxMois,3)
                message = MessageTelegram.addMessageComponent(message, f" - Best solde ce mois-ci : {soldeMaxMois}$ le {jourMaxMois}/{moisMaxMois} à {heureMaxMois}h")
            if 'soldeMaxAnnee' in locals():
                soldeMaxAnnee=round(soldeMaxAnnee,3)
                message = MessageTelegram.addMessageComponent(message, f" - Best solde cette année : {soldeMaxAnnee}$ le {jourMaxAnnee}/{moisMaxAnnee}/{anneeMaxAnnee} à {heureMaxAnnee}h")
                
            message = MessageTelegram.addMessageComponent(message, " ")

            if 'soldeMinJour' in locals():
                soldeMinJour=round(soldeMinJour,3)
                message = MessageTelegram.addMessageComponent(message, f" - Pire solde aujourd'hui : {soldeMinJour}$ à {heureMinJour}h")
            if 'soldeMinMois' in locals():
                soldeMinMois=round(soldeMinMois,3)
                message = MessageTelegram.addMessageComponent(message, f" - Pire solde ce mois-ci : {soldeMinMois}$ le {jourMinMois}/{moisMinMois} à {heureMinMois}h")
            if 'soldeMinAnnee' in locals():
                soldeMinAnnee=round(soldeMinAnnee,3)
                message = MessageTelegram.addMessageComponent(message, f" - Pire solde cette année : {soldeMinAnnee}$ le {jourMinAnnee}/{moisMinMois}/{anneeMinAnnee} à {heureMinAnnee}h")


        #=================================================================
        #  Affiche le bilan d'évolution continue dans le message telegram
        #=================================================================

        if notifBilanEvolutionContinue=="true" :
            message = MessageTelegram.addMessageComponent(message, "\n===================\n")
            message = MessageTelegram.addMessageComponent(message, "Bilan d'évolution continue :")
            if 'soldeLastExec' in locals():
                bonus=100*(todaySolde-soldeLastExec)/soldeLastExec 
                gain=bonus/100*soldeLastExec
                bonus=round(bonus,3)
                gain=round(gain,5)
                soldeLastExecRounded=round(soldeLastExec,3)
                if gain<0 :
                    message = MessageTelegram.addMessageComponent(message, f" - Dernière execution du bot : {bonus}% ({soldeLastExecRounded}$ {gain}$)")
                else :
                    message = MessageTelegram.addMessageComponent(message, f" - Dernière execution du bot : +{bonus}% ({soldeLastExecRounded}$ +{gain}$)")
            if 'solde6heures' in locals():
                bonus=100*(todaySolde-solde6heures)/solde6heures 
                gain=round(bonus/100*todaySolde,2)
                bonus=round(bonus,3)
                gain=round(gain,5)
                solde6heures=round(solde6heures,3)
                if gain<0 :
                    message = MessageTelegram.addMessageComponent(message, f" - il y a 6h : {bonus}% ({solde6heures}$ {gain}$)")
                else :
                    message = MessageTelegram.addMessageComponent(message, f" - il y a 6h : +{bonus}% ({solde6heures}$ +{gain}$)")
            if 'solde12heures' in locals():
                bonus=100*(todaySolde-solde12heures)/solde12heures 
                gain=round(bonus/100*todaySolde,2)
                bonus=round(bonus,3)
                gain=round(gain,5)
                solde12heures=round(solde12heures,3)
                if gain<0 :
                    message = MessageTelegram.addMessageComponent(message, f" - il y a 12h : {bonus}% ({solde12heures}${gain}$)")
                else :
                    message = MessageTelegram.addMessageComponent(message, f" - il y a 12h : +{bonus}% ({solde12heures}$ +{gain}$)")
            if 'solde1jours' in locals():
                bonus=100*(todaySolde-solde1jours)/solde1jours
                gain=round(bonus/100*todaySolde,2)
                bonus=round(bonus,3)
                gain=round(gain,5)
                solde1jours=round(solde1jours,5)
                if gain<0 :
                    message = MessageTelegram.addMessageComponent(message, f" - il y a 1j : {bonus}% ({solde1jours}$ {gain}$)")
                else :
                    message = MessageTelegram.addMessageComponent(message, f" - il y a 1j : +{bonus}% ({solde1jours}$ +{gain}$)")
            if 'solde3jours' in locals():
                bonus=100*(todaySolde-solde3jours)/solde3jours
                gain=round(bonus/100*todaySolde,2)
                bonus=round(bonus,3)
                gain=round(gain,5)
                solde3jours=round(solde3jours,3)
                if gain<0 :
                    message = MessageTelegram.addMessageComponent(message, f" - il y a 3j : {bonus}% ({solde3jours}$ {gain}$)")
                else :
                    message = MessageTelegram.addMessageComponent(message, f" - il y a 3j : +{bonus}% ({solde3jours}$ +{gain}$)")
            if 'solde7jours' in locals():
                bonus=100*(todaySolde-solde7jours)/solde7jours
                gain=round(bonus/100*todaySolde,2)
                bonus=round(bonus,3)
                gain=round(gain,5)
                solde7jours=round(solde7jours,3)
                if gain<0 :
                    message = MessageTelegram.addMessageComponent(message, f" - il y a 7j : {bonus}% ({solde7jours}$ {gain}$)")
                else :
                    message = MessageTelegram.addMessageComponent(message, f" - il y a 7j : +{bonus}% ({solde7jours}$ +{gain}$)")
            if 'solde14jours' in locals():
                bonus=100*(todaySolde-solde14jours)/solde14jours
                gain=round(bonus/100*todaySolde,2)
                bonus=round(bonus,3)
                gain=round(gain,5)
                solde14jours=round(solde14jours,3)
                if gain<0 :
                    message = MessageTelegram.addMessageComponent(message, f" - il y a 14j : {bonus}% ({solde14jours}$ {gain}$)")
                else :
                    message = MessageTelegram.addMessageComponent(message, f" - il y a 14j : +{bonus}% ({solde14jours}$ +{gain}$)")
            if 'solde1mois' in locals():
                bonus=100*(todaySolde-solde1mois)/solde1mois
                gain=round(bonus/100*todaySolde,2)
                bonus=round(bonus,3)
                gain=round(gain,5)
                solde1mois=round(solde1mois,3)
                if gain<0 :
                    message = MessageTelegram.addMessageComponent(message, f" - il y a 1 mois : {bonus}% ({solde1mois}$ {gain}$)")
                else :
                    message = MessageTelegram.addMessageComponent(message, f" - il y a 1 mois : +{bonus}% ({solde1mois}$ +{gain}$)")
            if 'solde2mois' in locals():
                bonus=100*(todaySolde-solde2mois)/solde2mois
                gain=round(bonus/100*todaySolde,2)
                bonus=round(bonus,3)
                gain=round(gain,5)
                solde2mois=round(solde2mois,3)
                if gain<0 :
                    message = MessageTelegram.addMessageComponent(message, f" - il y a 2 mois : {bonus}% ({solde2mois}$ {gain}$)")
                else :
                    message = MessageTelegram.addMessageComponent(message, f" - il y a 2 mois : +{bonus}% ({solde2mois}$ +{gain}$)")

        
        bonus=100*(todaySolde-totalInvestment)/totalInvestment
        gain=round((bonus/100)*totalInvestment,3)
        bonus=round(bonus,3)
        totalInvestment=round(totalInvestment,5)
        message = MessageTelegram.addMessageComponent(message, "\n===================\n")
        message = MessageTelegram.addMessageComponent(message, f"INVESTISSEMENT INITIAL => {totalInvestment}$")
        if gain<0 :
            message = MessageTelegram.addMessageComponent(message, f"PERTE TOTAL => {gain} $ ({bonus}%)\n")
        else :
            message = MessageTelegram.addMessageComponent(message, f"GAIN TOTAL => +{gain} $ (+{bonus}%)\n")
        message = MessageTelegram.addMessageComponent(message, f"SOLDE TOTAL => {usdAmount}$")
        message = MessageTelegram.addMessageComponent(message, f"N'hésitez pas à me soutenir pour le travail du bot :\n • Adresse BTC : 1CetuWt9PuppZ338MzBzQZSvtMW3NnpjMr\n • Adresse ETH (Réseau ERC20) : 0x18f71abd7c2ee05eab7292d8f34177e7a1b62236\n • Adresse SOL : AsLvBCG1fpmpaueTYBmU5JN5QKVkt9a1dLR44BAGUZbV\n• Adresse MATIC : 0x18f71abd7c2ee05eab7292d8f34177e7a1b62236\n• Adresse BNB : 0x18f71abd7c2ee05eab7292d8f34177e7a1b62236\n")

        message = message.replace(' , ',' ')
        message = message.replace('-USDT','')

        #======================================================
        #  Se base sur les configurations pour déterminer s'il  
        #  faut vous envoyer une notification telegram ou non
        #======================================================


        #Si on a activé de toujours recevoir la notification telegram
        if configuration['telegram_on'] == "True":
            if alwaysNotifTelegram=='true':
                telegram_send.send(messages=[f"{message}"])
            elif notifTelegramOnChangeOnly=='true' and changement>0 :
                telegram_send.send(messages=[f"{message}"])
            else :
                print("Aucune information n'a été envoyé à Telegram")
            
        print("...................................................")
        print("...................................................")
        
        
   