# ufo_repo
Repo used for the UFO coding challenge


# Environment
```
conda create --name ufo python=3.9
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

# Setup dev env
You need to install *conda* environment manager with python 3.9 installed on it. To replicate the env just execute:
```
conda create --name <env_name> --file requirements.txt
```
Once created, make sure to activate it:
```
conda activate <env_name>
```

# Web scraper manual run
From *scrapper* folder execute:
```
scrapy crawl observations --loglevel INFO -a url=https://nuforc.org/webreports/ndxevent.html -a date_from=05/19/2023 -a bucket_name=codingchallengeimportfiles -a table_name=scrap_run
```
Alternatively, it can be run by just executing next command (being positioned on folder <workspace_folder>/scrapper):
```
python run_crawler.py
```


# Links
* Run scrapy in a container : [link](https://shinesolutions.com/2018/09/13/running-a-web-crawler-in-a-docker-container/)
* Run python and DB in a container using compose [link](https://stefanopassador.medium.com/docker-compose-with-python-and-posgresql-45c4c5174299)
    * Another one for DB only [link](https://www.docker.com/blog/how-to-use-the-postgres-docker-official-image/)
* Run a cronjob inside docker [link](https://devtron.ai/blog/running-a-cronjob-inside-docker-container-in-5-steps/)
