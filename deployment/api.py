from fastapi import FastAPI
import uvicorn
from deployment.backend import Majority, Generate
import logging
from configs import APIConfig
from pydantic import BaseModel

logging.basicConfig(
    filename= APIConfig.log_filename,
    level=logging.INFO,
    format = APIConfig.log_format,
    filemode = APIConfig.log_filemode
    )
logger = logging.getLogger(__name__)

generator = Generate()

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

@app.post("/get_article")
def get_article(article: Article) -> dict:
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

uvicorn.run(app, 
            host = APIConfig.host,
            port = APIConfig.port
            )