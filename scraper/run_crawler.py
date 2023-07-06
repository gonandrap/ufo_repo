from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scraper_project.spiders.observations import ObservationsSpider
from datetime import datetime
import os 
import logging

date_pattern = '%m/%d/%Y'

date_from = datetime.strftime(datetime.now(), date_pattern)
if 'DATE_FROM' in os.environ:
    try:
        date_from = os.environ['DATE_FROM']
    except ValueError as e:
        logging.warning(f"`Env variable DATE_FROM=[{os.environ['DATE_FROM']}] doesn't match [{date_pattern}]. Using today's date instead")

process = CrawlerProcess(get_project_settings())
process.crawl(ObservationsSpider, url='https://nuforc.org/webreports/ndxevent.html', date_from=date_from, bucket_name='codingchallengeimportfiles', table_name='scrap_run')
process.start()