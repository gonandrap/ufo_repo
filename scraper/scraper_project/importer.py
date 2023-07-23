import csv
import pandas as pd
from database.connection import UFODatabase, DBConnectionException
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation
import logging
import os

class DBImporter:
    db = None
    logger = None

    def __init__(self):
        self.db = UFODatabase()
        self.logger = logging.getLogger('db_importer')

    def run(self, filename, index_col):
        df = pd.read_csv(filename, index_col=index_col, encoding='utf_8')           # see encoding options here : https://docs.python.org/3/library/codecs.html#standard-encodings
        df_ufo_observation = df.iloc[:, 0:7]
        df_ufo_description = df.iloc[:, 7:]

        try:
            with self.db.get_connection() as connection:
                df_ufo_observation.to_sql('ufo_observation', connection, if_exists='append', dtype=self.db.get_columns_types('ufo_observation'), method=self.__run_insertion)
                df_ufo_description.to_sql('ufo_description', connection, if_exists='append', dtype=self.db.get_columns_types('ufo_description'), method=self.__run_insertion)
        except DBConnectionException as e:
                # if we got this, then we stop execution
                self.logger.error(f'Trying to insert imported data into DB. Description -> {repr(e)}')
        except Exception as e:
            self.logger.error(repr(e))


    def __run_insertion(self, pd_table, conn, keys, data_iter):
        """
        Execute SQL statement inserting data

        Parameters
        ----------
        table : pandas.io.sql.SQLTable
        conn : sqlalchemy.engine.Engine or sqlalchemy.engine.Connection
        keys : list of str
            Column names
        data_iter : Iterable that iterates the values to be inserted
        """
        
        for data in data_iter:                              # got from here : https://stackoverflow.com/questions/55187884/insert-into-postgresql-table-from-pandas-with-on-conflict-update
            data = {key: data[i] for i, key in enumerate(keys)}
            insert_stmt = insert(self.db.get_table(pd_table.name)).values(**data)
            try:
                conn.execute(insert_stmt)
            except IntegrityError as e:
                if isinstance(e.orig, UniqueViolation):
                    self.logger.warning(f'[WARNING=Duplicated Entry] {e.orig.pgerror}')
                else:
                    logging.warning(f'[WARNING=INTEGRITY_ERROR] {str(e)}')

            except Exception as e:
                self.logger.error(f'Trying to execute [{insert_stmt}]. \nDescription -> {repr(e)}')


def set_env_variables():
    import os

    os.environ['DB_HOSTNAME'] = 'localhost'
    os.environ['DB_PORT'] = '5432'
    os.environ['DB_USER'] = 'coding'
    os.environ['DB_PASSWORD'] = 'coding'
    os.environ['DB_NAME'] = 'ufo'

if __name__ == '__main__':
    set_env_variables()

    importer = DBImporter()
    importer.run('./testing/mock_data.csv')
