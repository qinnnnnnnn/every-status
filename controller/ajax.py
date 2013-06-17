#encoding=utf-8
import web
import requests
from datetime import datetime
from config import setting
from model import user
import urllib
from util import login
from util import oauth
import json

config = setting.config
render = setting.render
db = setting.db

def common_check(post=[],get=[]):
    """ request decorator """
    def check(post,get):
        """ 检查登录与否及参数 """
        post_data = web.input(_method="post")
        get_data = web.input(_method="get")
        user = login.logged()
        if not user:
            raise Exception(json.dumps({"code":403,"msg":"access deny"}))

        for k in post:
            if not k in post_data:
                raise Exception(json.dumps({"code":500,"msg":str(k)+" is required"}))

        for k in get:
            if not k in get_data:
                raise Exception(json.dumps({"code":500,"msg":str(k)+" is required"}))

        return {"post":post_data,"get":get_data,"user":user}

    def checkwrap(fn):
        def inner(self):
            try:
                ctx = check(post,get)
                return ok(msg=fn(self,ctx))
            except Exception, e:
                return e
        return inner
    return checkwrap

def ok(msg="ok"):
    return json.dumps({"code":200,"msg":msg})

def fail(msg="fail"):
    return json.dumbs({"code":500,"msg":msg})

def unfavpiece(pieceid,userid):
    where={"pieceid":pieceid,"userid":userid}
    row = db.select("fav",where="pieceid=$pieceid and userid=$userid",vars=where)
    if not row:
        raise Exception(json.dumps({"code":300,"msg":"you've not faved this piece"}))

    db.delete("fav",where="pieceid=$pieceid and userid=$userid",vars=where)

def favpiece(pieceid,userid):
    row = db.select("fav",where="pieceid=$pieceid and userid=$userid",vars={"pieceid":pieceid,"userid":userid})

    if row:
        raise Exception(json.dumps({"code":200,"msg":{"id":row[0]["id"]}}))

    db.insert("fav",pieceid=pieceid,userid=userid,addtime=datetime.now())

class add:
    @common_check(post=["content"])
    def POST(self,ctx):
        """ add one """
        content = ctx["post"]["content"]
        userid = ctx["user"]["id"]
        if "link" in ctx["post"]:
            link = ctx["post"]["link"]
        else:
            link = None

        pieces = db.select("piece",where="content=$content",vars={"content":content})
        # 检查是否已有相同内容
        if not pieces:
            pieceid = db.insert("piece",content=content,user=userid,addtime=datetime.now(),link=link)
        else:
            pieceid = pieces[0]["id"]

        share = ctx["post"]["share"].split(",")

        for key in share:
            if not key: 
                continue
            client = oauth.createClientWithName(key,ctx["user"])
            post_content = u"「" + content + u"」" + " http://" + web.ctx.host + "/piece/" + str(pieceid)
            client.post(post_content)

        favpiece(pieceid,userid)

        return {"id":pieceid}

class fav:
    @common_check(post=["pieceid"])
    def POST(self,ctx):
        """ fav a piece """
        pieceid=ctx["post"]["pieceid"]
        favpiece(pieceid,ctx["user"]["id"])
        return {"id":pieceid}

class userinfo:
    @common_check()
    def GET(self,ctx):
        user = ctx["user"]
        return {"name":user["name"],"id":user["id"],"avatar":user["avatar"]}



class unfav:
    @common_check(post=["pieceid"])
    def POST(self,ctx):
        """ fav a piece """
        unfavpiece(ctx["post"]["pieceid"],ctx["user"]["id"])
        return 

# class delete:
#     def POST(self):
#         try:
#             ctx = common_check(post=["pieceid"])
#             pieceid = ctx["post"]["pieceid"]
#             userid = ctx["user"]["id"]
#             unfavpiece(pieceid,userid)
#             row = db.select("piece",where="id=$id and user=$user",vars={"id":pieceid,"user":userid})
#             if not row:
#                 raise Exception(json.dumps({"code":401,"msg":"permission denied"}))
#             db.delete("piece",where="id=$id and user=$user",vars={"id":pieceid,"user":userid})
#         except Exception, e:
#             return e

#         return ok()

class pieces:
    def GET(self):
        "get pieces"
        pieces_itr = db.query('select id,content from piece order by rand() limit 10')
        pieces=[]
        for piece in pieces_itr:
            pieces.append(piece)
        return json.dumps(pieces)