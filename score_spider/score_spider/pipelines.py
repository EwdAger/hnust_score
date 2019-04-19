# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import MySQLdb
import MySQLdb.cursors
from twisted.enterprise import adbapi
from score_spider.settings import SQL_DATETIME_FORMAT


class ScoreSpiderPipeline(object):
    def process_item(self, item, spider):
        return item.check_item()


class MysqlTwistedPipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbparams = dict(
            host=settings["MYSQL_HOST"],
            db=settings["MYSQL_DBNAME"],
            user=settings["MYSQL_USER"],
            passwd=settings["MYSQL_PASSWORD"],
            charset='utf8',
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True,
        )
        dbpool = adbapi.ConnectionPool("MySQLdb", **dbparams)

        return cls(dbpool)

    def process_item(self, item, spider):
        # 使用twisted将mysql插入变成异步执行
        # query = self.dbpool.runInteraction(self.do_insert_stu, item)
        query = self.dbpool.runInteraction(self.do_insert, item)
        # 处理异常
        query.addErrback(self.handle_error, item, spider)

    def handle_error(self, failure, item, spider):
        # 处理异步插入的异常
        # 在此处打断点截获异常信息
        print(failure)

    def do_insert(self, cursor, item):
        # 执行具体的插入
        insert_sql = """
            INSERT INTO student_info(stu_id, stu_name, class_name, term, 
            fail_nums, avg_nums, credit_nums, avg_credit_nums,
            avg_credit_point_nums, rank, crawl_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        for i in range(len(item["stu_id"])):
            params = (
                item["stu_id"][i], item["stu_name"][i], item["class_name"], item["term"],
                item["fail_nums"][i], item["avg_nums"][i], item["credit_nums"][i], item["avg_credit_nums"][i],
                item["avg_credit_point_nums"][i], item["rank"][i], item["crawl_time"].strftime(SQL_DATETIME_FORMAT)
            )
            cursor.execute(insert_sql, params)
        # 插
        insert_sql2 = """
            INSERT INTO score_info(stu_id, stu_name, term,
            course_name, course_nature, course_credit, course_time, score, crawl_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        loop = 0
        for i in range(len(item["stu_id"])):
            for j in range(len(item["course_name_list"])):
                params2 = (
                    item["stu_id"][i], item["stu_name"][i], item["term"], item["course_name_list"][j],
                    item["course_nature_list"][j], item["course_credit_list"][j], item["course_time_list"][j],
                    item["score_list"][j+item["course_len"]*loop], item["crawl_time"].strftime(SQL_DATETIME_FORMAT)
                )
                cursor.execute(insert_sql2, params2)
            loop += 1
