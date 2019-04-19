# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst
from score_spider.settings import SQL_DATETIME_FORMAT


def remove_space(value):
    return value.strip()


def return_value(value):
    return value


def set_score_list(value, lens):
    return [value[i:i+lens] for i in range(0, len(value), lens)]


class kdjwSpiderItemLoader(ItemLoader):
    default_input_processor = MapCompose(remove_space)


class kdjwSpiderItem(scrapy.Item):
    stu_id = scrapy.Field()
    course_name_list = scrapy.Field()
    course_nature_list = scrapy.Field()
    course_credit_list = scrapy.Field()
    course_time_list = scrapy.Field()
    stu_name = scrapy.Field()
    score_list = scrapy.Field()
    class_name = scrapy.Field()
    fail_nums = scrapy.Field()
    avg_nums = scrapy.Field()
    credit_nums = scrapy.Field()
    avg_credit_nums = scrapy.Field()
    avg_credit_point_nums = scrapy.Field()
    rank = scrapy.Field()
    term = scrapy.Field()
    crawl_time = scrapy.Field(
        input_processor=MapCompose(return_value),
        output_processor=TakeFirst()
    )
    course_len = scrapy.Field(
        input_processor=MapCompose(return_value),
        output_processor=TakeFirst()
    )

    def check_item(self):
        loop = self["course_len"]
        for i in range(len(self["stu_id"])):
            for j in range(len(self["course_name_list"])):
                params = (
                    self["stu_id"][i], self["stu_name"][i], self["term"], self["course_name_list"][j],
                    self["course_nature_list"][j], self["course_credit_list"][j], self["course_time_list"][j],
                    self["score_list"][j+j*loop], self["crawl_time"]
                )
                print(params[1]+":"+params[3]+":"+params[7])



