import glob
import os

from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
import pandas as pd
from pymongo import MongoClient
from datetime import datetime

from models.indexes import Index

app = FastAPI()
user = 'root'
password = 'DOCKER123!'


# date time now

@app.on_event("startup")
async def startup_event():
    app.mongodb_client = AsyncIOMotorClient(f'mongodb://{user}:{password}@localhost:27017')
    app.mongodb1 = app.mongodb_client['index_data']
    app.mongodb2 = app.mongodb_client['stock_data']



### ASINKRONI DIO
@app.get("/return_index_data")
async def return_index_data(collection_name: Index):
    """
        Returns all documents from the NASDAQ collection in the index_data database
        Use symbol name: NASDAQ, SP500, QQQ
    """
    cursor = app.mongodb1[collection_name.value].find()
    # convert to list
    data = await cursor.to_list(length=10000)  # specify a length limit
    # convert ObjectId to string
    for item in data:
        item['_id'] = str(item['_id'])
    # convert to dataframe and save to csv
    df = pd.DataFrame(data)
    df.to_csv(f'indexes/{collection_name}.async.csv', index=False)

    return data

@app.post("/add_stock_data")
async def add_stock_data(file_name: str):
    df = pd.read_csv(f'stocks/{file_name}.csv')
    data = df.to_dict(orient='records')
    db = app.mongodb2
    collection = db[file_name.split('.')[0] + '_' + datetime.now().isoformat()]
    await collection.insert_many(data)

    return {
        "message": f"Data from {file_name} uploaded to {file_name.split('.')[0]} collection in 'stock_data' database"}


## SINKRONI DIO
@app.get("/return_index_data_sync")
def return_nasdaq_sync(collection_name: Index):
    client = MongoClient(f'mongodb://{user}:{password}@localhost:27017')
    db = client['index_data']
    cursor = db[collection_name.value].find()
    # convert to list
    data = list(cursor)
    # convert ObjectId to string
    for item in data:
        item['_id'] = str(item['_id'])
    # convert to dataframe
    df = pd.DataFrame(data)
    df.to_csv(f'indexes/{collection_name}.sync.csv', index=False)
    return data

@app.post("/add_stock_data_sync")
def add_stock_data_sync(file_name: str):
    df = pd.read_csv(f'stocks/{file_name}.csv')
    data = df.to_dict(orient='records')
    client = MongoClient(f'mongodb://{user}:{password}@localhost:27017')
    db = client['stock_data']
    collection = db[file_name.split('.')[0] + '_' + datetime.now().isoformat()]
    collection.insert_many(data)
    return {
        "message": f"Data from {file_name} uploaded to {file_name.split('.')[0]} collection in 'stock_data' database"}

# if __name__ == "__main__":
#     import uvicorn
#
#     uvicorn.run(app, host="0.0.0.0", port=8001, reload=)
