BOT_NAME = 'sylph'
SPIDER_MODULES = ['crawler.spider']
NEWSPIDER_MODULE = 'crawler'

USER_AGENT = 'Sylph Search Engine Bot (+ http://yourdomain.com)'
CONCURRENT_REQUESTS = 32
DOWNLOAD_DELAY = 1

CONCURRENT_REQUESTS = 32
CONCURRENT_REQUESTS_PER_DOMAIN = 16
DOWNLOAD_DELAY = 1
RANDOMIZE_DOWNLOAD_DELAY = True

COOKIES_ENABLED = False
ITEM_PIPELINES = {}

DEPTH_LIMIT = 2  # Adjust this value to control how deep the crawler goes
DEPTH_PRIORITY = 1
SCHEDULER_DISK_QUEUE = 'scrapy.squeues.PickleLifoDiskQueue'
SCHEDULER_MEMORY_QUEUE = 'scrapy.squeues.LifoMemoryQueue'


HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 0
HTTPCACHE_DIR = 'httpcache'
HTTPCACHE_IGNORE_HTTP_CODES = []
HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429]   