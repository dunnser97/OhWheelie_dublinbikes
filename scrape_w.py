
import json
import requests
import mysql.connector
import dbinfo
from datetime import datetime
import time

mydb = mysql.connector.connect(
            host=dbinfo.host,
            user=dbinfo.user,
            passwd=dbinfo.passwd,
            database=dbinfo.database,
            charset=dbinfo.charset
        )
mycursor = mydb.cursor(dictionary=False)
epoch_start_time = time.time()
APIKEY = "506c510e623a5c7c5526de04c7e769f9"

#URL = "https://api.openweathermap.org/data/2.5/onecall?lat=" +str(latitude) + "&long=" + str(longitude) +"&exclude=minutely&appid=506c510e623a5c7c5526de04c7e769f9'

def collect_weather(lati, longi):
    URL = "https://api.openweathermap.org/data/2.5/onecall?lat=" + str(lati) + "&lon=" + str(
    longi) + "&exclude=minutely&appid=c0df90e98d85453f86f46197e2a4c551"

    response = requests.get(URL)
    weather_obj = json.loads(response.text)
    weather_info = ()
    try:
        long = weather_obj['lon']
        lat = weather_obj['lat']
        today = weather_obj['current']
        date1 = today['dt']
        timestamp = str(datetime.fromtimestamp(date1))
        sunrise = today['sunrise']
        sunset = today['sunset']
        temp = today['temp']
        feels_like = today['feels_like']
        pressure = today['pressure']
        humidity = today['humidity']
        uvi = today['uvi']
        wind_speed = today['wind_speed']
        wind_deg = today['wind_deg']
        clouds = today['clouds']
        visibility = today['visibility']
        weather_detail = today['weather']
        for i in weather_detail:
            for value in i:
                if value == 'main':
                    main = i[value]
                elif value == 'description':
                    desc = i[value]

        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        time_added = time.time()

        #print(timestamp, current_time, long, lat, temp, feels_like, min_temp, max_temp, pressure, humidity, wind_speed, wind_deg, clouds,
        #      visibility, sunrise, sunset, main, desc)
        weather_info = weather_info + ((timestamp, current_time, long, lat, temp, uvi, feels_like, pressure, humidity, wind_speed,
             wind_deg, clouds, visibility, sunrise, sunset, main, desc, time_added),)
        print(weather_info)
        initiate_db()
        get_48_hour_weather(long, lat, weather_obj['hourly'])
        send_weather(weather_info, 'current')

    except Exception as e:
        print(e)
        print('error')

def get_48_hour_weather(long, lat, obj):
    forecast = ()
    for i in range(0, len(obj)):
        ft_date = obj[i]['dt']
        timestamp = datetime.fromtimestamp(ft_date)
        #print(timestamp.strftime('%Y-%m-%d %H:%M:%S'))
        ft_temp = obj[i]['temp']
        ft_feels_like = obj[i]['feels_like']
        ft_pressure = obj[i]['pressure']
        ft_humidity = obj[i]['humidity']
        ft_uvi = obj[i]['uvi']
        ft_wind_speed = obj[i]['wind_speed']
        ft_wind_deg = obj[i]['wind_deg']
        ft_clouds = obj[i]['clouds']
        ft_visibility = obj[i]['visibility']
        ft_weather_detail = obj[i]['weather']
        for detail in ft_weather_detail:
            for value in detail:
                if value == 'main':
                    ft_main = detail[value]
                elif value == 'description':
                    ft_desc = detail[value]
        time_added = time.time()
        #print(long, lat, timestamp, ft_temp, ft_feels_like, ft_pressure, ft_humidity, ft_wind_speed, ft_wind_deg, ft_clouds,
        #      ft_visibility, ft_main, ft_desc)
        forecast = forecast + ((timestamp, long, lat, ft_temp, ft_feels_like, ft_uvi, ft_pressure, ft_humidity, ft_wind_speed, ft_wind_deg, ft_clouds,
              ft_visibility, ft_main, ft_desc, time_added),)

        #send_weather(forecast, 'future')

def initiate_db():
    try:
        print('testing db')

        mydb = mysql.connector.connect(
            host=dbinfo.host,
            user=dbinfo.user,
            passwd=dbinfo.passwd,
            database=dbinfo.database,
            charset=dbinfo.charset
        )

        # Check if both tables exist. If they don't, create them.
        mycursor = mydb.cursor(dictionary=False)
        mycursor.execute(" SELECT count(*) FROM information_schema.tables WHERE table_name = 'weather_new_hist'")
        if (mycursor.fetchone()[0] == 0):
            mycursor.execute("CREATE TABLE weather_new_hist (timestamp VARCHAR(30), "
                             "time VARCHAR(30), longitude DOUBLE, "
                             "latitude DOUBLE, temp_val DOUBLE, uvi DOUBLE, feels_like DOUBLE, "
                             "pressure DOUBLE, humidity DOUBLE, wind_speed DOUBLE, wind_deg DOUBLE, "
                             "cloudy DOUBLE, visibility DOUBLE, sunrise DOUBLE, sunset DOUBLE, "
                             "main_weather VARCHAR(30), "
                            "descript VARCHAR(30), time_added INT ) ")


        mycursor.execute(" SELECT count(*) FROM information_schema.tables WHERE table_name = 'weather_new_forecast'")
        if (mycursor.fetchone()[0] == 0):
            mycursor.execute("CREATE TABLE weather_new_forecast (timestamp VARCHAR(30), "
                             "longitude DOUBLE, "
                             "latitude DOUBLE, temp_val DOUBLE, uvi DOUBLE, feels_like DOUBLE, "
                             "pressure DOUBLE, humidity DOUBLE, wind_speed DOUBLE, wind_deg DOUBLE, "
                             "cloudy DOUBLE, visibility DOUBLE,  "
                             "main_weather VARCHAR(30), "
                              "descript VARCHAR(30), time_added INT ) ")

        mydb.commit()
    except Exception as e:
        print(e)
        print('Failed to create tables')

def send_weather(data, command):
    try:
        mydb = mysql.connector.connect(
            host=dbinfo.host,
            user=dbinfo.user,
            passwd=dbinfo.passwd,
            database=dbinfo.database,
            charset=dbinfo.charset
        )
        mycursor = mydb.cursor(dictionary=False)
        if command == "current":
            sql = "INSERT INTO weather_new_hist VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            # #  "(timestamp, time, longitude, latitude, temp_val, uvi, feels_like, pressure, humidity, wind_speed, wind_deg, cloudy, visibility, sunrise, sunset,  main_weather, descript)
        else:
            sql = "INSERT INTO weather_new_forecast (timestamp, longitude, latitude, temp_val, uvi, feels_like, " \
                    "pressure, humidity, wind_speed, wind_deg, cloudy, visibility, main_weather, descript) " \
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

        mycursor.executemany(sql, data)
        print('done')
        #mycursor.executemany(sql, data)
        mydb.commit()

    except Exception as e:
        print(e)
        print("ERROR: Sending data to database failed!")
        return


def get_cordinates_for_weather():
    APIKEY = dbinfo.APIKEY
    NAME = "Dublin"
    Stations = "https://api.jcdecaux.com/vls/v1/stations"

    r = requests.get(Stations,
                     params={"apiKey": APIKEY, "contract": NAME})
    bikes_obj = json.loads(r.text)
    for i in range(0, len(bikes_obj) - 1):
        try:
            latitude = bikes_obj[i]["position"]["lat"]
            longitude = bikes_obj[i]["position"]["lng"]
            print("WRITING STATION: Latitude =", latitude, '| Longitude =', longitude)
            collect_weather(latitude, longitude)
        except:
            print("Error with station", str(bikes_obj[i]["number"]))
            print(bikes_obj[i])

    try:
        mycursor.execute("DELETE FROM weather_new_forecast WHERE time_added < " + str(epoch_start_time))
        mydb.commit()
    except:
        print("Error deleting previous forecast.")

    print("WEATHER SCRIPT FINISHED:", datetime.now())

get_cordinates_for_weather()
