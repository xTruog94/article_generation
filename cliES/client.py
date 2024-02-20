from elasticsearch import helpers, Elasticsearch
import time

class ElasticClient:
    def __init__(self, host, port, index_name):
        self.host = host
        self.port = port
        self.index_name = index_name
        self.es = Elasticsearch(host + ":" + str(port))
    
    def complete_script(self,addition):
        script_query ={ "size": 20,
                            "track_total_hits" : True,
                            "query": addition
                        }
        return script_query
    
    def base_query(self, script_query, is_addional_script = True):
        if is_addional_script:
            script_query = self.complete_script(script_query)
        response = self.es.search(
            index = self.index_name,
            body = script_query,
            request_timeout = 300
        )
        res =[]
        for hit in response["hits"]["hits"]:
            res.append({
                "title": hit["_source"]["title"],
                "content": hit["_source"]["content"],
                "url": hit["_source"]["url"]
            })
        return res

    def get_article(self, term):
        script = {
                    "match":{
                        "content":term
                    }
                }
        res = self.base_query(script)
        return res
    
    
    def delete_by_query(self):
        script_query ={ "size": 20000,
                        "track_total_hits" : True,
                        "query": {
                            "bool":{
                                "must_not":[{
                                    "exists":{
                                        "field": "company_id"
                                        }
                            }],
                            }
                            },                            
                        }
        self.es.delete_by_query(
            index = self.index_name,
            body = script_query,
        )
        return 1
    
    def get_all(self):
        script_query ={ "size": 20,
                        "query": {
                                "match_all":{
                                }
                            },                            
                        }
        response = self.es.search(
            index = self.index_name,
            body = script_query,
            request_timeout = 3000
        )
        return response
    
    def get_article_by_domain(self, domain, seed):
        script ={
                    "function_score": {
                        "query" : { 
                            "match_phrase": {
                                "domain": domain
                                } 
                            },
                        "random_score": {
                            "seed": seed
                        }
                    }
                }
        res = self.base_query(script)
        return res

    def push_data(self, data,):
        self.es.indices.put_settings(index=self.index_name,
                                body= {"index" : {
                                    "max_result_window" : 10000000
                                }})
        if isinstance(data, list):
            helpers.bulk(self.es, data)
        else:
            helpers.bulk(self.es,[data])

    def remove_doc(self, product_id):
        script_query ={ "size": 20,
                        "query": {
                            "match_phrase":{
                                "id_product": str(product_id)
                                }
                            },
                        }
        self.es.delete_by_query(
            index = self.index_name,
            body = script_query,
        )
        return 1
    
    def create_index(self, index):
        self.es.indices.delete(index = self.index_name, ignore=[404])
        self.es.indices.create(index = self.index_name, body=index)
        self.es.indices.put_settings(index = self.index_name,
                            body= {"index" : {
                                    "max_result_window" : 10000000
                                }})
        return