import concurrent
import json
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

# load the environment variables from the .env file
load_dotenv()

# database credentials
db_user = os.getenv('MYSQL_USER')
db_password = os.getenv('MYSQL_PASSWORD')
db_host = os.getenv('MYSQL_HOST')
db = os.getenv('MYSQL_DATABASE')

# RapidAPI credentials
rapidapi_key = os.getenv('RAPIDAPI_KEY')
rapidapi_endpoint = os.getenv('RAPIDAPI_ENDPOINT')

# start the application
app = FastAPI()

# SQLAlchemy db connection string
mysql_url = f'mysql+pymysql://{db_user}:{db_password}@{db_host}/{db}'
engine = create_engine(mysql_url)
metadata = MetaData()


### RAPIDAPI METHODS
# connects to RapidApi and fetches stock info and after that runs the second api call for stock price

@app.get("/")  # redirect to swagger, to avoid Not found error
async def root():
    return RedirectResponse(url="/docs", status_code=HTTP_302_FOUND)


@app.get("/status")  # check if the server is running (used for monitoring tools)
async def status():
    return {"status": "OK"}


@app.get("/indices_data")  # fetch indices data from RapidAPI (eg. NASDAQ, DOW JONES, SP500, FTSE100, DAX, etc.)
async def fetch_indices_data():
    with open('../db_data/market_data.json',
              'r') as file:  # tu koristim json file, inače se dođe api call na rapidAPI (potrošio sam sve tokene, pa da ne plaćam pretplatu :D )
        data = json.load(file)  # load the data from the file
        # create a dictionary with the extracted data
        symbol_data = {
            item['symbol']: {
                'symbol': item['symbol'],
                'shortName': item['shortName'],
                'exchangeName': item['fullExchangeName'],
                'quoteType': item['quoteType'],
                'lastClose': item['regularMarketPreviousClose']['raw'],
                'market': item['market'],
            } for item in data['marketSummaryAndSparkResponse']['result']
        }

        # truncate the table before inserting new data (obriši sve iz tabele pre nego što ubaciš nove podatke)
    with engine.connect() as connection:
        query = text("TRUNCATE TABLE indices")
        connection.execute(query)

        # ubaci podatke u bazu
    for symbol, data in symbol_data.items():
        with concurrent.futures.ThreadPoolExecutor():
            try:
                df = pd.DataFrame([data])  # create a DataFrame from the symbol data, easier to insert into the database
                df.to_sql("indices", con=engine, if_exists='append', index=False)
                print(f"Indices data for {symbol} inserted successfully")
            except Exception as e:
                print(e)
                traceback.print_exc()
    return symbol_data  # return the data that has been inserted into the database


@app.get("/stock_info/{symbol}")  # fetch stock info from RapidAPI
async def fetch_data(symbol: str):  # input a stock symbol (eg. AMZN, AAPL, TSLA, BRK-B, use stocks listed on US stock exchanges)
    symbol = symbol.upper()
    try:
        async with aiohttp.ClientSession() as session: # use aiohttp to make an asynchronous request to the RapidAPI endpoint
            url = f"{rapidapi_endpoint}/stock/v2/get-summary?symbol={symbol}&region=US"
            headers = {"X-RapidAPI-Key": rapidapi_key}

            async with session.get(url, headers=headers) as response: # make a GET request to the specified URL
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
        query = text(
            "SELECT EXISTS(SELECT 1 FROM stock_info WHERE symbol = :symbol)")  # check if the symbol exists in the database, if not insert it
        symbol_exists = connection.execute(query, {"symbol": symbol}).scalar()
        print(f'Symbol {symbol} exists: ', symbol_exists)
        if not symbol_exists:
            with concurrent.futures.ThreadPoolExecutor():  # use a thread pool to insert the data, will be faster
                try:
                    # if the data exists, it will be updated, if not just skip
                    df.to_sql("stock_info", con=engine, if_exists='append', index=False)
                    print(f"Stock info for {symbol} inserted successfully")
                    # default date range for stock price data (a new table is used with the stock symbol as the table name)
                    start_date = "2023-10-01"
                    end_date = "2024-01-01"
                    await fetch_price_data(symbol, start_date, end_date)  # call the second api to fetch stock price data
                except Exception as e:
                    print(e)
                    traceback.print_exc()
    return stock_info, {"message": "Stock info inserted successfully"}


@app.get("/stock_price/{symbol}") # connects to rapidapi and fetches stock price data
async def fetch_price_data(symbol: str, start_date: str, end_date: str):
    try:
        async with aiohttp.ClientSession() as session: # use aiohttp to make an asynchronous request to the RapidAPI endpoint
            url = f"{rapidapi_endpoint}/stock/v2/get-historical-data?symbol={symbol}&region=US&from={start_date}&to={end_date}"
            headers = {"X-RapidAPI-Key": rapidapi_key}

            async with session.get(url, headers=headers) as response: # make a GET request to the specified URL
                response_data = await response.json()
                stock_data_list = response_data["prices"]
    except Exception as e:
        print(e)
        return {"message": "Symbol not found"} # if the symbol is not found, return a message

    with concurrent.futures.ThreadPoolExecutor() as executor:  # use a thread pool to insert the data, will be faster
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
                try: # insert the data into the database
                    executor.submit(df.to_sql, symbol, con=engine, if_exists='append', index=False)
                except Exception as e:
                    print(e)

    return stock_data, {"message": "Data has been successfully added to the database."}

@app.delete("/stock_delete/{symbol}") # delete stock from database
async def delete_stock(symbol: str):
    with engine.connect() as connection:
        query = text("DELETE FROM stock_info WHERE symbol = :symbol") # query to delete the stock info from the database
        result = connection.execute(query, {"symbol": symbol})
        try:
            table_to_drop = Table(symbol, metadata)
            table_to_drop.drop(engine)
        except exc.NoSuchTableError: # if the table is not found, return a message
            return {"message": f"No table named {symbol} found"}
        if result.rowcount == 0: # if the symbol is not found, return a message
            return {"message": "Symbol not found"}
            # Drop the table with the same symbol

        return {"message": "Symbol and corresponding table deleted successfully"}

# used for testing purposes only:
# if __name__ == "__main__":
#     import uvicorn
#
#     uvicorn.run(app, host="0.0.0.0", port=8001, reload=)
