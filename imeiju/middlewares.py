import asyncio
import hashlib
import logging
import os
import time

import pyppeteer
from fake_useragent import UserAgent
from scrapy import signals
from scrapy.http import HtmlResponse

logger = logging.getLogger(__name__)
pyppeteer.DEBUG = False


class TvDownloaderMiddleware(object):

    def __init__(self):
        print("Init downloaderMiddleware use pypputeer.")
        os.environ['PYPPETEER_CHROMIUM_REVISION'] = '588429'
        print(os.environ.get('PYPPETEER_CHROMIUM_REVISION'))
        loop = asyncio.get_event_loop()
        task = asyncio.ensure_future(self.getbrowser())
        loop.run_until_complete(task)

        # self.browser = task.result()
        print(self.browser)
        print(self.page)
        # self.page = await browser.newPage()

    async def getbrowser(self):
        self.browser = await pyppeteer.launch(headless=False, dumpio=True)
        self.page = await self.browser.newPage()
        await self.page.setViewport(viewport={'width': 1366, 'height': 768})
        await self.page.setUserAgent(
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3494.0 Safari/537.36')
        await self.page.setJavaScriptEnabled(enabled=True)
        await self.page.evaluate(
            '''() =>{ Object.defineProperties(navigator,{ webdriver:{ get: () => false } }) }''')
        await self.page.evaluate('''() =>{ window.navigator.chrome = { runtime: {},  }; }''')
        await self.page.evaluate(
            '''() =>{ Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] }); }''')
        await self.page.evaluate(
            '''() =>{ Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5,6], }); }''')

        return self.page

    async def getnewpage(self):
        return await self.browser.newPage()

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        loop = asyncio.get_event_loop()
        task = asyncio.ensure_future(self.usePypuppeteer(request))
        loop.run_until_complete(task)
        # return task.result()
        return HtmlResponse(url=request.url, body=task.result(), encoding="utf-8", request=request)

    async def usePypuppeteer(self, request):
        print(request.url)
        # page = await self.browser.newPage()

        await self.page.goto(request.url, {"waitUntil": "networkidle2"})
        await self.page.waitFor('.container')
        content = await self.page.content()
        return content

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        logger.info('Spider opened: %s' % spider.name)


class ProxyDownloaderMiddleware(object):
    """使用讯代理的动态转发，随机获取代理"""

    def __init__(self, secret, orderno):
        self.secret = secret
        self.orderno = orderno

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            secret=crawler.settings.get('SECRET'),
            orderno=crawler.settings.get('ORDERNO')
        )

    def process_request(self, request, spider):
        timestamp = str(int(time.time()))
        string = "orderno=" + self.orderno + "," + "secret=" + self.secret + "," + "timestamp=" + timestamp
        string = string.encode()
        md5_string = hashlib.md5(string).hexdigest()
        sign = md5_string.upper()
        auth = "sign=" + sign + "&" + "orderno=" + self.orderno + "&" + "timestamp=" + timestamp

        request.meta['proxy'] = 'http://forward.xdaili.cn:80'
        request.headers["Proxy-Authorization"] = auth
        logger.debug('正在使用动态转发')


class RandomUserAgentDownloaderMiddleware(object):
    """使用fake_useragent库，随机获取UserAgent"""

    def process_request(self, spider, request):
        agent = UserAgent()
        user_agent = agent.chrome
        request.headers['User-Agent'] = user_agent
        logger.debug('User-Agent:{}'.format(user_agent))
