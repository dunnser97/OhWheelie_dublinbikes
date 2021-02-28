import requests
import json
import mysql.connector
import datetime
import dbinfo

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
                date = last_update.date()
                time = last_update.time()
                name = bikes_obj[i]["name"]
                number = bikes_obj[i]["number"]
                latitude = bikes_obj[i]["position"]["lat"]
                longitude = bikes_obj[i]["position"]["lng"]
                status = bikes_obj[i]["status"]
                info_bikes = info_bikes + ((address, abs, ab, banking, bs, bonus, cn,
                                                date, time, name, number, latitude, longitude, status),)
            except:
                print("Error with station", str(bikes_obj[i]["number"]))
                print(bikes_obj[i])

        stations_db(info_bikes)
        print("Finished.")
    except Exception as e:
        print(e)
        print("Error with saving to database")


def stations_db(x):

    """Saves data to each individual sql table, one for current
    entries and the other for historical data obtained. Will create
    tables for the data if none exists"""

    try:
        sql = "INSERT INTO dbbikes_info (address, available_bike_stands, available_bikes, " \
              "banking , bike_stands, bonus, contract_name, date, time, name, Station_number, " \
              "latitude, longitude, status) " \
              "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

        current_bikes = "INSERT INTO dbbikes_current_info (address, available_bike_stands, available_bikes, " \
              "banking , bike_stands, bonus, contract_name, date, time, name, Station_number, " \
              "latitude, longitude, status) " \
              "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

        mydb = mysql.connector.connect(
            host=dbinfo.dbhost,
            user=dbinfo.dbuser,
            passwd=dbinfo.dbpasswd,
            database=dbinfo.dbdatabase,
        )
        mycursor = mydb.cursor(dictionary=False)
        mycursor.execute(" SELECT count(*) FROM information_schema.tables WHERE table_name = 'dbbikes_info'")

        #Creates table for historical bike info

        if (mycursor.fetchone()[0] == 0):
            mycursor.execute("CREATE TABLE dbbikes_info ( id INT PRIMARY KEY AUTO_INCREMENT, address VARCHAR(100), "
                            "available_bike_stands INT, available_bikes INT, "
                            "banking VARCHAR(20), bike_stands INT, bonus VARCHAR(20), "
                             "contract_name VARCHAR(20), date DATE, time TIME, "
                             "name VARCHAR(100), Station_number INT, latitude VARCHAR(25), "
                             "longitude VARCHAR(25),  status VARCHAR(20)) ")
        mycursor.executemany(sql, x)
        mydb.commit()

        #Deletes any duplicate entries for any bike station
        mycursor.execute("Delete temp1 "
                         "from dbbikes_info as temp1 "
                         "Inner Join dbbikes_info as temp2 "
                         "where temp1.id < temp2.id "
                         "and temp1.time = temp2.time;")
        mydb.commit()

        mycursor.execute(" SELECT count(*) FROM information_schema.tables WHERE table_name = 'dbbikes_current_info'")

        #Checks for existance of table for current bike stations and creates one if it doesn't exist

        if (mycursor.fetchone()[0] == 0):
            mycursor.execute("CREATE TABLE dbbikes_current_info ( id INT PRIMARY KEY AUTO_INCREMENT, address VARCHAR(100), "
                            "available_bike_stands INT, available_bikes INT, "
                            "banking VARCHAR(20), bike_stands INT, bonus VARCHAR(20), "
                             "contract_name VARCHAR(20), date DATE, time TIME, "
                             "name VARCHAR(100), Station_number INT, latitude VARCHAR(25), "
                             "longitude VARCHAR(25),  status VARCHAR(20)) ")
        #Clears previous entries in current table
        mycursor.execute("truncate dbbikes_current_info;")

        mydb.commit()
        mycursor.executemany(current_bikes, x)
        mydb.commit()
    except Exception as e:
        print(e)
        print("Database Failed!")
        return
main()