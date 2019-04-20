# 湖南科技大学班级成绩爬虫

## 关于使用

已测试的环境

`Linux + Python 3.6.5 + MySQL 5.7.21-1`

安装依赖模块

`pip install -r requirements.txt`

导入 `sql` 文件

`mysql> source ./hnust_score.sql`

运行 `main.py`文件

`python ./score_spider/main.py`

## 注意事项

该项目所有配置文件全部在`./score_spider/settings.py`文件下, 请按该文件注释进行维护。
通常情况只需要维护数据库连接以下的配置参数，特别是那个迷之MD5参数2333。

还请维护该项目天(lan)赋(de)过(yao)人(si)的同学发挥想象，破解这个MD5的加密过程，
来基本实现全自动化爬取

当前项目没有统一的错误消息处理， 单单只是`print`了一下错误代码，再该项目接入`Web`后台后，
务必将错误消息加入统一管理中。未接入时请注意log，出现中文提示或者结束过快多半是报错了，
重新执行爬虫即可。当然不放心多执行几次爬虫也没关系。

*以下是含错误处理的文件*
```
./score_spider/pipelines.py  # 数据库插入操作
./score_spider/spiders/kdjw.py  # 登陆
```

- **本项目并未在多账号多学院的情况下进行测试！但理论支持多账号多学院**

- **本项目账号使用的是学院辅导员账号（只能查看当前学院信息），
    如有校级权限的账户可以把代码改的更简单点，当然学生账号直接无法使用本项目（逃**

## 已知问题
- `Linux` 环境安装 `mysqlclient` 失败请安装依赖

    `sudo apt install libmysqlclient-dev`
    
- `MySQL 5.7` 版本以上数据无法覆盖更新，并报错`only_full_group_by`

    在root账户下执行 
    
    `SET GLOBAL  sql_mode=(SELECT REPLACE(@@sql_mode,'ONLY_FULL_GROUP_BY',''));`

- 登录失败后爬虫直接停止不执行后续插入操作

    可能是验证码错误，或者 session 失效，懒得写验证中间件了。
    
    解决方法： 那就多执行几次吧～ 直到所有学院爬完不显示登录失败提示为止，反正重复数据不会覆盖，
    且是异步插入操作，不会多用多少时间。如果看不顺眼就自行在`middlewares.py`添加中间件处理重试吧（逃
    
- 插入数据报错 `[Failure instance: Traceback: <class 'KeyError'>: 'stu_id'`

    默认爬取学期范围是近四年，大四以外的班级肯定会又出现没有数据的情况，但每一个返回的`request`
    都会传递到`pipeline`里处理写入，所以会报错。但是并没有什么影响，只是看的不舒服（虽然也不严谨233
    