import sqlalchemy as db
import logging
import os
from sqlalchemy.pool import QueuePool
from sqlalchemy import Integer, Float, Date, DateTime, Time, String, Enum, ForeignKey, JSON, PickleType, ForeignKeyConstraint, Boolean, MetaData, Text
from sqlalchemy.exc import IntegrityError
import enum

class ShapeEnum(enum.Enum):
    Oval = 1
    Triangle = 2
    Light = 3
    Dark = 4
    Orb = 5
    Fireball = 6
    Circle = 7
    Changing = 8
    Disk = 9
    Cylinder = 10
    Rectangle = 11
    Egg = 12
    Cube = 13
    Sphere = 14
    Formation = 15
    Chevron = 16
    Flash = 17
    Star = 18
    Cone = 19
    Other = 20
    Unknown = 21

class DBConnectionException(Exception):
    pass

class UFODatabase:
    engine = None
    connection = None
    metadata = None
    logger = None

    column_types = None

    def __init__(self):
        self.logger = logging.getLogger('db_connection')
        self.__init_column_names()

        try:
            db_string = self.__create_db_connection_string()
            self.engine = db.create_engine(db_string, poolclass=QueuePool, isolation_level='AUTOCOMMIT')        # default pool_size and max_overflow parameters will be more than enough to handle the load
            self.connection = self.engine.connect()
            self.__init_metadata()
        except Exception as e:
            raise DBConnectionException(repr(e))

    
    def get_connection(self):
        """
            Returns a proxy to the actual connection. Client is reponsible for handling exceptions. See details 
            here in regards to engine and connection semantics : https://docs.sqlalchemy.org/en/20/core/connections.html#setting-transaction-isolation-levels-including-dbapi-autocommit
        """
        return self.engine.connect()


    def get_columns_types(self, table_name):
        try:
            return self.column_types[table_name]
        except KeyError as e:
            raise DBConnectionException(f'Table [{table_name}] doesnt exist. Stoping execution.')

    def get_table(self, table_name):
        try:
            return self.metadata.tables[table_name]
        except KeyError as e:
            raise DBConnectionException(f'Table [{table_name}] doesnt seems to exist. Make sure to create it before importing.')
        except Exception as e:
            raise DBConnectionException(f'Trying to get table from name [{table_name}]')


    def __init_column_names(self):
        self.column_types = {}
        self.column_types['ufo_observation'] = {'obs_id':String,'obs_posted':Date,'obs_city':String,'obs_state':String,'obs_country':String,'obs_shape':Enum(ShapeEnum),'obs_duration':String,'obs_images':Boolean}
        self.column_types['ufo_description'] = {'obs_id':String, 'obs_ocurred':Time, 'obs_reported':Time, 'obs_summary':Text, 'obs_detailed_description':Text}

    def __create_db_connection_string(self):
        try:
            db_user = self.__safe_load('DB_USER')
            db_password = self.__safe_load('DB_PASSWORD')
            db_host = self.__safe_load('DB_HOSTNAME')
            db_port = int(self.__safe_load('DB_PORT'))
            db_name = self.__safe_load('DB_NAME')

            return f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
        except ValueError as e:
            raise ValueError(f'Trying to load DB environment variables. \n\tDescription : {repr(e)}')


    def __init_metadata(self):
        self.metadata = MetaData()
        self.metadata.reflect(bind=self.engine, views=True)

    def __safe_load(self, key):
        value = os.getenv(key)
        if value is None:
            raise DBConnectionException(f'Missing en variable [{key}], cant connect to db. Stopping.')
        else:
            return value


    