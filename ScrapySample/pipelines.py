# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymysql as sql
import pymysql.cursors
import scrapy

config = {
    'host': '127.0.0.1',
    'port': 8081,
    'user': 'root',
    'password': 'root',
    'db': 'xietao',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor,
}


class ScrapySamplePipeline(object):

    def __init__(self):
        self.db = sql.connect(**config)
        self.cursor = self.db.cursor()

    def process_item(self, item, spider):
        # 先保存作者信息
        sql = 'INSERT INTO author (name, birthday, address, detail) VALUES (%s, %s, %s, %s)'
        self.cursor.execute(sql, (item['author']['name'], item['author']['birthday'], item['author']['address'], item['author']['description']))
        # 获取作者id
        author_id = self.cursor.lastrowid

        # 保存引述信息
        sql = 'INSERT INTO spider (text, tags, author) VALUES (%s, %s, %s)'
        self.cursor.execute(sql, (item['text'], ','.join(item['tags']), author_id))
        self.db.commit()

    def close_spider(self, spider):
        self.db.close()
        self.cursor.close()
        print('close db')
