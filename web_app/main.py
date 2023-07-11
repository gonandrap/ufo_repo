
from fastapi import FastAPI
from business.search_criteria import SearchCriteria
from model import SearchModel, UfoObservation
from typing import Union



app = FastAPI()

@app.get('/')
async def root():
    return {'message':'Welcome to the best UFO DB search engine!'}

@app.post('/search', response_model=Union[UfoObservation, None])
async def search(item: SearchModel):
    return SearchCriteria.create(item).search()
    