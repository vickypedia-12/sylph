import scrapy
from urllib.parse import urlparse
from typing import Any, Generator
import logging

logger = logging.getLogger(__name__)

class SylphSpider(scrapy.Spider):
    name = "sylph_spider"
    custom_settings = {
        'ROBOTSTXT_OBEY': False,
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
        try:
            content_type = response.headers.get('Content-Type', b'').decode('utf-8').lower()
            if not ('text/html' in content_type or 'application/xhtml+xml' in content_type):
                logger.warning(f"Skipping non-HTML content at {response.url} (Content-Type: {content_type})")
                return

            if response.status != 200:
                logger.warning(f"Skipping URL {response.url} due to status code {response.status}")
                return

            visible_text = ' '.join([
                text.strip() for text in response.css('body *::text').getall()
                if text.strip() and not text.strip().startswith(('<', '[', '{'))  
            ])

            if not visible_text:
                logger.warning(f"No visible text content found at {response.url}")
                return
            
            
            visible_text = ' '.join([
                text.strip() for text in response.css('body *::text').getall()
                if text.strip() and not text.strip().startswith(('<', '[', '{'))  
            ])
            content = {
                'url': response.url,
                'title': response.css('title::text').get('').strip(),
                'text' : visible_text,
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
            
            current_depth = response.meta.get('depth', 0)
            if current_depth < self.settings.getint('DEPTH_LIMIT', 2):
                for link in response.css('a::attr(href)').getall():
                    try:
                        parsed_link = urlparse(response.urljoin(link))
                        if parsed_link.netloc in self.allowed_domains:
                            yield scrapy.Request(
                                response.urljoin(link),
                                callback=self.parse,
                                meta={'depth': current_depth + 1},
                                errback=self.errback,
                                dont_filter=False
                            )
                    except Exception as e:
                        logger.error(f"Error following link {link} from {response.url}: {str(e)}")

        except Exception as e:
            logger.error(f"Error parsing {response.url}: {str(e)}")
            return
        
    def errback(self, failure):
        try:
            url = failure.request.url
            logger.error(f"Request failed for {url}: {str(failure.value)}")
        except Exception as e:
            logger.error(f"Error in errback: {str(e)}")