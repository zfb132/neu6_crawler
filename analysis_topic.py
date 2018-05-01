#!/usr/bin/python3
# encoding: utf-8
from __future__ import print_function
import pickle
from collections import OrderedDict
import sys
import json
import time
from config import threadid
datafilename = "data_{threadid}.pickle".format(**locals())
data=pickle.load(open(datafilename,"rb"))

try:
    from config import config_top
except:
    config_top = 20

try:
    from config import after_analysis
except:
    after_analysis = lambda i:None

postid2post = {}
username2post = {}
replied = {}
user_notice = {} #用户收到的提醒列表 floor
user_replied_to = {}
user_shenyou = {}
posttime_count = OrderedDict()
ziyin_count = {}
user_replieusers = {}
palou_count = {}
user_yinyong = {}
quote_depth = {} #引用链深度 如5引用3引用1，则为{1:0, 3:1, 5:2}

def dict_add_list(dictname, key, value):
    if key not in dictname:
        dictname[key] = [value]
    else:
        dictname[key].append(value)

def dict_add_set(dictname, key, value):
    if key not in dictname:
        dictname[key] = set([value])
    else:
        dictname[key].add(value)

def dict_incr(dictname, key, value=1):
    if key not in dictname:
        dictname[key] = value
    else:
        dictname[key] += value

def dict_extend(dictname, key, value):
    if key not in dictname:
        dictname[key] = value
    else:
        dictname[key].extend(value)

id2username = lambda id:postid2post[id][2]

for post in data: #遍历一遍所有的回帖
    postid, floor, username, contenthtml, content, posttime, replytarget = post
    postid2post[postid]=post #用回复id查到回复
    dict_add_list(username2post, username, postid) #用户名查到回复id
    if replytarget!="-1":
        if id2username(replytarget) == username:
            dict_incr(ziyin_count, username) #自引用计数
        if postid2post[replytarget][6]!="-1" and id2username(postid2post[replytarget][6])!=username:
            dict_incr(palou_count, username) #爬楼计数 引用的引用不是自己
        dict_add_list(replied, replytarget, postid) #被引用楼层replied加入此楼id
        dict_add_list(user_notice, postid2post[replytarget][2], floor) #写入被引用用户的通知
        dict_add_list(user_replied_to, username, postid2post[replytarget][1]) #写入回复关系
        dict_add_set(user_replieusers, username, postid2post[replytarget][2]) #用户引用覆盖的用户加入set
        if username not in user_yinyong:
            user_yinyong[username] = {}
        dict_add_list(user_yinyong[username], postid2post[replytarget][1], floor)
        dict_incr(quote_depth, int(floor), 1+quote_depth[int(postid2post[replytarget][1])])
    else:
        dict_add_list(user_shenyou, username, floor) #没有引用直接回复 加入神游
        dict_incr(quote_depth, int(floor), 0)
    posthour = posttime.split(":")[0] #提取日期、小时
    dict_incr(posttime_count, posthour) #时间统计
    
maxfloor = floor #统计截至maxfloor楼
maxposttime = posttime

for username in palou_count:
    palou_count[username] = palou_count[username]/(len(username2post[username])-len(user_shenyou.get(username, [])))

yinyong_weigui = {}
yinyong_weigui_count = {}
for username, floordict in user_yinyong.items():
    for floor, quotefloors in floordict.items():
        count = len(quotefloors)
        if count>1:
            dict_extend(yinyong_weigui, username, quotefloors)
            dict_incr(yinyong_weigui_count, username, count-1)

notice_reply_ratio = {}
for username, floors in user_notice.items():
    fenzi = 0
    fenmu = len(floors)
    for floor in floors:
        if floor in user_replied_to.get(username,[]):
            fenzi += 1
    notice_reply_ratio[username] = fenzi/fenmu

print("统计截至 "+maxfloor+" 楼 "+maxposttime)

def sort_by_len(dictname):
    return sorted(dictname.items(), key=lambda i:len(i[1]), reverse=True)

def sort_reverse(dictname):
    return sorted(dictname.items(), key=lambda i:i[1], reverse=True)

def print_name_len_example(name, list, func=None, start=5, end=3):
    if func is None:
        func = lambda i:i
    print("%-10s"%name+"\t"+str(len(list))+"\t"+(",".join([func(i) for i in list[:start]])+",...,"+",".join([func(i) for i in list[-end:]]) if start>0 else ""))

def floor2id(floor):
    return data[floor-1][0]

def floor2url(floor): #输入楼层输出对应的url
    floor = int(floor)
    pageid = (floor+9)//10
    pid = floor2id(floor)
    return "[url=/forum.php?mod=viewthread&tid=1623494&page={pageid}#pid{pid}]{floor}[/url]".format(**locals())

starttime = int(time.mktime(time.strptime(data[1][5], "%Y-%m-%d %H:%M"))) #开始时间按沙发的发帖时间计算

def trenddata(userposts):
    result = [[0,0]]
    tmp = 0
    for postid in userposts:
        tmp += 1
        if tmp %3 != 0 and postid!=userposts[-1]:
            continue
        posttime = postid2post[postid][5]
        timestamp = int(time.mktime(time.strptime(posttime, "%Y-%m-%d %H:%M")))
        elasped_seconds = timestamp-starttime
        elasped_hours = elasped_seconds/3600
        result.append([elasped_hours, tmp])
    return result

floor_handled = {}
def print_quote_link(floor, t, depth=-1):
    post = data[int(floor)-1]
    floor = str(floor)
    if floor_handled.get(floor, False) == True:
        return False#如果这条链是之前链的子链 跳过
    floor_handled[floor] = True
    result = [floor]
    while post[6]!="-1":
        post = postid2post[post[6]]
        if floor_handled.get(post[1], False):
            continue
        result.append(post[1])
        floor_handled[post[1]] = True
    if len(result)>30:
        len_result = len(result)
        if depth>0:
            result = result[0:depth]
        print("第%d条链(长度%d)："%(t, len_result)+"\n".join([floor2url(i)+" "+"%-10s"%data[int(i)-1][2]+"\t"+data[int(i)-1][4].replace("\n","").replace("\r","") for i in result])+"\n----\n")
        return True
    else:
        return False

if len(sys.argv)==1:
    print("\n[发帖时间统计] 小时 回复数量")
    for hour, count in posttime_count.items():
        print(hour+"点"+"\t"+str(count))

    print("\n[用户Top{config_top}]\n[table]".format(config_top=config_top))
    print("[tr][td]"+"[/td][td]".join(["排名","用户名","回帖次数","爬楼率(引用的引用不是自己的比率)","提醒处理率(别人回复了我 我接着回复别人)","神游次数(不引用直接回复, 大于1则违规)","重复引用违规(同一层不能引用两次)","回复平均字数","楼层"])+"[/td][/tr]")
    sortbypostcount = sort_by_len(username2post)
    t = 1
    trendjson = []
    for username, user_posts in sortbypostcount[:config_top]:
        #print_name_len_example(username, user_posts, lambda i:postid2post[i][1])
        name = username
        list = user_posts
        func = lambda i:floor2url(postid2post[i][1])
        start = 1
        end = 1
        splitchar = "[/td][td]"
        print("[tr][td]"+str(t)+splitchar+\
              name+splitchar+\
              str(len(list))+splitchar+\
              "%2.1f%%"%(palou_count.get(username, 0)*100)+splitchar+\
              "%2.1f%%"%(notice_reply_ratio.get(username, 0)*100)+splitchar+\
              str(len(user_shenyou.get(username,[])))+splitchar+\
              str(yinyong_weigui_count.get(username,0))+splitchar+\
              "%.0f"%(sum([len(postid2post[i][4]) for i in username2post[username]])/len(username2post[username]))+splitchar+\
              (",".join([func(i) for i in list[:start]])+",...,"+",".join([func(i) for i in list[-end:]]) if start>0 else "")+\
              "[/td][/tr]")
        if t<=10:
            trendjson.append({"name":username, "data": trenddata(user_posts), "type":"line", "showAllSymbol":True})
        t+=1
    print("[tr][td]"+"[/td][td]".join(["排名","用户名","回帖次数","爬楼率(引用的引用不是自己的比率)","提醒处理率(别人回复了我 我接着回复别人)","神游次数(不引用直接回复, 大于1则违规)","多次引用违规","回复平均字数","楼层"])+"[/td][/tr]")
    print("[/table]\n")

    print("\n[被引用Top10] 被引楼层 被引数 引用它的楼层")
    for reply_target, replys in sort_by_len(replied)[:10]:
        print_name_len_example(postid2post[reply_target][1], replys, lambda i:postid2post[i][1], end=1)

    print("\n[自引用违规] 用户名 自引数量")
    for username, count in sort_reverse(ziyin_count):
        print(username+": "+str(count), end="; ")
    print()

    print("\n[神游违规Top10] 用户名 神游次数 楼层")
    for username, shenyou_floors in sort_by_len(user_shenyou)[:10]:
        print_name_len_example(username, shenyou_floors)

    print("\n[回复覆盖率Top10] 用户名 ta回复的用户数 (用户数总数%d)"%len(username2post))
    for username, reply_users in sort_by_len(user_replieusers)[:10]:
        print_name_len_example(username, sorted(reply_users), start=0)

    #print("\n[爬楼计数] 用户名 爬楼数量")
    #for username, count in sort_reverse(palou_count):
    #    print("%-10s"%username+"\t"+"%.1f%%"%(count*100))

    print("\n[重复引用违规]\n[table][tr][td]用户名[/td][td]违规次数[/td][td]违规相应楼层[/td][/tr]")
    for username, count in sort_reverse(yinyong_weigui_count):
        print("[tr][td]"+"[/td][td]".join([username,str(count),",".join([floor2url(i) for i in yinyong_weigui[username]])])+"[/td][/tr]")
    print("[/table]")

    template = open("trend.template.html","r", encoding="utf-8").read()
    open("trend.html", "w", encoding="utf-8").write(
        template.replace("{{trendjson}}",json.dumps(trendjson).replace("'","\\'"))\
                .replace("{{starttime}}",str(starttime))\
                .replace("{{titletext}}","统计截至 "+maxfloor+" 楼 "+maxposttime)
    )
    
    print("\n[最长引用链] 按完整链长度排序，但只显示每条链最后一层楼")
    t = 1
    for floor, depth in sort_reverse(quote_depth):
        if print_quote_link(floor, t, 1):
            t += 1
    print()
    lastfloor = data[-1][1]
    after_analysis(lastfloor)

else:
    username = sys.argv[1]

    print("所有回复：")
    for postid in username2post[username]:
        postid, floor, username, contenthtml, content, posttime, replytarget = postid2post[postid]
        print(floor, content)
    
    print("\n回复数量：",len(username2post[username]))
    
    print("爬楼率：%2.1f%%"%(palou_count.get(username, 0)*100))
    
    print("提醒处理率: %2.1f%%"%(notice_reply_ratio.get(username, 0)*100))
    
    print("神游次数 %d 楼层："%len(user_shenyou.get(username,[])))
    for floor in user_shenyou.get(username,[]):
        print(floor2url(floor), end=",")
    print()
    
    print("重复引用违规次数 %d 楼层："%yinyong_weigui_count.get(username,0))
    print(",".join([floor2url(i) for i in yinyong_weigui.get(username,[])]))


print("\n统计截至 "+maxfloor+" 楼 "+maxposttime)