
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
import csv
import threading
import random
import string
from scrapy import signals
import os


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
        :param table_name: name of the dynamo table to write results of the run
    """
    name = 'observations'
    timeout = 3

    csvfilename = None
    csvfile = None
    item_writer = None

    csv_writer_lock = None
    persisted_items = None
    expected_items = None

    aws_session = None

    def __init__(self, url, date_from, bucket_name, table_name, *args, **kwargs):
        super(ObservationsSpider, self).__init__(*args, **kwargs) 
        self.run_id = ''.join(random.choices(string.ascii_lowercase, k=20))
        self.url = url 
        self.date_from = datetime.strptime(date_from, '%m/%d/%Y') 
        self.bucket_name = bucket_name
        self.table_name = table_name

        self.__init_logger()
        self.__init_csv_writer()

        self.aws_session = boto3.Session(profile_name='coding_challenge_api_access')

    def __init_signals(self):
        self.errors = []
        crawler.signals.connect(self.__item_error, signal=signals.item_error)
        crawler.signals.connect(self.__spider_error, signal=signals.spider_error)

    def __item_error(self, item, response, spider, failure):
        self.errors.append(failure)

    def __spider_error(self, failure, response, spider):
        self.errors.append(failure)

    def __init_logger(self):
        self.spider_logger = logging.getLogger(f'scraper_app] [RUN_ID={self.run_id}')

    def __init_csv_writer(self):
        self.csv_writer_lock = threading.Lock()
        columns=['obs_id','obs_posted','obs_city','obs_state','obs_country','obs_shape','obs_duration','obs_images','obs_ocurred','obs_reported','obs_summary','obs_detailed_description']
        
        self.csvfilename = os.path.join(tempfile.gettempdir(), datetime.strftime(datetime.now(), "%m_%d_%y__%H_%M_%S") + '.csv')

        self.persisted_items = 0
        self.expected_items = 0
        
        with self.csv_writer_lock:
            self.csvfile = open(self.csvfilename, 'a+', newline='')
            self.item_writer = csv.DictWriter(self.csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL, fieldnames=columns)
            self.item_writer.writeheader()
            self.csvfile.flush()

            self.spider_logger.info(f'CSV temporary file created [{self.csvfilename}]')

    def __cleanup_csv_writer(self):
        """
            Not thread safe, must be called from inside a critical section
        """
        self.csvfilename = None
        self.csvfile = None
        self.item_writer = None
        

    def start_requests(self):
        self.spider_logger.info(f'Scrapping [{self.url}]')
        yield scrapy.Request(url=self.url, callback=self.download_data)

    def closed(self, reason):
        self.spider_logger.info(f'Spider [{self.name}] is closing due to reason [{reason}]. [{self.persisted_items}] Items scraped and persisted')
        filename = os.path.basename(self.csvfilename)
        upload_result = self.__upload_file(filename)
        self.__log_run_result(filename, self.__run_result(upload_result, reason))

    def __run_result(self, upload_result, finished_reason):
        return (self.persisted_items == self.expected_items) and (upload_result == True) and (finished_reason == 'finished')

    def download_data(self, response):
        rows = response.xpath('//tbody//tr')
        
        for row in rows:
            columns = row.xpath('./td')
            date = datetime.strptime(columns[0].xpath('./a/text()').extract_first(), '%m/%Y')
            date_after_month = date + relativedelta(months=1) # this is because the page counts by end of month, but python assumes first day of month
            if date_after_month >= self.date_from:
                try:
                    number_items = int(columns[1].xpath('./text()').extract_first())
                except ValueError as e:
                    self.spider_logger.error(f'Trying to read number of expected items for date [{date_after_month}]. Description [{e}]')
                    number_items = 0

                self.spider_logger.info(f'Found [{number_items}] observations for date [{date}]')
                self.expected_items += number_items
                follow_url = response.urljoin(columns[0].xpath('./a/@href').extract_first())
                self.spider_logger.debug(f'Following url [{follow_url}]')
                yield response.follow(url=follow_url, meta={'observations_date':date_after_month}, callback=self.parse_observations_per_date)
            else:
                # reports are cronologically ordered, we can safely stop iterating and we won't miss any DataFrame
                break

        # FIXME : the problem with processing in parallel is that if there is an error, there could be gaps in the dates

    def parse_observations_per_date(self, response):
        rows = response.xpath('//tbody//tr')
        for row in rows:        # iterate over the observations for the given date (parameter 'observations_date')
            df_row = {}

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
            self.spider_logger.debug(f'Following url [{follow_url}] to grab observation details')
            yield response.follow(url=follow_url, meta={'df_row':df_row}, callback=self.__parse_observation_detail)


    def __parse_observation_detail(self, response):      
        row = response.meta['df_row']
        
        # From the first row, grab the ocurred and reported times
        ocurred_str = response.xpath('//tbody/tr/td')[0].xpath('./font/text()')[0].extract()
        chopped_ocurred_str = ocurred_str[:ocurred_str.find('  (')]
        row['obs_ocurred'] = datetime.strptime(chopped_ocurred_str, 'Occurred : %m/%d/%Y %H:%M')
        reported_str = response.xpath('//tbody/tr/td')[0].xpath('./font/text()')[1].extract()
        chopped_reported_str = reported_str[:-6]
        row['obs_reported'] = datetime.strptime(chopped_reported_str, 'Reported: %m/%d/%Y %I:%M:%S %p')

        # For the second row, grab the detailed description
        row['obs_detailed_description'] = response.xpath('//tbody/tr/td')[1].xpath('./font/text()')[-1].extract()

        self.__persist_item(row)

    
    def __persist_item(self, row):
        # Have all I need to persist the item in disk
        with self.csv_writer_lock:
            self.spider_logger.debug(f'Adding new entry [id={row["obs_id"]}] to csv [{self.csvfilename}]')
            self.item_writer.writerow(row)
            self.csvfile.flush()

            self.persisted_items += 1


    def __upload_file(self, filename):        
        try:
            s3_client = self.aws_session.client('s3')

            self.spider_logger.info(f'Uploading file [{self.csvfilename}] to bucket [{self.bucket_name}] with object name [{filename}]')
            with self.csv_writer_lock:
                response = s3_client.upload_file(self.csvfilename, self.bucket_name, filename)      # files will be of small size, no need to to keep track of upload progress

                # Finally, remove generated csv file
                self.csvfile.close()
                os.remove(self.csvfilename)
                self.__cleanup_csv_writer()

            return True
        except botocore.exceptions.ClientError as e:
            self.spider_logger.error(f'Trying to create a boto client for S3. Description [{e}]')
        except boto3.exceptions.S3UploadFailedError as e:
            self.spider_logger.error(f'Trying to upload file [{self.csvfilename} to bucket [{self.bucket_name}]. Description [{e}].')
        except Exception as e:
            self.spider_logger.error(f'Trying to upload and clean up files. Description [{e}]')

        return False

    def __log_run_result(self, filename, result):
        """
            Not thread safe.
        """ 
        try:
            dynamodb = self.aws_session.resource('dynamodb')
            table = dynamodb.Table(self.table_name)

            object_url = f'https://s3.console.aws.amazon.com/s3/object/{self.bucket_name}?region={self.aws_session.region_name}&prefix={filename}'
            response = table.put_item(
                Item={
                    'run_id': self.run_id,
                    'input_url': self.url,
                    'input_date_from': datetime.strftime(self.date_from, '%m/%d/%Y'),
                    'input_bucket_name': self.bucket_name,
                    'result': 'SUCCESS' if result else 'FAIL',
                    'number_records_persisted': self.persisted_items,
                    'number_records_expected': self.expected_items,
                    'file_location': object_url
                }
            )


            return True
        except botocore.exceptions.ClientError as e:
            self.spider_logger.error(f'Trying to create a boto client for DynamoDB. Description [{e}]')

        return False