# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import mysql.connector
from local_configs import DBConfig
class MmoPipeline:
    def process_item(self, item, spider):
        return item

class MysqlHealthPipeline:
    
    def __init__(self):
        self.conn = mysql.connector.connect(
            host = DBConfig.host,
            user = DBConfig.user,
            password = DBConfig.password,
            database = DBConfig.database,
            auth_plugin='mysql_native_password'
        )

        ## Create cursor, used to execute commands
        self.cur = self.conn.cursor()
        self.table_name = DBConfig.table
        # self.cur.execute(f"""
        # DROP TABLE IF EXISTS {self.table_name};
        # """)
        # self.conn.commit()
        ## Create quotes table if none exists
        self.cur.execute(f"""
        CREATE TABLE IF NOT EXISTS {self.table_name}(
            id int NOT NULL auto_increment,
            hash_url text,
            domain text,
            url text,
            title TEXT,
            content LONGTEXT,
            tags LONGTEXT,
            description LONGTEXT,
            insertDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (id)
        )
        """)

    def process_item(self, item, spider):
        ## Define insert statement
        self.cur.execute(f""" INSERT INTO {self.table_name} (hash_url, domain ,url ,title ,content ,tags ,description, insertDate) values (%s,%s,%s,%s,%s,%s,%s,%s)""", 
                         (
                            item["hash_url"],
                            item["domain"],
                            item["url"],
                            item["title"],
                            item["content"],
                            item["tags"],
                            item["description"],
                            item["insertDate"],
                            ))

        ## Execute insert of data into database
        self.conn.commit()

    
    def close_spider(self, spider):

        ## Close cursor & connection to database 
        self.cur.close()
        self.conn.close()
        
class MysqlWssPipeline:
    
    def __init__(self):
        self.conn = mysql.connector.connect(
            host = DBConfig.host,
            user = DBConfig.user,
            password = DBConfig.password,
            database = DBConfig.database,
            auth_plugin='mysql_native_password'
        )

        ## Create cursor, used to execute commands
        self.cur = self.conn.cursor()
        self.table_name = DBConfig.table
        # self.cur.execute(f"""
        # DROP TABLE IF EXISTS {self.table_name};
        # """)
        # self.conn.commit()
        ## Create quotes table if none exists
        self.cur.execute(f"""
        CREATE TABLE IF NOT EXISTS {self.table_name}(
            id int NOT NULL auto_increment,
            hash_url text,
            domain text,
            url text,
            title TEXT,
            content LONGTEXT,
            tags LONGTEXT,
            description LONGTEXT,
            images LONGTEXT,
            article_type TEXT,
            insertDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (id)
        )
        """)

    def process_item(self, item, spider):
        ## Define insert statement
        self.cur.execute(f""" INSERT INTO {self.table_name} 
                         (hash_url, 
                         domain ,
                         url ,
                         title,
                         content,
                         tags,
                         description,
                         images,
                         article_type,
                         insertDate)
                         values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                         """, 
                         (
                            item["hash_url"],
                            item["domain"],
                            item["url"],
                            item["title"],
                            item["content"],
                            item["tags"],
                            item["description"],
                            item["images"],
                            item["article_type"],
                            item["insertDate"],
                            ))

        ## Execute insert of data into database
        self.conn.commit()

    
    def close_spider(self, spider):

        ## Close cursor & connection to database 
        self.cur.close()
        self.conn.close()