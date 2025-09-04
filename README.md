# KALLABOX

## What is KALLABOX? 

From as old as Ancient Greece, people of various trades used **_Gallaboxes_**  (Cash boxes) to organize their income and expenditure in an ordered manner. Most of them had locks, that would prevent an adversary from trying to steal the money inside them. This was the inspiration when **KALLABOX** was designed and developed (Using **Python**), a way of keeping account of influx and efflux of money, in a scalable way. It consists of 2 components, namely

  1. Kallabox-api alongwith a Database system (Backend)
  2. Kallabox-tui (Frontend)

## Kallabox API

Kallabox API is the backend API that can be used for general small-scale commercial accounting, written in Python using **FastAPI** and utilizes **Postgresql**, a database system. 

## Kallabox 101 

There are broadly 2 different ways, you can use the API, each with its unique API endpoints for various functionalities. They are,

  1. User -> Account Administrator (or) regular User 
  2. Service Administrator 

### 1. User

A regular **User** has the following endpoints alongwith their functionalities,

![Authentication](https://github.com/kallabox/kallabox-tui/assets/102421860/6e460180-590d-46ae-af54-72a85d030156)

![Income](https://github.com/kallabox/kallabox-tui/assets/102421860/a0268ec4-09af-48a4-9ae1-0929ebe8f006)

![Expenditure](https://github.com/kallabox/kallabox-tui/assets/102421860/e7be1de9-dbb8-431a-881e-e4588e1a7919)

![Expense Type](https://github.com/kallabox/kallabox-tui/assets/102421860/467fe9e6-1869-4774-a29c-525237690836)


An **Account Administrator** has some extra account specific functionalities on top of that of a regular user. Also, for an account administrator, a regular user's privileges extend to all the users within the account. They are,

![Account](https://github.com/kallabox/kallabox-tui/assets/102421860/0ca58958-01fa-4895-a392-8c608417622f)


### 2. Service Administrator

A **Service Administrator** is the highest privileged, and has the functionality to create and delete accounts, accounts, in which users can work. They have the following endpoints alongwith their functionalities,

![Super Admin](https://github.com/kallabox/kallabox-tui/assets/102421860/ee7ed5d9-ef5b-4149-91dc-5fca73728545)

## Requirements 

1. **Docker** -> On how to install Docker, [Click Here!](https://docs.docker.com/engine/install/). Now open Docker Desktop.

2. **Command Line Interface (CLI)** -> Install / Update to the latest version.

## Getting Started

1. Open a new Command Line Interface (CLI).
2. Make a new directory named **_kallabox_** using the following command.
```
mkdir kallabox
```
3. Navigate to the newly created **_kallabox_** directory using the following command.
```
cd kallabox
```
4. Clone the Github Repository for **_kallabox-api_** using the following command.
```
git clone https://github.com/kallabox/kallabox-api.git
```
5. Navigate to the newly cloned **_kallabox-api_** directory using the following command.
```
cd kallabox-api
```
6. Create and run the docker containers using the following command.
```
docker compose up -d
```

You should be able to see an output like this at the end.

![Kallabox-api success](https://github.com/kallabox/kallabox-api/assets/102421860/cbe4e6dc-e965-4e53-9929-288c3763a969)

To verify, type the following command and under the **Containers** section check for 2 containers named **_kallabox-db_** and **_kallabox-api_**. 
```
docker network inspect kallabox-network
```
A sample output is shown below.

![Kallabox-api check](https://github.com/kallabox/kallabox-tui/assets/102421860/9f15cc2b-90f3-4922-b80a-b878a7198a89)

Now, the backend of **Kallabox** is up and running.

**Note :-** If you want to access the **_kallabox-api_** on a different port, change the ```${KALLABOX_HTTP_PORT:-8888}:8888``` to ```${KALLABOX_HTTP_PORT:-"Host Port Number"}:"Container Port Number"```
in the docker-compose.yml file before the ```docker compose up -d``` command.

### Stopping containers

To stop and remove the containers, use the following command.
```
docker compose down
```

Your output should look something like this at the end.

![Kallabox-api stop](https://github.com/kallabox/kallabox-api/assets/102421860/ccbdd409-f369-45ef-8397-162a7b411e85)

**Note** :- Deleting the containers does not delete the data stored in the database, since **volumes** are used to persist data.

To cleanup the stack and start afresh, use the following command.
```
docker compose down --rmi all --volumes --remove-orphans
```
Your output should look something like this at the end.

![Kallabox-api stop](https://github.com/kallabox/kallabox-api/assets/102421860/c2b08d5a-5425-4690-9738-67c516a78a9c)




**Note** :- The above method completely erases all data stored in the database, user caution is advised.

## Swagger UI Documentation

To checkout the working of the ***Kallabox-API*** in Swagger UI, go to your browser and type the following URL when the containers are running.
```
localhost:8888/docs
```

## Credits 

To [@shibme](https://github.com/shibme), for guiding me through this project.

