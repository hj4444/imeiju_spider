import logging
import re

import scrapy

from imeiju.items import TVItem, TvEpisode

logger = logging.getLogger(__name__)


class TvSpider(scrapy.Spider):
    start_url = 'https://www.imeiju.io/vcat/ustv'
    name = "tv_spider"
    allowed_domains = ['www.imeiju.io']

    def start_requests(self):
        yield scrapy.Request(self.start_url, callback=self.parse)

    def parse(self, response):
        tv_list = response.selector.xpath(
            '//div[@class="m-movies clearfix"]/article[@class="u-movie"]/a/@href').extract()
        # yield scrapy.Request('https://www.imeiju.io/show/2693.html', callback=self.parse_detail, dont_filter=True)
        for item in tv_list:
            yield scrapy.Request(item, callback=self.parse_detail, dont_filter=True)

    def parse_detail(self, response):
        """
        process detail info of tv
        :param response:
        :return:
        """
        tv_detail = response.selector.xpath('//ul[@class="video_info"]/li')
        item = TVItem()
        tv_id = int(re.search(r'\d+', response.url).group(0))
        item['id'] = tv_id
        title = response.selector.xpath('//div[@class="info-main-title"]/span/a/text()').extract_first()
        item['name'] = str(title).split(" ", 1)[0]
        item['season'] = self.get_value_by_key(tv_detail, "季数:")
        item['episode_num'] = self.get_value_by_key(tv_detail, "集数:")
        item['desc'] = ""
        item['episode'] = []
        video_list = response.selector.xpath('//div[@class="playlist"]/a')
        for video in video_list:
            episode = TvEpisode()
            episode['tv_id'] = tv_id
            episode['num'] = video.xpath('./text()').extract_first()
            episode['video_url'] = video.attrib['href']
            item['episode'].append(episode)
        yield item

    def get_value_by_key(self, tv_detail, key):

        for item in tv_detail:
            name = item.xpath('.//span/text()').extract_first()
            value = item.xpath('./text()').extract_first()
            if key == name:
                return value
        return ""
