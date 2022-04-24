# Mitsusa-Robot
一款基于QQ开放平台提供的API开发的QQ频道管家机器人

# 简介
应用于B站主播[蜜球兔](https://space.bilibili.com/1750561/?spm_id_from=333.999.0.0)的QQ频道，支持将B站UP主的直播与动态信息，微博博主的最新微博推送至QQ频道

# 功能展示
+ 可以主动获取目标用户的直播状态、微博、动态
![avatar](https://github.com/SuperKuroko/Mitsusa-Robot/blob/main/git_image/help.jpg)
+ 当目标用户微博更新时，自动推送至指定子频道
![avatar](https://github.com/SuperKuroko/Mitsusa-Robot/blob/main/git_image/weibo.jpg)
+ 用目标用户开播、下播是，自动推送ark消息至指定子频道(点击即可直接跳转直播间)
![avatar](https://github.com/SuperKuroko/Mitsusa-Robot/blob/main/git_image/live.jpg)
+ 当目标用户B站动态更新时，会通过playwright库模拟一次浏览器截图，将截图推送至指定子频道
![avatar](https://github.com/SuperKuroko/Mitsusa-Robot/blob/main/git_image/dynamic.jpg)
+ 可以设置关键词列表，当频道成员发言包含关键词时，机器人将自动撤回消息
![avatar](https://github.com/SuperKuroko/Mitsusa-Robot/blob/main/git_image/ban.jpg)
![avatar](https://github.com/SuperKuroko/Mitsusa-Robot/blob/main/git_image/ban_before.jpg)
![avatar](https://github.com/SuperKuroko/Mitsusa-Robot/blob/main/git_image/ban_after.jpg)
+ 当有新成员加入频道时，自动的发送包含子频道跳转超链接的迎新欢迎语
![avatar](https://github.com/SuperKuroko/Mitsusa-Robot/blob/main/git_image/welcome.jpg)
+ 可以自由的对以上功能进行开关、设置是否@全体成员
![avatar](https://github.com/SuperKuroko/Mitsusa-Robot/blob/main/git_image/pusher.jpg)

# 开发框架
+ [qq开放平台](q.qq.com)提供的[Python SDK](https://bot.q.qq.com/wiki/develop/pythonsdk/)
+ [HarukaBot](https://github.com/SK-415/HarukaBot)提供的获取B站request源码

# 文件说明
+ dynamics_image 图片存储文件夹
+ bilireq.py b站动态、直播信息获取
+ browser.py 通过动态url获取其浏览器截图
+ chromium.py playwright组件安装，对于某些操作系统需要先执行此文件
+ config.py 配置文件
+ config.yaml 机器人ID配置文件
+ cookie.txt 填写微博cookie
+ dynamic.py 动态类
+ info.txt 存储功能开关的数据文件
+ main.py 机器人逻辑实现
+ util.py 文件读写相关工具
+ word.txt 关键词列表

# 需要安装的库
+ python 3.7+
+ bs4
+ lxml
+ Pillow
+ playwright
+ python-dateutil
+ PyYAML
+ qq-bot
+ urllib3

# 运行
+ 用bot-id,bot-token填写config.yaml文件
+ 在cookie.txt填写微博cookie
+ 在main.py的全局变量定义处填写频道id(gid)，目标B站id(uid)，目标微博id(wid)，根据需求修改部分channel_id
+ python main.py

# 特别感谢
+ [HarukaBot](https://github.com/SK-415/HarukaBot)提供的框架
+ [cnSchwarzer](https://github.com/cnSchwarzer)在开发过程中提供的帮助
