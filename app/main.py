import concurrent
from datetime import datetime
import traceback
import aiohttp
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
import pandas as pd
from sqlalchemy import create_engine, Table, MetaData, text
from sqlalchemy.sql import select, exists


app = FastAPI()
user = 'root'
password = 'DOCKER123!'

rapidapi_key = ""
rapidapi_endpoint = "https://apidojo-yahoo-finance-v1.p.rapidapi.com"

# Assuming you have a MySQL connection URL. Adjust accordingly.
mysql_url = "mysql+pymysql://root:DOCKER123!@127.0.0.1/stock_data"
engine = create_engine(mysql_url)
metadata = MetaData()
# Assuming your_table_name is the name of your MySQL table
symbol = None


### RAPIDAPI METHODS
@app.get("/stock_info/{symbol}")
async def fetch_data(symbol: str):
    global global_symbol
    global_symbol = symbol
    async with aiohttp.ClientSession() as session:
        url = f"{rapidapi_endpoint}/stock/v2/get-summary?symbol={symbol}&region=US"
        headers = {"X-RapidAPI-Key": rapidapi_key}

        async with session.get(url, headers=headers) as response:
            stock_info = await response.json()

    # Extract the required fields
    longBusinessSummary = stock_info["summaryProfile"]["longBusinessSummary"]
    industryDisp = stock_info["summaryProfile"]["industryDisp"]
    sectorDisp = stock_info["summaryProfile"]["sectorDisp"]
    fullTimeEmployees = stock_info["summaryProfile"]["fullTimeEmployees"]

    # Create a dictionary with the extracted data
    stock_info_data = {
        "symbol": symbol,
        "longBusinessSummary": longBusinessSummary,
        "industryDisp": industryDisp,
        "sectorDisp": sectorDisp,
        "fullTimeEmployees": fullTimeEmployees
    }

    # Create a DataFrame from the stock info data
    df = pd.DataFrame([stock_info_data])
    print(df)

    with engine.connect() as connection:
        query = text("SELECT EXISTS(SELECT 1 FROM stock_info WHERE symbol = :symbol)")
        symbol_exists = connection.execute(query, {"symbol": symbol}).scalar()
        print(f'Symbol {symbol} exists: ', symbol_exists)
        if not symbol_exists:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                try:
                    # if the data exists, it will be updated, if not do nothing
                    executor.submit(df.to_sql, "stock_info", con=engine, if_exists='append', index=False)
                    print(f"Stock info for {symbol} inserted successfully")
                except Exception as e:
                    print(e)
                    traceback.print_exc()
    return stock_info, {"message": "Stock info inserted successfully"}


@app.get("/stock_price/{symbol}")
async def fetch_price_data(symbol: str, start_date: str, end_date: str):

    async with aiohttp.ClientSession() as session:
        url = f"{rapidapi_endpoint}/stock/v2/get-historical-data?symbol={symbol}&region=US&from={start_date}&to={end_date}"
        headers = {"X-RapidAPI-Key": rapidapi_key}

        async with session.get(url, headers=headers) as response:
            response_data = await response.json()
            stock_data_list = response_data["prices"]

        with concurrent.futures.ThreadPoolExecutor() as executor:
            for stock_data in stock_data_list:
                if all(key in stock_data for key in ["date", "open", "high", "low", "close", "volume", "adjclose"]):
                    # Convert the date from a timestamp to a datetime object
                    stock_data["date"] = datetime.fromtimestamp(stock_data["date"])

                    # Ensure the other fields are of the correct data type
                    stock_data["open"] = float(stock_data["open"])
                    stock_data["high"] = float(stock_data["high"])
                    stock_data["low"] = float(stock_data["low"])
                    stock_data["close"] = float(stock_data["close"])
                    stock_data["volume"] = int(stock_data["volume"])
                    stock_data["adjclose"] = float(stock_data["adjclose"])

                    # Create a DataFrame from the stock data
                    df = pd.DataFrame([stock_data])

                    try:
                        # Run the to_sql() method in a separate thread
                        executor.submit(df.to_sql, symbol, con=engine, if_exists='append',
                                        index=False, insert='multi')
                    except Exception as e:
                        print(e)

    return stock_data, {"message": "Data has been successfully added to the database."}


# if __name__ == "__main__":
#     import uvicorn
#
#     uvicorn.run(app, host="0.0.0.0", port=8001, reload=)
