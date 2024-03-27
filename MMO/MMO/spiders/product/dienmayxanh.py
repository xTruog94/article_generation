#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from datetime import datetime
import json
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin
import requests
from MMO.items import ArticleItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
import hashlib
import requests


hash_sha = hashlib.sha256()
URL = 'https://www.dienmayxanh.com/'
DOMAIN = "dienmayxanh.com"

class Dienmayxanh(CrawlSpider):
    '''Crawl tin tức từ https://dienmayxanh.com/ website
        limit: Giới hạn số trang để crawl, có thể bỏ trống.
    '''
    name = "dienmayxanh"
    folder_path = "dienmayxanh"
    page_limit = None
    start_urls = [
        URL
    ]
    # allowed_domains = [URL]
    rules = (
        Rule(LinkExtractor(restrict_xpaths='//a',allow_domains=DOMAIN), callback='parse', follow=True),
    )
    def __init__(self, limit=-1, *args, **kwargs):
        super(Dienmayxanh, self).__init__(*args, **kwargs)
        self.page_limit = int(limit)
        # Tạo thư mục
        if not os.path.exists(self.folder_path):
            os.mkdir(self.folder_path)
        self.SITE_COUNTER = 0
        self.visited_urls = set()
        self.today = datetime.today()
    
    def parse(self, response):
        if (self.page_limit >= 0) and (self.SITE_COUNTER >= self.page_limit):
            return
        url = response.url
        if url.startswith("/"):
            url = URL + url
        if "http" in url and url not in self.visited_urls:
            jsonData = self.extract_news(response)
            self.visited_urls.add(url)
            if jsonData['content'] is not None and jsonData['content'] != "" :
                item = ArticleItem()
                item['hash_url'] = hash_sha.update(jsonData['url'].encode())
                item['domain'] = DOMAIN
                item['url'] = jsonData['url']
                item['title'] = jsonData['title']
                item['content'] = jsonData['content']
                item['tags'] = jsonData['tags']
                item['description'] = jsonData['description']
                item['images'] = jsonData['images']
                item['article_type'] = jsonData['article_type']
                item['insertDate'] = self.today
                # hash_sha.update(jsonData['url'].encode())
                # with open(self.folder_path + "/" + str(hash_sha.hexdigest()) +".json", 'w', encoding = 'utf-8') as fp:
                #     json.dump(jsonData, fp, ensure_ascii= False)
                yield item
        else:
            print(url)
            
    def extract_news(self, response):
        url = response.url
        if "kinh-nghiem-hay" in url:
            tmp = self.extract_content_review(response)
            if tmp:
                content, images = tmp[0], tmp[1]
            else:
                content, images = "", ""
            jsonData = {
                'url': url,
                'content': content,
                'title': self.extract_title(response),
                'tags': self.extract_tags(response),
                'description': self.extract_description(response),
                'images': images,
                'article_type': 'product_review'
            }
        else:
            tmp = self.extract_content_infor(response)
            if tmp:
                content, images = tmp[0], tmp[1]
            else:
                content, images = "", ""
            jsonData = {
                'url': url,
                'content': content,
                'title': '',
                'tags': '',
                'description': '',
                'images': images,
                'article_type': 'product_information'
            }
        return jsonData

    def extract_content_infor(self, response):
        content = response.css("div.content-article")
        if content is not None and len(content) > 0:
            data = content[0].getall()
            data = "".join(data)
            data = data.split("\n")[:3]
            data = "".join(data)
            images = self.extract_images(data)
            return data, images
        return None
    
    def extract_content_review(self, response):
        content = response.css("div.contentnews")
        if content is not None and len(content) > 0:
            data = content[0].getall()
            data = "".join(data)
            images = self.extract_images(data)
            return data, images
        return None
    
    def extract_title(self, response):
        return response.css("h1::text").extract_first()
    
    def extract_tags(self, response):
        content = response.css("div.tags>a::text").getall()
        return ",".join(content)

    def extract_description(self, response):
        return ""
    
    def extract_images(self, html):
        soup = bs(html, 'lxml')
        images = soup.findAll('img')
        urls = []
        for image in images:
            url = image.get('src', None)
            if url and len(url) > 10:
                urls.append(url)
        return ",".join(urls)