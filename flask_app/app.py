import joblib
from flask import Flask, render_template, request
import pandas as pd
from sqlalchemy import create_engine
import dbinfo
import numpy as np
from flask_caching import Cache
import datetime
from math import cos, asin, sqrt

cache = Cache()
app = Flask(__name__, template_folder='templates')
app.config['CACHE_TYPE'] = 'simple'

cache.init_app(app)

def distance(lat1, lon1, lat2, lon2):
    """Returns distance between two co-ords"""
    p = 0.017453292519943295
    a = 0.5 - cos((lat2-lat1)*p)/2 + cos(lat1*p)*cos(lat2*p) * (1-cos((lon2-lon1)*p)) / 2
    return 12742 * asin(sqrt(a))


def closest(data, v):
    """Returns closest from dataset of station to inputted co-ords - v"""
    return min(data, key=lambda p: distance(float(v['latitude']), float(v['longitude']), float(p['latitude']), float(p['longitude'])))

def nearest_stat(x):
    """Takes address, lat and long oof all stations, generates user co-ords and returns nearest station"""
    dict = x.to_dict('records')
    hard_coded_lat = 53.328764
    hard_coded_lng = -6.271060
    simulated_user_location = {'latitude': hard_coded_lat, 'longitude': hard_coded_lng}
    return closest(dict, simulated_user_location)

@app.route("/")

@app.route("/index")
def hello():
    return render_template("index.html")

@app.route("/index/<int:station_id>")
def weather(station_id):
    """Returns individual stations weather to html"""

    engine = create_engine(dbinfo.engine)
    bike_engine = create_engine(dbinfo.bike_engine)
    x = station_num(bike_engine, station_id)
    lat = x["latitude"]
    long = x["longitude"]
    y = station_weather(engine, lat, long)
    x['time'] = x['time'].astype(str)
    #print(y.head(2))
    return y.to_json(orient="records")

@app.route("/index/<int:station_id>/chart")
def avg_bike_data(station_id):
    """Returns avg bikes for individual station to html"""
    engine = create_engine(dbinfo.engine)
    #Selects average bikes where bikes are put within their interval period split by hour.
    row_query = "select FLOOR(AVG(available_bikes)) as avg,  date_format(DATE_ADD(bikes.time, interval 30 minute), '%H:00:00') as T " \
                "from dbbikes_info as bikes where bikes.Station_number =" + str(format(station_id)) + \
                " group by T ORDER BY T ASC;"
    df1 = pd.read_sql_query(row_query, engine)
    return df1.to_json(orient="records")



@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/stations")
@cache.cached(timeout=600)
def stations():
    """Returns all stations to html accounting for time differences"""
    engine = create_engine(dbinfo.engine, echo=False)
    #Checks current date and passes them as integer values representing month and date
    date = datetime.datetime.now()
    date_1 = date.strftime("%m")
    date_2 = date.strftime("%d")
    date_2 = int(date_2)
    month = int(date_1)

    #If it is a date betweeen 03/27 to 03/31 then adds 1 to convert from gmt to local time
    if (month > 3 and month < 11) or (month == 3 and date_2 > 27) or (month == 10 and date_2 > 31):
        #selects most columns from current info database and sorts in ascending order by name
        row_query = "select address, available_bike_stands, available_bikes, banking, bike_stands, date, " \
                    "ADDTIME(time, '1:00:00') as time, name, Station_number, latitude, longitude, status " \
                    "from dbbikes_current_info order by address asc"
        df = pd.read_sql_query(row_query, con=engine)
        #Error occurred where time was converting back to integer. Change of type to string solved this.
        df['time'] = df['time'].astype(str)
        dflatlong = df[['address', 'latitude', 'longitude']]

        nearest = nearest_stat(dflatlong)
        stations = df.to_json(orient="records")
        return {'stations': stations, 'nearest': nearest}

    #else utc = localtime
    else:
        row_query = "select address, available_bike_stands, available_bikes, banking, bike_stands, " \
                    "date, time, name, Station_number, latitude, longitude, status " \
                    "from dbbikes_current_info order by address asc"
        df = pd.read_sql_query(row_query, con=engine)
        df['time'] = df['time'].astype(str)
        dflatlong = df[['address', 'latitude', 'longitude']]

        nearest = nearest_stat(dflatlong)
        stations = df.to_json(orient="records")
        return {'stations': stations, 'nearest': nearest}


@app.route("/allstations/<int:station_id>", methods = ['GET','POST'])
#@cache.cached(timeout=600)
def station(station_id):

    """Returns individual stations html"""

    if request.method == 'POST':
        time_from_midnight = request.form.get("times")
        day_check = request.form.get("days")
        time_object = datetime.datetime.now()
        #If Either day or time is unselected will give todays day and 1 hour forward
        if (day_check == "-1"):
            day_check = datetime.datetime.today().weekday()
        if (time_from_midnight == "-1"):
            time_from_midnight = int(time_object.strftime("%H")) + 1
            if time_from_midnight <10:
                time_from_midnight =  "0" + str(time_from_midnight)
            else:
                time_from_midnight = str(time_from_midnight)
        # Intialises database for bikes and weather
        engine = create_engine(dbinfo.engine)
        bike_engine = create_engine(dbinfo.bike_engine)
        # calls station_num function returning all info bikes database
        x = station_num(bike_engine, station_id)
        # Extracts longitude and latitude to feed to station_weather function
        lat = x["latitude"]
        long = x["longitude"]
        if x.shape[0] == 0:
            return "<h1>Error 404 - Page Not Found</h1>"
        # calls station_weather function returning all info weather database with longitude and latitude from above
        y = station_weather(engine, lat, long)
        predict_db = y[y["clock_time"] == time_from_midnight + ":00:00"]
        #Changes time to be minutes
        time = int(time_from_midnight) * 60
        #converts day_check to integer for the below check to see what day is being requested
        day_check = int(day_check)
        mon = tue = wed = thur = fri = sat = sun = 0
        if (day_check) ==0:
            day ="Monday"
            mon=1
        elif (day_check ==1):
            day = "Tuesday"
            tue = 1
        elif (day_check ==2):
            day = "Wednesday"
            wed = 1
        elif (day_check ==3):
            day = "Thursday"
            thur = 1
        elif (day_check ==4):
            day = "Friday"
            fri = 1
        elif (day_check ==5):
            day = "Saturday"
            sat = 1
        else:
            day = "Sunday"
            sun = 1

        dt_string = int(time_object.strftime("%H"))
        date_temp = datetime.datetime.today().weekday()
        month_temp = datetime.datetime.now()
        month_temp = int(month_temp.strftime("%m")) -1

        #Function Checks if day is in the next 24 hours for which forecast information is available and applies it to the predictive model
        if date_temp == day_check or (day_check%7 == 1 and dt_string-1 > int(time_from_midnight)):
            temp_val = predict_db["temp_val"].values[0]
            rain_val = predict_db["rain_val"].values[0]
            wind_val = predict_db["wind_val"].values[0]
            test_arr = np.array([time / 1439, temp_val / 30, rain_val / 2, wind_val / 20, pow(int(time), 2) / (1439 ** 2),pow(temp_val, 2) / (30 ** 2), pow(rain_val, 2) / (2 ** 2), pow(wind_val, 2) / (20 ** 2),pow(int(time), 3) / (1439 ** 3), pow(temp_val, 3) / (30 ** 3), pow(rain_val, 3) / (2 ** 3),pow(wind_val, 3) / (20 ** 3), fri, mon, sat, sun, thur, tue, wed]).reshape(1, -1)
            loaded_model = joblib.load(str(x["Station_number"][0]) + ".sav")
            avail_bikes = loaded_model.predict(test_arr)
            avail_bikes = int(avail_bikes[0])
            # Returns information as a dataframe to be read in HTML
            result = pd.DataFrame({"available_bikes": [avail_bikes], "available_bike_stands": [(40 - avail_bikes)],"time": [(day +"\n" + time_from_midnight + ":00:00")]})
            return render_template("stations_individual.html", indiv_stat=x, weather_data=y, user=result)

        #Otherwise it will select the average values for the weather for a day and month previously gone by
        else:
            avg_day_over = "SELECT AVG(temp_val), AVG(rain_val), AVG(wind_val) " \
                           "FROM weather_hourDB.weather_history " \
                           "where weekday(date) = " + str(day_check) +" and month(date) = " + str(month_temp) + " and latitude = " + lat[0]  +" and longitude = " + long[0] + ";"
            avg_day_db = pd.read_sql_query(avg_day_over, engine)
            temp_val = avg_day_db["AVG(temp_val)"].values[0]
            rain_val = avg_day_db["AVG(rain_val)"].values[0]
            wind_val = avg_day_db["AVG(wind_val)"].values[0]
            test_arr = np.array([time / 1439, temp_val / 30, rain_val / 2, wind_val / 20, pow(int(time), 2) / (1439 ** 2),pow(temp_val, 2) / (30 ** 2), pow(rain_val, 2) / (2 ** 2), pow(wind_val, 2) / (20 ** 2),pow(int(time), 3) / (1439 ** 3), pow(temp_val, 3) / (30 ** 3), pow(rain_val, 3) / (2 ** 3),pow(wind_val, 3) / (20 ** 3), fri, mon, sat, sun, thur, tue, wed]).reshape(1, -1)
            loaded_model = joblib.load(str(x["Station_number"][0]) + ".sav")
            avail_bikes = loaded_model.predict(test_arr)
            avail_bikes = int(avail_bikes[0])
            #Returns information as a dataframe to be read in HTML
            result = pd.DataFrame({"available_bikes": [avail_bikes], "available_bike_stands": [(40 - avail_bikes)], "time": [(day + " " +  time_from_midnight + ":00:00")]})
            return render_template("stations_individual.html", indiv_stat=x, weather_data=y, user=result)



    else:
        # Intialises database for bikes and weather
        engine = create_engine(dbinfo.engine)
        bike_engine = create_engine(dbinfo.bike_engine)
        # calls station_num function returning all info bikes database
        x = station_num(bike_engine, station_id)
        # Extracts longitude and latitude to feed to station_weather function
        lat = x["latitude"]
        long = x["longitude"]
        if x.shape[0] == 0:
            return "<h1>Error 404 - Page Not Found</h1>"
        # calls station_weather function returning all info weather database with longitude and latitude from above
        y = station_weather(engine, lat, long)
        time_object = datetime.datetime.now()
        time_from_midnight = str(time_object.strftime("%H"))
        result = pd.DataFrame({"available_bikes": [x.available_bikes[0]], "available_bike_stands": [x.available_bike_stands[0]], "time": [(time_from_midnight + ":00:00")]})
        return render_template("stations_individual.html", indiv_stat=x, weather_data=y, user=result)

@app.route("/allstations")
def allstations():
    return render_template("stations.html")

def station_num(bike_engine, station_id):
    """Gets information on current bike info
    returns it to various webpages as called by flask
    """

    #Checks daylight savings if between 28 march to October 31st adds 1 hour to utc time from database
    date = datetime.datetime.now()
    date_1 = date.strftime("%m")
    date_2 = date.strftime("%d")
    date_2 = int(date_2)
    month = int(date_1)
    if (month > 3 and month < 11) or (month == 3 and date_2 > 27) or (month == 10 and date_2 > 31):
        row_query = "select address, available_bike_stands, available_bikes, banking, bike_stands, date, " \
                    "ADDTIME(time, '1:00:00') as time, name, Station_number, latitude, longitude, status " \
                    "from dbbikes_current_info where Station_number = " + str(format(station_id))
        x = pd.read_sql_query(row_query, bike_engine)
        return x
    else:
        row_query = "select * from dbbikes_current_info where Station_number = " + str(format(station_id))
        x = pd.read_sql_query(row_query, bike_engine)
        return x

def station_weather(engine, lat, long):
    """Gets information on current weather forcast
        returns it to various webpages as called by flask
        """
    # Checks daylight savings if between 28 march to October 31st adds 1 hour to utc time from database
    date = datetime.datetime.now()
    date_1 = date.strftime("%m")
    date_2 = date.strftime("%d")
    date_2 = int(date_2)
    month = int(date_1)
    if (month > 3 and month < 11) or (month == 3 and date_2 > 27) or (month == 10 and date_2 > 31):
        #Selects columns from weather forecast where latitude and longitude are given as inputs into the function and grouped by time
        row_query_1 = " select date, ADDTIME(clock_time, '1:00:00') as clock_time , latitude, longitude, temp_val, " \
                      "humidity_val, cloudi_val, rain_val, wind_val, weather_symbol, weekday(date) as day  " \
                      "from weather_forecast " \
                      "where latitude = " + str(format(lat[0])) + " and longitude = " + str(format(long[0])) + \
                      " group by clock_time"
        y = pd.read_sql_query(row_query_1, engine)
        return y
    else:
        row_query_1 = "select date, ADDTIME(clock_time, '1:00:00') as clock_time , latitude, longitude, temp_val, " \
                      "humidity_val, cloudi_val, rain_val, wind_val, weather_symbol, weekday(date) as day  " \
                      "from weather_forecast where latitude = " + str(format(lat[0])) + " and longitude = " + str(format(long[0])) + " group by clock_time"
        y = pd.read_sql_query(row_query_1, engine)
        return y

@app.route("/allstations/<int:station_id>/temp")
def temperature(station_id):
    """Selects temperature values for the upcoming day
    returns as json object
    """
    engine = create_engine(dbinfo.engine)
    bike_engine = create_engine(dbinfo.bike_engine)
    #Station_num called to obtain the latitude and longitude of the wanted station
    x = station_num(bike_engine, station_id)
    lat = x["latitude"]
    long = x["longitude"]
    date = datetime.datetime.now()
    date_1 = date.strftime("%m")
    date_2 = date.strftime("%d")
    date_2 = int(date_2)
    month = int(date_1)
    if (month > 3 and month < 11) or (month == 3 and date_2 > 27) or (month == 10 and date_2 > 31):
        #Selects all temperature values in forcast with time +1 as daylight savings in Ireland
        cur_temp = "SELECT temp_val, ADDTIME(clock_time, '1:00:00') as clock_time FROM weather_hourDB.weather_forecast " \
                   "where longitude = " + str(format(long[0])) + " and latitude = " + str(format(lat[0])) +";"
        temp = pd.read_sql_query(cur_temp, engine)
        return temp.to_json(orient="records")
    else:
        # Selects all temperature values in forcast from given longitude and latitude
        cur_temp = "SELECT temp_val, clock_time FROM weather_hourDB.weather_forecast " \
                   "where longitude = " + str(format(long[0])) + " and latitude = " + str(format(lat[0])) + ";"
        temp = pd.read_sql_query(cur_temp, engine)
        return temp.to_json(orient="records")

@app.route("/allstations/<int:station_id>/avg_bikes_day")
def avg_bikes_day(station_id):
    """Returns average bikes per day of station as object to html"""
    bike_engine = create_engine(dbinfo.bike_engine)
    #selects avg available bikes floored and the weekday given as an integer where 0 is Monday
    #Only checks bike availability between 6 and 8 as bikes cannot be removed after 12. Thus this interval was chosen for a more meaningful average
    day_avg = "select floor(AVG(available_bikes)) as avg_day, weekday(date) as day from dbbikes_info where Station_number = "  + str(format(station_id)) +  \
        " and time Between '06:00:00' AND '20:00:00' group by weekday(date) order by weekday(date) asc;"
    day_avg_db = pd.read_sql_query(day_avg, bike_engine)
    #Renames numbers as the day each represents for graphical representation.
    day_avg_db["day"].replace({0:"Monday",1:"Tueday", 2:"Wednesday", 3:"Thursday", 4:"Friday", 5:"Saturday", 6:"Sunday"}, inplace=True)
    return day_avg_db.to_json(orient="records")


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>Error 404 - Page Not Found</h1>"

@app.errorhandler(500)
def server_error(e):
    return "<h1>Error 500</h1>"

if __name__ == "__main__":
    app.run(debug=True, port=5000)