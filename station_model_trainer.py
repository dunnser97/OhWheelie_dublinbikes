
# In[1]:


# This script is used to generate a unique Polynomial, linear regression model for EACH station...
# ...based on historical data from the previous month.
# It is intended to be run on the 1st of every month using CRONTAB, thus retraining the model...
#...based on the previous month's data.


from sklearn.linear_model import LinearRegression

import pandas as pd
from sqlalchemy import create_engine
import dbinfo
import joblib
import datetime

from datetime import date
from dateutil.relativedelta import relativedelta
import calendar


# In[2]:


engine = create_engine(dbinfo.bike_engine, echo=True)
row_query = "SELECT DISTINCT Station_number from dbbikes_info;"
top_df = pd.read_sql_query(row_query, con=engine)
top_df.to_json(orient="records")


# In[3]:


#Create an array of all stations.
station_numbers = []

for index, row in top_df.iterrows():
    station_numbers.append(top_df.at[index, 'Station_number'])


# In[4]:


#Set the bounds for which SQL data will be retrieved (previous month only).
lower_bound_date = date.today() - relativedelta(months=1)


# In[5]:


lower_bound_date = str(lower_bound_date)[0:8] + "01"
lower_bound_date


# In[6]:


upper_bound_date = str(lower_bound_date)[0:8] + str(calendar.monthrange(int(str(lower_bound_date)[0:4]), int(str(lower_bound_date)[5:7]))[1])


# In[7]:


def create_df(station_num):

    #Fetch initial DataFrame
    engine = create_engine(dbinfo.bike_engine, echo=True)
    row_query = "SELECT available_bike_stands, available_bikes, date, time, latitude, longitude from dbbikes_info WHERE Station_number='" + str(station_num) + "' and date >= '" + lower_bound_date + "' and date <= '" + upper_bound_date + "' order by date;"
    df = pd.read_sql_query(row_query, con=engine)
    df['time'] = df['time'].astype(str)
    df.to_json(orient="records")

    
    #Format time correctly
    for column in df[['time']].columns:
        df[column] = df[column].str.slice(6)
    
    #Add Weather columns
    df.insert(6, "temp_val", "0")
    df.insert(7, "rain_val", "0")
    df.insert(8, "wind_val", "0")
    
    #Append Weather Data to DF from Weather Database
    lat = df.at[0, 'latitude']
    long = df.at[0, 'longitude']
    engine = create_engine(dbinfo.engine, echo=True)
    
    for index, row in df.iterrows():
        bike_date = str(row['date'])
        bike_time = str(row['time'])
        bike_time = bike_time[1 : 3] + ":00:00"

        row_query = "SELECT temp_val, rain_val, wind_val from weather_history WHERE latitude='" + lat + "' AND longitude='" + long + "' AND date ='" + bike_date + "' AND clock_time ='" + bike_time + "' LIMIT 1;"
        row_weather_df = pd.read_sql_query(row_query, engine)

        temperature = str(row_weather_df['temp_val'])
        temperature = temperature[5:8]

        rain = str(row_weather_df['rain_val'])
        rain = rain[5:8]

        wind = str(row_weather_df['wind_val'])
        wind = wind[5:8]

        df.at[index, 'temp_val'] = temperature
        df.at[index, 'rain_val'] = rain
        df.at[index, 'wind_val'] = wind
        
    #Drop lat and long columns as no longer needed.
    df.drop(columns=['latitude'], inplace=True)
    df.drop(columns=['longitude'], inplace=True)
    
    
    #Date is converted into 'DAY of the week' and treated as a categorical feature.
    for index, row in df.iterrows():
        
        hour = str(row['time'])[1:3]
        minute = str(row['time'])[4:6]

        int_time = (int(minute, base=10)) + (60 * int(hour, base=10))

        df.at[index, 'time'] = int_time

        year = int(str(row['date'])[0:4], base=10)
        month = int(str(row['date'])[5:7], base=10)
        day = int(str(row['date'])[8:], base=10)

        date = datetime.date(year, month, day)
        
        if date.weekday() == 0:
            df.at[index, 'date'] = 'Monday'

        elif date.weekday() == 1:
            df.at[index, 'date'] = 'Tuesday'

        elif date.weekday() == 2:
            df.at[index, 'date'] = 'Wednesday'

        elif date.weekday() == 3:
            df.at[index, 'date'] = 'Thursday'

        elif date.weekday() == 4:
            df.at[index, 'date'] = 'Friday'

        elif date.weekday() == 5:
            df.at[index, 'date'] = 'Saturday'

        elif date.weekday() == 6:
            df.at[index, 'date'] = 'Sunday'
            
    
    #Adding all polynomial rows for continuous features
    df.insert(7, "time_squared", "0")
    df.insert(8, "temp_val_squared", "0")
    df.insert(9, "rain_val_squared", "0")
    df.insert(10, "wind_val_squared", "0")
    df.insert(11, "time_cubed", "0")
    df.insert(12, "temp_val_cubed", "0")
    df.insert(13, "rain_val_cubed", "0")
    df.insert(14, "wind_val_cubed", "0")
    
    for index, row in df.iterrows():
        #Adding time squared and cubed to rows.
        time_squared = float(row['time']) ** 2
        time_cubed = float(row['time']) ** 3

        df.at[index, 'time_squared'] = time_squared
        df.at[index, 'time_cubed'] = time_cubed

        #Adding temp_val squared and cubed to rows.
        temp_val_squared = float(row['temp_val']) ** 2
        temp_val_cubed = float(row['temp_val']) ** 3

        df.at[index, 'temp_val_squared'] = temp_val_squared
        df.at[index, 'temp_val_cubed'] = temp_val_cubed

        #Adding rain_val squared and cubed to rows.
        rain_val_squared = float(row['rain_val']) ** 2
        rain_val_cubed = float(row['rain_val']) ** 3

        df.at[index, 'rain_val_squared'] = rain_val_squared
        df.at[index, 'rain_val_cubed'] = rain_val_cubed

        #Adding wind_val squared and cubed to rows.
        wind_val_squared = float(row['wind_val']) ** 2
        wind_val_cubed = float(row['wind_val']) ** 3

        df.at[index, 'wind_val_squared'] = wind_val_squared
        df.at[index, 'wind_val_cubed'] = wind_val_cubed
        
    #Convert Categorical feature (day of week)
    date_dummies = pd.get_dummies(df['date'], prefix='date')
    categ_features = date_dummies.columns.values.tolist()

    df = pd.concat([df, date_dummies], axis=1)
    df = df.drop('date', axis = 1)
    
    #Convert all columns data types.
    integer_columns = df[['available_bike_stands', 'available_bikes', 'date_Friday', 'date_Monday', 'date_Saturday', 'date_Sunday' ,'date_Thursday' , 'date_Tuesday' , 'date_Wednesday']].columns
    float_columns = df[['time','temp_val','rain_val','wind_val','time_squared','temp_val_squared','rain_val_squared','wind_val_squared','time_cubed', 'temp_val_cubed','rain_val_cubed','wind_val_cubed']].columns
    
    for column in integer_columns:
        df[column] = df[column].astype('int64')
    
    for column in float_columns:
        df[column] = df[column].astype('float64')
    
    # NORMALISING all continuous features to between 0 and 1 using appropriate values for each.
    # Values are chosen as reasonable upper limit values for each feature.
    for index, row in df.iterrows():
        df.at[index, 'time'] /= 1439
        df.at[index, 'temp_val'] /= 30
        df.at[index, 'rain_val'] /= 2
        df.at[index, 'wind_val'] /= 20
        df.at[index, 'time_squared'] /= (1439 ** 2)
        df.at[index, 'temp_val_squared'] /= (30 ** 2)
        df.at[index, 'rain_val_squared'] /= (2 ** 2)
        df.at[index, 'wind_val_squared'] /= (20 ** 2)
        df.at[index, 'time_cubed'] /= (1439 ** 3)
        df.at[index, 'temp_val_cubed'] /= (30 ** 3)
        df.at[index, 'rain_val_cubed'] /= (2 ** 3)
        df.at[index, 'wind_val_cubed'] /= (20 ** 3)
    
        
    return df


# In[8]:


def create_model(df, station_num):
    
    continuous_features = ['time', 'temp_val', 'rain_val', 'wind_val', 'time_squared', 'temp_val_squared', 'rain_val_squared', 'wind_val_squared', 'time_cubed', 'temp_val_cubed', 'rain_val_cubed', 'wind_val_cubed']
    categ_features = ['date_Friday','date_Monday','date_Saturday','date_Sunday','date_Thursday','date_Tuesday','date_Wednesday']
    features = continuous_features + categ_features
    
    x = df[features]
    y = df.available_bikes

    model = LinearRegression().fit(x, y)
    
    filename = str(station_num) + '.sav'
    joblib.dump(model, filename)


# In[ ]:

fail_counter = 0
failed_stations = []

for i in station_numbers:
    try:
        df = create_df(i)
        create_model(df, i)
    except:
        print("THIS STATION HAS FAILED!!!" + str(i))
        fail_counter += 1
        failed_stations.append(i)

print("FINISHED GENERATING MODELS")
print("FAILED" + str(fail_counter) + " TIMES")
print(failed_stations)
