# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class CrawlingErrorDetectionItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    post_title = scrapy.Field()
    post_body = scrapy.Field()
    post_writer = scrapy.Field()
    post_date = scrapy.Field()
    published_institution = scrapy.Field()
    published_institution_url = scrapy.Field()
    top_category = scrapy.Field()
    original_url = scrapy.Field()
    file_name = scrapy.Field()
    file_download_url = scrapy.Field()
    file_id_in_fsfiles = scrapy.Field()
    file_extracted_content = scrapy.Field()
    hash_key = scrapy.Field()
    timestamp = scrapy.Field()
