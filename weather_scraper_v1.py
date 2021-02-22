import json
import xmltodict
import requests

from datetime import datetime, timedelta

#set current time, rounded up to the hour
current_time = datetime.now() + timedelta(hours=1)
current_time = current_time.strftime("%H:%M:%S")
current_time = current_time[0:2] + ":00:00"

def weather_retrieval(latitude, longitude):

    URL = "http://metwdb-openaccess.ichec.ie/metno-wdb2ts/locationforecast?lat=" + str(latitude) + ";long=" + str(longitude)

    response = requests.get(URL)
    xmltxt = response.content

    x = xmltodict.parse(xmltxt)
    json_weather = json.dumps(x)

    weather_obj = json.loads(json_weather)
    weather_dic = weather_obj['weatherdata']

    time, temp_val, cloudi_val, wind_val, rain_val, clock_time, date, humidity_val = '', '', '', '', '', '', '', ''

    #Loop through XML
    for i in range(0, 48, 2):
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
            if temp_val == '':
                pass
            else:
                if clock_time == current_time:
                    # If weather data is the closest forecast
                    print("PLACEHOLDER: WRITE THIS DATA TO WEATHER HISTORY DB")
                print(date + ' ' + clock_time + ' ' + temp_val + ' ' + wind_val + ' ' + cloudi_val + ' ' + rain_val + ' ' + humidity_val)
                temp_val = ''
                wind_val = ''
                cloudi_val = ''
                rain_val = ''
                clock_time = ''
                date = ''
                time = ''
                humidity_val = ''
                break

weather_retrieval(53.2734, -7.77832031)