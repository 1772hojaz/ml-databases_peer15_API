import mysql.connector
from mysql.connector import Error

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host="ku2ag.h.filess.io",  # Database host
            database="liverDisease_soilbrass",  # Database name
            user="liverDisease_soilbrass",  # Database username
            password="863f959b357d8fbb9e466fc5ca6ba6b96341cf03",  # Database password
            port=3307  # Database port
        )
        return connection
    except Error as e:
        raise Exception(f"Database connection error: {str(e)}")

