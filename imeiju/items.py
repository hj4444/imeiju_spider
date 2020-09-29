from scrapy import Item, Field


class TVItem(Item):
    id = Field()
    name = Field()
    season = Field()
    desc = Field()
    episode_num = Field()
    episode = Field()


class TvEpisode(Item):
    tv_id = Field()
    num = Field()
    video_url = Field()
