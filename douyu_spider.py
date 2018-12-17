import json
import time

from selenium import webdriver


class SaveItem:
    '''保存数据'''
    def __init__(self):
        self.data = {}

class DouyuSpider(object):
    '''爬取数据'''
    def __init__(self):
        # 定义起始url
        self.start_url = 'https://www.douyu.com/directory/all'
        # 实例化driver对象
        self.driver = webdriver.Chrome()
        self.save_item = SaveItem()

    def get_content_list(self):
        # 获取url
        li_list = self.driver.find_elements_by_xpath('//ul[@id="live-list-contentbox"]/li')
        content_list = []
        for li in li_list:
            item = {}
            item['room_img'] = li.find_element_by_xpath(".//span[@class='imgbox']/img").get_attribute("src")
            item['room_title'] = li.find_element_by_xpath("./a").get_attribute('title')
            item['room_cate'] = li.find_element_by_xpath(".//span[@class='tag ellipsis']").text
            item['anchor_name'] = li.find_element_by_xpath(".//span[@class='dy-name ellipsis fl']").text
            item['watch_num'] = li.find_element_by_xpath(".//span[@class='dy-num fr']").text
            content_list.append(item)
        next_url_list = self.driver.find_elements_by_xpath('//div[@id="J-pager"]/a[@class="shark-pager-next"]')
        next_url = next_url_list[0] if len(next_url_list) > 0 else None
        return content_list, next_url

    def run(self):  # 实现主要逻辑
        # 对起始url发送请求
        self.driver.get(self.start_url)

        # 关闭提示弹窗, 没有弹窗则需要注释掉
        # self.driver.find_element_by_class_name('pop-zoom-hide').click()
        # time.sleep(1)

        # 提取数据, 提取下一页元素
        content_list, next_url = self.get_content_list()

        # 保存数据
        count = 1
        self.save_item.data[count] = content_list

        # 点击下一页元素, 循环
        while next_url != None:
            print(count)
            next_url.click()
            time.sleep(2)
            content_list, next_url = self.get_content_list()
            count += 1
            self.save_item.data[count] = content_list
        self.driver.close()
        with open('douyu02018_12_17.json', 'w', encoding='utf-8') as fp:
            json.dump(self.save_item.data, fp, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    douyu = DouyuSpider()
    douyu.run()
    print('ok')