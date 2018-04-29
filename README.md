# neu6_crawler
6维 统计爆楼帖

本项目基于[EasyLogin](https://github.com/zjuchenyuan/EasyLogin)

目前可以爬取帖子每一页，进行分析

代码文件结构：
- login.py 登录逻辑 基类NEU6
- gettopic.py 爬取帖子
- analysis_topic.py 对爬取得到的数据进行分析

类、函数说明：

```
login.py
class NEU6(): 
    def __init__(username, password, login=True)
        使用用户名密码进行登录，如果不需要自动登录可以login=False
        使用EasyLogin提供的_import和export函数持久化cookie避免反复登录
        登录前会调用islogin() 判断是否需要登录

gettopic.py
class NEU6_TOPIC(NEU6):
    def thread_page(self, threadid, pageid, extraid=1, usecache=True):
        获得一个页面，返回[标题, 页面总数, 帖子的数组]
        帖子的数组：[postid, floor, username, contenthtml, content, posttime, replytarget] 全部为str类型
```