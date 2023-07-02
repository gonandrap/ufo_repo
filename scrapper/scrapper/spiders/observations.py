
import scrapy
from datetime import datetime]
from enum import Enum

class COLUMN(Enum):
    CITY = 1
    SATE = 2
    COUNTRY = 3
    SHAPE = 4
    DURATION = 5
    SUMMARY = 5
    POSTED = 6
    IMAGES =7


class ObservationsSpider(scrapy.Spider):
    name = 'observations'

    def start_requests(self):
        urls = ['https://nuforc.org/webreports/ndxpost.html']

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        rows = response.xpath('//tbody//tr/td')
        
        for row in rows:
            relative_link = rows[0].xpath('//a/@href')
            date = datetime.strptime(rows[0].xpath('//a/text()', '%m/%d/%Y'))
            if date >= self.date_from:
                follow_url = relative_link[0].extract()+'/webreports/'+relative_link[1].extract()
                print(f'FOLLOW_URL={follow_url}')
                yield scrapy.Request(url=follow_url, callback=self.parse_observations_per_date)


    def parse_observations_per_date(self, response):
        rows = response.xpath('//tbody//tr/td')
        for row in rows:
            relative_link = rows[0].xpath('//a/@href')
            unique_id = rows[0].xpath('//a/text()')
            city = rows[0][COLUMN.CITY]
            state = rows[0][COLUMN.SATE]
            country = rows[0][COLUMN.COUNTRY]
            shape = rows[0][COLUMN.SHAPE]
            duration = rows[0][COLUMN.DURATION]
            summary = row[0][COLUMN.SUMMARY]
            posted = datetime.strptime(row[0][COLUMN.DURATION], '%m/%d/%Y')
            images = (row[0][COLUMN.IMAGES] == 'Yes')

            # TODO follow link to get details of the observations
