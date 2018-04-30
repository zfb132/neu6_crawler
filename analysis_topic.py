import pickle
from collections import OrderedDict
import sys
data=pickle.load(open("data.pickle","rb"))
postid2post = {}
username2post = {}
replied = {}
user_shenyou = {}
posttime_count = OrderedDict()
ziyin_count = {}
user_replieusers = {}
palou_count = {}

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

def dict_incr(dictname, key):
    if key not in dictname:
        dictname[key] = 1
    else:
        dictname[key] += 1

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
        dict_add_set(user_replieusers, username, postid2post[replytarget][2]) #用户引用覆盖的用户加入set
    else:
        dict_add_list(user_shenyou, username, floor) #没有引用直接回复 加入神游
    posthour = posttime.split(":")[0] #提取日期、小时
    dict_incr(posttime_count, posthour) #时间统计
    
maxfloor = floor #统计截至maxfloor楼
maxposttime = posttime

for username in palou_count:
    palou_count[username] = palou_count[username]/(len(username2post[username])-len(user_shenyou.get(username, [])))

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

if len(sys.argv)==1:
    print("\n[神游Top10] 用户名 神游次数 楼层")
    for username, shenyou_floors in sort_by_len(user_shenyou)[:10]:
        print_name_len_example(username, shenyou_floors)

    print("\n[发帖时间统计] 小时 回复数量")
    for hour, count in posttime_count.items():
        print(hour+"点"+"\t"+str(count))

    print("\n[被引用Top10] 被引楼层 被引数 引用它的楼层")
    for reply_target, replys in sort_by_len(replied)[:10]:
        print_name_len_example(postid2post[reply_target][1], replys, lambda i:postid2post[i][1], end=1)

    print("\n[自引用违规] 用户名 自引数量")
    for username, count in sort_reverse(ziyin_count):
        print(username+": "+str(count), end="; ")
    print()

    print("\n[回复覆盖率Top10] 用户名 ta回复的用户数 (用户数总数%d)"%len(username2post))
    for username, reply_users in sort_by_len(user_replieusers)[:10]:
        print_name_len_example(username, sorted(reply_users), start=0)

    #print("\n[爬楼计数] 用户名 爬楼数量")
    #for username, count in sort_reverse(palou_count):
    #    print("%-10s"%username+"\t"+"%.1f%%"%(count*100))

    print("\n[用户Top20]\n[table]")
    print("[tr][td]"+"[/td][td]".join(["排名","用户名","回帖次数","爬楼率(引用的引用不是自己的比率)","神游次数(不引用直接回复, 大于1则违规)","回复平均字数","楼层"])+"[/td][/tr]")
    sortbypostcount = sort_by_len(username2post)
    t = 1
    for username, user_posts in sortbypostcount[:20]:
        #print_name_len_example(username, user_posts, lambda i:postid2post[i][1])
        name = username
        list = user_posts
        func = lambda i:floor2url(postid2post[i][1])
        start = 5
        end = 3
        splitchar = "[/td][td]"
        print("[tr][td]"+str(t)+splitchar+name+splitchar+str(len(list))+splitchar+"%2.1f%%"%(palou_count.get(username, 0)*100)+splitchar+str(len(user_shenyou.get(username,[])))+splitchar+"%.0f"%(sum([len(postid2post[i][4]) for i in username2post[username]])/len(username2post[username]))+splitchar+(",".join([func(i) for i in list[:start]])+",...,"+",".join([func(i) for i in list[-end:]]) if start>0 else "")+"[/td][/tr]")
        t+=1
    print("[/table]\n")
else:
    username = sys.argv[1]
    print("神游楼层：")
    for floor in user_shenyou[username]:
        print(floor2url(floor), end=",")
    print()
    
    print("所有回复：")
    for postid in username2post[username]:
        postid, floor, username, contenthtml, content, posttime, replytarget = postid2post[postid]
        print(floor, content)

print("统计截至 "+maxfloor+" 楼 "+maxposttime)