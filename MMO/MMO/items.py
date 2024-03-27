# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Item, Field

class ArticleItem(Item):
    hash_url = Field()
    domain = Field()
    url = Field()
    title = Field()
    content = Field()
    tags = Field()
    description = Field()
    images = Field()
    article_type = Field()
    insertDate = Field()