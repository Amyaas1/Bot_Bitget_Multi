import mysql.connector
import datetime

class MysqlDashboard():
    def __init__(self, configuration):
        try:
            mydb = mysql.connector.connect(
                host=configuration['mysql_host'],
                user=configuration['mysql_user'],
                password=configuration['mysql_password'],
                database=configuration['mysql_database']
            )
        except mysql.connector.Error as err:
            print("Erreur de connexion à la base de données: {}".format(err))
            self._auth = False
        else:
            mycursor = mydb.cursor(prepared=True)
            self._auth = True
            self.mydb = mydb
            self.mycursor = mycursor
    
    def update_solde(self, usdAmount):
        if self._auth:
            now_recap = datetime.datetime.now()
            date_recap = now_recap.strftime("%Y-%m-%d")
            sql_query = "INSERT INTO boll_strat  (date, wallet) VALUES (%s, %s)"
            self.mycursor.execute(sql_query, (date_recap, usdAmount))
            self.mydb.commit()

    def log_close_long(self, close_long_quantity, coin, close_long_market_price):
        if self._auth:
            sql = "INSERT INTO boll_strat_orderBook (type, amount, symbol, price) VALUES (%s, %s, %s, %s)"
            val = ("3", close_long_quantity, coin, close_long_market_price)
            self.mycursor.execute(sql, val)
            self.mydb.commit()

    def log_open_long(self, long_quantity_in_usd, coin, long_market_price):
        if self._auth:
            sql = "INSERT INTO boll_strat_orderBook (type, amount, symbol, price) VALUES (%s, %s, %s, %s)"
            val = ("2", long_quantity_in_usd, coin, long_market_price)
            self.mycursor.execute(sql, val)
            self.mydb.commit()

    def log_close_short(self, exchange_close_short_quantity, coin, close_short_market_price):
        if self._auth:
            sql = "INSERT INTO boll_strat_orderBook (type, amount, symbol, price) VALUES (%s, %s, %s, %s)"
            val = ("4", exchange_close_short_quantity, coin, close_short_market_price)
            self.mycursor.execute(sql, val)
            self.mydb.commit()

    def log_open_short(self, short_quantity_in_usd, coin, short_market_price):
        if self._auth:
            sql = "INSERT INTO boll_strat_orderBook (type, amount, symbol, price) VALUES (%s, %s, %s, %s)"
            val = ("1", short_quantity_in_usd, coin, short_market_price)
            self.mycursor.execute(sql, val)
            self.mydb.commit()

    def __del__(self):
        if self._auth:
            self.mydb.close()