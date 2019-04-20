# -*- coding: utf-8 -*-
import scrapy
from tools.captcha_verify import verify
from score_spider.items import kdjwSpiderItem, kdjwSpiderItemLoader
from datetime import datetime
from score_spider.settings import ADMIN_LIST, PASSWORD_LIST
from score_spider.settings import mystery_post_data


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
        for yx in range(len(mystery_post_data["yx"])):
            post_data = {
                "USERNAME": ADMIN_LIST[yx],
                "PASSWORD": PASSWORD_LIST[yx],
                "RANDOMCODE": ""
            }

            captcha_url = "http://kdjw.hnust.edu.cn/kdjw/verifycode.servlet"
            yield scrapy.Request(captcha_url, cookies=cookies, meta={"post_data": post_data, "yx": yx},
                                 callback=self.login_after_captcha, dont_filter=True)

    def login_after_captcha(self, response):
        with open("captcha.jpg", "wb") as f:
            f.write(response.body)
            f.close()
        captcah_code = verify("captcha.jpg")

        post_data = response.meta.get("post_data", {})
        post_data["RANDOMCODE"] = captcah_code
        post_url = "http://kdjw.hnust.edu.cn/kdjw/Logon.do?method=logon"
        yx = response.meta.get("yx")
        return [scrapy.FormRequest(url=post_url, formdata=post_data, meta={"yx": yx},
                                   callback=self.check_login, dont_filter=True)]

    def check_login(self, response):
        yx = response.meta.get("yx")
        # 校验是否登陆成功
        success_code = '<script language=\'javascript\'>window.location.href=\'http://kdjw.hnust.edu.cn/kdjw/framework/main.jsp\';</script>\r\n'
        if response.text != success_code:
            # 接入系统后请自行添加至错误处理
            msg = mystery_post_data["yx"][yx]
            print("院系编号 {0} 的账号登陆失败！如果多次出现该错误，请检查账号密码是否有误".format(msg))
        else:
            mystery = mystery_post_data
            search_url = "http://kdjw.hnust.edu.cn/kdjw/cjzkAction.do?method=tofindCj0708ByXNBJ"
            years = int(datetime.now().strftime("%Y"))
            # 控制8个学期的循环
            # 此处取前四年至当前年份的8个学期的数据，没有数据默认是取不到的，可以自定义这个循环参数
            for i in range(years-4, years+1):
                for j in range(1, 3):
                    term = "-".join(list(map(str, [i, i+1, j])))
                    # 控制一个院系不同班级的循环
                    for mystery_index in range(len(mystery["zy"])):
                        post_data = {
                            "kcly": "1",
                            "xqmc": term,
                            "xnxq": term,
                            "yx": str(yx),
                            "zy": mystery["zy"][mystery_index],
                            "hbqkMc": mystery["hbqkMc"][mystery_index],
                            "hbqkid": mystery["hbqkid"][mystery_index],
                            "pxfs": "1",
                            "pmfs": "3",
                            "xsfs": "1",
                            "xjzt": "01"
                        }
                        yield scrapy.FormRequest(url=search_url, formdata=post_data, meta={
                            "class_name": post_data["hbqkMc"], "term": post_data["xqmc"]}, dont_filter=True)
