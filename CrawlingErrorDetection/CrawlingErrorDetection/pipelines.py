# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

import pymongo
import logging
import sys
import configparser
config = configparser.ConfigParser()
config.read('./../lib/config.cnf')

sys.path.append(config['LOCAL']['PATH_SPIDER'])
mongo_database = config['DB']['MONGO_DB']
mongo_collection = "temp"

class CrawlingErrorDetectionPipeline(object):

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=mongo_database
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        valid = True
        for data in item:
            if not data:
                valid = False
                print("Add to MongoDB Fail!!!!")

        if valid:
            self.db[mongo_collection].insert(dict(item))

        return item
