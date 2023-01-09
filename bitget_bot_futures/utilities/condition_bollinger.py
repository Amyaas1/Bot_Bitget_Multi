class ConditionTrade():
    #====================
    # CONDITION LONG - SHORT
    #====================
    def open_long(row, configuration):
        if configuration['debug_detail'] == "True":
                print("---------------  open_long  --------------- ")
                print("row['n1_close']:" + str(row['n1_close']) + " row['n1_higher_band']:"+str(row['n1_higher_band'])  )
                print(" row['close']:"+str(row['close'] )+ " row['higher_band']:" + str(row['higher_band']))
                print("row['n1_higher_band']:" + str(row['n1_higher_band']) + " row['n1_lower_band']:" + str(row['n1_lower_band']) + " configuration['min_bol_spread']:" + str(configuration['min_bol_spread']))
                print("row['long_ma']:"+str(row['long_ma']))
           
        if (row['n1_close'] < row['n1_higher_band']):
            if ((row['close'] > row['higher_band'])):
                band = (row['n1_higher_band'] - row['n1_lower_band']) / row['n1_lower_band']
                if (float(band) > float(configuration['min_bol_spread'])):
                    if(row['close'] > row['long_ma']):
                        if configuration['debug_detail'] == "True":
                            print("True")
                            print("------------------------------------------- ")
                            
                        return True
        else:
            if configuration['debug_detail'] == "True":
                print("False")
                print("------------------------------------------- ")
                
            return False

    def close_long(row, configuration):
        if configuration['debug_detail'] == "True":
                print("---------------  close_long  --------------- ")
                print("row['close']:" + str(row['close']) + " row['ma_band']:"+str(row['ma_band'] ) )
       
        if (row['close'] < row['ma_band']):
            if configuration['debug_detail'] == "True":
                print("True")
                print("------------------------------------------- ")
            return True
        else:
            if configuration['debug_detail'] == "True":
                print("False")
                print("------------------------------------------- ")
            return False

    def open_short(row, configuration):
        if configuration['debug_detail'] == "True":
                print("---------------  open_short  --------------- ")
                print("row['n1_close']:" + str(row['n1_close']) + " row['n1_higher_band']:"+str(row['n1_higher_band'] ) )
                print(" row['close']:"+str(row['close']) + " row['higher_band']:" + str(row['higher_band']))
                print("row['n1_higher_band']:" + str(row['n1_higher_band']) + " row['n1_lower_band']:" + str(row['n1_lower_band'])  + " configuration['min_bol_spread']:" + str(configuration['min_bol_spread']))
                print("row['long_ma']:"+str(row['long_ma']))
                
        if (row['n1_close'] > row['n1_lower_band'] ):
            if(row['close'] < row['lower_band']) :
                band = (row['n1_higher_band'] - row['n1_lower_band']) / row['n1_lower_band']
                if(float(band) > float(configuration['min_bol_spread'])):
                    if(row['close'] < row['long_ma']):
                        if configuration['debug_detail'] == "True":
                            print("True")
                            print("------------------------------------------- ")
                        return True
        else:
            if configuration['debug_detail'] == "True":
                print("False")
                print("------------------------------------------- ")
            return False

    def close_short(row, configuration):
        if configuration['debug_detail'] == "True":
                print("---------------  close_short  --------------- ")
                print("row['close']:" + str(row['close']) + " row['ma_band']:"+str(row['ma_band'] ) )
       
        if (row['close'] > row['ma_band']):
            return True
        else:
            if configuration['debug_detail'] == "True":
                print("False")
                print("------------------------------------------- ")
            return False
  
        