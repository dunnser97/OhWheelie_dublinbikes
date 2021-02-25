import json
import xmltodict
import requests
import mysql.connector
import dbinfo

from datetime import datetime, timedelta

print("WEATHER SCRIPT START:", datetime.now())

print("Writing to:", dbinfo.host)

mydb = mysql.connector.connect(
            host=dbinfo.host,
            user=dbinfo.user,
            passwd=dbinfo.passwd,
            database=dbinfo.database,
            charset=dbinfo.charset
        )

#Check if both tables exist. If they don't, create them.
mycursor = mydb.cursor(dictionary=False)
mycursor.execute(" SELECT count(*) FROM information_schema.tables WHERE table_name = 'weather_history'")
if (mycursor.fetchone()[0] == 0):
    mycursor.execute("CREATE TABLE weather_history (date DATE, "
                 "clock_time VARCHAR(20), latitude DOUBLE, "
                 "longitude DOUBLE, temp_val DOUBLE, humidity_val DOUBLE, "
                 "cloudi_val DOUBLE, rain_val DOUBLE, "
                 "wind_val DOUBLE, weather_symbol VARCHAR(30)) ")

mycursor.execute(" SELECT count(*) FROM information_schema.tables WHERE table_name = 'weather_forecast'")
if (mycursor.fetchone()[0] == 0):
    mycursor.execute("CREATE TABLE weather_forecast (date DATE, "
                 "clock_time VARCHAR(20), latitude DOUBLE, "
                 "longitude DOUBLE, temp_val DOUBLE, humidity_val DOUBLE, "
                 "cloudi_val DOUBLE, rain_val DOUBLE, "
                 "wind_val DOUBLE, weather_symbol VARCHAR(30)) ")

def weather_retrieval(latitude, longitude):
    #Function which takes any given latitude and longitude, and writes the 24 hour forecast to database (forecast table) AS WELL as the current weather condition (weather history table).

    #Set current time, rounded up to the hour
    current_time = datetime.now() + timedelta(hours=1)
    current_time = current_time.strftime("%H:%M:%S")
    current_time = current_time[0:2] + ":00:00"

    URL = "http://metwdb-openaccess.ichec.ie/metno-wdb2ts/locationforecast?lat=" + str(latitude) + ";long=" + str(longitude)

    response = requests.get(URL)
    xmltxt = response.content

    x = xmltodict.parse(xmltxt)
    json_weather = json.dumps(x)

    weather_obj = json.loads(json_weather)
    weather_dic = weather_obj['weatherdata']

    weather_symbol, time, temp_val, cloudi_val, wind_val, rain_val, clock_time, date, humidity_val = '', '', '', '', '', '', '', '', ''

    #Loop through XML
    for i in range(1, 49):
        for obj in weather_dic['product']['time'][i]:
            data_titles_overview = weather_dic['product']['time'][i]
            for data in data_titles_overview:
                weather_status = data_titles_overview[data]
                for key in weather_status:
                    if len(key) == 1 and key != " ":
                        time += key
                        clock_time = time[19:27]
                        date = time[8:18]
                    if len(key) > 1:
                        weather_each = weather_status[key]
                        for key2 in weather_each:
                            if not isinstance(weather_each, dict):
                                pass
                            else:
                                column = key
                                data = weather_each[key2]
                                if column == 'temperature' and '@value' in key2:
                                    temp_val = data + ' '
                                elif column == 'humidity' and '@value' in key2:
                                    humidity_val = data
                                elif column == 'cloudiness' and '@percent' in key2:
                                    cloudi_val = data
                                elif column == 'windSpeed' and '@mps' in key2:
                                    wind_val = data
                                elif column == 'precipitation' and '@value' in key2:
                                    rain_val = data
                                elif column == 'symbol' and '@id' in key2:
                                    weather_symbol = data
            if temp_val == '':
                pass
            else:
                info_weather = ()
                info_weather = info_weather +((date, clock_time, latitude, longitude, temp_val, humidity_val, cloudi_val, rain_val, wind_val, weather_symbol),)
                if clock_time == current_time:
                    #If weather data is the closest forecast
                    weather_db(info_weather, "history")
                weather_db(info_weather, "forecast")
                weather_symbol, time, temp_val, cloudi_val, wind_val, rain_val, clock_time, date, humidity_val = '', '', '', '', '', '', '', '', ''
                break


def weather_db(x, table):
    try:
        if table == "history":
            sql = "INSERT INTO weather_history (date, clock_time, latitude, longitude, temp_val, humidity_val, cloudi_val, rain_val, wind_val, weather_symbol) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        else:
            sql = "INSERT INTO weather_forecast (date, clock_time, latitude, longitude, temp_val, humidity_val, cloudi_val, rain_val, wind_val, weather_symbol) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

        mycursor.executemany(sql, x)
        mydb.commit()

    except Exception as e:
        print(e)
        print("ERROR: Database Failed!")
        return


APIKEY = dbinfo.APIKEY
NAME = "Dublin"
Stations = "https://api.jcdecaux.com/vls/v1/stations"

r = requests.get(Stations,
                 params={"apiKey": APIKEY, "contract": NAME})
bikes_obj = json.loads(r.text)
info_bikes = ()

for i in range(0, len(bikes_obj) - 1):
    try:
        latitude = bikes_obj[i]["position"]["lat"]
        longitude = bikes_obj[i]["position"]["lng"]
        print("WRITING STATION: Latitude =", latitude,'| Longitude =', longitude)
        weather_retrieval(latitude, longitude)
    except:
        print("Error with station", str(bikes_obj[i]["number"]))
        print(bikes_obj[i])

print("WEATHER SCRIPT FINISHED:", datetime.now())