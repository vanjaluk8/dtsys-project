# Distributed systems project source code
This collection of applications and scripts is used as a demonstration on how a distributed system works in practice.

FastAPI will be used as a fronted and the results will be returned as simple json outputs. The database will be populated with dummy data that will serve for testing purposes only. A draw.io source diagram can be found [here](https://github.com/vanjaluk8/dtsys-project/blob/main/DistributedSystems.drawio).

## How to retrieve data from an end user perspective?
Any type of API call can be used, eg. via Postman, curl and jq or similar.

## Steps to prepare the environment 
*The host machine is an ordinary Ubuntu 22.04. distribution*

## run docker containers
1. mysql
2. grafana
3. fastapi

The infrastructure part is now ready to deploy other services

---

1. Create a simple docker container that will run a mysql and grafana, example here: [docker-compose.yaml](docker-compose.yaml)
2. Import some dummy data, sql source here: [sample_data](sample_dbs), for mongo use csv files
3. Use RapidAPI to get some dummy data, example here: [rapidapi](rapidapi) for yahoo finance data

### The code
- main.py is used for connecting to the databases.
  - using FASTApi to prove async communication and large-scale data processing
  - routes are added for each query or example that we need
  - swagger is available and adds some interactivity to the whole setup: http://localhost:8000/doc
  - start the application on localhost using uvicorn (later I will put it in a docker container)
- data_manipulation.ipynb (just for quick testing)
  - install Jupyter before using this file
  - just examples of how data can be pulled out and manipulated
- grafana visualisation
  - connect to 127.0.0.1:3000, some dashobards will be ready
  - connects to mysql to display the data and uses variables to be more dynamic when asking for certain stocks

------
## Diagram
- will add a newer one later or not, depends :D 

------
[CHANGELOG.md](CHANGELOG.md) 