import math
import numpy as np
import pandas as pd
import ta
import requests

class CustomIndocators():

    class trix():
        """ Trix indicator

            Args:
                close(pd.Series): dataframe 'close' columns,
                trixLength(int): the window length for each mooving average of the trix,
                trixSignal(int): the window length for the signal line
        """

        def __init__(
            self,
            close: pd.Series,
            trixLength: int = 9,
            trixSignal: int = 21
        ):
            self.close = close
            self.trixLength = trixLength
            self.trixSignal = trixSignal
            self._run()

        def _run(self):
            self.trixLine = ta.trend.ema_indicator(
                ta.trend.ema_indicator(
                    ta.trend.ema_indicator(
                        close=self.close, window=self.trixLength),
                    window=self.trixLength), window=self.trixLength)
            self.trixPctLine = self.trixLine.pct_change()*100
            self.trixSignalLine = ta.trend.sma_indicator(
                close=self.trixPctLine, window=self.trixSignal)
            self.trixHisto = self.trixPctLine - self.trixSignalLine

        def trix_line(self):
            """ trix line

                Returns:
                    pd.Series: trix line
            """
            return pd.Series(self.trixLine, name="TRIX_LINE")

        def trix_pct_line(self):
            """ trix percentage line

                Returns:
                    pd.Series: trix percentage line
            """
            return pd.Series(self.trixPctLine, name="TRIX_PCT_LINE")

        def trix_signal_line(self):
            """ trix signal line

                Returns:
                    pd.Series: trix siganl line
            """
            return pd.Series(self.trixSignal, name="TRIX_SIGNAL_LINE")

        def trix_histo(self):
            """ trix histogram

                Returns:
                    pd.Series: trix histogram
            """
            return pd.Series(self.trixHisto, name="TRIX_HISTO")

    def chop(high, low, close, window=14):
        """ Chopiness index

            Args:
                high(pd.Series): dataframe 'high' columns,
                low(pd.Series): dataframe 'low' columns,
                close(pd.Series): dataframe 'close' columns,
                window(int): the window length for the chopiness index,
            Returns:
                pd.Series: Chopiness index
        """
        tr1 = pd.DataFrame(high - low).rename(columns = {0:'tr1'})
        tr2 = pd.DataFrame(abs(high - close.shift(1))).rename(columns = {0:'tr2'})
        tr3 = pd.DataFrame(abs(low - close.shift(1))).rename(columns = {0:'tr3'})
        frames = [tr1, tr2, tr3]
        tr = pd.concat(frames, axis = 1, join = 'inner').dropna().max(axis = 1)
        atr = tr.rolling(1).mean()
        highh = high.rolling(window).max()
        lowl = low.rolling(window).min()
        chop = 100 * np.log10((atr.rolling(window).sum()) / (highh - lowl)) / np.log10(window)
        return pd.Series(chop, name="CHOP")
    
    

    def heikinAshiDf(df):
        """ HeikinAshi candles

            Args:
                df(pd.Dataframe): dataframe with 'open'|'high'|'low'|'close' columns
            Returns:
                pd.Dataframe: dataframe with 'HA_Open'|'HA_High'|'HA_Low'|'HA_Close' columns
        """
        df['HA_Close']=(df.open + df.high + df.low + df.close)/4
        ha_open = [ (df.open[0] + df.close[0]) / 2 ]
        [ ha_open.append((ha_open[i] + df.HA_Close.values[i]) / 2) \
        for i in range(0, len(df)-1) ]
        df['HA_Open'] = ha_open
        df['HA_High']=df[['HA_Open','HA_Close','high']].max(axis=1)
        df['HA_Low']=df[['HA_Open','HA_Close','low']].min(axis=1)
        return df

    #Volume Anomaly
    def volume_anomality(df, volume_window=10):
        dfInd = df.copy()
        dfInd["VolAnomaly"] = 0
        dfInd["PreviousClose"] = dfInd["close"].shift(1)
        dfInd['MeanVolume'] = dfInd['volume'].rolling(volume_window).mean()
        dfInd['MaxVolume'] = dfInd['volume'].rolling(volume_window).max()
        dfInd.loc[dfInd['volume'] > 1.5 * dfInd['MeanVolume'], "VolAnomaly"] = 1
        dfInd.loc[dfInd['volume'] > 2 * dfInd['MeanVolume'], "VolAnomaly"] = 2
        dfInd.loc[dfInd['volume'] >= dfInd['MaxVolume'], "VolAnomaly"] = 3
        dfInd.loc[dfInd['PreviousClose'] > dfInd['close'],
                "VolAnomaly"] = (-1) * dfInd["VolAnomaly"]
        return dfInd["VolAnomaly"]
    
    #---------------------------
    # indicateurs de tendance
    #---------------------------
    #EMA
    def ema(df, ask_window):
        return ta.trend.ema_indicator(close=df, window=ask_window, fillna=True)
    
    #SMA
    def sma(df, ask_window):
        return ta.trend.sma_indicator(close=df, window=ask_window)
    
    #TRIX
    def trixIndicator(df, trixLength, trixSignal):
        df['TRIX'] = ta.trend.ema_indicator(ta.trend.ema_indicator(ta.trend.ema_indicator(close=df['close'], window=trixLength), window=trixLength), window=trixLength)
        df['TRIX_PCT'] = df["TRIX"].pct_change()*100
        df['TRIX_SIGNAL'] = ta.trend.sma_indicator(df['TRIX_PCT'],trixSignal)
        df['TRIX_HISTO'] = df['TRIX_PCT'] - df['TRIX_SIGNAL']
        return df
    
    #ICHIMOKU
    def ichimoku(df):
        df['SSA'] = ta.trend.ichimoku_a(df['high'],df['low'],3,38).shift(periods=48)
        df['SSB'] = ta.trend.ichimoku_b(df['high'],df['low'],38,46).shift(periods=48)
        
        df['kijun'] = ta.trend.ichimoku_base_line(df['high'], df['low'])
        df['tenkan'] = ta.trend.ichimoku_conversion_line(df['high'], df['low'])
        df['ssa'] = ta.trend.ichimoku_a(df['high'], df['low'])
        df['ssb'] = ta.trend.ichimoku_b(df['high'], df['low'])
        df['ssa25'] = ta.trend.ichimoku_a(df['high'], df['low']).shift(25)
        df['ssb25'] = ta.trend.ichimoku_b(df['high'], df['low']).shift(25)
        df['ssa52'] = ta.trend.ichimoku_a(df['high'], df['low']).shift(50)
        df['ssb52'] = ta.trend.ichimoku_b(df['high'], df['low']).shift(50)
        df['close25'] = df['close'].shift(25)
        df['close1'] = df['close'].shift(1)
        return df
    
    #MACD
    def macdIndicator(df):
        macd = ta.trend.MACD(close=df['close'], window_fast=12, window_slow=26, window_sign=9)
        df['macd'] = macd.macd()
        df['macd_signal'] = macd.macd_signal()
        df['macd_histo'] = macd.macd_diff() #Histogramme MACD
        #print(df)
        return df
    
    #Awesome Oscillator
    def awesome_oscillator(df, window1, window2):
        return ta.momentum.awesome_oscillator(high=df['high'], low=df['low'], window1=window1, window2=window2, fillna=True)
    
    #ADX
    def adx(df):
        return ta.trend.adx(high=df['high'], low=df['low'], close = df['close'], window = 14)
    
    # Fear and Greed 
    def fear_and_greed(close):
        ''' Fear and greed indicator
        '''
        response = requests.get('https://api.alternative.me/fng/?limit=0&format=json')
        dataResponse = response.json()['data']
        fear = pd.DataFrame(dataResponse, columns = ['timestamp', 'value'])

        fear = fear.set_index(fear['timestamp'])
        fear.index = pd.to_datetime(fear.index, unit='s')
        del fear['timestamp']
        df = pd.DataFrame(close, columns = ['close'])
        df['fearResult'] = fear['value']
        df['FEAR'] = df['fearResult'].ffill()
        df['FEAR'] = df.FEAR.astype(float)
        return pd.Series(df['FEAR'], name='FEAR')
    
    
    #---------------------------
    # oscillateurs
    #---------------------------
    #STOCK_RSI
    def stoch_rsi(df, stochWindow):
        return ta.momentum.stochrsi(close=df['close'], window=stochWindow, fillna=True)
    
    #Stochastic
    def stochastic(df):
        df['stochastic'] = ta.momentum.stoch(high=df['high'],low=df['low'],close=df['close'], window=14,smooth_window=3)
        df['stoch_signal'] =ta.momentum.stoch_signal(high =df['high'],low=df['low'],close=df['close'], window=14, smooth_window=3)
        #print(df)
        return df
    
    #William R Indicator
    def william_r(df, willWindow):
        df['WillR'] = ta.momentum.williams_r(high=df['high'], low=df['low'], close=df['close'], lbp=willWindow, fillna=True)
    
        df['max_21'] = df['high'].rolling(21).max()
        df['min_21'] = df['low'].rolling(21).min()
        df['william_r'] = (df['close'] - df['max_21']) / (df['max_21'] - df['min_21']) * 100
        df['emaw'] = ta.trend.ema_indicator(close=df['william_r'], window=13)
        return df
    
    #CCI
    #def cci(df):
    #    df['hlc3'] = (df['high'] + df['low'] + df['close']) / 3 
    #    df['sma_cci'] = df['hlc3'].rolling(40).mean()
    #    df['mad'] = df['hlc3'].rolling(40).apply(lambda x: pd.Series(x).mad())
    #    df['cci'] = (df['hlc3'] - df['sma_cci']) / (0.015 * df['mad']) 
    #    return df
    
    #PPO
    def ppo(df):
        df['ppo'] = ta.momentum.ppo(close=df['close'], window_slow=26, window_fast=12, window_sign=9)
        df['ppo_signal'] = ta.momentum.ppo_signal(close=df['close'], window_slow=26, window_fast=12, window_sign=9)
        df['ppo_histo'] = ta.momentum.ppo_hist(close=df['close'], window_slow=26, window_fast=12, window_sign=9)
        return df
    
    #PVO
    def pvo(df):
        df['pvo'] = ta.momentum.pvo(volume = df['volume'], window_slow=26, window_fast=12, window_sign=9)
        df['pvo_signal'] = ta.momentum.pvo_signal(volume = df['volume'], window_slow=26, window_fast=12, window_sign=9)
        df['pvo_histo'] = ta.momentum.pvo_hist(volume = df['volume'], window_slow=26, window_fast=12, window_sign=9)
        return df
    
    #Aroon
    def aroon(df):
        df['aroon_up'] = ta.trend.aroon_up(close=df['close'], window=25)
        df['aroon_dow'] = ta.trend.aroon_down(close=df['close'], window=25)
        return df
    
    #---------------------------
    # volatilité/volume
    #---------------------------
    #Kaufman ou KAMA
    def kama(df):
        return ta.momentum.kama(df['close'], window=10, pow1=2, pow2=30)
    
    #ATR
    def atr(df, window):
        return ta.volatility.average_true_range(df['high'], df['low'], df['close'], window=window)
    
    #Les bandes de Bollingers
    def bollingers(df):
        df["bol_high"] = ta.volatility.bollinger_hband(df['close'], window=20, window_dev=2)
        df["bol_low"] = ta.volatility.bollinger_lband(df['close'], window=20, window_dev=2)
        df["bol_medium"] = ta.volatility.bollinger_mavg(df['close'], window=20)
        df["bol_gap"] = ta.volatility.bollinger_wband(df['close'], window=20, window_dev=2)
        # Return binaire 0 ou 1 
        df["bol_higher"] = ta.volatility.bollinger_hband_indicator(df['close'], window=20, window_dev=2)
        df["bol_lower"] = ta.volatility.bollinger_lband_indicator(df['close'], window=20, window_dev=2)
        return df
    
    #Le canal de Donchian
    def donchian(df):
        df["don_high"] = ta.volatility.donchian_channel_hband(df['high'], df['low'], df['close'], window=20, offset=0)
        df["don_low"] = ta.volatility.donchian_channel_lband(df['high'], df['low'], df['close'], window=20, offset=0)
        df["don_medium"] = ta.volatility.donchian_channel_mband(df['high'], df['low'], df['close'], window=20, offset=0)
        return df
    
    #Le canal de Keltner
    def keltner(df):
        df["kel_high"] = ta.volatility.keltner_channel_hband(df['high'], df['low'], df['close'], window=20, window_atr=10)
        df["kel_low"] = ta.volatility.keltner_channel_lband(df['high'], df['low'], df['close'], window=20, window_atr=10)
        df["kel_medium"] = ta.volatility.keltner_channel_mband(df['high'], df['low'], df['close'], window=20 ,window_atr=10)
        # Return binaire 0 ou 1 
        df["kel_higher"] = ta.volatility.keltner_channel_hband_indicator(df['high'], df['low'], df['close'], window=20, window_atr=10)
        df["kel_lower"] = ta.volatility.keltner_channel_lband_indicator(df['high'], df['low'], df['close'], window=20, window_atr=10)
        return df
    
    #ADI Indicator
    def adi(df):
        return ta.volume.acc_dist_index(high=df['high'], low=df['low'], close=df['close'], volume = df['volume'])
    
    #Force Index Indicator
    def fi_indicator(df):
        return ta.volume.force_index(close=df['close'] ,volume=df['volume'], window=13)

