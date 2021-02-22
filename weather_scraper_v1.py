import json
import xmltodict
import requests

lat = "54.7211"
long= "-8.7237"

URL = "http://metwdb-openaccess.ichec.ie/metno-wdb2ts/locationforecast?lat=" + lat + ";long=" + long

response = requests.get(URL)
xmltxt = response.content

x = xmltodict.parse(xmltxt)
json_weather = json.dumps(x)

weather_obj = json.loads(json_weather)
weather_dic = weather_obj['weatherdata']

time, temp_val, cloudi_val, wind_val, rain_val, clock_time, date = '', '', '', '', '', '', ''

for i in range(0, 48, 2):
    for obj in weather_dic['product']['time'][i]:
        data_titles_overview = weather_dic['product']['time'][i]
        for data in data_titles_overview:
            weather_status = data_titles_overview[data]
            weather_string_and_dic = weather_status
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
                            if column == 'humidity' and '@value' in key2:
                                humidity_val = data
                            if column == 'cloudiness' and '@percent' in key2:
                                cloudi_val = data
                            if column == 'windSpeed' and '@mps' in key2:
                                wind_val = data
                            if column == 'precipitation' and '@value' in key2:
                                rain_val = data
        if temp_val == '':
            pass
        else:
            print(date + ' ' + clock_time + ' ' + temp_val + ' ' + wind_val + ' ' + cloudi_val + ' ' + rain_val)
            temp_val = ''
            wind_val = ''
            cloudi_val = ''
            rain_val = ''
            clock_time = ''
            date = ''
            time = ''
            break
