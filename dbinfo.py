##host= "bikesdb.c9qozhat0dxv.us-east-1.rds.amazonaws.com"
##user= "admin"
##passwd= "mybikes99"
##database= "weather_hourDB"

#Weather Database
host = "bikesdb.c9qozhat0dxv.us-east-1.rds.amazonaws.com"
user = "admin"
passwd = "mybikes99"
database = "weather_hourDB"

#My Database
dbhost = "dbbikes-kms.cb4a7u7bkk6j.us-east-1.rds.amazonaws.com"
dbuser = "Shane"
dbpasswd = "Oh_Wheeliekms"
dbdatabase = "dbbikes"
APIKEY = "https://api.jcdecaux.com/vls/v1/stations"

engine = f"mysql+mysqlconnector://{user}:{passwd}@{host}:3306/{database}"
bike_engine = f"mysql+mysqlconnector://{dbuser}:{dbpasswd}@{dbhost}:3306/{dbdatabase}"