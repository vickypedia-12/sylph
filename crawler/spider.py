import scrapy
from urllib.parse import urlparse
from typing import Any, Generator

class SylphSpider(scrapy.Spider):
    name = "sylph_spider"
    custom_settings = {
        'ROBOTSTXT_OBEY': True,
        'CONCURRENT_REQUESTS': 32,
        'DOWNLOAD_DELAY': 1,
        'COOKIES_ENABLED': False,
    }

    def __init__(self,start_urls = None,allowed_domains = None, *args, **kwargs):
        super(SylphSpider, self).__init__(*args, **kwargs)
        self.start_urls = start_urls.split(',') if start_urls else ['https://google.com']
        if allowed_domains:
            self.allowed_domains = allowed_domains.split(',')
        else:
            self.allowed_domains = [urlparse(url).netloc for url in self.start_urls]

    def parse(self, response: scrapy.http.Response) -> Generator[dict[str, Any], None,None]:
        content = {
            'url': response.url,
            'title': response.css('title::text').get('').strip(),
            'text' : ' '.join([
                text.strip() for text in response.css('body::text').get()
                if text.strip()                    
                ]),
            'meta_description': response.css('meta[name="description"]::attr(content)').get(''),
            'meta_keywords': response.css('meta[name="keywords"]::attr(content)').get(''),
            'headers' :[
                h.strip() for h in response.css('h1::text, h2::text, h3::text').getall()
                if h.strip()
            ],
            'links' : [
                {
                    'url' : response.urljoin(href),
                    'text' : text.strip()
                }
                for href, text in zip(
                    response.css('a::attr(href)').getall(),
                    response.css('a::text').getall()
                )

                if href and text.strip()
            ]
        }

        yield content

        for link in response.css('a::attr(href)').getall():
            parsed_link = urlparse(response.urljoin(link))
            if parsed_link.netloc in self.allowed_domains:
                yield scrapy.Request(
                    response.urljoin(link),
                    callback=self.parse,
                    meta={'depth': response.meta.get('depth,0') + 1}
                )