import requests
from lxml import etree

from meng import MengSql


class QiuShiSpider:
    def __init__(self):
        self.url_temp = "https://www.qiushibaike.com/8hr/page/{}/"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3610.2 Safari/537.36"}
        self.mysql = MengSql('localhost', 'root', '123456', 'qiushi')

    def get_url_list(self):
        """
        获取url列表
        :return:
        """
        return [self.url_temp.format(i) for i in range(1, 14)]

    def parse_url(self, url):
        """
        发送请求, 获取响应
        :param url:
        :return:
        """
        response = requests.get(url, headers=self.headers)
        try:
            return response.content.decode()
        except UnicodeDecodeError:
            return response.text

    def get_content_list(self, html_str):
        """
        提取数据
        :param html_str:
        :return:
        """

        html = etree.HTML(html_str)
        li_video_list = html.xpath('//div[@id="content"]/div/div/div/ul/li')
        li_img_list = html.xpath('//div[@id="content"]/div/div/div/ul/li[@class="item typs_multi"]')
        data = []
        for li_video, li_img in zip(li_video_list, li_img_list):
            item = {}
            try:
                item['title'] = li_video.xpath('./div/a/text()')[0]
                item['img_url'] = "http" + li_video.xpath('./a[@class="recmd-left video"]/img/@src')[0]
                '''http://pic.qiushibaike.com/system/avtnew/2755/27553574/thumb/20180427153625.JPEG?imageView2/1/w/50/h/50'''
                item['auther'] = li_video.xpath('./div/div/a/span[@class="recmd-name"]/text()')[0]
                item['head_img'] = "http" + li_video.xpath('./div/div/a/img/@src')[0]
                item['context_url'] = "https://www.qiushibaike.com" + li_video.xpath('./div/a/@href')[0]
                item['laugh_count'] = li_video.xpath('./div/div/div/span/text()')[0]
                item['comment_count'] = li_video.xpath('./div/div/div/span/text()')[3]

            except IndexError:
                item['title'] = li_img.xpath('./div/a/text()')[0]
                item['img_url'] = "http" + li_img.xpath('./a[@class="recmd-left multi"]/img/@src')[0]
                item['auther'] = li_img.xpath('./div/div/a/span[@class="recmd-name"]/text()')[0]
                item['head_img'] = "http" + li_img.xpath('./div/div/a/img/@src')[0]
                item['context_url'] = "https://www.qiushibaike.com" + li_img.xpath('./div/a/@href')[0]
                item['laugh_count'] = li_img.xpath('./div/div/div/span/text()')[0]
                try:
                    item['comment_count'] = li_img.xpath('./div/div/div/span/text()')[3]
                except IndexError:
                    item['comment_count'] = None
            data.append(item)
        return data

    def save_data(self, data, page):
        self.mysql.connet()
        # sql建表语句
        '''
        CREATE TABLE `qiushi` (
          `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键',
          `title` varchar(255) DEFAULT NULL COMMENT '标题',
          `img_url` varchar(255) DEFAULT NULL COMMENT '图片链接',
          `auther` varchar(255) DEFAULT NULL COMMENT '作者',
          `head_img` varchar(255) DEFAULT NULL COMMENT '作者头像',
          `context_url` varchar(255) DEFAULT NULL COMMENT '内容链接',
          `laugh_count` varchar(255) DEFAULT NULL COMMENT '好笑数',
          `comment_count` varchar(255) DEFAULT NULL COMMENT '评论数',
          PRIMARY KEY (`id`)
        ) ENGINE=InnoDB AUTO_INCREMENT=78 DEFAULT CHARSET=utf8;
        '''
        for i in data:
            sql = """INSERT INTO `qiushi`.`qiushi`(`title`, `img_url`, `auther`, `head_img`, `context_url`, `laugh_count`, `comment_count`) 
            VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}');""".format(
                i['title'], i['img_url'], i['auther'], i['head_img'], i['context_url'], i['laugh_count'],
                i['comment_count'])
            self.mysql.insert(sql)
        print(page)

    def run(self):
        """
        实现主要逻辑
        :return:
        """
        # 1. url_list
        url_list = self.get_url_list()
        # 2. 遍历, 发送请求, 获取响应
        for url in url_list:
            html_str = self.parse_url(url)
            if html_str is not None:
                # 3. 提取数据
                data = self.get_content_list(html_str)
                # 　4. 保存
                self.save_data(data, url_list.index(url))


if __name__ == '__main__':
    qiushi = QiuShiSpider()
    qiushi.run()
