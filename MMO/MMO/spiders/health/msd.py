#!/usr/bin/env python
# -*- coding: utf-8 -*-

import scrapy
import os
import json
from codecs import open
from datetime import datetime
import re
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin
import requests
from MMO.items import ArticleItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
import hashlib
import time

hash_sha = hashlib.sha256()
URL = 'https://www.msdmanuals.com/vi-vn/chuy%C3%AAn-gia'
DOMAIN = "msdmanuals.com"

class MSD(CrawlSpider):
    '''Crawl tin tức từ https://www.msdmanuals.com/vi-vn/chuy%C3%AAn-gia website
        limit: Giới hạn số trang để crawl, có thể bỏ trống.
    '''
    name = "msd"
    folder_path = "msd"
    page_limit = None
    start_urls = [
        URL
    ]
    # allowed_domains = [URL]
    rules = (
        Rule(LinkExtractor(restrict_xpaths='//a',allow_domains=DOMAIN), callback='parse', follow=True),
    )
    custom_settings = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
    }
    def __init__(self, limit=-1, *args, **kwargs):
        super(MSD, self).__init__(*args, **kwargs)
        self.page_limit = int(limit)
        # Tạo thư mục
        if not os.path.exists(self.folder_path):
            os.mkdir(self.folder_path)
        self.SITE_COUNTER = 0
        self.visited_urls = set()
        self.today = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    
    def parse(self, response):
        if (self.page_limit >= 0) and (self.SITE_COUNTER >= self.page_limit):
            return
        url = response.url
        if url.startswith("/"):
            url = URL + url
        if "http" in url and url not in self.visited_urls:
            jsonData = self.extract_news(response)
            self.visited_urls.add(url)
            if jsonData['content'] is not None :
                item = ArticleItem()
                item['hash_url'] = hash_sha.update(jsonData['url'].encode())
                item['domain'] = DOMAIN
                item['title'] = jsonData['title']
                item['url'] = jsonData['url']
                item['content'] = jsonData['content']
                item['tags'] = jsonData['tags']
                item['description'] = jsonData['description']
                item['insertDate'] = self.today
                # hash_sha.update(jsonData['url'].encode())
                # with open(self.folder_path + "/" + str(hash_sha.hexdigest()) +".json", 'wb', encoding = 'utf-8') as fp:
                #     json.dump(jsonData, fp, ensure_ascii= False)
                yield item
        else:
            print(url)
            
    def extract_news(self, response):
        title = self.extract_title(response)
        content = self.extract_content(response)
        tags = self.extract_tags(response)
        description = self.extract_description(response)
        jsonData = {
            'title': title,
            'url': response.url,
            'content': content,
            'tags': tags,
            'description': description
        }
        return jsonData

    def extract_title(self, response):
        title = response.css("h1.topic__header__headermodify--title::text").extract_first()
        if title is not None:
            return title
        return None

    def extract_description(self, response):
        description = response.css("div.topic__explanation::text").extract_first()
        if description is not None:
            return description
        return None

    def extract_content(self, response):
        content = response.css("div.topic__accordion").getall()
        if content is not None and len(content) > 0:
            return content[0]
        return None

    def extract_tags(self, response):
        return None