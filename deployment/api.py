from fastapi import FastAPI
import uvicorn
from deployment.backend import Generate, get_images, insert_image
import logging
from configs.common_configs import APIConfig
from pydantic import BaseModel
import json
from memoization import cached


logging.basicConfig(
    filename= APIConfig.log_filename,
    level=logging.INFO,
    format = APIConfig.log_format,
    filemode = APIConfig.log_filemode
    )
logger = logging.getLogger(__name__)

generator = Generate(policy = "gemini")

app = FastAPI()
class Article(BaseModel):
    content:str
    category: str = None

class Product(BaseModel):
    name:str
    code: str = ""
    keywords: str = ""
    description: str = ""
    domain: str = "dienmayxanh.com"
    type_article: str = "product_information"
  
base_response = {
    "status_code": 200,
    "data": None,
    "message": ""
}
@app.get("/")
def healthcheck():
    return {"status":"ok"}

@app.post("/generate_article", tags=["Article"])
def get_article(product: Product) -> dict:
    response = base_response.copy()
    try:
        new_article, urls, status_code, ref_article_url, images = generator.generate(
            name = product.name,
            code = product.code,
            keywords = product.keywords,
            description = product.description,
            domain = product.domain,
            type_article = product.type_article
        )
        if status_code == 200:
            data = {
                "article": new_article,
                "source":{
                    "domain": product.domain,
                    "url": ref_article_url
                },
                "images": images
                }
            response['data'] = data
        else:
            response['status_code'] = status_code
            response['message'] = new_article
    except Exception as e:
        status_code = 500
        response['status_code'] = 500
        response['message'] = str(e)
    logger.info(f"Generate image with status {status_code} with {product.name} - {product.code} - {product.keywords} - {product.domain}")
    return response

uvicorn.run(app, 
            host = APIConfig.host,
            port = APIConfig.port
            )