# ufo_repo`
Repo used for the UFO coding challenge


# Environment
```
conda create --name <env_name> python=3.9
pip install -r requirements.txt
```

# Assumptions
* observations on the UFO original DB are only appended, they don't change once they were persisted.
* it seems that the column "Images" is a string instead of a boolean. I'll import as a boolean for consistency, 
interpreting null values as false
* it seems the column "Shape" is an enumerated type, for which I don't have the spec. I'll assume the values are the one observed in the DB. The reasoning of using an enum instead of just an string is to add a layer of Data validation to keep data normalized, considering that in the future we could potentially support search by shape. 
The downside of this design decision is a coupling between app & data layer.
* per date files of dumped data from the web scrapper have small size, therefore, no need to keep track of upload progress
* to facilitate the scraping, reports will be scraped by following the listing of "*index by EVENT DATE*"
    * all the entries with an approximated event date (name "*UNSPECIFIED / APPROXIMATE*") will be discarded.
* 


# Web scraper manual run
From *scrapper* folder execute:
```
scrapy crawl observations --loglevel INFO -a url=https://nuforc.org/webreports/ndxevent.html -a date_from=05/19/2023 -a bucket_name=codingchallengeimportfiles -a table_name=scrap_run
```
Alternatively, it can be run by just executing next command (being positioned on folder <workspace_folder>/scrapper):
```
python run_crawler.py
```

# How to create a build the containers?
## PostgresDB
### Create image
```
    cd <root_directory>
    cd db_scripts
    docker build -t postgres_db_image .
```
### Run image
Don't forget to do the port mapping (```-p``` option) to have the external container port being forwared to the one internal where the server is listening
```
    docker run --name postgres_db_container -p 50000:5432 -d postgres_db_image
```
### Confirm DB is running
```
    docker exec -it postgres_db_container bash
    psql postgres://coding:coding@localhost:5432/ufo
    \dt
```
## WebApp
### Create image
```
    cd <root_directory>
    docker build -t web_app_image -f web_app/Dockerfile .
```
Note that I'm using as build context the root directory of the repo (referred by ```.```). The reason for that is that ```docker build``` only accept manipulate files and directories within the build context, so in 
order to be able to access the **database** directory, I need to set the context to a parent level that can access both, the **database** and the **web_app** dirs.

### Run image
```
    docker run --name web_app_container -p 8001:8000 -d web_app_image
```
TODO : there is a problem! it is failing to connect to the database because I'm passing **localhost** as server, which is correct for the host machine but not when running dockerized! Need
to figure out how to obtain the address of the DB server programatically I guess (this all will be resolved when using k8s)

# Docker compose
When combinining multiple containers, we need to use docker-compose to manage them at the very basic. For learning purposes, before switching to minikube, I'll configure docker-compose.
To build and run the whole thing, execute :
```
    docker-compose up --build
```
the option ```build``` is not really needed, but I like to force rebuild the images, just in case.

## Throubleshooting
* make sure to set the startup dependencies correctly. For example, to start the web_app service, the db service must be up & running (accepting new connections). Check option ```depends_on``` on the compose file
    * to define when a service is in a healthy state (accepting connections for example), define the property ```healthcheck``` in the dependant service (**db_service** in this case)
* make sure to have the proper port forwarding on each service. See property ```ports```
* if you want docker to handle what happends if a containers stop running, use the property ```restart```
* for the particular case of the *web_app* and it's dependency with the database module, I had to define the build context for docker as the root folder of the repo and manually specify where it is the Dockefile,
check the property ```dockerfile```
* instead of defining the env vars on each Dockerfile, I think is a better practice to have them all centralized on the docker-compose, in particular the ones that refer to other services.
    * Take for example DB_HOSTNAME=db_service -> what it is actually doing is to use the hostname of the service ```db_service``` define in the compose.
* if you try to use env vars on a healthcheck test, make sure to specify **$$** since otherwise docker will try to parse it and don't recognize it as env var.
    * also, the CMD option doesn't work with env vars (at least for me), is better to use the CMD-SHELL option.

# Links
* Run scrapy in a container : [link](https://shinesolutions.com/2018/09/13/running-a-web-crawler-in-a-docker-container/)
* Run python and DB in a container using compose [link](https://stefanopassador.medium.com/docker-compose-with-python-and-posgresql-45c4c5174299)
    * Another one for DB only [link](https://www.docker.com/blog/how-to-use-the-postgres-docker-official-image/)
* Run a cronjob inside docker [link](https://devtron.ai/blog/running-a-cronjob-inside-docker-container-in-5-steps/)
