import sys
import json

class InfosTokens():
    def get_infos_tokens(path_bot, configuration):
        f = open(sys.path[0]+'/pair_list.json',)
        pairJson = json.load(f)
        f.close()
        pairList_coin = pairJson['list_token']

        #====================
        # List Token
        #====================
        print("************* Pair List *************")
        #print("[")
        pairList=[]
        for pair in pairList_coin:
            pairList.append(pair+'/'+configuration['stableCoin']) 
           # print('{ '+pair+'/'+configuration['stableCoin']+' },')
        print(pairList)
        #print("]")
        print("*************************************")
        
        return pairList