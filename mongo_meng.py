# -*- coding: utf-8 -*-

import pickle
import zlib
from datetime import datetime, timedelta
from pymongo import MongoClient
from bson.binary import Binary


class MongoMeng(object):
    """
    封装MongoDB, 实现快速达到快速存储/检索/对比的效果
    """

    def __init__(self, expires=timedelta(days=30)):
        """
        初始化实例对象, 完成数据库的连接
        :param client: 数据库连接对象
        :param expires: 时间设置(把days转换成秒)
        """
        # 创建数据库连接
        self.client = MongoClient("localhost", 27017)
        # 创建数据库 cache
        self.db = self.client.cache
        # 设置索引, 加速查找, 设置数据生命期(到达时间后自动删除数据库中的数据)
        self.db.webpage.create_index('timestamp', expireAfterSeconds=expires.total_seconds())

    def set_client(self, host, port):
        """
        TODO 设置数据库连接
        :param host: 主机
        :param port: 端口
        :return:
        """
        self.client = MongoClient(host, port)
        return True

    def __setitem__(self, key, value):
        """
        向数据库存网页数据
        :param key: url
        :param value: 网页
        :return:
        """
        # 使用pickle.dumps序列化, 使用compress压缩, 然后使用Binary转成二进制, timestamp:设置时间戳
        record = {"result": Binary(zlib.compress(pickle.dumps(value))), "timestamp": datetime.utcnow()}
        # upsert, 如果库中没有则插入, 如果库中存在则更新成新数据
        self.db.webpage.update({"_id": key}, {'$set': record}, upsert=True)

    def __getitem__(self, item):
        """
        根据'_id'以item作为关键字取出网页
        :param item: key == _id == url, 例如:'http://www.itemng.top'
        :return: 解压缩和反序列化后的原网页数据
        """
        record = self.db.webpage.find_one({"_id": item})
        if record:
            return pickle.loads(zlib.decompress(record["result"]))
        else:
            # 找不到数据抛出自定义异常
            raise KeyError(item + "does not exist")

    def __contains__(self, item):
        """
        判断网页内容是否发生改变
        :param item:
        :return:
        """
        try:
            self[item]  # 自动调用__getitem__方法
        except KeyError:
            # 捕获到自定义异常, 代表没有该数据(参考51行抛出异常的条件)
            return False
        else:
            # 代表数据库中包含该数据(可以进行内容对比等操作)
            return True

    def clear(self):
        # 把数据库缓存清空
        self.db.webpage.drop()


if __name__ == '__main__':
    # test
    # pass
    m = MongoMeng()
    # url = 'https://blog.csdn.net/qq_43125439/article/details/85059743'
    print('测试成功')

    # 存
    # import requests
    # m[url] = requests.get(url).content

    # 取
    # res = m[url]
    # print(res.decode())

    # 查
    # if url in m:
    #     a = '有了'
    # else:
    #     a = '没有'
    # print(a)
