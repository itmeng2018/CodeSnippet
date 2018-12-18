from pymongo import MongoClient


class MengMongo(object):
    def __init__(self, db_name, collect_name, host=None, port=None):
        self.host = '127.0.0.1' if host is None else host
        self.port = 27017 if port is None else port
        self.db_name = db_name
        self.collect_name = collect_name
        self.__collection = None

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
    def connect(self):
        """
        实例化MangoDB对象,创建连接
        :return: collection 选择[数据库][集合]
        """
        client = MongoClient(host=self.host, port=self.port)
        self.__collection = client[self.db_name][self.collect_name]

    @__try_operation
    def insert_one(self, item):
        """
        增加一条数据
        :param item: {'name': 'xxx', 'age': 19}
        :return: item id
        """
        result = self.__collection.insert(item)
        return {'_id': result}

    @__try_operation
    def insert_many(self, item_list):
        """
        一次增加多条数据
        :param item_list: [{'name': 'xx1', 'age': 19}, {'name': 'xx2', 'age': 23}]
        :return: item IDs_list
        """
        results = self.__collection.insert_many(item_list)
        return [{"_id": i} for i in results.inserted_ids]

    @__try_operation
    def try_find_one(self, item):
        """
        查询一条数据
        :param item: {'name': 'xxx', 'age': 19}
        :return: 返回查询结果
        """
        result = self.__collection.find_one(item)
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
        result = self.__collection.find(item)
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
        self.__collection.update_one(load_item, new_item)

    @__try_operation
    def try_update_many(self, load_item, new_item):
        """
        更新全部满足条件的数据
        :param load_item: 旧数据 {'name': 'x1'}
        :param new_item: 新数据 {'$set': {'name': 'x2'}}
        :return:
        """
        self.__collection.update_many(load_item, new_item)

    @__try_operation
    def try_delete_one(self, item):
        """
        删除一条数据
        :param item: {'name': 'xxx', 'age': 19}
        :return:
        """
        self.__collection.delete_one(item)

    @__try_operation
    def try_delete_many(self, item):
        """
        删除所有满足条件的数据
        :param item: {'name': 'xxx', 'age': 19}
        :return:
        """
        self.__collection.delete_many(item)


if __name__ == '__main__':
    # 测试连接
    client = MengMongo('test', 'students')
    client.connect()

    # 测试增加一条数据
    # item = {'id': '20181213', 'name': 'itmeng2', 'age': 239, 'gender': 'he23he'}
    # id = client.insert_one(item)
    # print(id)

    # 测试查询一条数据
    # item = {'name': 'xxx741', 'age': 84}
    # s = client.try_find_one(item)
    # print(s)
    # item2 = {'name': 'xxxx741', 'age': 25}
    # print(client.try_find_one(item2))

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
    # ids = client.insert_many(items)
    # print(ids)

    # 测试查询多条数据
    # item = {'sex': 0}
    # s = client.try_find_many(item)
    # print(s)

    # 测试更新一条数据
    # load_item = {'name': 'xxx741', 'age': 84}
    # new_item = {"$set": {'name': 'xxxx741', 'age':25}}
    # client.try_update_one(load_item, new_item)

    # 更新全部满足条件的数据
    # item = {'sex': 0}
    # new_item = {'$set': {'id': 33}}
    # client.try_update_many(item, new_item)

    # 测试数据删除
    # item = {'sex': 0}
    # client.try_delete_one(item)
    # client.try_delete_many(item)
