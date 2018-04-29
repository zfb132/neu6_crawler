import pickle
from collections import OrderedDict
data=pickle.load(open("data.pickle","rb"))
postid2post = {}
username2post = {}
replied = {}
user_shenyou = {}
posttime_count = OrderedDict()
ziyin_count = {}

def dict_add_list(dictname, key, value):
    if key not in dictname:
        dictname[key] = [value]
    else:
        dictname[key].append(value)

def dict_incr(dictname, key):
    if key not in dictname:
        dictname[key] = 1
    else:
        dictname[key] += 1


for post in data:
    postid, floor, username, contenthtml, content, posttime, replytarget = post
    postid2post[postid]=post
    dict_add_list(username2post, username, postid)
    if replytarget!="-1":
        if postid2post[replytarget][2] == username:
            dict_incr(ziyin_count, username)
        dict_add_list(replied, replytarget, postid)
    else:
        dict_add_list(user_shenyou, username, floor)
    posthour = posttime.split(":")[0]
    dict_incr(posttime_count, posthour)

print("统计截至 "+floor+" 楼 "+posttime)

def sort_by_len(dictname):
    return sorted(dictname.items(), key=lambda i:len(i[1]), reverse=True)

def sort_reverse(dictname):
    return sorted(dictname.items(), key=lambda i:i[1], reverse=True)

def print_name_len_example(name, list, func=None, start=5, end=3):
    if func is None:
        func = lambda i:i
    print("%-10s"%name+"\t"+str(len(list))+"\t"+",".join([func(i) for i in list[:start]])+",...,"+",".join([func(i) for i in list[-end:]]))

print("[用户Top20] 用户名 回帖次数 楼层")
sortbypostcount = sort_by_len(username2post)
for username, user_posts in sortbypostcount[:20]:
    print_name_len_example(username, user_posts, lambda i:postid2post[i][1])

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
    print("%-10s"%username+"\t"+str(count))
