from sqlalchemy import Column, String, Integer, create_engine, MetaData, Table, inspect, Float, Text, Date
from dotenv import load_dotenv
import os

load_dotenv()

db_user = os.getenv('MYSQL_USER')
db_password = os.getenv('MYSQL_PASSWORD')
db_host = os.getenv('MYSQL_HOST')
db = os.getenv('MYSQL_DATABASE')

mysql_url = f'mysql+pymysql://{db_user}:{db_password}@{db_host}/{db}'



def setup_database():
    engine = create_engine(mysql_url)
    inspector = inspect(engine)
    try:
        if inspector.has_table("stock_info"):  # If table exists
            stock_info = Table('stock_info', MetaData(), autoload_with=engine)
            stock_info.drop(engine)  # Drop the table

        # Recreate the table
        metadata = MetaData()
        stock_info = Table(
           'stock_info', metadata,
           Column('symbol', String(255), primary_key=True),
            Column('longBusinessSummary', Text),
            Column('industryDisp', String(255)),
            Column('sectorDisp', String(255)),
            Column('fullTimeEmployees', Integer),
            Column('website', String(255)),
            Column('shortname', String(255)),
            Column('beta', Float()),
            Column('forwardPE', Float()),
            Column('EPS', Float()),
            Column('dividendYield', Float()),
            Column("mktCap", Float()),

        )
        metadata.create_all(engine)
        print("Table created successfully")
    except Exception as e:
        print(e)
        return {"message": "Error creating table"}


if __name__ == "__main__":
    setup_database()
