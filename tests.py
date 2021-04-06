import unittest
import pandas as pd
from sqlalchemy import create_engine
import dbinfo
import datetime

class MyTestCase(unittest.TestCase):
    def test_stations_q(self):
        print('Testing bikes')
        engine = create_engine(dbinfo.engine)
        row_query = "select * from dbbikes_current_info"
        df = pd.read_sql_query(row_query, con=engine)
        length = len(df)
        self.assertEqual(length, 108)

    def test_weather_q(self):
        print('testing weather')
        engine = create_engine(dbinfo.engine)
        row_query = "select * from dbbikes_current_info where Station_number = 32"
        x = pd.read_sql_query(row_query, engine)
        lat = x["latitude"]
        long = x["longitude"]
        x['time'] = x['time'].astype(str)
        row_query_1 = "select *  from weather_forecast where latitude = " + str(
            format(lat[0])) + "and longitude = " + str(
            format(long[0])) + "group by clock_time"
        y = pd.read_sql_query(row_query_1, engine)
        self.assertEqual(len(y), 24)

    def test_bike_avg_q(self):
        print('testing avg bike query')
        engine = create_engine(dbinfo.engine)
        row_query = "select FLOOR(AVG(available_bike_stands)) as avg,  date_format(DATE_ADD(bikes.time, interval 30 minute), '%H:00:00') as T from weather_hourDB.dbbikes_info as bikes where bikes.Station_number = 32 group by T ORDER BY T ASC;"
        df1 = pd.read_sql_query(row_query, engine)
        self.assertEqual(len(df1), 24)

    def test_bike_avg_daily(self):
        print('testing avg bike query num 2')
        bike_engine = create_engine(dbinfo.bike_engine)
        day_avg = "select floor(AVG(available_bikes)) as avg_day, weekday(date) as day from dbbikes_info where Station_number = 32 and time Between '06:00:00' AND '20:00:00' group by weekday(date) order by weekday(date) asc;"
        day_avg_db = pd.read_sql_query(day_avg, bike_engine)
        day_avg_db["day"].replace(
            {0: "Monday", 1: "Tueday", 2: "Wednesday", 3: "Thursday", 4: "Friday", 5: "Saturday", 6: "Sunday"},
            inplace=True)
        self.assertEqual(len(day_avg_db), 7)

    def test_temp(self):
        print('testing temperature query')
        station_id = 32
        engine = create_engine(dbinfo.engine)
        bike_engine = create_engine(dbinfo.bike_engine)
        row_query = "select available_bike_stands, date, ADDTIME(time, '1:00:00') as time, Station_number, latitude, longitude from dbbikes_current_info where Station_number = " + str(
            format(station_id))
        x = pd.read_sql_query(row_query, bike_engine)
        lat = x["latitude"]
        long = x["longitude"]
        date = datetime.datetime.now()
        date_1 = date.strftime("%m")
        date_2 = date.strftime("%d")
        date_2 = int(date_2)
        month = int(date_1)
        if (month > 3 and month < 11) or (month == 3 and date_2 > 27):
            cur_temp = "SELECT temp_val, ADDTIME(clock_time, '1:00:00') as clock_time FROM weather_hourDB.weather_forecast " \
                       "where longitude = " + str(format(long[0])) + " and latitude = " + str(format(lat[0])) + ";"
            temp = pd.read_sql_query(cur_temp, engine)
        else:
            cur_temp = "SELECT temp_val, clock_time FROM weather_hourDB.weather_forecast " \
                       "where longitude = " + str(format(long[0])) + " and latitude = " + str(format(lat[0])) + ";"
            temp = pd.read_sql_query(cur_temp, engine)
        self.assertEqual(len(temp), 24)

    def test_individ_station_weather(self):
            print('testing individual station weather')
            engine = create_engine(dbinfo.bike_engine)
            lat = 53.349562
            long = -6.278198
            date = datetime.datetime.now()
            date_1 = date.strftime("%m")
            date_2 = date.strftime("%d")
            date_2 = int(date_2)
            month = int(date_1)
            if (month > 3 and month < 11) or (month == 3 and date_2 > 27):
                row_query_1 = "select date, ADDTIME(clock_time, '1:00:00') as clock_time , latitude, longitude, temp_val, humidity_val, cloudi_val, rain_val, wind_val, weather_symbol from weather_forecast where latitude = 53.349562" \
             " and longitude = -6.278198 " + "group by clock_time"
                y = pd.read_sql_query(row_query_1, engine)
            else:
                row_query_1 = "select * from weather_forecast where latitude =  53.349562" \
                     " and longitude = -6.278198 group by clock_time"
                y = pd.read_sql_query(row_query_1, engine)
            self.assertEqual(len(y), 24)

if __name__ == '__main__':
    unittest.main()