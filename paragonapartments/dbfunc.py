import mysql.connector
from mysql.connector import errorcode
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
 
# MYSQL CONFIG VARIABLES
hostname = os.getenv('DB_HOST', '127.0.0.1')
username = os.getenv('DB_USER', 'root')
passwd = os.getenv('DB_PASSWORD', '')
database = os.getenv('DB_NAME', 'paragonapartments')

def getConnection():    
    try:
        conn = mysql.connector.connect(host=hostname,                              
                              user=username,
                              password=passwd,
                              db=database)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print('User name or Password is not working')
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print('Database does not exist')
        else:
            print(err)                        
    else:  #will execute if there is no exception raised in try block
        return conn   
                
