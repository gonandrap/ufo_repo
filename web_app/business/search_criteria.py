from model.search_item import SearchModel, SearchAll, SearchByDate, SearchByLocation, SearchByDateRange, search_types
from model.entity_object import UfoObservationList
import logging

class SearchCriteria:
    search_item = None
    logger = None

    def __init__(self, search_item):
        self.search_item = search_item
        self.logger = logging.getLogger('search_criteria')

    @classmethod
    def create(cls, item):
        if item.type == search_types[SearchByDate.__name__]:
            return SearchByDateCriteria(item)
        elif item.type == search_types[SearchByDateRange.__name__]:
            return SearchByDateRangeCriteria(item)
        elif item.type == search_types[SearchByLocation.__name__]:
            return SearchByLocationCriteria(item)
        elif item.type == search_types[SearchAll.__name__]:
            return SearchAllCriteria(item)
        else:
            self.logger.error(f'Unrecognized item type [{item.type}], defaulting to SearchAll')
            return SearchAllCriteria(item)

    def search(self, search_engine):
        raise NotImplemented('Cant instantiate an abstract SearchCriteria')

class SearchAllCriteria(SearchCriteria):
    def search(self, search_engine):
        self.logger.info('Retrieving all observations')
        return UfoObservationList(observations=search_engine.search_all())

class SearchByDateCriteria(SearchCriteria):
    def search(self, search_engine):
        self.logger.info(f'Retrieving date-based observations for date {self.item.date}')
        return search_engine.search_by_date(self.item.date)

class SearchByDateRangeCriteria(SearchCriteria):
    def search(self, search_engine):
        self.logger.info(f'Retrieving date-based observations for date_from {self.item.date_from} and date_to {self.item.date_to}')
        return search_engine.search_by_date_range(self.item.date_from, self.item.date_to)

class SearchByLocationCriteria(SearchCriteria):
    def search(self, search_engine):
        self.logger.info(f'Retrieving location-based observations for location {self.item.location}')
        return search_engine.search_by_location(self.item.location)