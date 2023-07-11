from model.search_item import SearchModel, SearchAll, SearchByDate, SearchByLocation, search_types
import logging

class SearchCriteria:
    search_item = None
    logger = None

    def __init__(self, search_item):
        self.search_item = search_item
        self.logger = logging.getLogger('search_criteria')

    @classmethod
    def create(self, item):
        if item.type == search_types[SearchByDate.__name__]:
            return SearchByDateCriteria(item)
        elif item.type == search_types[SearchByLocation.__name__]:
            return SearchByLocationCriteria(item)
        elif item.type == search_types[SearchAll.__name__]:
            return SearchAllCriteria(item)
        else:
            self.logger.error(f'Unrecognized item type [{item.type}], defaulting to SearchAll')
            return SearchAllCriteria(item)

    def search(self):
        raise NotImplemented('Cant instantiate an abstract SearchCriteria')

class SearchAllCriteria(SearchCriteria):
    def search(self):
        self.logger.info('Retrieving all observations')
        return None

class SearchByDateCriteria(SearchCriteria):
    def search(self):
        self.logger.info(f'Retrieving date-based observations for date {self.item.date}')
        return None

class SearchByLocationCriteria(SearchCriteria):
    def search(self):
        self.logger.info(f'Retrieving location-based observations for location {self.item.location}')
        return None