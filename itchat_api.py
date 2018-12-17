import requests
import itchat

KEY = 'd5591c43fc08471fac90e329bf09e99c'
def get_response(msg):
    # 构发送给服务器的数据包
    apiUrl = 'http://www.tuling123.com/openapi/api'
    data = {
        'key'    : KEY,
        'info'   : msg,
        'userid' : 'wechat-robot',
    }
    try:
        # 捕获get没有取到'text'值时的异常
        r = requests.post(apiUrl, data=data).json()
        return r.get('text')
    except:
        # 将会返回一个None
        return

@itchat.msg_register(itchat.content.TEXT)
def tuling_reply(msg):
    # 设置一个默认回复
    defaultReply = 'I received: ' + msg['Text']
    reply = get_response(msg['Text'])
    # 如果a有内容，返回a，否则返回b
    return reply or defaultReply

# 设置登录方式
# itchat.auto_login(hotReload=True) #热启动方式,//不稳定
itchat.auto_login()
# 保持程序循环运行状态
itchat.run()
