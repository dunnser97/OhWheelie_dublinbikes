from flask import Flask, render_template, jsonify
import pandas as pd
from jinja2 import Template
from sqlalchemy import create_engine
import dbinfo
app = Flask(__name__, template_folder='templates')

@app.route("/")

@app.route("/index")
def hello():
    return render_template("index.html")

@app.route("/about")
def about():
    return app.send_static_file("about.html")


@app.route("/stations")
def stations():
    engine = create_engine(f"mysql+mysqlconnector://{dbinfo.user}:{dbinfo.passwd}@{dbinfo.host}:3306/{dbinfo.database}")
   #result = engine.execute("select * from weather_hourDB.dbbikes_current_info")
    df = pd.read_sql_table("dbbikes_current_info", engine)
    print(df.head(3).to_json(orient="records"))
    return df.to_json(orient="records")

@app.route("/stations/<int:station_id>")
def station(station_id):
    engine = create_engine(f"mysql+mysqlconnector://{dbinfo.user}:{dbinfo.passwd}@{dbinfo.host}:3306/{dbinfo.database}", echo=True)
    row_query = "select * from dbbikes_current_info where Station_number = " + str(format(station_id))
    x = pd.read_sql_query(row_query, engine)
    lat = x["latitude"]
    long = x["longitude"]
    row_query_1 = "select * from weather_forecast where latitude = " + str(format(lat[0])) + "and longitude = " + str(format(long[0])) + "group by clock_time"
    y = pd.read_sql_query(row_query_1, engine)
    results = y.to_json(orient="split")
    return render_template("stations_individual.html", indiv_stat=x, weather_data=y, results=results)


if __name__ == "__main__":
    app.run(debug=True, port=5000)

