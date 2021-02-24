import json
import xmltodict
import requests
import mysql.connector
import time

from datetime import datetime, timedelta

def weather_retrieval(latitude, longitude):
    ## IDEA FOR SCRAPER IS TO INSERT ARGS THAT CHANGE THE RANGE
    ## so will look like def weather_retrieval(latitude, longitude, *args)
    ## when args = '', make range 48 just and do the current weather push to history db
    ## when args == 'forecast', range == 100 and push the weather for the next 48 hours to forecast table
    ## when user wants forcast for x station tomorrow, scraper extends range and sends to the forecast db
    ## then query whichever time they want to get weather and send to ML algorithm for prediction
    ## clear the forecast db every few hours because they change so frequently
    '''Function which takes any given latitude and longitude,'''

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
    for i in range(1, 48):
        for obj in weather_dic['product']['time'][i]:
            data_titles_overview = weather_dic['product']['time'][i]
            data_titles_overview_rain = weather_dic['product']['time'][i+1]
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
                    weather_db(info_weather)
                    print("DATE:" + date + '  TIME:' + clock_time + '  Temperature:' + temp_val + ' Wind:' + wind_val + '  Cloudiness:' + cloudi_val + '  Rain:' + rain_val + '  Humidity:' + humidity_val + '  Weather Symbol:' + weather_symbol)
                weather_symbol, time, temp_val, cloudi_val, wind_val, rain_val, clock_time, date, humidity_val = '', '', '', '', '', '', '', '', ''
                break


def weather_db(x):
    try:
        sql = "INSERT INTO weather_history (date, clock_time, latitude, longitude, temp_val, humidity_val, cloudi_val, rain_val, wind_val, weather_symbol) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

        mydb = mysql.connector.connect(
            host="",
            user="",
            passwd="",
            database="",
            charset="",
        )
        mycursor = mydb.cursor(dictionary=False)

        mycursor.execute(" SELECT count(*) FROM weather_hourDB.weather_history")
        if (mycursor.fetchone()[0] == 0):
            mycursor.execute("CREATE TABLE weather_history (date DATE, "
                         "clock_time VARCHAR(20), latitude DOUBLE, "
                         "longitude DOUBLE, temp_val DOUBLE, humidity_val DOUBLE, "
                         "cloudi_val DOUBLE, rain_val DOUBLE, "
                         "wind_val DOUBLE, weather_symbol VARCHAR(30)) ")
        mycursor.executemany(sql, x)
        mydb.commit()
        print("Weather written to Database")
    except Exception as e:
        print(e)
        print("ERROR: Database Failed!")
        return

while True:
    weather_retrieval(51.2734, -20.77832031)
    time.sleep(60 * 60)
