from fastapi import FastAPI
from pyspark.sql import SparkSession
import mysql.connector
import pandas as pd

app = FastAPI()

# Initialize PySpark
spark = SparkSession.builder.appName("MySQLExample").getOrCreate()

# MySQL Database Configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'DOKER123!',
    'database': 'world',
}


# Function to connect to MySQL and execute a query
def query_mysql(query):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    return result


@app.get("/")
async def read_root():
    return {"message": "Welcome to your FastAPI app!"}


@app.get("/query-city.json")
async def query_mysql_endpoint():
    # Example MySQL query
    query = "SELECT Name, CountryCode, District, Population FROM city;"
    results = query_mysql(query)
    result_list = [
        {"Name": row[0],
         "CountryCode": row[1],
         "District": row[2],
         "Population": row[3]
         } for row in results]

    return result_list



# if __name__ == "__main__":
#     import uvicorn
#
#     uvicorn.run(app, host="0.0.0.0", port=8001, reload=)
