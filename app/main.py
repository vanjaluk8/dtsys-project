import glob
import os

from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
import pandas as pd
import asyncio
from pymongo import MongoClient
from datetime import datetime

app = FastAPI()
user = 'root'
password = 'DOCKER123!'

# date time now

@app.on_event("startup")
async def startup_event():
    app.mongodb_client = AsyncIOMotorClient(f'mongodb://{user}:{password}@localhost:27017')
    app.mongodb1 = app.mongodb_client['index_data']
    app.mongodb2 = app.mongodb_client['stock_data']

@app.get("/return_nasdaq_async")
async def return_nasdaq_async():
    cursor = app.mongodb1['NASDAQ'].find()
    # convert to list
    data = await cursor.to_list(length=1000)  # specify a length limit
    # convert ObjectId to string
    for item in data:
        item['_id'] = str(item['_id'])
    # convert to dataframe
    return data

@app.get("/return_nasdaq_sync")
def return_nasdaq_sync():
    client = MongoClient(f'mongodb://{user}:{password}@localhost:27017')
    db = client['index_data']
    cursor = db['NASDAQ'].find()
    # convert to list
    data = list(cursor)
    # convert ObjectId to string
    for item in data:
        item['_id'] = str(item['_id'])
    # convert to dataframe

    return data

@app.post("/add_stock_data_async")
async def add_stock_data_async(file_name: str):
    df = pd.read_csv(f'stocks/{file_name}.csv')
    data = df.to_dict(orient='records')
    db = app.mongodb2
    collection = db[file_name.split('.')[0] + '_' + datetime.now().isoformat()]
    await collection.insert_many(data)

    return {"message": f"Data from {file_name} uploaded to {file_name.split('.')[0]} collection in 'stock_data' database"}


@app.post("/add_stock_data_sync")
def add_stock_data_sync(file_name: str):
    df = pd.read_csv(f'stocks/{file_name}.csv')
    data = df.to_dict(orient='records')
    client = MongoClient(f'mongodb://{user}:{password}@localhost:27017')
    db = client['stock_data']
    collection = db[file_name.split('.')[0]+'_'+datetime.now().isoformat()]
    collection.insert_many(data)
    return {"message": f"Data from {file_name} uploaded to {file_name.split('.')[0]} collection in 'stock_data' database"}

# if __name__ == "__main__":
#     import uvicorn
#
#     uvicorn.run(app, host="0.0.0.0", port=8001, reload=)


