import pymysql

def get_db_connection():
    try:
        connection = pymysql.connect(
            host="orgr9.h.filess.io",  # Database host
            user="mlgroup_childrenof",  # Database username
            password="284b5b9f1bf250ee916853314f97240c8317249e",  # Database password
            database="mlgroup_childrenof",  # Database name
            port=3307,  # Database port
            cursorclass=pymysql.cursors.DictCursor  # Use dictionary cursors
        )
        return connection
    except pymysql.Error as e:
        raise Exception(f"Database connection error: {str(e)}")
