
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime, date
from typing import Union

search_types : dict = {'SearchAll':'all', 'SearchByLocation':'location', 'SearchByDate':'date', 'SearchByDateRange':'date_range'}

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

class SearchByDateRange(SearchModel):
    type : str = search_types['SearchByDateRange']
    date_from: date
    date_to: date = Field(default=datetime.now())
