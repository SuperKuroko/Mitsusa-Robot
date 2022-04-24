#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import urllib3
import base64
import os.path
import os
import qqbot
import datetime
import json
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from qqbot.core.util.yaml_util import YamlUtil
from qqbot.model.message import MessageArk, MessageArkKv
from qqbot.model.guild_member import GuildMember, QueryParams
from browser import get_dynamic_screenshot
from bilireq import BiliReq
from dynamic import Dynamic
from util import *
test_config = YamlUtil.read(os.path.join(os.path.dirname(__file__), "config.yaml"))

'''
请注意switch的所有取值类型均为字符串
switch[0] = 是否推送直播, switch[1] = 推送直播时是否@全体成员
switch[2] = 是否推送微博, switch[3] = 推送微博时是否@全体成员
switch[4] = 是否推送动态, switch[5] = 推送动态时是否@全体成员
switch[7] = 最新动态ID,  switch[1] = 最新微博ID
switch的取值，更新操作请参见util.py中的函数
'''

switch = ['1', '1', '1', '0', '1', '0', '1', '0', '0']
ban_switch = 1     # 是否开启消息撤回
hide_switch = True # 消息撤回时是否隐藏灰度条
ban_words = ["word1","word2"] # 会触发消息撤回的关键词

# 微博request的headers, 其中headers["cookie"]需要更新
headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
    'cache-control': 'max-age=0',
    'cookie': 'SINAGLOBAL=2031330909735.9888.1639250218782; ULV=1650530100951:3:1:1:8834643755048.133.1650530100930:1648692874783; UOR=,,www.baidu.com; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WFJ2lzKHZFdfvgLs7-o1dNy5JpX5KMhUgL.FoqfS0eES0M7e022dJLoI7LTUPiaIcvlU-Yt; ALF=1682240796; SSOLoginState=1650704797; SCF=AlkXKtpp1jnRVtF7dFqE3BSrqNRwA9bmbphdizOi1sNoQ5pzajaEd9Xmg8BSu3wPWfHm3WJ3bHfk5D9tAYGOZZA.; SUB=_2A25PZ7HNDeRhGeBL7FET9ynMyD2IHXVsFKQFrDV8PUNbmtAfLXnukW9NRvS2XijaSNMw89bKNbEx1aQtAaz-WZuq; XSRF-TOKEN=dIYxeRi3InnOCeqzALG3uFZ3; WBPSESS=mep8doSfTsnQTvgmx6EFGbHg9ENVyXSU9FM7wFinGSTWWWnjg-0WDHqSUwwRjcF7XImga0OPRtdqrC5zioal1jFGobdNof3WQmN45feJgVXyvL9Fq0VxyP81X1kNEyqgA32SWjn5xdM3gBnrlGGimw==',
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36',
}

# 你的QQ频道ID
gid = ""

# 需要推送的B站用户uid
uid = "1750561" # 此ID为主播"蜜球兔"的id

# 需要推送的微博用户id
wid = "6482128820" # 此ID为主播"蜜球兔"的id

# 事件循环，用于轮询
loop = asyncio.get_event_loop()


# 获取用户最新微博
async def get_weibo():
    global headers
    url = f"https://weibo.com/ajax/statuses/mymblog?uid={wid}&page=1&feature=1"
    response = requests.get(url,headers=headers)
    html = BeautifulSoup(response.content,"html.parser")
    soup = str(html)

    # cookie过期
    if soup.find("新浪通行证") != -1:
        return "error"

    # 提取data字段
    while soup[0] != '{': soup = soup[1:]
    while soup[-1] != '}': soup = soup[:-1] 
    return soup


# 直播、动态、微博推送
async def pusher(message):
    global switch, gid, headers
    role_api = qqbot.GuildRoleAPI(t_token, False)
    msg_api = qqbot.AsyncMessageAPI(t_token, False)
    chl_api = qqbot.ChannelAPI(t_token, False)
    old = 0   # 上轮查询的直播状态
    while True:
        await asyncio.sleep(5)   # 轮询间隔为5s
        headers["cookie"] = await new_cookie()  # 从cookie.txt处更新cookie
        if switch[0] == '1':
            br = BiliReq()
            res = await br.get_live_list([uid])
            res = res[uid]
            new = res["live_status"]
            name = res["uname"]
            title = res["title"]
            if new != old:  # 如果直播状态发生变化
                ark = MessageArk()
                ark.template_id = 37
                if new == 0:
                    ark.kv = [
                        MessageArkKv(key="#PROMPT#", value="下播通知"),
                        MessageArkKv(key="#METATITLE#", value=name+" 下播了"),
                        MessageArkKv(key="#METASUBTITLE#", value="晚安哦"),
                        MessageArkKv(
                            key="#METACOVER#",
                            value="https://kuroko.info/wp-content/goodNight.png",
                        ),
                        MessageArkKv(
                            key="#METAURL#",
                            value="https://kuroko.info/wp-content/video-mitsusa.html",
                        ),
                    ]
                elif new == 1:
                    cover = (res["cover_from_user"] if res["cover_from_user"] else res["keyframe"])
                    http = urllib3.PoolManager()
                    response = http.request('GET',cover)
                    result = response.data
                    with open(os.path.join('dynamics_image',"cover.jpg"),'wb') as f:
                        f.write(result)
                    day = datetime.datetime.now().strftime('%Y-%m-%d')
                    os.system("scp dynamics_image/cover.jpg root@106.15.1.98:/home/www/htdocs/wp-content/cover-"+uid+"-"+day+".jpg")
                    ark.kv = [
                        MessageArkKv(key="#PROMPT#", value="开播提醒"),
                        MessageArkKv(key="#METATITLE#", value=name+" 正在直播"),
                        MessageArkKv(key="#METASUBTITLE#", value=title),
                        MessageArkKv(
                            key="#METACOVER#",
                            value="https://kuroko.info/wp-content/cover-"+uid+"-"+day+".jpg",
                        ),
                        MessageArkKv(
                            key="#METAURL#",
                            value="https://kuroko.info/wp-content/link-mitsusa.html",
                        ),
                    ]
                    if switch[1] == '1':
                        send = qqbot.MessageSendRequest(content="@everyone 兔兔正在直播", msg_id=message.id)
                        await msg_api.post_message("5604103", send)
                send = qqbot.MessageSendRequest(content="", ark=ark, msg_id=message.id)
                await msg_api.post_message(message.channel_id, send)
            old = new
        if switch[2] == '1':
            soup = await get_weibo()
            if soup == "error":  # error则提取用户更新cookie
                send = qqbot.MessageSendRequest(content="请更新cookie!", msg_id=message.id)
                await msg_api.post_message(message.channel_id, send)
            else:
                weibos = json.loads(soup)
                weibo = weibos['data']['list'][0]
                if weibo['mblogid'] != switch[7]:
                    await update("last_weibo", weibo['mblogid'])
                    switch[7] = weibo['mblogid']
                    d = {"Jan":"01","Feb":"02","Mar":"03","Apr":"04",
                    "May":"05","Jan":"06","Jul":"07","Aug":"08",
                    "Sep":"09","Oct":"10","Nov":"11","Dec":"12"}
                    phone = weibo["source"]
                    time = weibo["created_at"].split() 
                    name = weibo['user']['screen_name']
                    url = weibo['user']['profile_image_url']
                    phone = "iPhone XR"
                    text = "[微博 @"+name+"]"+"\n["+time[5]+"-"+d[time[1]]+"-"+time[2]+" "+time[3]+" by "+phone+"]\n\n"
                    text += weibo['text_raw']+"\n\n"+"https://kuroko.info/wp-content/weibo-mitsusa.html"
                    cmd = "wget -O /home/ubuntu/mitsusa/dynamics_image/weibo.jpg \"%s\""%url
                    os.system(cmd)
                    os.system("scp dynamics_image/weibo.jpg root@106.15.1.98:/home/www/htdocs/wp-content/weibo.jpg")
                    url = "https://kuroko.info/wp-content/weibo.jpg"
                    send = qqbot.MessageSendRequest(content=text, image=url,  msg_id = message.id)
                    await msg_api.post_message(message.channel_id, send)

        if switch[4] == '1':
            br = BiliReq()
            dynamics = (await br.get_user_dynamics(uid)).get('cards', [])
            dynamic = Dynamic(dynamics[0])
            await dynamic.format()
            if str(dynamic.id) != switch[6]:
                await update("last_dynamic",str(dynamic.id))
                switch[6] = dynamic.id
                image = await get_dynamic_screenshot(dynamic.url)
                with open(os.path.join('dynamics_image',"dynamic.jpg"),'wb') as f:
                    f.write(image)
                os.system("scp dynamics_image/dynamic.jpg root@106.15.1.98:/home/www/htdocs/wp-content/dynamic.jpg")
                url = "https://kuroko.info/wp-content/dynamic.jpg"
                send = qqbot.MessageSendRequest(content=dynamic.message, image=url, msg_id=message.id)
                await msg_api.post_message(message.channel_id, send)


async def _message_handler(event, message: qqbot.Message):
    global switch, ban_switch, loop, hide_switch, ban_words, gid, headers
    role_api = qqbot.GuildRoleAPI(t_token, False)
    msg_api = qqbot.AsyncMessageAPI(t_token, False)
    chl_api = qqbot.ChannelAPI(t_token, False)
    mem_api = qqbot.GuildMemberAPI(t_token, False)

    # log information
    qqbot.logger.info("event %s" % event + ",receive message %s" % message.content)
    
    cmds = message.content.split()
    size = len(cmds)

    # default reply
    error = qqbot.MessageSendRequest("指令有误，使用'/帮助'查看指令格式哦~",message.id)

    if size == 1:
        send = qqbot.MessageSendRequest("你好，我是兔宝！使用'/帮助'命令可以查看使用说明哦~",message.id)
        await msg_api.post_message(message.channel_id, send)
    elif cmds[1] == "/启动" and size == 2:
        caller = message.author.id
        caller = mem_api.get_guild_member(message.guild_id, caller)
        if '2' in caller.roles or '4' in caller.roles:
            switch = await data_init()
            ban_words = await words_init()
            if len(switch) == 0:
                switch = ['1', '1', '1', '0', '1', '0', '1', '1']
            headers["cookie"] = await new_cookie()
            send = qqbot.MessageSendRequest("启动成功~",message.id)
            await msg_api.post_message(message.channel_id, send)
            loop.run_until_complete(await pusher(message))

    elif cmds[1] == "/查询配置" and size == 2:
        caller = message.author.id
        caller = mem_api.get_guild_member(message.guild_id, caller)
        if '2' in caller.roles or '4' in caller.roles:
            L = [0 for i in range(8)]
            for i in range(6):
                if switch[i] == '1': L[i] = "开"
                else: L[i] = "关"
            if ban_switch: L[6] = "开"
            else: L[6] = "关"

            if hide_switch: L[7] = "开"
            else: L[7] = "关"
            send = qqbot.MessageSendRequest("当前配置:\
            \n-推送直播: %s, @全体: %s\
            \n-推送微博: %s, @全体: %s\
            \n-推送动态: %s, @全体: %s\
            \n-消息撤回: %s,  灰条: %s"%(L[0],L[1],L[2],L[3],L[4],L[5],L[6],L[7]),message.id)
            await msg_api.post_message(message.channel_id, send)

    elif cmds[1] == "/帮助" and size == 2:
        send = qqbot.MessageSendRequest(content="命令列表:\
            \n-帮助 : 查看所有命令\
            \n-兔兔动态 X : 获取兔兔最近X条动态\
            \n-兔兔微博 X : 获取兔兔最近X条微博\
            \n-直播状态 : 获取兔兔当前直播状态\
            \n-领取身份 : 在<#你的子频道id>输入获取哦\
            \n-以下为管理员命令\
            \n-启动 : 初始化数据并启动 \
            \n-推送直播 A B : A=0表示关  \
            \n-推送微博 A B : A=1表示开\
            \n-推送动态 A B : B=1表示@全体\
            \n-消息撤回 A B : B=1表示显示撤回\
            \n-查询禁词 : 显示禁词列表\
            \n-增加禁词 : 增加禁词\
            \n-查询配置 : 显示当前服务开关\
            ", msg_id=message.id)
        await msg_api.post_message(message.channel_id, send)

    elif cmds[1] == "/兔兔动态":
        if size == 2:
            count = 1
        elif size == 3 and cmds[2].isnumeric() and 6 > int(cmds[2]) > 0:
            count = int(cmds[2])
        else:
            count = 404
            await msg_api.post_message(message.channel_id, error)

        if count != 404:
            br = BiliReq()
            dynamics = (await br.get_user_dynamics(uid)).get('cards', [])
            
            for i in range(count):
                dynamic = Dynamic(dynamics[i])
                await dynamic.format()
                image = await get_dynamic_screenshot(dynamic.url)
                with open(os.path.join('dynamics_image',"dynamic.jpg"),'wb') as f:
                    f.write(image)
                os.system("scp dynamics_image/dynamic.jpg root@106.15.1.98:/home/www/htdocs/wp-content/dynamic.jpg")
                url = "https://kuroko.info/wp-content/dynamic.jpg"
                send = qqbot.MessageSendRequest(content=dynamic.message, image=url, msg_id=message.id)
                await msg_api.post_message(message.channel_id, send)
    elif cmds[1] == "/兔兔微博":
        if size == 2:
            count = 1
        elif size == 3 and cmds[2].isnumeric() and 4 > int(cmds[2]) > 0:
            count = int(cmds[2])
        else:
            count = 404
            await msg_api.post_message(message.channel_id, error)
        if count != 404:
            soup = await get_weibo()
            if soup == "error":
                send = qqbot.MessageSendRequest(content="微博cookie已过期，请等待管理员更新", msg_id = message.id)
                await msg_api.post_message(message.channel_id, send)
                send = qqbot.MessageSendRequest(content="请更新cookie!", msg_id = message.id)
                await msg_api.post_message(message.channel_id, send)
                return 
            weibos = json.loads(soup)
            weibos = weibos['data']['list']
            for i in range(count):
                d = {"Jan":"01","Feb":"02","Mar":"03","Apr":"04",
                "May":"05","Jan":"06","Jul":"07","Aug":"08",
                "Sep":"09","Oct":"10","Nov":"11","Dec":"12"}
                weibo = weibos[i]
                phone = weibo["source"]
                time = weibo["created_at"].split() 
                name = weibo['user']['screen_name']
                url = weibo['user']['profile_image_url']
                phone = "iPhone XR"
                text = "["+name+"]"+"\n["+time[5]+"-"+d[time[1]]+"-"+time[2]+" "+time[3]+" by "+phone+"]\n\n"
                text += weibo['text_raw']+"\n\n"+"https://kuroko.info/wp-content/weibo-mitsusa.html"
                cmd = "wget -O /home/ubuntu/mitsusa/dynamics_image/weibo.jpg \"%s\""%url
                os.system(cmd)
                os.system("scp dynamics_image/weibo.jpg root@106.15.1.98:/home/www/htdocs/wp-content/weibo.jpg")
                url = "https://kuroko.info/wp-content/weibo.jpg"
                #print("text = ",text)
                send = qqbot.MessageSendRequest(content=text, image=url, msg_id=message.id)
                await msg_api.post_message(message.channel_id, send)

    elif cmds[1] == "/直播状态" and size == 2:
        br = BiliReq()
        res = await br.get_live_list([uid])
        res = res[uid]
        name = res["uname"]
        title = res["title"]
        status = int(res["live_status"])
        ark = MessageArk()
        ark.template_id = 37
        
        if status == 0:
            ark.kv = [
                MessageArkKv(key="#PROMPT#", value="下播通知"),
                MessageArkKv(key="#METATITLE#", value=name+" 下播了"),
                MessageArkKv(key="#METASUBTITLE#", value="晚安哦"),
                MessageArkKv(
                    key="#METACOVER#",
                    value="https://kuroko.info/wp-content/goodNight.png",
                ),
                MessageArkKv(
                    key="#METAURL#",
                    value="https://kuroko.info/wp-content/video-mitsusa.html",
                ),
            ]

        elif status == 1:
            cover = (res["cover_from_user"] if res["cover_from_user"] else res["keyframe"])
            http = urllib3.PoolManager()
            response = http.request('GET',cover)
            result = response.data
            with open(os.path.join('dynamics_image',"cover.jpg"),'wb') as f:
                f.write(result)
            day = datetime.datetime.now().strftime('%Y-%m-%d')
            os.system("scp dynamics_image/cover.jpg root@106.15.1.98:/home/www/htdocs/wp-content/cover-"+uid+"-"+day+".jpg")
            ark.kv = [
                MessageArkKv(key="#PROMPT#", value="开播提醒"),
                MessageArkKv(key="#METATITLE#", value=name+" 正在直播"),
                MessageArkKv(key="#METASUBTITLE#", value=title),
                MessageArkKv(
                    key="#METACOVER#",
                    value="https://kuroko.info/wp-content/cover-"+uid+"-"+day+".jpg",
                ),
                MessageArkKv(
                    key="#METAURL#",
                    value="https://kuroko.info/wp-content/link-mitsusa.html",
                ),
            ]
        send = qqbot.MessageSendRequest(content="", ark=ark, msg_id=message.id)
        await msg_api.post_message(message.channel_id, send)

    elif cmds[1] == "/推送直播" and size == 4 and (cmds[2] in ['0','1']) and (cmds[3] in ['0','1']):
        await update("live", cmds[2], cmds[3])
        switch[0],switch[1] = cmds[2], cmds[3]
        reply = "已设置推送直播: "
        if cmds[2] == '1': reply += "开，"
        else: reply += "关， "
        if cmds[3] == '1': reply += "@全体: 开"
        else: reply += "@全体: 关"
        send = qqbot.MessageSendRequest(reply,message.id)
        await msg_api.post_message(message.channel_id, send)

    elif cmds[1] == "/推送微博" and size == 4 and (cmds[2] in ['0','1']) and (cmds[3] in ['0','1']):
        await update("weibo", cmds[2], cmds[3])
        switch[2],switch[3] = cmds[2], cmds[3]
        reply = "已设置推送微博: "
        if cmds[2] == '1': reply += "开，"
        else: reply += "关， "
        if cmds[3] == '1': reply += "@全体: 开"
        else: reply += "@全体: 关"
        send = qqbot.MessageSendRequest(reply,message.id)
        await msg_api.post_message(message.channel_id, send)

    elif cmds[1] == "/推送动态" and size == 4 and (cmds[2] in ['0','1']) and (cmds[3] in ['0','1']):
        await update("dynamic", cmds[2], cmds[3])
        switch[4],switch[5] = cmds[2], cmds[3]
        reply = "已设置推送动态: "
        if cmds[2] == '1': reply += "开，"
        else: reply += "关， "
        if cmds[3] == '1': reply += "@全体: 开"
        else: reply += "@全体: 关"
        send = qqbot.MessageSendRequest(reply,message.id)
        await msg_api.post_message(message.channel_id, send)
    elif cmds[1] == "/消息撤回" and size == 4 and (cmds[2] in ['0','1']) and (cmds[3] in ['0','1']):
        reply = "已设置消息撤回: "
        if cmds[2] == '0': 
            ban_switch = 0
            reply += "关， "
        else: 
            ban_switch = 1
            reply += "开，"
        if cmds[3] == '0': 
            hide_switch = False
            reply += "隐藏灰条: 关"
        else: 
            hide_switch = True
            reply += "隐藏灰条: 开"
        send = qqbot.MessageSendRequest(reply,message.id)
        await msg_api.post_message(message.channel_id, send)
    elif cmds[1] == "/查询禁词" and size == 2:
        reply = "当前禁词:"
        for e in ban_words:
            reply += "\n-"+e
        send = qqbot.MessageSendRequest(reply,message.id)
        await msg_api.post_message(message.channel_id, send)

    elif cmds[1] == "/增加禁词" and size == 3:
        if cmds[2] in ban_words:
            send = qqbot.MessageSendRequest("该禁词已存在",message.id)
            await msg_api.post_message(message.channel_id, send)
        else:
            ban_words.append(cmds[2])
            await words_add(cmds[2])
            send = qqbot.MessageSendRequest("添加成功",message.id)
            await msg_api.post_message(message.channel_id, send)
    elif cmds[1] == "/领取身份" and size == 2:
        send = qqbot.MessageSendRequest("请前往<#5604181>频道输入身份组名领取哦",message.id)
        await msg_api.post_message(message.channel_id, send)
    elif cmds[1] == "debug":
        caller = message.author.id
        caller = mem_api.get_guild_member(message.guild_id, caller)
        if '2' in caller.roles or '4' in caller.roles:
            if cmds[2] == "message":
                send = qqbot.MessageSendRequest("Message Info:\
                \n-Guild ID: %s\
                \n-Channel ID: %s\
                \n-Message ID: %s\
                \n-User ID: %s"%(message.guild_id, message.channel_id,message.id,message.author.id),msg_id=message.id)
                await msg_api.post_message(message.channel_id, send)
            if cmds[2] == "welcome":
                send = qqbot.MessageSendRequest(content = "@Kuroko 欢迎第1位小月兔加入兔频!\
                \n我是兔宝，@我可以了解我的使用方法哦，\
                \n<#5604181>频道可以领取身份，\
                \n<#5604103>频道会进行直播通知，\
                \n<#5604144>频道会进行动态推送，\
                \n更多详情请阅读全局公告了解~",msg_id=message.id)
                await msg_api.post_message(message.channel_id,send)
            if cmds[2] == "find":
                try:
                    member = mem_api.get_guild_member(gid, cmds[3])
                    send = qqbot.MessageSendRequest("此人为："+member.nick,message.id)
                    await msg_api.post_message(message.channel_id, send)
                except:
                    send = qqbot.MessageSendRequest("查无此人",message.id)
                    await msg_api.post_message(message.channel_id, send)

    elif message.channel_id == "你的身份组子频道id" and size == 2:
        guild_roles = role_api.get_guild_roles(message.guild_id)
        roles = guild_roles.roles
        role_dict = {}
        for role in roles:
            role_dict[role.name] = role.id
        if cmds[1] not in role_dict:
            send = qqbot.MessageSendRequest("<@%s> '%s'身份尚未创建哦"%(message.author.id,cmds[1]),message.id)
        elif cmds[1] in ["创建者","管理员","子频道管理员","普通成员"]:
            send = qqbot.MessageSendRequest("<@%s> '%s'身份无权限获取"%(message.author.id,cmds[1]),message.id)
        elif cmds[1] in ["舰长"]:
            send = qqbot.MessageSendRequest("<@%s> '%s'身份请联系管理员获取"%(message.author.id,cmds[1]),message.id)
        else:
            channel = chl_api.get_channel(message.channel_id)
            result = role_api.create_guild_role_member(message.guild_id, role_dict[cmds[1]], message.author.id, channel)
            send = qqbot.MessageSendRequest("<@%s> 已添加 %s"%(message.author.id,cmds[1]),message.id)
        await msg_api.post_message(message.channel_id, send)
    else:
        await msg_api.post_message(message.channel_id, error)


async def _guild_member_handler(event, guild_member: GuildMember): 
    global gid
    if event == "GUILD_MEMBER_ADD":
        user_id = guild_member.user.id
        msg_api = qqbot.AsyncMessageAPI(t_token, False)
        guild_api = qqbot.GuildAPI(t_token, False)
        mem_api = qqbot.GuildMemberAPI(t_token, False)
        guild = guild_api.get_guild(gid)
        member_count = guild.member_count
        try:
            member = mem_api.get_guild_member(gid, user_id)
            test = member.nick
            send = qqbot.MessageSendRequest(content="<@%s>欢迎第%s位小月兔加入兔频!\
            \n我是兔宝，@我可以了解我的使用方法哦，\
            \n<#5604181>频道可以领取身份，\
            \n<#5604103>频道会进行直播通知，\
            \n<#5604144>频道会进行动态推送，\
            \n更多详情请阅读全局公告了解哦~"%(guild_member.user.id,member_count))
            await msg_api.post_message('''<你的推送子频道id>''', send)
        except:
            print("来了个陌生人")

        #await msg_api.post_message("5544453", send)
        #qqbot.logger.info("有人加入了频道")

async def _recall_handler(event, message: qqbot.Message):
    role_api = qqbot.GuildRoleAPI(t_token, False)
    msg_api = qqbot.AsyncMessageAPI(t_token, False)
    chl_api = qqbot.ChannelAPI(t_token, False)
    mem_api = qqbot.GuildMemberAPI(t_token, False)
    global ban_switch, hide_switch

    if not ban_switch:
        return 
    caller = message.author.id
    caller = mem_api.get_guild_member(message.guild_id, caller)
    if '2' in caller.roles or '4' in caller.roles:
        return 
    for word in ban_words:
        if message.content.find(word) != -1:
            await msg_api.recall_message(message.channel_id, message.id, hide_switch)

if __name__ == "__main__":
    # async的异步接口的使用示例
    t_token = qqbot.Token(test_config["token"]["appid"], test_config["token"]["token"])
    qqbot_recall_handler = qqbot.Handler(
        qqbot.HandlerType.MESSAGE_EVENT_HANDLER, _recall_handler
    )
    qqbot_handler = qqbot.Handler(
        qqbot.HandlerType.AT_MESSAGE_EVENT_HANDLER, _message_handler
    )   
    qqbot_guild_member_handler = qqbot.Handler(
        qqbot.HandlerType.GUILD_MEMBER_EVENT_HANDLER, _guild_member_handler
    )
    qqbot.async_listen_events(t_token, False, qqbot_recall_handler, qqbot_handler, qqbot_guild_member_handler)
    
