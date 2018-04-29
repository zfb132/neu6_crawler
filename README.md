# neu6_crawler
6维 爆楼帖统计

本项目基于[EasyLogin](https://github.com/zjuchenyuan/EasyLogin)

目前可以爬取帖子每一页，进行分析

## 运行方法

```
# 依赖库安装
pip3 install -U requests[socks] bs4 -i https://pypi.doubanio.com/simple/ --trusted-host pypi.doubanio.com
# 复制本项目
git clone https://github.com/zjuchenyuan/neu6_crawler
# 将用户名username密码password写入config.py
vim config.py
# 执行爬取 也许你想修改爬取目标 自己改代码吧
./gettopic.py
# 输出分析结果
./analysis_topic.py
```

## 代码文件结构

- login.py 登录逻辑 基类NEU6
- gettopic.py 爬取帖子 生成data.pickle
- analysis_topic.py 读取data.pickle 对爬取得到的数据进行分析

### 类、函数说明：

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