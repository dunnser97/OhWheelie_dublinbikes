from flask import Flask, render_template
import pandas as pd
from sqlalchemy import create_engine
import dbinfo
from flask_caching import Cache
import datetime

cache = Cache()
app = Flask(__name__, template_folder='templates')
app.config['CACHE_TYPE'] = 'simple'

cache.init_app(app)

@app.route("/")

@app.route("/index")
def hello():
    return render_template("index.html")

@app.route("/index/<int:station_id>")
def weather(station_id):
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
    engine = create_engine(dbinfo.engine)
    row_query = "select FLOOR(AVG(available_bikes)) as avg,  date_format(DATE_ADD(bikes.time, interval 30 minute), '%H:00:00') as T from dbbikes_info as bikes where bikes.Station_number =" + str(format(station_id)) + " group by T ORDER BY T ASC;"
    df1 = pd.read_sql_query(row_query, engine)
    return df1.to_json(orient="records")



@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/stations")
@cache.cached(timeout=600)
def stations():
    engine = create_engine(dbinfo.engine, echo=True)
    date = datetime.datetime.now()
    date_1 = date.strftime("%m")
    date_2 = date.strftime("%d")
    date_2 = int(date_2)
    month = int(date_1)
    if (month > 3 and month < 11) or (month == 3 and date_2 > 27):
        row_query = "select address, available_bike_stands, available_bikes, banking, bike_stands, date, ADDTIME(time, '1:00:00') as time, name, Station_number, latitude, longitude, status from dbbikes_current_info order by address asc"
        df = pd.read_sql_query(row_query, con=engine)
        df['time'] = df['time'].astype(str)
        return df.to_json(orient="records")
    else:
        row_query = "select address, available_bike_stands, available_bikes, banking, bike_stands, date, time, name, Station_number, latitude, longitude, status from dbbikes_current_info order by address asc"
        df = pd.read_sql_query(row_query, con=engine)
        df['time'] = df['time'].astype(str)
        # print(df.head(3).to_json(orient="records"))
        return df.to_json(orient="records")

@app.route("/allstations/<int:station_id>")
@cache.cached(timeout=600)
def station(station_id):
    engine = create_engine(dbinfo.engine)
    bike_engine = create_engine(dbinfo.bike_engine)
    x = station_num(bike_engine, station_id)
    lat = x["latitude"]
    long = x["longitude"]
    if x.shape[0] == 0:
        return "<h1>Error 404 - Page Not Found</h1>"
    y = station_weather(engine, lat, long)
    return render_template("stations_individual.html", indiv_stat=x, weather_data=y)

@app.route("/allstations")
def allstations():
    return render_template("stations.html")

def station_num(bike_engine, station_id):
    date = datetime.datetime.now()
    date_1 = date.strftime("%m")
    date_2 = date.strftime("%d")
    date_2 = int(date_2)
    month = int(date_1)
    if (month > 3 and month < 11) or (month == 3 and date_2 > 27):
        row_query = "select address, available_bike_stands, available_bikes, banking, bike_stands, date, ADDTIME(time, '1:00:00') as time, name, Station_number, latitude, longitude, status from dbbikes_current_info where Station_number = " + str(format(station_id))
        x = pd.read_sql_query(row_query, bike_engine)
        return x
    else:
        row_query = "select * from dbbikes_current_info where Station_number = " + str(format(station_id))
        x = pd.read_sql_query(row_query, bike_engine)
        return x

def station_weather(engine, lat, long):
    date = datetime.datetime.now()
    date_1 = date.strftime("%m")
    date_2 = date.strftime("%d")
    date_2 = int(date_2)
    month = int(date_1)
    if (month > 3 and month < 11) or (month == 3 and date_2 > 27):
        row_query_1 = " select date, ADDTIME(clock_time, '1:00:00') as clock_time , latitude, longitude, temp_val, humidity_val, cloudi_val, rain_val, wind_val, weather_symbol from weather_forecast where latitude = " + str(format(lat[0])) + "and longitude = " + str(
            format(long[0])) + "group by clock_time"
        y = pd.read_sql_query(row_query_1, engine)
        return y
    else:
        row_query_1 = "select * from weather_forecast where latitude = " + str(format(lat[0])) + "and longitude = " + str(
            format(long[0])) + "group by clock_time"
        y = pd.read_sql_query(row_query_1, engine)
        return y

@app.route("/allstations/<int:station_id>/temp")
def temperature(station_id):
    engine = create_engine(dbinfo.engine)
    bike_engine = create_engine(dbinfo.bike_engine)
    x = station_num(bike_engine, station_id)
    lat = x["latitude"]
    long = x["longitude"]
    date = datetime.datetime.now()
    date_1 = date.strftime("%m")
    date_2 = date.strftime("%d")
    date_2 = int(date_2)
    month = int(date_1)
    if (month > 3 and month < 11) or (month == 3 and date_2 > 27):
        cur_temp = "SELECT temp_val, ADDTIME(clock_time, '1:00:00') as clock_time FROM weather_hourDB.weather_forecast " \
                   "where longitude = " + str(format(long[0])) + " and latitude = " + str(format(lat[0])) +";"
        temp = pd.read_sql_query(cur_temp, engine)
        return temp.to_json(orient="records")
    else:
        cur_temp = "SELECT temp_val, clock_time FROM weather_hourDB.weather_forecast " \
                   "where longitude = " + str(format(long[0])) + " and latitude = " + str(format(lat[0])) + ";"
        temp = pd.read_sql_query(cur_temp, engine)
        return temp.to_json(orient="records")

@app.route("/allstations/<int:station_id>/avg_bikes_day")
def avg_bikes_day(station_id):
    bike_engine = create_engine(dbinfo.bike_engine)
    day_avg = "select floor(AVG(available_bikes)) as avg_day, weekday(date) as day from dbbikes_info where Station_number = "  + str(format(station_id)) +  \
        " and time Between '06:00:00' AND '20:00:00' group by weekday(date) order by weekday(date) asc;"
    day_avg_db = pd.read_sql_query(day_avg, bike_engine)
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
