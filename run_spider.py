from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from crawler.spider import SylphSpider
def run_spider(start_urls):
    settings = get_project_settings()

    process = CrawlerProcess(settings)
    process.crawl(SylphSpider, start_urls=start_urls)
    process.start()

if __name__ == '__main__':
    run_spider('https://example.com')