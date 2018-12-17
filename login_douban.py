import json
import time
import requests
from selenium import webdriver

class YDMHttp:
    apiurl = 'http://api.yundama.com/api.php'
    username = ''
    password = ''
    appid = ''
    appkey = ''

    def __init__(self, username, password, appid, appkey):
        self.username = username
        self.password = password
        self.appid = str(appid)
        self.appkey = appkey

    def request(self, fields, files=[]):
        response = self.post_url(self.apiurl, fields, files)
        response = json.loads(response)
        return response

    def balance(self):
        data = {'method': 'balance', 'username': self.username, 'password': self.password, 'appid': self.appid,
                'appkey': self.appkey}
        response = self.request(data)
        if (response):
            if (response['ret'] and response['ret'] < 0):
                return response['ret']
            else:
                return response['balance']
        else:
            return -9001

    def login(self):
        data = {'method': 'login', 'username': self.username, 'password': self.password, 'appid': self.appid,
                'appkey': self.appkey}
        response = self.request(data)
        if (response):
            if (response['ret'] and response['ret'] < 0):
                return response['ret']
            else:
                return response['uid']
        else:
            return -9001

    def upload(self, filename, codetype, timeout):
        data = {'method': 'upload', 'username': self.username, 'password': self.password, 'appid': self.appid,
                'appkey': self.appkey, 'codetype': str(codetype), 'timeout': str(timeout)}
        file = {'file': filename}
        response = self.request(data, file)
        if (response):
            if (response['ret'] and response['ret'] < 0):
                return response['ret']
            else:
                return response['cid']
        else:
            return -9001

    def result(self, cid):
        data = {'method': 'result', 'username': self.username, 'password': self.password, 'appid': self.appid,
                'appkey': self.appkey, 'cid': str(cid)}
        response = self.request(data)
        return response and response['text'] or ''

    def decode(self, filename, codetype, timeout):
        cid = self.upload(filename, codetype, timeout)
        if (cid > 0):
            for i in range(0, timeout):
                result = self.result(cid)
                if (result != ''):
                    return cid, result
                else:
                    time.sleep(1)
            return -3003, ''
        else:
            return cid, ''

    def post_url(self, url, fields, files=[]):
        res = requests.post(url, files=files, data=fields)
        return res.text

username = 'whoarewe'
password = 'zhoudawei123'
appid = 4283
appkey = '02074c64f0d0bb9efb2df455537b01c3'
codetype = 3007
timeout = 60


def indetify(response_content):
    if (username == 'username'):
        print('请设置好相关参数再测试')
    else:
        yundama = YDMHttp(username, password, appid, appkey)
        uid = yundama.login()
        balance = yundama.balance()
        cid, result = yundama.decode(response_content, codetype, timeout)
        print('cid: %s, result: %s' % (cid, result))
        return result

url = "https://www.douban.com/"

driver = webdriver.Chrome()
driver.get(url)
driver.find_element_by_id("form_email").send_keys("itmeng2018@163.com")
driver.find_element_by_id("form_password").send_keys("mengfei123")
try:
    ver_code_url = driver.find_element_by_id("captcha_image").get_attribute('src')
    print(ver_code_url)
    ver_content = requests.get(ver_code_url).content
    with open("ver_code.png", 'wb') as f:
        f.write(ver_content)
    var_code = indetify(ver_content)
    driver.find_element_by_id("captcha_field").send_keys(var_code)
    time.sleep(3)
except Exception as e:
    print('不存在验证码')
driver.find_element_by_class_name('bn-submit').click()
cookies = {i['name']: i['value'] for i in driver.get_cookies()}
print('登录成功')
print('cookies', cookies)
time.sleep(3)
driver.quit()
