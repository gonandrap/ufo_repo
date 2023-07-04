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

