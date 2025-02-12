BOT_NAME = 'sylph'
SPIDER_MODULES = ['crawler.spider']
NEWSPIDER_MODULE = 'crawler'

USER_AGENT = 'Sylph Search Engine Bot (+ http://yourdomain.com)'
CONCURRENT_REQUESTS = 32
DOWNLOAD_DELAY = 1

COOKIES_ENABLED = False
ITEM_PIPELINES = {}

HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 0
HTTPCACHE_DIR = 'httpcache'
HTTPCACHE_IGNORE_HTTP_CODES = []
HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
