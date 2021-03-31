import unittest
import pandas as pd
from sqlalchemy import create_engine
import dbinfo

class MyTestCase(unittest.TestCase):
    def test_stations_q(self):
        print('Testing bikes')
        engine = create_engine(f"mysql+mysqlconnector://{dbinfo.user}:{dbinfo.passwd}@{dbinfo.host}:3306/{dbinfo.database}", echo=False)
        row_query = "select * from dbbikes_current_info"
        df = pd.read_sql_query(row_query, con=engine)
        length = len(df)
        self.assertEqual(length, 108)

    def test_weather_q(self):
        print('testing weather')
        engine = create_engine(
            f"mysql+mysqlconnector://{dbinfo.user}:{dbinfo.passwd}@{dbinfo.host}:3306/{dbinfo.database}",
            echo=False)
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
        engine = create_engine(
            f"mysql+mysqlconnector://{dbinfo.user}:{dbinfo.passwd}@{dbinfo.host}:3306/{dbinfo.database}",
            echo=False)
        row_query = "select FLOOR(AVG(available_bike_stands)) as avg,  date_format(DATE_ADD(bikes.time, interval 30 minute), '%H:00:00') as T from weather_hourDB.dbbikes_info as bikes where bikes.Station_number = 32 group by T ORDER BY T ASC;"
        df1 = pd.read_sql_query(row_query, engine)
        self.assertEqual(len(df1), 24)





if __name__ == '__main__':
    unittest.main()