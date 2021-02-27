import requests
import json
import mysql.connector
import datetime

APIKEY = "7188e828188de75359fb293a4f4fd405a53fdfe8"
NAME = "Dublin"
Stations = "https://api.jcdecaux.com/vls/v1/stations"


def main():
    try:
        r = requests.get(Stations,
                        params={"apiKey": APIKEY, "contract": NAME})
        bikes_obj = json.loads(r.text)
        info_bikes = ()

        for i in range(0, len(bikes_obj) - 1):
            try:
                address = bikes_obj[i]["address"]
                abs = bikes_obj[i]["available_bike_stands"]
                ab = bikes_obj[i]["available_bikes"]
                banking = bikes_obj[i]["banking"]
                bs = bikes_obj[i]["bike_stands"]
                bonus = bikes_obj[i]["bonus"]
                cn = bikes_obj[i]["contract_name"]
                last_update = datetime.datetime.fromtimestamp(bikes_obj[i]["last_update"] / 1e3)
                name = bikes_obj[i]["name"]
                number = bikes_obj[i]["number"]
                latitude = bikes_obj[i]["position"]["lat"]
                longitude = bikes_obj[i]["position"]["lng"]
                status = bikes_obj[i]["status"]
                info_bikes = info_bikes + ((address, abs, ab, banking, bs, bonus, cn,
                                                last_update, name, number, latitude, longitude, status),)
            except:
                print("Error with station", str(bikes_obj[i]["number"]))
                print(bikes_obj[i])

        stations_db(info_bikes)
        print("Successfully saved bikes from API.")
    except Exception as e:
        print(e)
        print("Error with saving to database")


def stations_db(x):
    try:
        sql = "INSERT INTO dbbikes_info (address, available_bike_stands, available_bikes, " \
              "banking , bike_stands, bonus, contract_name, last_update, name, Station_number, " \
              "latitude, longitude, status) " \
              "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

        current_bikes = "INSERT INTO dbbikes_current_info (address, available_bike_stands, available_bikes, " \
              "banking , bike_stands, bonus, contract_name, last_update, name, Station_number, " \
              "latitude, longitude, status) " \
              "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

        mydb = mysql.connector.connect(
            host="",
            user="",
            passwd="",
            database="",
            charset='',
        )
        mycursor = mydb.cursor(dictionary=False)
        mycursor.execute(" SELECT count(*) FROM information_schema.tables WHERE table_name = 'dbbikes_info'")
        if (mycursor.fetchone()[0] == 0):
            mycursor.execute("CREATE TABLE dbbikes_info ( id INT PRIMARY KEY AUTO_INCREMENT, address VARCHAR(100), "
                            "available_bike_stands INT, available_bikes INT, "
                            "banking VARCHAR(20), bike_stands INT, bonus VARCHAR(20), "
                             "contract_name VARCHAR(20), last_update DATETIME, "
                             "name VARCHAR(100), Station_number INT, latitude VARCHAR(25), "
                             "longitude VARCHAR(25),  status VARCHAR(20)) ")
        mycursor.executemany(sql, x)
        mydb.commit()

        mycursor.execute("Delete temp1 "
                         "from dbbikes_info as temp1 "
                         "Inner Join dbbikes_info as temp2 "
                         "where temp1.id < temp2.id "
                         "and temp1.last_update = temp2.last_update;")
        mydb.commit()

        mycursor.execute(" SELECT count(*) FROM information_schema.tables WHERE table_name = 'dbbikes_current_info'")

        if (mycursor.fetchone()[0] == 0):
            mycursor.execute("CREATE TABLE dbbikes_current_info ( id INT PRIMARY KEY AUTO_INCREMENT, address VARCHAR(100), "
                            "available_bike_stands INT, available_bikes INT, "
                            "banking VARCHAR(20), bike_stands INT, bonus VARCHAR(20), "
                             "contract_name VARCHAR(20), last_update DATETIME, "
                             "name VARCHAR(100), Station_number INT, latitude VARCHAR(25), "
                             "longitude VARCHAR(25),  status VARCHAR(20)) ")
        mycursor.execute("truncate dbbikes_current_info;")
        mydb.commit()
        mycursor.executemany(current_bikes, x)
        mydb.commit()
    except Exception as e:
        print(e)
        print("Database Failed!")
        return