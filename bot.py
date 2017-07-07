#!/usr/bin/env python3
# coding: utf-8

from wxpy import *
from config import *
import re
from wxpy.utils import start_new_thread
import time
import random
import os
import platform
'''
使用 cache 来缓存登陆信息，同时使用控制台登陆
'''
console_qr=(False if platform.system() == 'Windows' else True)
bot = Bot('bot.pkl', console_qr=console_qr)
bot.messages.max_history = 0

'''
开启 PUID 用于后续的控制
'''
bot.enable_puid('wxpy_puid.pkl')


'''
邀请信息处理
'''
rp_new_member_name = (
    re.compile(r'^"(.+)"通过'),
    re.compile(r'邀请"(.+)"加入'),
)

'''
管理员群及被管理群初始化
'''
def fresh_groups():
    global groups, admin_group
    # 格式化被管理群 Groups
    try:
        groups = list(filter(lambda x: x.name.startswith(group_prefix), bot.groups(update = True).search(group_prefix)))
    except:
        print("查找被管理群出错！请检查被管理群前缀（group_prefix）是否配置正确")
        quit()

    # 格式化管理员群 Admin_group
    try:
        admin_group = ensure_one(bot.groups(update = True).search(admin_group_name))
    except:
        print("查找管理员群出错！请检查管理群群名（admin_group_name）是否配置正确")
        print("现将默认设置为只有本帐号为管理员")
        admin_group = None

fresh_groups()

# 远程踢人命令: 移出 @<需要被移出的人>
rp_kick = re.compile(r'^(?:移出|移除|踢出|拉黑)\s*@(.+?)(?:\u2005?\s*$)')


# 下方为函数定义

def get_time():
    return str(time.strftime("%Y-%m-%d %H:%M:%S"))

def replyPicker(category):
    collegeAnthem = [
    '悠悠珠江文脉长',
    '诸贤会同意气昂',
    '筚路蓝缕创吾校',
    '华夏教育谱新章',
    '本生命之源，根文化之壤',
    '启德性之门，明智慧之光',
    '师生家国齐努力',
    '博文雅志筑梦想',
    '浩浩南海通八方',
    '凤凰展翼天际翔',
    '兼容并蓄纳百川',
    '情系中华怀万邦',
    '聚四方学子，育国家栋梁',
    '容中西思想，通古今文章',
    '躬身服务彰仁爱',
    '真知笃行创辉煌'
    ]
    majorRequiredCourses = [
    'COMP1003 Computer Organisation 计算机组织',
    'COMP1013 Structured Programming 结构化编程',
    'COMP2003 Data Structures and Algorithms 数据结构和算法',
    'COMP2013 Object-Oriented Programming 面向对象编程',
    'COMP2023 Software Development Workshop I 软件开发工作坊 I',
    'COMP3003 Data Communications and Networking 数据通讯和网络',
    'COMP3013 Database Management Systems 数据库管理系统',
    'COMP3023 Design and Analysis of Algorithms 算法设计和分析',
    'COMP3033 Operating Systems 操作系统',
    'COMP3043 Software Development Workshop II 软件开发工作坊 II',
    'COMP3053 Software Development Workshop III 软件开发工作坊 III',
    'COMP3063 Software Engineering 软件工程',
    'COMP3173 Compiler Construction 编译原理',
    'COMP4004 Final Year Project I (COMP) 毕业论文 I',
    'MATH1003 Linear Algebra 线性代数',
    'MATH2003 Discrete Structures 离散结构 '
    ]
    majorElectiveCourses = [
    'COMP3083 Numerical Computation 数值计算',
    'COMP4003 Theory of Computation 计算理论',
    'COMP4023 Computer and Network Security 计算机和网络安全',
    'COMP4043 Data Mining and Knowledge Discovery 数据挖掘与知识发现',
    'COMP4053 Database System Implementation 数据库系统开发',
    'COMP4063 Digital Media Computing 数字媒体计算',
    'COMP4073 Distributed Computing Systems 分布式计算系统',
    'COMP4083 E-technology Architectures, Tools and Applications E-技术结构、 工具和应用',
    'COMP4093 Internet and the World Wide Web 互联网及万维网',
    'COMP4103 Artificial Intelligence and Machine Learning 人工智能和机器学习',
    'COMP4123 Information Retrieval and Search Engine 信息检索及搜索引擎',
    'COMP4033 Computer Graphics 计算机图形',
    'COMP4113 Computer Vision and Pattern Recognition 计算机视觉和模式识别',
    'COMP3073 Introduction to Robotics 机器人技术导论',
    'COMP3103 Design Patterns 设计模式',
    'COMP3123 Software Testing 软件测试',
    'COMP3163 Mobile Application Development 移动平台应用开发',
    'COMP3183 Financial Computing 金融计算',
    'COMP4003 Theory of Computation 计算理论',
    'COMP4005 Final Year Project II (COMP)* 毕业论文 II',
    'COMP4133 System Analysis and Design 系统分析与设计',
    'MATH1093 Speaking of Mathematics 数学漫谈'
    ]
    replyQueue = [majorElectiveCourses,majorRequiredCourses,collegeAnthem]
    replyQueueChinese = ['选修专业课一门：','必修专业课一门：','校歌一句：']
    final = '\n' + str(replyQueueChinese[category]) + str(random.choice(replyQueue[category]))
    return final

def reply_by_keyword(msg):
    for reply, keywords in kw_replies.items():
        for kw in keywords:
            if kw in msg.text.lower():
                msg.reply(reply + str(get_time()) + replyPicker(random.randint(0,2)))
                return reply

'''
机器人消息提醒设置
'''
alert_level = 30 # DEBUG: 10, INFO: 20, WARNING: 30, ERROR: 40, FATAL: 50
if alert_group:
    try:
        alert_receiver = ensure_one(bot.groups().search(alert_group))
    except:
        print("警报群设置有误，请检查群名是否存在且唯一")
        alert_receiver = bot.file_helper
else:
    alert_receiver = bot.file_helper
logger = get_wechat_logger(alert_receiver, str(alert_level))
logger.error(str("机器人登陆成功！"+ get_time()))

'''
重启机器人
'''
def _restart():
    os.execv(sys.executable, [sys.executable] + sys.argv)

'''
状态汇报
'''
def status():
    status_text = get_time() + " 机器人目前在线,共有好友 【" + str(len(bot.friends())) + "】 群 【 " + str(len(bot.groups())) + "】"
    return status_text

'''
定时报告进程状态
'''
def heartbeat():
    while bot.alive:
        time.sleep(3600)
        # noinspection PyBroadException
        try:
            logger.error(status())
        except ResponseError as e:
            if 1100 <= e.err_code <= 1102:
                logger.critical('LCBot offline: {}'.format(e))
                _restart()

start_new_thread(heartbeat)

'''
条件邀请
'''
def condition_invite(user):
    if user.sex == 2:
        female_groups = bot.groups().search(female_group)[0]
        try:
            female_groups.add_members(user, use_invitation=True)
            pass
        except:
            pass
    if (user.province in city_group.keys() or user.city in city_group.keys()):
        try:
            target_city_group = bot.groups().search(city_group[user.province])[0]
            pass
        except:
            target_city_group = bot.groups().search(city_group[user.city])[0]
            pass
        try:
            if user not in target_city_group:
                target_city_group.add_members(user, use_invitation=True)
        except:
            pass

'''
判断消息发送者是否在管理员列表
'''
def from_admin(msg):
    """
    判断 msg 中的发送用户是否为管理员
    :param msg:
    :return:
    """
    if not isinstance(msg, Message):
        raise TypeError('expected Message, got {}'.format(type(msg)))
    from_user = msg.member if isinstance(msg.chat, Group) else msg.sender
    return from_user in admin_group.members if admin_group else from_user == bot.self

'''
远程踢人命令
'''
def remote_kick(msg):
    if msg.type is TEXT:
        match = rp_kick.search(msg.text)
        if match:
            name_to_kick = match.group(1)

            if not from_admin(msg):
                if not silence_mode:
                    return 'ANBUL 大佬才能命令我，你还不够格 @{}'.format(msg.member.name)
                else:
                    return

            member_to_kick = ensure_one(list(filter(
                lambda x: x.name == name_to_kick, msg.sender.members)))
            if member_to_kick  == bot.self:
                return '这个群还需要我，无法移出 @{}'.format(member_to_kick.name)
            if member_to_kick in admin_group.members:
                return '无法移出 @{}'.format(member_to_kick.name)

            logger.error(get_time() + str(" 【"+member_to_kick.name + "】 被 【"+msg.member.name+"】 移出 【" + msg.sender.name+"】"))
            try:
                member_to_kick.set_remark_name("[黑名单]-"+get_time())
            except:
                logger.error(get_time() + str("为 【" + member_to_kick.name + "】 设置黑名单时出错"))

            if member_to_kick in msg.sender:
                msg.sender.remove_members(member_to_kick)
                kick_info = '成功移出 @{}'.format(member_to_kick.name)
            else:
                kick_info = '@{} 已不在群中'.format(member_to_kick.name)

            for ready_to_kick_group in  groups:
                if member_to_kick in ready_to_kick_group:
                    ready_to_kick_group.remove_members(member_to_kick)
                    ready_to_kick_group.send(str("【" + member_to_kick.name + "】 因其在 【" + msg.sender.name + "】 的行为被系统自动移出"))
                    logger.error(get_time()+ str("【"+member_to_kick.name + "】 被系统自动移出 " +  ready_to_kick_group.name))

            return kick_info


'''
邀请消息处理
'''
def get_new_member_name(msg):
    # itchat 1.2.32 版本未格式化群中的 Note 消息
    from itchat.utils import msg_formatter
    msg_formatter(msg.raw, 'Text')

    for rp in rp_new_member_name:
        match = rp.search(msg.text)
        if match:
            return match.group(1)

'''
定义邀请用户的方法。
按关键字搜索相应的群，如果存在相应的群，就向用户发起邀请。
'''
def invite(user, keyword):
    from random import randrange
    group = bot.groups().search(keyword_of_group[keyword])
    if len(group) > 0:
        for i in range(0, len(group)):
            if user in group[i]:
                content = "您已经加入了 {} [微笑]".format(group[i].nick_name)
                user.send(content)
                return
        if len(group) == 1:
            target_group = group[0]
        else:
            index = randrange(len(group))
            target_group = group[index]
        try:
            target_group.add_members(user, use_invitation=True)
        except:
            user.send("邀请错误！机器人邀请好友进群已达当日限制。请等待管理员手动邀请")
    else:
        user.send("该群状态有误，请等待管理员手动邀请")

# 下方为消息处理

'''
处理加好友请求信息。
如果验证信息文本是字典的键值之一，则尝试拉群。
'''
@bot.register(msg_types=FRIENDS)
def new_friends(msg):
    user = msg.card.accept()
    if msg.text.lower() in keyword_of_group.keys():
        invite(user, msg.text.lower())
    else:
        user.send(invite_text)

@bot.register(Friend, msg_types=TEXT)
def exist_friends(msg):
    if msg.sender.name.find("黑名单") != -1:
        return "您已被拉黑！"
    else:
        if msg.text.lower() in keyword_of_group.keys():
            invite(msg.sender, msg.text.lower())
        else:
            return invite_text


# 管理群内的消息处理
@bot.register(groups, except_self=False)
def wxpy_group(msg):
    ret_msg = remote_kick(msg)
    if ret_msg:
        return ret_msg
    elif msg.is_at and not silence_mode:
        reply_by_keyword(msg)


@bot.register(groups, NOTE)
def welcome(msg):
    name = get_new_member_name(msg)
    if name and not silence_mode:
        return welcome_text.format(name)

@bot.register(alert_receiver, except_self=False)
def alert_command(msg):
    if from_admin(msg):
        if msg.text == "状态":
            return status()
        elif msg.text == "重启":
            _restart()
        elif msg.text == "刷新":
            fresh_groups()
            return "群信息已更新，现有被管理群 【{}】，管理员 【{}】".format(len(groups), len(admin_group) if admin_group else 1)

embed()
