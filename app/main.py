import glob
import os

from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
import pandas as pd
import asyncio
from pymongo import MongoClient

app = FastAPI()
user = 'root'
password = 'DOCKER123!'


@app.on_event("startup")
async def startup_event():
    app.mongodb_client = AsyncIOMotorClient(f'mongodb://{user}:{password}@localhost:27017')
    app.mongodb = app.mongodb_client['index_data']

@app.get("/return_nasdaq_async")
async def return_nasdaq_async():
    cursor = app.mongodb['NASDAQ'].find()
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

# if __name__ == "__main__":
#     import uvicorn
#
#     uvicorn.run(app, host="0.0.0.0", port=8001, reload=)
