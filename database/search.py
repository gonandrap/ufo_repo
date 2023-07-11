import logging
from connection import UFODatabase
from datetime import date
from sqlalchemy import select

class DBSearch:
    db = None
    logger = None


    def __init__(self):
        self.db = UFODatabase()
        self.logger = logging.getLogger('db_search')

    def search_by_date(self, date : date) -> list:
        ufo_obs_table = self.db.get_table('ufo_observation')
        ufo_desc_table = self.db.get_table('ufo_description')
        stmt = select(ufo_obs_table, ufo_desc_table).where(
                ufo_obs_table.c.obs_posted == date,                             # the correct columns to use are ufo_desc_table.c.obs_ocurred or ufo_desc_table.c.obs_reported, but only considerig the date, not the time.
                ufo_obs_table.c.obs_id == ufo_desc_table.c.obs_id
                )
        return self.__execute_query(stmt)
        
    def search_by_date_range(self, date_from : date, date_to : date) -> list:
        ufo_obs_table = self.db.get_table('ufo_observation')
        ufo_desc_table = self.db.get_table('ufo_description')
        stmt = select(ufo_obs_table, ufo_desc_table).where(
                ufo_obs_table.c.obs_posted >= from_date,                        # the correct columns to use are ufo_desc_table.c.obs_ocurred or ufo_desc_table.c.obs_reported, but only considerig the date, not the time.
                ufo_obs_table.c.obs_posted <= to_date,
                ufo_obs_table.c.obs_id == ufo_desc_table.c.obs_id
                )
        return self.__execute_query(stmt)


    def search_by_location(self, location : str):
        ufo_obs_table = self.db.get_table('ufo_observation')
        ufo_desc_table = self.db.get_table('ufo_description')
        stmt = select(ufo_obs_table, ufo_desc_table).where(
                ufo_obs_table.c.obs_city == location,
                ufo_obs_table.c.obs_id == ufo_desc_table.c.obs_id
                )
        return self.__execute_query(stmt)

    def search_all(self):
        ufo_obs_table = self.db.get_table('ufo_observation')
        ufo_desc_table = self.db.get_table('ufo_description')
        stmt = select(ufo_obs_table, ufo_desc_table).where(
                ufo_obs_table.c.obs_id == ufo_desc_table.c.obs_id
                )
        return self.__execute_query(stmt)



    def __execute_query(self, stmt):
        try:
            with self.db.get_connection() as connection:
                return connection.execute(stmt)
        except DBConnectionException as e:
            self.logger.error(f'Error trying to execute query [{stmt}] -> {repr(e)}')
            return []


# ----- TESTING ----- 
def set_env_variables():
    import os

    os.environ['DB_HOSTNAME'] = 'localhost'
    os.environ['DB_PORT'] = '5432'
    os.environ['DB_USER'] = 'coding'
    os.environ['DB_PASSWORD'] = 'coding'
    os.environ['DB_NAME'] = 'ufo'

def print_results(results):
    for row in results:
        print(row)

def test_search_by_date():
    from datetime import datetime

    set_env_variables()
    db_search = DBSearch()

    date_from = datetime.strptime('03/01/2023', '%M/%d/%Y')
    print_results(db_search.search_by_date(date_from))

def test_search_by_location():
    set_env_variables()
    db_search = DBSearch()

    print_results(db_search.search_by_location('Tacoma'))

if __name__ == '__main__':
    #test_search_by_location() 
    test_search_by_date()