from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from crawler.spider import SylphSpider
def run_spider():
    settings = get_project_settings

    process = CrawlerProcess(settings)
    start_urls = [
        'https://example.com'
    ]
    process.crawl(SylphSpider, start_urls=','.join(start_urls))
    process.start()

if __name__ == '__main__':
    run_spider()