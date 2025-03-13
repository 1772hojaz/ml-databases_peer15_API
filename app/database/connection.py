import mysql.connector
from mysql.connector import Error

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host="orgr9.h.filess.io",  # Database host
            database="mlgroup_childrenof",  # Database name
            user="mlgroup_childrenof",  # Database username
            password="284b5b9f1bf250ee916853314f97240c8317249e",  # Database password
            port=3307  # Database port
        )
        return connection
    except Error as e:
        raise Exception(f"Database connection error: {str(e)}")
