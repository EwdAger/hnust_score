# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import MySQLdb
import MySQLdb.cursors
from twisted.enterprise import adbapi
from score_spider.settings import SQL_DATETIME_FORMAT
import hashlib


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
        query = self.dbpool.runInteraction(self.do_insert, item)
        # 处理异常
        query.addErrback(self.handle_error, item, spider)

    def handle_error(self, failure, item, spider):
        # 处理异步插入的异常
        # 在此处打断点截获异常信息
        print(failure)

    def do_insert(self, cursor, item):
        # 执行具体的插入
        # MySQL 5.7 版本以上记得关闭默认的 only_full_group_by 不然无法进行更新且不会报错！
        # 在root账户下执行 SET GLOBAL  sql_mode=(SELECT REPLACE(@@sql_mode,'ONLY_FULL_GROUP_BY',''));
        stu_insert_sql = """
            INSERT INTO student_info(id, stu_id, stu_name, class_name, term, 
            fail_nums, avg_nums, credit_nums, avg_credit_nums,
            avg_credit_point_nums, term_rank, crawl_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
            stu_name=VALUES(stu_name), class_name=VALUES(class_name), fail_nums=VALUES(fail_nums),
            avg_nums=VALUES(avg_nums), credit_nums=VALUES(credit_nums), avg_credit_nums=VALUES(avg_credit_nums),
            avg_credit_point_nums=VALUES(avg_credit_point_nums), term_rank=VALUES(term_rank)
        """
        for i in range(len(item["stu_id"])):
            stu_id, term = item["stu_id"][i], item["term"]
            stu_params = (
                self.get_md5(stu_id, term), stu_id, item["stu_name"][i], item["class_name"], term,
                item["fail_nums"][i], item["avg_nums"][i], item["credit_nums"][i], item["avg_credit_nums"][i],
                item["avg_credit_point_nums"][i], item["rank"][i], item["crawl_time"].strftime(SQL_DATETIME_FORMAT)
            )
            cursor.execute(stu_insert_sql, stu_params)

        sco_insert_sql = """
            INSERT INTO score_info(id, stu_id, stu_name, term,
            course_name, course_nature, course_credit, course_time, score, crawl_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
            stu_name=VALUES(stu_name), score=VALUES(score)
        """
        loop = 0
        for i in range(len(item["stu_id"])):
            for j in range(len(item["course_name_list"])):
                stu_id, course_name = item["stu_id"][i], item["course_name_list"][j]
                sco_params = (
                    self.get_md5(stu_id, course_name), stu_id, item["stu_name"][i], item["term"], course_name,
                    item["course_nature_list"][j], item["course_credit_list"][j], item["course_time_list"][j],
                    item["score_list"][j+item["course_len"]*loop], item["crawl_time"].strftime(SQL_DATETIME_FORMAT)
                )
                cursor.execute(sco_insert_sql, sco_params)
            loop += 1

    def get_md5(self, a, b):
        m = hashlib.md5()
        m.update(a.encode("utf-8") + b.encode("utf-8"))
        return m.hexdigest()
