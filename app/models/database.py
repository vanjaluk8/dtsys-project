from sqlalchemy import Column, String, Integer, create_engine, MetaData, Table, text
from sqlalchemy.sql import select, exists


mysql_url = "mysql+pymysql://root:DOCKER123!@127.0.0.1/stock_data"
engine = create_engine(mysql_url)
metadata = MetaData()


def setup_database():
    engine = create_engine(mysql_url)
    metadata = MetaData()
    stock_info = Table(
       'stock_info', metadata,
       Column('symbol', String(255), primary_key=True),
       Column('longBusinessSummary', String(255)),
       Column('industryDisp', String(255)),
       Column('sectorDisp', String(255)),
       Column('fullTimeEmployees', Integer),
       Column('website', String(255)),
       Column('shortname', String(255))
    )
    metadata.create_all(engine)


if __name__ == "__main__":
    setup_database()
