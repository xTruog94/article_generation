from cliES import ElasticClient
from cliDB import SQLClient
from config import ElasticConfig, DBConfig
from utils import Cleaner
from datetime import datetime
import json
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('-c','--create_new_index',action='store_true')
args = parser.parse_args()

es_client = ElasticClient(
    ElasticConfig.host,
    ElasticConfig.port,
    ElasticConfig.index
)
db_client = SQLClient(
    DBConfig.host,
    DBConfig.user,
    DBConfig.password,
    DBConfig.database,
    DBConfig.table
)

cleaner = Cleaner()

if __name__ ==  "__main__":
    if args.create_new_index:
        with open("cliES/index.json","r") as f:
            index = json.load(f)
        es_client.create_index(index)
    
    data = db_client.get_all(limit = -1)
    list_es_data = []
    for row in data:
        es_data = {}
        _id, hash_url, domain, url, title, content, tags, description, insertDate = row
        title = cleaner.clean_space(title)
        description = cleaner.clean(description)
        content = cleaner.clean(content)
        es_data['_id'] = _id
        es_data['_index'] = ElasticConfig.index
        es_data['domain'] = domain
        es_data['url'] = url
        es_data['title'] = title
        es_data['content'] = content
        es_data['tags'] = tags
        es_data['insertDate'] = insertDate.strftime("%Y-%m-%d %H:%M:%s")[:19]
        list_es_data.append(es_data)
        if len(list_es_data) > 0 and len(list_es_data) % 200 == 0:
            es_client.push_data(list_es_data)
            list_es_data = []
    if len(list_es_data) > 0:
            es_client.push_data(list_es_data)
            list_es_data = []