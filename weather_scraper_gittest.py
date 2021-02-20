import json
import xmltodict
import requests

URL = "http://metwdb-openaccess.ichec.ie/metno-wdb2ts/locationforecast?lat=54.7211;long=-8.7237"

response = requests.get(URL)
xmltxt = response.content

x = xmltodict.parse(xmltxt)
json_weather = json.dumps(x)

weather_obj = json.loads(json_weather)
weather_dic = weather_obj['weatherdata']

long = ''
lat = ''
time = ''
longi = ''
temp_val = ''
cloudi_val = ''
wind_val = ''
rain_val = ''

for i in range(0, 50):
    for obj in weather_dic['product']['time'][i]:
        date = time[8:18]
        clock_time = time[19:27]
        # print(lati)
        lati = ''
        # print(longi)
        longi = ''
        #print(date)
        #print(clock_time)
        time = ''
        data_titles_overview = weather_dic['product']['time'][i]
        # print(data_titles_overview)
        for data in data_titles_overview:
            weather_status = data_titles_overview[data]
            weather_string_and_dic = weather_status
            #print(weather_status)
            for key in weather_status:
                if len(key) == 1 and key != " ":
                    time += key
                if len(key) > 1:
                    weather_each = weather_status[key]
                    #print(key, weather_each)
                    if key == '@latitude':
                        lati += weather_status[key]
                    if key == '@longitude':
                        longi += weather_status[key]
                    for key2 in weather_each:
                        if not isinstance(weather_each, dict):
                            pass
                        else:
                            column = key
                            data = weather_each[key2]
                            if column == 'temperature' and '@value' in key2:
                                temp_val = data + ' '
                                #print(column, data)
                            if column == 'humidity' and '@value' in key2:
                                humidity_val = data
                            if column == 'cloudiness' and '@percent' in key2:
                                cloudi_val = data
                                #print(column, data)
                            if column == 'windSpeed' and'@mps' in key2:
                                wind_val = data
                                #print(column, data)
                            if column == 'precipitation' and '@value' in key2:
                                rain_val = data


        if temp_val == '':
            pass
        else:
            #weather_db(date, clock_time, temp_val, wind_val, cloudi_val, rain_val, longi,
            #            lati)
            print(date + ' '  + clock_time + ' ' + temp_val + ' ' + wind_val + ' ' + cloudi_val + ' ' + rain_val)
            temp_val = ''
            wind_val = ''
            cloudi_val = ''
            rain_val = ''
        break

