
from pydantic import BaseModel
from datetime import date

search_types : dict = {'SearchAll':'all', 'SearchByLocation':'location', 'SearchByDate':'location'}

class SearchModel(BaseModel):
    type : str

class SearchAll(SearchModel):
    type : str = search_types['SearchAll'] 

class SearchByLocation(SearchModel):
    type : str = search_types['SearchByLocation']
    location: str

class SearchByDate(SearchModel):
    type : str = search_types['SearchByDate']
    date: date
