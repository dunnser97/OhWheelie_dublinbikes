from flask import Flask, render_template
import pandas as pd
from sqlalchemy import create_engine
import dbinfo
from flask_caching import Cache
import time

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
    engine = create_engine(f"mysql+mysqlconnector://{dbinfo.user}:{dbinfo.passwd}@{dbinfo.host}:3306/{dbinfo.database}",
                           echo=True)
    row_query = "select * from dbbikes_current_info where Station_number = " + str(format(station_id))
    x = pd.read_sql_query(row_query, engine)
    lat = x["latitude"]
    long = x["longitude"]
    x['time'] = x['time'].astype(str)
    row_query_1 = "select * from weather_forecast where latitude = " + str(format(lat[0])) + "and longitude = " + str(
        format(long[0])) + "group by clock_time"
    y = pd.read_sql_query(row_query_1, engine)
    return y.to_json(orient="records")

@app.route("/about")
def about():
    return app.send_static_file("about.html")

@app.route("/stations")
@cache.cached(timeout=600)
def stations():
    engine = create_engine(f"mysql+mysqlconnector://{dbinfo.user}:{dbinfo.passwd}@{dbinfo.host}:3306/{dbinfo.database}", echo=True)
    row_query = "select * from dbbikes_current_info"
    df = pd.read_sql_query(row_query, con=engine)
    df['time'] = df['time'].astype(str)
    print(df.head(3).to_json(orient="records"))
    return df.to_json(orient="records")

@app.route("/allstations/<int:station_id>")
@cache.cached(timeout=600)
def station(station_id):
    engine = create_engine(f"mysql+mysqlconnector://{dbinfo.user}:{dbinfo.passwd}@{dbinfo.host}:3306/{dbinfo.database}")
    sd_engine = create_engine(f"mysql+mysqlconnector://{dbinfo.dbuser}:{dbinfo.dbpasswd}@{dbinfo.dbhost}:3306/{dbinfo.dbdatabase}")
    row_query = "select * from dbbikes_current_info where Station_number = " + str(format(station_id))
    x = pd.read_sql_query(row_query, engine)
    lat = x["latitude"]
    long = x["longitude"]
    row_query_1 = "select * from weather_forecast where latitude = " + str(format(lat[0])) + "and longitude = " + str(format(long[0])) + "group by clock_time"
    y = pd.read_sql_query(row_query_1, engine)
    mean_day = "select AVG(available_bike_stands), weekday(date) from dbbikes_info where Station_number = " + str(format(station_id)) + " and time Between '06:00:00' AND '20:00:00' group by weekday(date) order by weekday(date) asc"
    mean_day = pd.read_sql_query(mean_day, sd_engine)
    mean_time ="select AVG(available_bike_stands), hour(time) from dbbikes_info where Station_number = " + str(format(station_id)) + " group by hour(time) order by hour(time) asc"
    mean_time = pd.read_sql_query(mean_time, sd_engine)
    return render_template("stations_individual.html", indiv_stat=x, weather_data=y)

@app.route("/allstations")
def allstations():
    return render_template("stations.html")

if __name__ == "__main__":
    app.run(debug=True, port=5000)
