
import scrapy
from datetime import datetime
from dateutil.relativedelta import relativedelta
from enum import Enum
import pandas as pd
import tempfile
import os
import logging
import boto3
import botocore
import requests


class COLUMN(Enum):
    ID = 0
    CITY = 1
    SATE = 2
    COUNTRY = 3
    SHAPE = 4
    DURATION = 5
    SUMMARY = 6
    POSTED = 7
    IMAGES =8


class ObservationsSpider(scrapy.Spider):
    """Parameters of the spider

        :param url: the url to start scrapping
        :param date_from: date to start looking for observations. 
        :param bucket_name: name of the S3 bucket to upload csv generated files
    """
    name = 'observations'
    timeout = 3

    def __init__(self, url, date_from, bucket_name, *args, **kwargs):
        super(ObservationsSpider, self).__init__(*args, **kwargs) 
        self.url = url 
        self.date_from = datetime.strptime(date_from, '%m/%d/%Y') 
        self.bucket_name = bucket_name

    def start_requests(self):
        logging.info(f'Scrapping [{self.url}]')
        yield scrapy.Request(url=self.url, callback=self.download_data)


    def download_data(self, response):
        rows = response.xpath('//tbody//tr')
        
        for row in rows:
            reports = row.xpath('./td')[0]
            date = datetime.strptime(reports.xpath('./a/text()').extract_first(), '%m/%Y')
            date_after_month = date + relativedelta(months=1) # this is because the page counts by end of month, but python assumes first day of month
            if date_after_month >= self.date_from:
                logging.info(f'Found observations for date [{date}]')
                follow_url = response.urljoin(reports.xpath('./a/@href').extract_first())
                logging.debug(f'Following url [{follow_url}]')
                yield response.follow(url=follow_url, meta={'observations_date':date_after_month}, callback=self.parse_observations_per_date)
            else:
                # reports are cronologically ordered, we can safely stop iterating and we won't miss any DataFrame
                break

        # FIXME : the problem with processing in parallel is that if there is an error, there could be gaps in the dates

    def parse_observations_per_date(self, response):
        df = pd.DataFrame(columns=['obs_id','obs_posted','obs_city','obs_state','obs_country','obs_shape','obs_duration','obs_images','obs_ocurred','obs_reported','obs_summary','obs_detailed_description'])
        df_row = {}

        rows = response.xpath('//tbody//tr')
        for row in rows:        # iterate over the observations for the given date (parameter 'observations_date')
            # Once I have each row splited in an array, I can re-split again based on columns
            columns = row.xpath('./td')
            df_row['obs_id'] = columns[COLUMN.ID.value].xpath('./a/text()').extract_first()
            df_row['obs_posted'] = datetime.strptime(columns[COLUMN.POSTED.value].xpath('./text()').extract_first(), '%m/%d/%y')
            df_row['obs_city'] = columns[COLUMN.CITY.value].xpath('./text()').extract_first()
            df_row['obs_state'] = columns[COLUMN.SATE.value].xpath('./text()').extract_first()
            df_row['obs_country'] = columns[COLUMN.COUNTRY.value].xpath('./text()').extract_first()
            df_row['obs_shape'] = columns[COLUMN.SHAPE.value].xpath('./text()').extract_first()
            df_row['obs_duration'] = columns[COLUMN.DURATION.value].xpath('./text()').extract_first()
            df_row['obs_images'] = (columns[COLUMN.IMAGES.value].xpath('./text()').extract_first() == 'Yes')
            df_row['obs_summary'] = columns[COLUMN.SUMMARY.value].xpath('./text()').extract_first()
            
            follow_url = response.urljoin(columns[COLUMN.ID.value].xpath('./a/@href').extract_first())
            logging.debug(f'Following url [{follow_url}] to grab observation details')
            #response = requests.get(follow_url, timeout=self.timeout)
            #self.__parse_observation_detail(scrapy.Selector(response=response), df_row)
            yield response.follow(url=follow_url, meta={'df_row':df_row}, callback=self.__parse_observation_detail)

            logging.debug(f'Adding new entry to csv [id={df_row["obs_id"]}]')
            df_to_concat = pd.DataFrame(df_row, index=[df_row['obs_id']])
            df = pd.concat([df, df_to_concat])

        # Dump all observations to a csv file in a temp location
        filename = response.meta['observations_date'].strftime('%m_%d_%Y') + '.csv'
        csv_location_path = os.path.join(tempfile.gettempdir(), filename)
        logging.info(f'Dumping csv file to location [{csv_location_path}]')
        df.to_csv(csv_location_path)

        # Upload csv to final storage (which will trigger the DB import event)
        if self.__upload_file(csv_location_path):
            pass    # write result to dynamo

        # Remove temp file
        os.remove(csv_location_path)


    def __parse_observation_detail(self, response):      
        # From the first row, grab the ocurred and reported times
        ocurred_str = response.xpath('//tbody/tr/td')[0].xpath('./font/text()')[0].extract()
        chopped_ocurred_str = ocurred_str[:ocurred_str.find('  (')]
        response.meta['df_row']['obs_ocurred'] = datetime.strptime(chopped_ocurred_str, 'Occurred : %m/%d/%Y %H:%M')
        reported_str = response.xpath('//tbody/tr/td')[0].xpath('./font/text()')[1].extract()
        chopped_reported_str = reported_str[:-6]
        response.meta['df_row']['obs_reported'] = datetime.strptime(chopped_reported_str, 'Reported: %m/%d/%Y %I:%M:%S %p')

        # For the second row, grab the detailed description
        response.meta['df_row']['obs_detailed_description'] = response.xpath('//tbody/tr/td')[1].xpath('./font/text()')[-1].extract()

    
    def __upload_file(self, file_location):
        result = True
        filename = os.path.basename(file_location)
        
        try:
            session = boto3.Session(profile_name='coding_challenge')
            s3_client = session.client('s3')

            logging.info(f'Uploading file [{file_location}] to bucket [{self.bucket_name}] with object name [{filename}]')
            response = s3_client.upload_file(file_location, self.bucket_name, filename)      # files will be of small size, no need to to keep track of upload progress
        except botocore.exceptions.ClientError as e:
            logging.error(f'Trying to create a boto client. Description [{e}]')
            result = False
        except boto3.exceptions.S3UploadFailedError as e:
            logging.error(f'Trying to upload file [{file_location} to bucket [{self.bucket_name}]. Description [{e}]')
            result = False
        
        return result
