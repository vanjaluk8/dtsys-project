import concurrent
from datetime import datetime
import traceback
import aiohttp
from fastapi import FastAPI
import pandas as pd
from sqlalchemy import create_engine, Table, MetaData, text, exc
from dotenv import load_dotenv
import os
from starlette.responses import RedirectResponse
from starlette.status import HTTP_302_FOUND

load_dotenv()
# database credentials
db_user = os.getenv('MYSQL_USER')
db_password = os.getenv('MYSQL_PASSWORD')
db_host = os.getenv('MYSQL_HOST')
db = os.getenv('MYSQL_DATABASE')

# RapidAPI credentials
rapidapi_key = os.getenv('RAPIDAPI_KEY')
rapidapi_endpoint = os.getenv('RAPIDAPI_ENDPOINT')


app = FastAPI()

# spajanje na mysql preko sqlalchemy
mysql_url = f'mysql+pymysql://{db_user}:{db_password}@{db_host}/{db}'
engine = create_engine(mysql_url)
metadata = MetaData()



### RAPIDAPI METHODS
# connects to rapidapi and fetches stock info and after that runs the second api call for stock price

@app.get("/")
async def root():
    return RedirectResponse(url="/docs", status_code=HTTP_302_FOUND)

@app.get("/status")
async def status():
    return {"status": "OK"}

@app.get("/stock_info/{symbol}")
async def fetch_data(symbol: str):
    symbol = symbol.upper()
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{rapidapi_endpoint}/stock/v2/get-summary?symbol={symbol}&region=US"
            headers = {"X-RapidAPI-Key": rapidapi_key}

            async with session.get(url, headers=headers) as response:
                stock_info = await response.json()
                if 'summaryProfile' not in stock_info:
                    raise Exception(f'Symbol {symbol} not found')

    except Exception as e:
        print(e)
        return {"message": "Symbol not found"}


    # Create a dictionary with the extracted data, if the data is not available, it will be None - avoid KeyError
    stock_info_data = {
        "symbol": symbol,
        "longBusinessSummary": stock_info.get("summaryProfile", {}).get("longBusinessSummary", None),
        "industryDisp": stock_info.get("summaryProfile", {}).get("industryDisp", None),
        "sectorDisp": stock_info.get("summaryProfile", {}).get("sectorDisp", None),
        "fullTimeEmployees": stock_info.get("summaryProfile", {}).get("fullTimeEmployees", None),
        "website": stock_info.get("summaryProfile", {}).get("website", None),
        "shortname": stock_info.get("quoteType", {}).get("shortName", None),
        "beta": stock_info.get("defaultKeyStatistics").get("beta").get("raw", None),
        "forwardPE": stock_info.get("defaultKeyStatistics").get("forwardPE").get("raw", None),
        "EPS": stock_info.get("defaultKeyStatistics").get("trailingEps").get("raw", None),
        "dividendYield": stock_info.get("summaryDetail").get("dividendYield").get("raw", None),
        "mktCap": stock_info.get("summaryDetail").get("marketCap").get("raw", None),
    }

    # Create a DataFrame from the stock info data
    df = pd.DataFrame([stock_info_data])
    print(df)

    with engine.connect() as connection:
        query = text("SELECT EXISTS(SELECT 1 FROM stock_info WHERE symbol = :symbol)")  # check if the symbol exists in the database, if not insert it
        symbol_exists = connection.execute(query, {"symbol": symbol}).scalar()
        print(f'Symbol {symbol} exists: ', symbol_exists)
        if not symbol_exists:
            with concurrent.futures.ThreadPoolExecutor(): # use a thread pool to insert the data, will be faster
                try:
                    # if the data exists, it will be updated, if not do nothing
                    df.to_sql("stock_info", con=engine, if_exists='append', index=False)
                    print(f"Stock info for {symbol} inserted successfully")

                    start_date = "2023-10-01"
                    end_date = "2024-01-01"
                    await fetch_price_data(symbol, start_date, end_date) # call the second api to fetch stock price data

                except Exception as e:
                    print(e)
                    traceback.print_exc()
    return stock_info, {"message": "Stock info inserted successfully"}


# connects to rapidapi and fetches stock price data
@app.get("/stock_price/{symbol}")
async def fetch_price_data(symbol: str, start_date: str, end_date: str):
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{rapidapi_endpoint}/stock/v2/get-historical-data?symbol={symbol}&region=US&from={start_date}&to={end_date}"
            headers = {"X-RapidAPI-Key": rapidapi_key}

            async with session.get(url, headers=headers) as response:
                response_data = await response.json()
                stock_data_list = response_data["prices"]
    except Exception as e:
        print(e)
        return {"message": "Symbol not found"}

    with concurrent.futures.ThreadPoolExecutor() as executor: # use a thread pool to insert the data, will be faster
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
                    executor.submit(df.to_sql, symbol, con=engine, if_exists='append', index=False)
                except Exception as e:
                    print(e)

    return stock_data, {"message": "Data has been successfully added to the database."}


# delete stock from database
@app.delete("/stock_delete/{symbol}")
async def delete_stock(symbol: str):
    with engine.connect() as connection:
        query = text("DELETE FROM stock_info WHERE symbol = :symbol")
        result = connection.execute(query, {"symbol": symbol})
        try:
            table_to_drop = Table(symbol, metadata)
            table_to_drop.drop(engine)
        except exc.NoSuchTableError:
            return {"message": f"No table named {symbol} found"}
        if result.rowcount == 0:
            return {"message": "Symbol not found"}
            # Drop the table with the same symbol

        return {"message": "Symbol and corresponding table deleted successfully"}


# if __name__ == "__main__":
#     import uvicorn
#
#     uvicorn.run(app, host="0.0.0.0", port=8001, reload=)
