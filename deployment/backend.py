from cliES import ElasticClient
import requests
from bs4 import BeautifulSoup as bs
from generation import PromptGenerate
from configs import common_configs, server_configs
import json
import random

cc = common_configs
sc = server_configs

class Majority:
    def __init__(self,
                 domain: str = 'https://hellobacsi.com',
                 category_path: str = "https://hellobacsi.com/categories/",
                 ):
        self.domain = domain
        self.all_categories = self.get_all_categories(category_path)
        
    def get_all_categories(self, cate_path):
        html = requests.get(cate_path)
        soup = bs(html.text, 'lxml')
        cates = soup.findAll('p',attrs={"class":"category_name"})
        cate_names = [x.text for x in cates]
        urls = [self.domain + x.parent.parent['href'] for x in cates]
        return {x:y for x,y in zip(cate_names, urls)}


    def get_article_by_cate(self, cate_name):
        cate_url = self.all_categories[cate_name]
        html = requests.get(cate_url)
        soup = bs(html.text, 'lxml')
        articles = soup.findAll('article')
        titles = []
        urls = []
        for article in articles:
            title = article.find('h3', attrs = {"class":"title"})
            url = article.find('a')
            # sapo = article.find('p', attrs = {"class":"text"})
            if title:
                titles.append(title.text)
                urls.append(self.domain + url['href'])
        return titles,urls
    
class Generate():
    
    def __init__(self, master_domain = "hellobacsi.com"):
        self.es_cli = ElasticClient(
            host = sc.ElasticConfig.host, 
            port = sc.ElasticConfig.port, 
            index_name= sc.ElasticConfig.index
        )
        self.generator = PromptGenerate(
            api = cc.ChatGPTConfig.api,
            cookie = cc.ChatGPTConfig.cookie,
            assistant_id = cc.ChatGPTConfig.assistant_id
            
        )
        self.cate_slug_to_name = None
        self.master_domain = master_domain
        category_mapping = json.load(open("deployment/mapping_category.json"))
        for item in category_mapping:
            if item['domain'] == master_domain:
                self.cate_slug_to_name = item["categories"]
                break
            
    def get_article_from_url(self, url):
        full_article = []
        html = requests.get(url)
        soup = bs(html.text, "lxml")
        content = soup.find_all("div", {"class":"unique-content-wrapper"})
        for div in content:
            text = div.text
            full_article.append(text)
        return " ".join(full_article)
    
    def get_category(self, url):
        slug = url.split("/")[3]
        return self.cate_slug_to_name[slug]
    
    def get_random_article_from_es(self):
        content = ''
        while content == '':
            seed = random.randint(0,1e6)
            article = self.es_cli.get_article_by_domain(self.master_domain, seed)[0]
            content = article['content']
        if content != '':
            article['category'] = self.get_category(article['url'])
        return article
    
    def find_related(self, text, max_length  = 512):
        text = text[:max_length]
        related_article = self.es_cli.get_article(text)
        articles = [x['content'] for x in related_article]
        urls = [x['url'] for x in related_article]
        return articles, urls
    
    def generate_from_url(self, url: str):
        article = self.get_article(url)
        related_items, urls = self.find_related(article)
        new_article = self.generator.get_response(article,  related_items[0], related_items[1])
        return new_article, urls[:2]
    
    def generate_from_text(self, article: str):
        related_items, urls = self.find_related(article)
        new_article = self.generator.get_response(article,  related_items[0], related_items[1])
        return new_article, urls[:2]