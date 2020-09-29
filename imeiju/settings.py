# -*- coding: utf-8 -*-

BOT_NAME = 'imeiju_spider'

SPIDER_MODULES = ['imeiju.spiders']
NEWSPIDER_MODULE = 'imeiju.spiders'

ROBOTSTXT_OBEY = False

DEFAULT_REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
}

MYSQL_USER = 'root'
MYSQL_PASSWORD = '123456'
MYSQL_DBNAME = 'meiju'
MYSQL_HOST = 'localhost'
MYSQL_PORT = 3306
MYSQL_CHARSET = 'utf8'

DOWNLOADER_MIDDLEWARES = {
    # 'gerapy_pyppeteer.downloadermiddlewares.PyppeteerMiddleware': 543,
    'imeiju.middlewares.TvDownloaderMiddleware': 543,
    # 'middlewares.RandomUserAgentDownloaderMiddleware': 600,
    # 'middlewares.ProxyDownloaderMiddleware': 610,
}
# 扩展设置
EXTENSIONS = {
    'imeiju.latencies.Latencies': 500,
}

ITEM_PIPELINES = {
   'imeiju.pipelines.MysqlAsyncPipeline': 300,
}

# 设置设置吞吐量和延迟的时间间隔
LATENCIES_INTERVAL = 5

# 如果为True，则进程的所有标准输出（和错误）将重定向到日志。
LOG_STDOUT = False
GERAPY_PYPPETEER_HEADLESS = False
GERAPY_PYPPETEER_PRETEND = False
GERAPY_PYPPETEER_DOWNLOAD_TIMEOUT = 10