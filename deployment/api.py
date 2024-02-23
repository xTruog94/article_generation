from fastapi import FastAPI
import uvicorn
from deployment.backend import Generate, get_images
import logging
from configs.common_configs import APIConfig
from pydantic import BaseModel
import json

logging.basicConfig(
    filename= APIConfig.log_filename,
    level=logging.INFO,
    format = APIConfig.log_format,
    filemode = APIConfig.log_filemode
    )
logger = logging.getLogger(__name__)

generator = Generate(policy = "paid")

app = FastAPI()
class Article(BaseModel):
    content:str
    category: str = None
    
base_response = {
    "status_code": 200,
    "data": None,
    "message": ""
}
@app.get("/")
def healthcheck():
    return {"status":"ok"}

@app.post("/generate_article", tags=["Article"])
def gen_article(article: Article) -> dict:
    response = base_response.copy()
    try:
        new_article, urls = generator.generate_from_text(article.content)
        data = {
            "article": new_article,
            "references": urls
            }
        response['data'] = data
    except Exception as e:
        response['status_code'] = 500
        response['message'] = str(e)
    return response

@app.get("/get_article", tags=["Article"])
def get_article() -> dict:
    response = base_response.copy()
    try:
        article_from_es = generator.get_random_article_from_es()
        new_article, urls, status_code = generator.generate_from_text(article_from_es['content'])
        if status_code == 200:
            new_article['category'] = article_from_es['category']
            new_article['images'] = get_images(article_from_es['url'])
            data = {
                "article": new_article,
                "source":{
                    "domain": generator.master_domain,
                    "url": article_from_es['url'],
                    "title": article_from_es['title']
                },
                "references": urls
                }
            response['data'] = data
        else:
            response['status_code'] = status_code
            response['message'] = new_article
    except Exception as e:
        response['status_code'] = 500
        response['message'] = str(e)
    return response

@app.get("/get_category", tags=["Category"])
def get_category(domain: str = "hellobacsi.com") -> dict:
    category_mapping = json.load(open("deployment/mapping_category.json"))
    category = {}
    for item in category_mapping:
        if item['domain'] == domain:
            category = item["categories"]
            break
    all_cate = list(category.values())
    response = base_response.copy()
    try:
        response['data'] = all_cate
    except Exception as e:
        response['status_code'] = 500
        response['message'] = str(e)
    return response

uvicorn.run(app, 
            host = APIConfig.host,
            port = APIConfig.port
            )