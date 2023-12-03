from pyspark.sql import SparkSession
import pandas as pd


def read_city_data(): # Function to read the data from the MySQL database
    spark = SparkSession.builder\
        .config("spark.jars", "mysql-connector-j-8.2.0.jar") \
        .master("local").appName("PySpark_MySQL_test").getOrCreate()

    
    # The JDBC URL to connect to the MySQL database
    jdbc_url = "jdbc:mysql://localhost:3306/world"
    connection_properties = {
        "user": "root",
        "password": "DOCKER123!",
        "driver": "com.mysql.cj.jdbc.Driver"
    }

    # The query to retrieve the data from the database
    query = "(SELECT * FROM city) AS city_data"

    # Read the data from the MySQL database
    city_data = spark.read.format("jdbc")\
        .option("url", jdbc_url)\
        .option("dbtable", query)\
        .option("user", connection_properties["user"])\
        .option("password", connection_properties["password"])\
        .option("driver", connection_properties["driver"]).load()

    # Convert the Spark DataFrame to a Pandas DataFrame
    if city_data.head(1):
        pandas_df = city_data.toPandas()
        return pandas_df
    else:
        print("The DataFrame is empty! Check the query for any issues.")
        return pd.DataFrame()