#!/bin/bash
echo "Passage dans l'environement virtuel"
source /home/user/Bot_Bitget_Multi/bitget_bot/.venv/bin/activate 
echo "Execution du Bot"
python3 /home/user/Bot_Bitget_Multi/bitget_bot/bitget_bot.py


#Executer sur ce fichier start_bot_venv.sh un : 
#chmod +x start_bot_venv.sh
#
#puis dans le crontab ajouter :
#0 * * * * bash /home/user/Bot_Bitget_Multi/bitget_bot/start_bot.sh >>/home/user/Bot_Bitget_Multi/bitget_bot/bitget_bot.log
