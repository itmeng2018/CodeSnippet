import pickle
import zlib
from datetime import timedelta, datetime

from bson import Binary
from pymongo import MongoClient


class MengMongo(object):

    def __init__(self, expires=timedelta(days=30), host='localhost', port=27017):
        """
        初始化实例对象, 完成数据库的连接
        :param expires: 时间设置(把days转换成秒)
        """
        # 创建数据库连接
        self.client = MongoClient(host, port)
        # 创建数据库 cache
        self.db = self.client.cache.webpage
        # 设置索引, 加速查找, 设置数据生命期(到达时间后自动删除数据库中的数据)
        self.db.create_index('timestamp', expireAfterSeconds=expires.total_seconds())
        self.model = 'html'  # 选择数据库操作模型 [html] or [no html]

    def __try_operation(func):
        def try_func(self, *args, **kwargs):
            try:
                result = func(self, *args, **kwargs)
                print('操作成功')
                return result
            except Exception as e:
                print('操作异常')
                print(e)

        return try_func

    @__try_operation
    def insert_one(self, item):
        """
        增加一条数据
        :param item: {'name': 'xxx', 'age': 19}
        :return: item id
        """
        result = self.db.insert(item)
        return {'_id': result}

    @__try_operation
    def insert_many(self, item_list):
        """
        一次增加多条数据
        :param item_list: [{'name': 'xx1', 'age': 19}, {'name': 'xx2', 'age': 23}]
        :return: item IDs_list
        """
        results = self.db.insert_many(item_list)
        return [{"_id": i} for i in results.inserted_ids]

    @__try_operation
    def try_find_one(self, item):
        """
        查询一条数据
        :param item: {'name': 'xxx', 'age': 19}
        :return: 返回查询结果
        """
        result = self.db.find_one(item)
        if result is None:
            result = '查询数据不存在'
        return result

    @__try_operation
    def try_find_many(self, item):
        """
        查询所有满足条件的数据
        :param item: {'name': 'xxx', 'age': 19}
        :return: 返回所有满足条件的结果，如果条件为空，则返回数据库的所有, list
        """
        result = self.db.find(item)
        # 结果是一个Cursor游标对象，是一个可迭代对象，可以类似读文件的指针,
        result = [i for i in result]
        if len([i for i in result]) < 1:
            result = '查询数据不存在'
        return result

    @__try_operation
    def try_update_one(self, load_item, new_item):
        """
        更新一条数据
        :param load_item: 旧数据 {'name': 'x1'}
        :param new_item: 新数据 {'$set': {'name': 'x2'}}
        :return:
        """
        self.db.update_one(load_item, new_item)

    def __setitem__(self, key, value):
        """
        向数据库存网页数据
        :param key: url
        :param value: 网页
        :return:
        """
        # 使用pickle.dumps序列化, 使用compress压缩, 然后使用Binary转成二进制, timestamp:设置时间戳
        if self.model == 'html':
            record = {"result": Binary(zlib.compress(pickle.dumps(value))), "timestamp": datetime.utcnow()}
        else:
            record = {"result": value}
        # upsert, 如果库中没有则插入, 如果库中存在则更新成新数据
        self.db.update({"_id": key}, {'$set': record}, upsert=True)
        print({"_id": key})

    def __getitem__(self, item, model='html'):
        """
        根据'_id'以item作为关键字取出网页
        :param item: key == _id == url, 例如:'http://www.itemng.top'
        :return: 解压缩和反序列化后的原网页数据
        """

        record = self.db.find_one({"_id": item})
        if record:
            if self.model == 'html':
                return pickle.loads(zlib.decompress(record["result"]))
            else:
                return record["result"]
        else:
            # 找不到数据抛出自定义异常
            raise KeyError(item + "does not exist")

    @__try_operation
    def try_update_many(self, load_item, new_item):
        """
        更新全部满足条件的数据
        :param load_item: 旧数据 {'name': 'x1'}
        :param new_item: 新数据 {'$set': {'name': 'x2'}}
        :return:
        """
        self.db.update_many(load_item, new_item)

    @__try_operation
    def try_delete_one(self, item):
        """
        删除一条数据
        :param item: {'name': 'xxx', 'age': 19}
        :return:
        """
        self.db.delete_one(item)

    @__try_operation
    def try_delete_many(self, item):
        """
        删除所有满足条件的数据
        :param item: {'name': 'xxx', 'age': 19}
        :return:
        """
        self.db.delete_many(item)

    def __contains__(self, item):
        """
        判断网页内容是否发生改变
        """
        try:
            self[item]  # 自动调用__getitem__方法
        except KeyError:
            # 捕获到自定义异常, 代表没有该数据(参考124行抛出异常的条件)
            return False
        else:
            # 代表数据库中包含该数据(可以进行内容对比等操作)
            return True

    @__try_operation
    def clear(self):
        # 把数据库缓存清空
        self.db.drop()


if __name__ == '__main__':
    # utils test

    # 测试连接
    m = MengMongo(host='139.196.137.234')
    # url = 'https://blog.csdn.net/qq_43125439/article/details/85059743'
    url = 'https://www.qiushibaike.com/hot/page/1/'
    # m.model = 'test'
    print('数据库连接成功')

    # 存
    # import requests
    # m[url] = requests.get(url).content

    # 取
    # res = m[url]
    # print(res)

    # # 查
    if url in m:
        a = '有了'
    else:
        a = '没有'
    print(a)

    # 测试增加一条数据
    # item = {'name': 'itmeng2', 'age': 19}
    # item = {"_id": "https://blog.csdn.net/qq_43125439/article/details/85059743"}
    # m[url] = item
    # id = m.insert_one(item)
    # print(id)
    # print(m[url])
    # m.clear()
    # print(m[url])


    # 测试查询一条数据
    # item = {'name': 'xxx741', 'age': 84}
    # s = m.get_one_html(item, 'result')
    # print(s)

    # print(m.try_find_one(item))

    # 测试增加多条数据
    # from random import randint
    #
    # items = []
    # for i in range(10):
    #     item = {
    #         'id': '{}'.format(randint(201000, 201999)),
    #         'name': 'xxx{}'.format(randint(1, 999)),
    #         'age': randint(10, 90),
    #         'sex': randint(0, 1)
    #     }
    #     items.append(item)
    # ids = m.insert_many(items)
    # print(ids)

    # 测试查询多条数据
    # s = m.try_find_many({})
    # print(s)


    # 测试更新一条数据
    # load_item = {'name': 'xxx58'}
    # new_item = {"$set": {'name': 'xxxx741111', 'age':25}}
    # m.try_update_one(load_item, new_item)

    # 更新全部满足条件的数据
    # new_item = {'$set': {'id': 33}}
    # m.try_update_many({}, new_item)

    # 测试数据删除
    # item = {'sex': 0}
    # m.try_delete_one(item)
    # m.try_delete_many(item)

    # 测试清空数据
    # m.clear()
