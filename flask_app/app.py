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
    p = 0.017453292519943295
    a = 0.5 - cos((lat2-lat1)*p)/2 + cos(lat1*p)*cos(lat2*p) * (1-cos((lon2-lon1)*p)) / 2
    return 12742 * asin(sqrt(a))


def closest(data, v):
    return min(data, key=lambda p: distance(float(v['latitude']), float(v['longitude']), float(p['latitude']), float(p['longitude'])))

def nearest_stat(x):
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
    """Returns individual stations to html"""

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
        print("post")
        time_from_midnight = request.form.get("times")
        day_check = request.form.get("days")
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
        test = y[y["clock_time"] == time_from_midnight + ":00:00"]
        time = int(time_from_midnight) * 60
        temp_val = test["temp_val"].values[0]
        rain_val = test["rain_val"].values[0]
        wind_val = test["wind_val"].values[0]
        mon = tue = wed = thur = fri = sat = sun = 0
        day_check = int(day_check)
        if (day_check) ==0:
            mon=1
        elif (day_check ==1):
            tue = 1
        elif (day_check ==2):
            wed = 1
        elif (day_check ==3):
            thur = 1
        elif (day_check ==4):
            fri = 1
        elif (day_check ==5):
            sat = 1
        elif (day_check ==6):
            sun = 1
        test_arr = np.array([time/1439, temp_val/30, rain_val/2, wind_val/20, pow(int(time),2)/(1439 ** 2), pow(temp_val,2)/(30 ** 2), pow(rain_val,2)/(2 ** 2), pow(wind_val,2)/(20 ** 2),
             pow(int(time),3)/(1439 ** 3), pow(temp_val,3)/(30 ** 3), pow(rain_val,3)/(2 ** 3), pow(wind_val,3)/(20 ** 3), fri, mon, sat, sun, thur, tue, wed]).reshape(1,-1)
        loaded_model = joblib.load(str(x["Station_number"][0]) + ".sav")
        avail_bikes = loaded_model.predict(test_arr)
        avail_bikes = int(avail_bikes[0])
        result = pd.DataFrame({"available_bikes":[avail_bikes], "available_bike_stands":[(40-avail_bikes)], "time":[(time_from_midnight + ":00:00")]})
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
        return render_template("stations_individual.html", indiv_stat=x, weather_data=y, user=x)

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