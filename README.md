# neu6_crawler
6维 爆楼帖统计

本项目基于[EasyLogin](https://github.com/zjuchenyuan/EasyLogin)

目前可以爬取帖子每一页，进行分析，并输出回复前10名趋势图

## 运行方法

```
# 依赖库安装
pip3 install -U requests[socks] bs4 -i https://pypi.doubanio.com/simple/ --trusted-host pypi.doubanio.com
# 复制本项目
git clone https://github.com/zjuchenyuan/neu6_crawler
mkdir -p cache
# 将用户名username密码password要爬的帖子threadid写入config.py
vim config.py
# 如果是首次使用，则需要先登录
python3 login.py
# 执行爬取 也许你想修改爬取目标 自己改代码吧
python3 gettopic.py
# 输出分析结果
python3 analysis_topic.py
```

## 代码文件结构

- login.py 登录逻辑 基类NEU6
- gettopic.py 爬取帖子 生成data_帖子id.pickle
- analysis_topic.py 读取pickle文件 对爬取得到的数据进行分析: 回复数Top20用户，被引用Top10，自引用、神游、多次引用违规，最长引用链

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
