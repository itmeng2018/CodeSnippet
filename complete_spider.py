# -*- coding: utf-8 -*-
import hashlib  # 实现信息摘要, md5
import queue  # 数据结构, 队列
import random
import re
import time
from datetime import datetime
from threading import Thread  # 多线程
from urllib import robotparser  # 解析网站的robots.txt数据
from urllib.parse import urlparse, urljoin, urldefrag  # 解析url

import requests
from retrying import retry  # 装饰器, 实现重试下载

from forge_headers import UserAgent
from mongo_cache import MongoCache


def save_url(html_content, url_str):
    """
    存储下载内容
    :param html_content:
    :param url_str:
    :return:
    """
    md5 = hashlib.md5()
    md5.update(html_content)
    file_path = "./download/" + get_html_name(url_str) + ".html"
    with open(file_path, 'wb') as f:
        f.write(html_content)


def get_html_name(url_str):
    """
    根据url生成文件名
    :param url_str: url
    :return: 从url中截取的文件名
    """
    path = urlparse(url_str).path
    path_array = path.split('/')
    file_name = "".join([i for i in path_array if i != ''])
    # print(file_name)
    if file_name[-5:] == '.html':
        file_name = file_name[:-5]
    if len(file_name) > 14:
        file_name = file_name[-14:]
    return file_name


def extractor_url_lists(html_content):
    """
    抽取网页中的链接
    :param html_content:
    :return: url_lists
    """
    url_regex = re.compile('<a[^>]+href=["\'](.*?)["\']', re.IGNORECASE)
    return url_regex.findall(html_content)


class CrawlerCommon(Thread):
    """
    实现一个通用爬虫, 蕴含基本的爬虫功能, 涉及简单反反爬虫技术
    """

    def __init__(self, init_url):
        super(CrawlerCommon, self).__init__()
        self.seed_url = init_url  # 初始化爬取的种子url
        self.crawler_queue = queue.Queue()  # 使用不同的队列会造成BFS和DFS的效果
        self.crawler_queue.put(init_url)  # 将种子url放入队列
        self.visited = {init_url: 0}  # 初始爬取深度为0
        self.headers = {}  # 设置默认headers
        self.proxies = {}  # 设置默认 proxies
        self.link_regex = '(index|view)'  # 抽取网址的过滤条件
        self.throttle = Throttle(3.0)  # 下载限流器, 3秒
        self.mcache = MongoCache()  # 初始化MongoCache()
        self.filter_keyword_for_url = ''  # 初始化url队列过滤关键字
        self.__max_dep = 2  # 初始化爬虫爬取深度, 默认2

    def get_user_agent(self):
        __ua = UserAgent()
        self.headers = {"User-Agent": __ua.get_headers()}

    def get_proxies(self, url_str):
        """
        获取随机代理值
        :param url_str: url地址
        :return: 随机一个代理, 赋值给self.proxies
        """
        proxies = {
            'http': [
                {'http': 'http://47.52.155.245:80'},
                {'http': 'http://120.236.128.201:8060'},
                {'http': "http://117.191.11.71:80"},
                {'http': "http://116.196.83.125:9999"},
                {'http': "http://39.137.107.98:80"},
            ],
            'https': [
                {'https': "https://106.86.208.98:37729"},
                {'https': "https://220.164.126.62:41146"},
                {'https': "https://60.216.101.46:32868"},
                {'https': "https://123.110.185.95:8888"},
                {'https': "https://122.117.65.107:49335"},
            ]
        }
        if re.match('http', url_str) is None:
            print('ParameterError: The parameter can only be HTTP or HTTPS')
        if re.match('https', url_str) is None:
            model = 'http'
        else:
            model = 'https'
        self.proxies = random.choice(proxies[model])

    def set_max_dep(self, depth):
        """
        设置爬取深度
        :param depth: 深度参数
        :return: 小于0默认1, 否则正常配置
        """
        self.__max_dep = depth if depth > 0 else 1

    @retry(stop_max_attempt_number=3)
    def retry_download(self, url_str, data, method):
        """
        使用装饰器的重试下载类
        :param url_str: 当前爬取url
        :param data: psot请求需要的请求数据
        :param method: 请求方式, 默认GET
        :return: 爬取的页面内容

        """
        if method == "POST":
            result = requests.post(url_str, data=data, headers=self.headers, proxies=self.proxies)
        else:
            result = requests.get(url_str, headers=self.headers, timeout=3, proxies=self.proxies)
            assert result.status_code == 200  # 断言: 请求是否成功
        return result.content

    def download(self, url_str, data=None, method="GET"):
        """
        真正的下载类
        :param url_str: http://www.xxxx.com/xxxx
        :param data: post请求需求的数据包
        :param method: 请求方式
        :param proxies: 设置代理
        :return: 响应内容
        """
        print('检测url: ', url_str)
        try:
            # 捕获 retry_download 异常, 结合断言
            result = self.retry_download(url_str, data, method)
        except Exception as e:
            print(e)
            result = None
        return result

    def nomalize(self, url_str):
        """
        补全下载链接
        :param url_str:
        :return:
        """
        real_url, _ = urldefrag(url_str)
        return urljoin(self.seed_url, real_url)

    def save_result(self, html_content, url_str):
        """
        把结果存入数据库, 存入前检查内容是否存在
        :param html_content: 下载的二进制内容
        :param url_str: 下载网页的url
        :return: 无️
        """
        if url_str not in self.mcache:
            self.mcache[url_str] = html_content
        else:
            # 计算数据库记录的MD5摘要
            mongo_md5_str = hashlib.md5(self.mcache[url_str]).hexdigest()

            # 生成下载内容的MD5摘要
            download_md5_str = hashlib.md5(html_content).hexdigest()

            # 进行内容对比
            if download_md5_str != mongo_md5_str:
                self.mcache[url_str] = html_content
                save_url(html_content, url_str)
                print('内容不存在, 开始下载......')
            else:
                print('内容已存在, 跳过下载')

    def run(self):
        """
        实现爬虫的主要逻辑
        :return:
        """
        while not self.crawler_queue.empty():
            url_str = self.crawler_queue.get()

            self.get_user_agent()  # 随机一个请求头
            # self.get_proxies(url_str)  # 随机一个代理

            self.throttle.wait_url(url_str)  # 下载限流器

            # 判断当前爬虫深度是否达标
            depth = self.visited[url_str]
            if depth < self.__max_dep:
                # 下载链接
                html_content = self.download(url_str)
                # 存储链接
                if html_content is not None:
                    self.save_result(html_content, url_str)

                    # 筛选出页面所有链接
                    try:
                        res = html_content.decode('utf-8')
                    except UnicodeDecodeError:
                        res = html_content.decode('gbk', 'ignore')

                    url_list = extractor_url_lists(res)

                    # 筛选出需要爬取的链接
                    filter_urls = [link for link in url_list if
                                   re.search('/({})'.format(self.filter_keyword_for_url), link)]
                    for url in filter_urls:
                        real_url = self.nomalize(url)
                        if real_url not in self.visited:
                            self.visited[real_url] = depth + 1
                            self.crawler_queue.put(real_url)


class Throttle(object):
    """
    下载限流器
    """

    def __init__(self, delay):
        """
        初始化限流器
        :param domains: 域名为key, 当前时间为value
        :param delay: 固定时间
        """
        self.domains = {}
        self.delay = delay

    def wait_url(self, url_str):
        # 返回url的域名('www.itmeng.top')
        domain_url = urlparse(url_str).netloc
        # 取出上一次的休眠时间
        last_accessed = self.domains.get(domain_url)
        if self.delay > 0 and last_accessed is not None:
            # 休眠间隔( 设置的固定时间 - (当前时间 - 上一次的时间))
            sleep_interval = self.delay - (datetime.now() - last_accessed).seconds
            if sleep_interval > 0:
                # 判断上文计算的休眠间隔大于0 则做休眠操作
                time.sleep(sleep_interval)
        # 存储到字典中, 域名为key, 当前时间为value
        self.domains[domain_url] = datetime.now()


if __name__ == '__main__':
    # test
    # 给定url,  输入关键字
    crawler = CrawlerCommon('https://www.qiushibaike.com/hot/page/2/')
    crawler.filter_keyword_for_url = 'hot/page'
    crawler.set_max_dep(3)
    crawler.start()
    # crawler = MongoCache()
    # s = crawler['http://www.runoob.com/python3/python3-module.html']
    # print(s.decode("utf-8", 'ignore'))
    # m = MengMongo("cache", "webpage")
    # m.connect()
    # htmls = m.get_many_html({}, 'result')
    #
    # print(htmls)
    # print(len(htmls), type(htmls))
    # html = m.get_one_html({'_id': 'http://www.xbiquge.la/2/2699/7196411.html'}, 'result')
    # print(html.decode('utf-8', 'ignore'))
    # for html in htmls:
    #     file_path = "./mongo/{}.html".format(htmls.index(html))
    #     with open(file_path, 'w', encoding='utf-8') as f:
    #         f.write(html.decode('utf-8', 'replace'))
    # print(html['result'].decode('gbk', 'ignore'))
