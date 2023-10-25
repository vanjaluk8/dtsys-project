# Distributed systems project source code

This source code will be used to deploy a MySQL cluster on a simple K8S installation. The MySQL instance will be connected towards end users via a PySpark module and data will be retrieved via REST API calls. FastAPI will be used as a fronted and the results will be returned as simple json outputs. The database will be populated with dummy data that will serve for testing purposes only. A draw.io source diagram can be found [here](https://github.com/vanjaluk8/dtsys-project/blob/main/DistributedSystems.drawio).


## Steps to prepare the environment 
*the host machine is an ordinary Ubuntu 22.04. distribution*

### 1. Install a K8S cluster using vagrant (follow this example):
1. install virtualbox on your machine
2. clone this repo: [vagrant kubeadm kubernetes](https://github.com/techiescamp/vagrant-kubeadm-kubernetes)
3. setup the machine requirements (eg number of pods, network, naming convention)
4. connect to the master node using vagrant ssh <master_node_name> and install kubectl
`snap install kubectl --classic`

### 2. Setup helm and add mysql deployment on your k8s master node (Ubunut 22.04 LTS in this example)
1. Install helm: `snap install helm --classic`
2. add `bitnami/mysql` repo: `sudo helm repo add bitnami https://charts.bitnami.com/bitnami` 
3. run `helm repo update`
4. setup a simple yaml file `values.yml` which will be used to setup all the necessary parameters for the mysql installation
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