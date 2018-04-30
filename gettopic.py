from login import NEU6
import re

class NEU6_TOPIC(NEU6):
    def thread_page(self, threadid, pageid, extraid=1, usecache=True):
        """
        获得一个页面，返回[标题, 页面总数, 帖子的数组]
        帖子[postid, floor, username, contenthtml, content, posttime, replytarget]
        """
        a = self.a
        cache = None
        if usecache:
            a.cachedir = "cache/"
            cache = "thread-{threadid}-{pageid}-{extraid}.html".format(**locals())
        url = self.ENDPOINT + "/thread-{threadid}-{pageid}-{extraid}.html".format(**locals())
        html = a.get(url, cache=cache)
        title = a.b.find("span",{"id":"thread_subject"}).text
        try:
            pages = int(a.b.find("a", {"class":"last"})["href"].split("-")[-2])
        except:
            pages = int(pageid)
        postsdiv = a.b.find("div", {"id":"postlist"})
        posts = [] #数据结构[postid, floor, username, contenthtml, content, posttime, replytarget] 全部为str类型
        postids = re.findall(r"checkmgcmn\('post_(\d+)", html)
        
        #for div in postsdiv.children:
        for postid in postids:
            div = a.b.find("div", {"id": "post_"+postid})
            if not (div.name == "div" and div["id"].startswith("post_")):
                continue
            assert postid == div["id"].replace("post_","")
            userinfodiv = div.find("div",{"id":"userinfo"+postid})
            username = userinfodiv.find("a").text
            contenttd = div.find("td",{"id":"postmessage_"+postid})
            contenthtml = "<".join(">".join(str(contenttd).split(">")[1:]).split("<")[:-1]).strip()
            quotediv = contenttd.find("div",{"class":"quote"})
            replytarget = "-1"
            if quotediv:
                replytarget = quotediv.find("blockquote").find("a")["href"].split("&pid=")[1].split("&")[0]
                quotediv.extract()
            content = contenttd.text.strip()
            floordiv = div.find("a",{"id":"postnum"+postid})
            if floordiv.text.strip()=="楼主":
                floor = "1"
            else:
                floor = floordiv.find("em").text.strip()
            posttime = div.find("em", {"id":"authorposton"+postid}).text.replace("发表于 ","")
            print(floor,username,content,posttime,replytarget)
            #print(floor)
            posts.append([postid, floor, username, contenthtml, content, posttime, replytarget])
        return [title, pages, posts]
    
    def thread_pages(self, threadid):
        return self.thread_page(threadid, pageid=1, extraid=1, usecache=False)[1]

if __name__=="__main__":
    from config import username, password
    import pickle
    posts = []
    threadid = 1623494
    x=NEU6_TOPIC(username, password, login=False)
    if 1:
        posts = pickle.load(open("data.pickle","rb"))
        for i in range(1, int(posts[-1][1])+1):
            try:
                assert i==int(posts[i-1][1]) # 检查缓存正确性 如果遗漏了楼层退出
            except:
                print(i,post[i-1])
                exit()
        lastfloor = int(posts[-1][1])
        lastpage = lastfloor//10
        pages = x.thread_pages(threadid) # 不使用缓存获取当前有多少页
        i = lastpage+1
        usecache = False # 最后一页不使用缓存
        while i<=pages:
            title, _pages, page_posts = x.thread_page(threadid, i, usecache=usecache)
            if _pages > pages:
                pages = _pages
            usecache= True # 后续页面继续允许缓存
            try:
                assert int(posts[-1][1])+1 == int(page_posts[0][1])
            except:
                posts = posts[:int(page_posts[0][1])-1] # 删掉旧数据的最后几楼
                assert int(posts[-1][1])+1 == int(page_posts[0][1])
            posts.extend(page_posts)
            if i%10==0:
                open("data.pickle","wb").write(pickle.dumps(posts))
            i += 1
        open("data.pickle","wb").write(pickle.dumps(posts))
    else:
        pass