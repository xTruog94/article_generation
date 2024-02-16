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
    description = Field()
    tags = Field()
    insertDate = Field()

class MainHealthItem(Item):
    hash_url = Field()
    domain = Field()
    url = Field()
    title = Field()
    content = Field()
    description = Field()
    tags = Field()
    insertDate = Field()
    category_id = Field()
    
class MainHealthCategoryItem(Item):
    hash_url = Field()
    domain = Field()
    url = Field()
    title = Field()
    content = Field()
    description = Field()
    tags = Field()
    insertDate = Field()
    category = Field()
    category_slug = Field()
