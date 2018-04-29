import pickle
from collections import OrderedDict
data=pickle.load(open("data.pickle","rb"))
postid2post = {}
username2post = {}
replied = {}
user_shenyou = {}
posttime_count = OrderedDict()
ziyin_count = {}
for post in data:
    postid, floor, username, contenthtml, content, posttime, replytarget = post
    postid2post[postid]=post
    if username not in username2post:
        username2post[username] = [postid]
    else:
        username2post[username].append(postid)
    if replytarget!="-1":
        if postid2post[replytarget][2] == username:
            if username not in ziyin_count:
                ziyin_count[username] = 1
            else:
                ziyin_count[username] += 1
        if replytarget not in replied:
            replied[replytarget] = [postid]
        else:
            replied[replytarget].append(postid)
    else:
        if username not in user_shenyou:
            user_shenyou[username] = [floor]
        else:
            user_shenyou[username].append(floor)
    posthour = posttime.split(":")[0]
    if posthour not in posttime_count:
        posttime_count[posthour] = 1
    else:
        posttime_count[posthour] += 1

print("统计截至 "+floor+" 楼 "+posttime)

print("[用户Top20] 用户名 回帖次数")
sortbypostcount = sorted(username2post.items(), key=lambda i:len(i[1]), reverse=True)
for username, user_posts in sortbypostcount[:20]:
    print("%-10s"%username+"\t"+str(len(user_posts)))

print("\n[神游Top10] 用户名 神游次数 楼层")
for username, shenyou_floors in sorted(user_shenyou.items(), key=lambda i:len(i[1]), reverse=True)[:10]:
    print("%-10s"%username+"\t"+str(len(shenyou_floors))+"\t"+",".join(shenyou_floors[:5])+",...,"+",".join(shenyou_floors[-3:]))

print("\n[发帖时间统计] 小时 回复数量")
for hour, count in posttime_count.items():
    print(hour+"点"+"\t"+str(count))

print("\n[被引用Top10] 被引楼层 被引数 引用它的楼层")
for reply_target, replys in sorted(replied.items(), key=lambda i:len(i[1]), reverse=True)[:10]:
    print(postid2post[reply_target][1]+"\t"+str(len(replys))+"\t"+",".join([postid2post[i][1] for i in replys[:5]])+",...,"+",".join([postid2post[i][1] for i in replys[-1:]]))

print("\n[自引用违规] 用户名 自引数量")
for username, count in sorted(ziyin_count.items(), key=lambda i:i[1], reverse=True):
    print("%-10s"%username+"\t"+str(count))
