from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapper_project.spiders.observations import ObservationsSpider
from datetime import datetime 

date_from = datetime.strftime(datetime.now(), "%m/%d/%Y")
process = CrawlerProcess(get_project_settings())
process.crawl(ObservationsSpider, url='https://nuforc.org/webreports/ndxevent.html', date_from=date_from, bucket_name='codingchallengeimportfiles', table_name='scrap_run')
process.start()