import os
import mysql.connector
from mysql.connector import Error

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DATABASE_HOST"),  # Database host
            database=os.getenv("DATABASE_NAME"),  # Database name
            user=os.getenv("DATABASE_USER"),  # Database username
            password=os.getenv("DATABASE_PASSWORD"),  # Database password
            port=int(os.getenv("DATABASE_PORT", 3307))  # Database port
        )
        return connection
    except Error as e:
        raise Exception(f"Database connection error: {str(e)}")