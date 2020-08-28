# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from pymongo import MongoClient


class InstascraperPipeline:
    def process_item(self, item, spider):
        client = MongoClient('localhost', 27017)
        db = client['Instagram']
        posts = db.Posts
        post_id = posts.insert_one(item)
        return item
