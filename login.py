from EasyLogin import EasyLogin

import time
myprint = lambda s: print("[{showtime}] {s}".format(showtime=time.strftime("%Y-%m-%d %H:%M:%S"), s=s))

class NEU6():
    def __init__(self, username, password):
        self.ENDPOINT = "http://bt.neu6.edu.cn"
        self.username = username
        self.password = password
        try:
            self.a = EasyLogin._import("neu6_"+username+".status")
        except:
            self.a = EasyLogin()
        if not self.islogin():
            self.login()
            self.a.export("neu6_"+username+".status")
    
    def islogin(self):
        a = self.a
        x = a.get("http://bt.neu6.edu.cn/forum.php", o=True)
        if x.status_code == 200:
            return True
        else:
            return False
    
    def login(self):
        myprint("Login: "+self.username)
        a = self.a
        a.get(self.ENDPOINT+"/member.php?mod=logging&action=login&referer=http%3A%2F%2Fbt.neu6.edu.cn%2Fforum.php")
        action = a.b.find("form")["action"]
        formhash = a.b.find("input",{"name":"formhash"})["value"]
        referer = "http://bt.neu6.edu.cn/forum.php"
        x = a.post_dict(self.ENDPOINT+"/"+action, {
            "formhash":formhash, 
            "referer":referer, 
            "username":self.username, 
            "password":self.password,
            "questionid": "0",
            "answer": ""
        })
        if b"home.php?mod=space&amp;uid=" in x.content:
            return True
        else:
            return False
    

if __name__=="__main__":
    from config import username, password
    x=NEU6(username, password)