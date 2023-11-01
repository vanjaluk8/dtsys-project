# Distributed systems project source code
This collection of applications and scripts is used as a demonstration on how a distributed system works in practice.
This source code will be used to deploy a **MySQL cluster** on a simple **K8S (Kubernetes)** installation. The MySQL instance will be connected towards end users via a PySpark module and data will be retrieved via *REST API calls*. 

FastAPI will be used as a fronted and the results will be returned as simple json outputs. The database will be populated with dummy data that will serve for testing purposes only. A draw.io source diagram can be found [here](https://github.com/vanjaluk8/dtsys-project/blob/main/DistributedSystems.drawio).

## How to retrieve data from an end user perspective?
Any type of API call can be used, eg. via Postman, curl and jq or similar.

## Steps to prepare the environment 
*The host machine is an ordinary Ubuntu 22.04. distribution*

### 1. Install a K8S cluster using vagrant (follow this example):
1. install Virtualbox on your machine (the easiest virtualization engine to use and configure)
2. install **Vagrant** an ultra simple interface that can talk with your virtualization software
3. clone this repo: [vagrant kubeadm kubernetes](https://github.com/techiescamp/vagrant-kubeadm-kubernetes)
4. set up the machine requirements (eg. number of pods, network parameters, naming convention and resources)
5. connect to the master node using vagrant ssh <master_node_name> and install **kubectl**: 
`snap install kubectl --classic`

### 2. Setup helm and add mysql deployment on your k8s master node (Ubunut 22.04 LTS in this example)
1. Install **`helm`**: `snap install helm --classic`
2. add **`bitnami/mysql`** repo: `sudo helm repo add bitnami https://charts.bitnami.com/bitnami` 
3. run `helm repo update`
4. set up a simple yaml file `values.yml` which will be used to setup all the necessary parameters for the MySQL installation
```
## MySQL User
mysqlUser: <set_username>

## MySQL Password
mysqlPassword: <set_password>

## MySQL Database
mysqlDatabase: <set_db_name>

## Service type
service:
  enabled: true
  type: ClusterIP

```
5. install mysql: `helm install mysql bitnami/mysql -f values.yaml`
6. follow the screen instructions to finish your mysql installation
7. run this command on your master node: `kubectl port-forward svc/mysql 3306:3306`

The infrastructure part is now ready to deploy other services

---

## 2. Testing part with sample data and a simple docker setup 
*I am using this most of the time because testing is faster and implementation of fixes does not require a lot of changes*

1. Create a simple docker container that will run a mysql database, example here: [docker-compose.yaml](docker-compose.yaml)
2. Import some dummy data, sql source here: [sample_data](sample_dbs)

### The code
- main.py is used for connecting to the database.
  - using FASTApi and Pyspark to prove async communication and large-scale data processing
  - routes are added for each query or example that we need
  - swagger is available and adds some interactivity to the whole setup: http://localhost:8000/doc
  - start the application on localhost using uvicorn (later I will put it in a docker container)
- data_manipulation.ipynb
  - install Jupyter before using this file
  - just examples of how data can be pulled out and manipulated


------
[CHANGELOG.md](CHANGELOG.md) 