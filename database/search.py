import logging
from connection import UFODatabase
from datetime import datetime, date, timedelta
from sqlalchemy import select

class DBSearch:
    db = None
    logger = None


    def __init__(self):
        self.db = UFODatabase()
        self.logger = logging.getLogger('db_search')

    def search_by_date(self, date : date) -> list:
        """
            Returns all observations that ocurred during the day represented by **date** (ignoring matching exact time)
        """
        return self.search_by_date_range(*self.__to_date_range(date))
        
    def search_by_date_range(self, date_from : date, date_to : date) -> list:
        ufo_obs_table = self.db.get_table('ufo_observation')
        ufo_desc_table = self.db.get_table('ufo_description')
        stmt = select(ufo_obs_table, ufo_desc_table).where(
                ufo_desc_table.c.obs_ocurred >= date_from,
                ufo_desc_table.c.obs_ocurred <= date_to,
                ufo_obs_table.c.obs_id == ufo_desc_table.c.obs_id
                ).order_by(ufo_desc_table.c.obs_ocurred)
        return self.__execute_query(stmt)


    def search_by_location(self, location : str):
        ufo_obs_table = self.db.get_table('ufo_observation')
        ufo_desc_table = self.db.get_table('ufo_description')
        stmt = select(ufo_obs_table, ufo_desc_table).where(
                ufo_obs_table.c.obs_city == location,
                ufo_obs_table.c.obs_id == ufo_desc_table.c.obs_id
                ).order_by(ufo_desc_table.c.obs_ocurred)
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

    def __to_date_range(self, specific_datetime : datetime) -> (datetime, datetime):
        """
            Given a datetime, it will return two datetimes that represent the beginning and end of the 
            date for that particular datetime 
        """
        from_datetime = datetime.strptime(datetime.strftime(specific_datetime, "%m/%d/%Y"), "%m/%d/%Y")
        to_datetime = from_datetime + timedelta(days=1)
        return (from_datetime, to_datetime)


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

def test_search_by_date_range():
    from datetime import datetime

    set_env_variables()
    db_search = DBSearch()

    date_from = datetime.strptime('07/01/2023', '%m/%d/%Y')
    date_to = datetime.strptime('07/31/2023', '%m/%d/%Y')
    print_results(db_search.search_by_date_range(date_from, date_to))

def test_search_by_date():
    from datetime import datetime

    set_env_variables()
    db_search = DBSearch()

    date_from = datetime.strptime('07/08/2023', '%m/%d/%Y')
    print_results(db_search.search_by_date(date_from))

def test_search_by_location():
    set_env_variables()
    db_search = DBSearch()

    print_results(db_search.search_by_location('Tacoma'))

if __name__ == '__main__':
    #test_search_by_location() 
    #test_search_by_date()
    test_search_by_date_range()