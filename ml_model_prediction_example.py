#!/usr/bin/env python
# coding: utf-8

# In[5]:


import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Allows plots to appear directly in the notebook.

import joblib



# In[6]:


def make_prediction(time, forecast_temp, forecast_rain, forecast_wind, day_of_week, station_number):
    
    # Load the correct Model for this station.
    filename = str(station_number) + ".sav"
    loaded_model = joblib.load(filename)
    
    # Create polynomial values.
    time_squared = time ** 2
    temp_val_squared = forecast_temp ** 2
    rain_val_squared = forecast_rain ** 2
    wind_val_squared = forecast_wind ** 2
    time_cubed = time ** 3
    temp_val_cubed = forecast_temp ** 3
    rain_val_cubed = forecast_rain ** 3
    wind_val_cubed = forecast_wind ** 3
    
    # Scale all values as per the model.
    time /= 1439
    forecast_temp /= 30
    forecast_rain /= 2
    forecast_wind /= 20
    time_squared /= (1439 ** 2)
    temp_val_squared /= (30 ** 2)
    rain_val_squared /= (2 ** 2)
    wind_val_squared /= (20 ** 2)
    time_cubed /= (1439 ** 3)
    temp_val_cubed /= (30 ** 3)
    rain_val_cubed /= (2 ** 3)
    wind_val_cubed /= (20 ** 3)
    
    # Set correct day of week categorical feature.
    if day_of_week == 0:
        mon = 1
    else:
        mon = 0
    
    if day_of_week == 1:
        tue = 1
    else:
        tue = 0
        
    if day_of_week == 2:
        wed = 1
    else:
        wed = 0
        
    if day_of_week == 3:
        thur = 1
    else:
        thur = 0
        
    if day_of_week == 4:
        fri = 1
    else:
        fri = 0
        
    if day_of_week == 5:
        sat = 1
    else:
        sat = 0
        
    if day_of_week == 6:
        sun = 1
    else:
        sun = 0
    
    # Make the prediction.
    test = np.array([time, forecast_temp, forecast_rain, forecast_wind, time_squared, temp_val_squared, rain_val_squared, wind_val_squared, time_cubed, temp_val_cubed, rain_val_cubed, wind_val_cubed, fri, mon, sat, sun, thur, tue, wed]).reshape(1, -1)
    result = loaded_model.predict(test)
    
    result = result[0]
    
    if result > 40:
        result = 40
        
    elif result < 0:
        result = 0
        
    
    return round(result)


# In[7]:


#6pm on a SUNDAY at station 106 where temperature is 10 degrees, rain is 0 and windspeed is 2
prediction = make_prediction((60*18), 10, 0, 2, 6, 106)

print("Number of bikes predicted: " + str(prediction))
# In[ ]:




