# -*- coding: utf-8 -*-
import scrapy
from tools.captcha_verify import verify
from scrapy.loader import ItemLoader
from score_spider.items import kdjwSpiderItem, kdjwSpiderItemLoader
from datetime import datetime
from score_spider.settings import ADMIN, PASSWORD


class KdjwSpider(scrapy.Spider):
    name = 'kdjw'
    allowed_domains = []
    start_urls = ['http://kdjw.hnust.edu.cn/kdjw/']

    def parse(self, response):
        item_loader = kdjwSpiderItemLoader(item=kdjwSpiderItem(), response=response)
        course_len = len(response.xpath("//tr[@bgcolor='#D1E4F8'][1]/th"))
        student_len = len(response.xpath("//tr[@class='smartTr']"))
        item_loader.add_value("class_name", response.meta.get("class_name"))
        item_loader.add_value("term", response.meta.get("term"))
        item_loader.add_value("crawl_time", datetime.now())
        # 1位为序号，后7位为合计之类的东西
        for i in range(5, course_len - 7 + 1):
            item_loader.add_xpath("course_name_list", "//tr[@bgcolor='#D1E4F8'][1]/th[{0}]/font/text()".format(i))
            item_loader.add_xpath("course_nature_list", "//tr[@bgcolor='#D1E4F8'][2]/th[{0}]/font/text()".format(i))
            item_loader.add_xpath("course_credit_list", "//tr[@bgcolor='#D1E4F8'][4]/th[{0}]/font/text()".format(i))
            item_loader.add_xpath("course_time_list", "//tr[@bgcolor='#D1E4F8'][5]/th[{0}]/font/text()".format(i))

        for i in range(1, student_len - 2 + 1):
            item_loader.add_xpath("stu_id", "//tr[@class='smartTr'][{0}]/td[2]/text()".format(i))
            item_loader.add_xpath("stu_name", "//tr[@class='smartTr'][{0}]/td[3]/text()".format(i))
            for j in range(5, course_len - 7 + 1):
                if response.xpath("//tr[@class='smartTr'][{0}]/td[{1}]/text()".format(i, j)):
                    item_loader.add_xpath("score_list", "//tr[@class='smartTr'][{0}]/td[{1}]/text()".format(i, j))
                else:
                    item_loader.add_xpath("score_list", "//tr[@class='smartTr'][{0}]/td[{1}]/font/text()".format(i, j))
            item_loader.add_xpath("fail_nums", "//tr[@class='smartTr'][{0}]/td[last()-6]/text()".format(i))
            item_loader.add_xpath("avg_nums", "//tr[@class='smartTr'][{0}]/td[last()-5]/text()".format(i))
            item_loader.add_xpath("credit_nums", "//tr[@class='smartTr'][{0}]/td[last()-3]/text()".format(i))
            item_loader.add_xpath("avg_credit_nums", "//tr[@class='smartTr'][{0}]/td[last()-2]/text()".format(i))
            item_loader.add_xpath("avg_credit_point_nums", "//tr[@class='smartTr'][{0}]/td[last()-1]/text()".format(i))
            item_loader.add_xpath("rank", "//tr[@class='smartTr'][{0}]/td[last()]/text()".format(i))
        # 去掉表头首尾得出的的课程总数
        item_loader.add_value("course_len", course_len - 11)

        score_item = item_loader.load_item()
        return score_item

    def start_requests(self):
        return [scrapy.Request("http://kdjw.hnust.edu.cn/kdjw/", callback=self.login, dont_filter=True)]

    def login(self, response):
        cookies_str = response.headers.get("Set-Cookie")
        cookies = {"Cookie": cookies_str}

        post_data = {
            "USERNAME": ADMIN,
            "PASSWORD": PASSWORD,
            "RANDOMCODE": ""
        }

        captcha_url = "http://kdjw.hnust.edu.cn/kdjw/verifycode.servlet"
        yield scrapy.Request(captcha_url, cookies=cookies, meta={"post_data": post_data},
                             callback=self.login_after_captcha)

    def login_after_captcha(self, response):
        with open("captcha.jpg", "wb") as f:
            f.write(response.body)
            f.close()
        captcah_code = verify("captcha.jpg")

        post_data = response.meta.get("post_data", {})
        post_data["RANDOMCODE"] = captcah_code
        post_url = "http://kdjw.hnust.edu.cn/kdjw/Logon.do?method=logon"
        return [scrapy.FormRequest(url=post_url, formdata=post_data, callback=self.check_login, dont_filter=True)]

    def check_login(self, response):
        # 校验是否登陆成功
        success_code = '<script language=\'javascript\'>window.location.href=\'http://kdjw.hnust.edu.cn/kdjw/framework/main.jsp\';</script>\r\n'
        if response.text != success_code:
            print("登陆失败！请重试")
        else:
            search_url = "http://kdjw.hnust.edu.cn/kdjw/cjzkAction.do?method=tofindCj0708ByXNBJ"
            post_data = {
                "kcly": "1",
                "xqmc": "2016-2017-2",
                "xnxq": "2016-2017-2",
                "yx": "05",
                "zy": "19B290C33DAE4EF1A152F5B92EAEC142",
                "hbqkMc": "15网络2班",
                "hbqkid": "C2AB1A6A42764013B37CF1E354DE25CF",
                "pxfs": "1",
                "pmfs": "3",
                "xsfs": "1",
                "xjzt": "01"
            }
            yield scrapy.FormRequest(url=search_url, formdata=post_data, meta={
                "class_name": post_data["hbqkMc"], "term": post_data["xqmc"]}, dont_filter=True)
