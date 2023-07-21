
import uvicorn
from fastapi import FastAPI
from business.search_criteria import SearchCriteria
from model import SearchModel, UfoObservation, UfoObservationList
from typing import Union
from database.search import DBSearch
import os

app = FastAPI()
search_engine = DBSearch()

@app.get('/')
async def root():
    return {'message':'Welcome to the best UFO DB search engine!'}
    

@app.post('/search', response_model=UfoObservationList)              
async def search(item: SearchModel):
    return SearchCriteria.create(item).search(search_engine)

if __name__ == '__main__':
    uvicorn.run(app, host=os.environ.setdefault('HOSTNAME', 'localhost'), port=os.environ.setdefault('PORT', '8000'))