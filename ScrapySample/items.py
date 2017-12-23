# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class QuoteItem(scrapy.Item):
    text = scrapy.Field()
    tags = scrapy.Field()
    author = scrapy.Field()

    next_page = scrapy.Field()
    pass


class AuthorItem(scrapy.Item):
    name = scrapy.Field()
    birthday = scrapy.Field()
    address = scrapy.Field()
    description = scrapy.Field()
    pass
