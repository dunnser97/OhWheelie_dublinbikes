import requests
import json
import time
import mysql.connector

APIKEY = "7188e828188de75359fb293a4f4fd405a53fdfe8"
NAME = "Dublin"
Stations = "https://api.jcdecaux.com/vls/v1/stations"


def main():
    while True:
        try:
            r = requests.get(Stations,
                             params={"apiKey": APIKEY, "contract": NAME})
            bikes_obj = json.loads(r.text)
            info_bikes = ()
            for i in range(0, len(bikes_obj) - 1):
                address = bikes_obj[i]["address"]
                abs = bikes_obj[i]["available_bike_stands"]
                ab = bikes_obj[i]["available_bikes"]
                banking = bikes_obj[i]["banking"]
                bs = bikes_obj[i]["bike_stands"]
                bonus = bikes_obj[i]["bonus"]
                cn = bikes_obj[i]["contract_name"]
                last_update = bikes_obj[i]["last_update"]
                name = bikes_obj[i]["name"]
                number = bikes_obj[i]["number"]
                latitude = bikes_obj[i]["position"]["lat"]
                longitude = bikes_obj[i]["position"]["lng"]
                status = bikes_obj[i]["status"]
                info_bikes = info_bikes + ((address, abs, ab, banking, bs, bonus, cn,
                                            last_update, name, number, latitude, longitude, status),)
            stations_db(info_bikes)
            time.sleep(5 * 60)
        except:
            print("Broke")
            return


def stations_db(x):
    try:
        sql = "INSERT INTO dbbikes_info (address, available_bike_stands, available_bikes, banking , bike_stands, bonus, contract_name, last_update, name, number, latitude, longitude, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)

        mydb = mysql.connector.connect(
            host="dbbikes-kms.cb4a7u7bkk6j.us-east-1.rds.amazonaws.com",
            user="Shane",
            passwd="Oh_Wheeliekms",
            database="dbbikes",
            charset='utf8mb4',
        )
        mycursor = mydb.cursor(dictionary=False)
        """
        mycursor.execute("CREATE TABLE dbbikes_info ( address VARCHAR(100), "
                         "available_bike_stands INT, available_bikes INT, "
                         "banking VARCHAR(20), bike_stands INT, bonus VARCHAR(20), "
                         "contract_name VARCHAR(20), last_update DATETIME, "
                         "name VARCHAR(100), number INT, latitude VARCHAR(25), "
                         "longitude VARCHAR(25),  status VARCHAR(20)) ")
        """
        print("Connected to database! Yay :smile: :D")
        mycursor.executemany(sql, x)
        mydb.commit()
    except Exception as e:
        print(e)
        print("Database Failed!")
        return


main()