import pymysql


class MengSql(object):
    def __init__(self, host, user, passwd, db_name):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.db_name = db_name

    def connet(self):
        self.db = pymysql.connect(self.host, self.user, self.passwd, self.db_name)
        self.cursor = self.db.cursor()

    def close(self):
        self.cursor.close()
        self.db.close()

    def get_one(self, sql):
        try:
            self.connet()
            self.cursor.execute(sql)
            result = self.cursor.fetchone()
            self.close()
        except Exception as e:
            result = None
            print("查询失败: ", e)
        return result

    def get_all(self, sql):
        try:
            self.connet()
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
            self.close()
        except Exception as e:
            result = None
            print("查询失败: ", e)
        return result

    def __edit(self, sql):
        count = 0
        try:
            self.connet()
            count = self.cursor.execute(sql)
            self.db.commit()
            self.close()
        except Exception as e:
            print("事物提交失败: ", e)
            self.db.rollback()
        return count

    def insert(self, table, items):
        if not all([table, items]):
            return print('参数不完整')
        base_sql = "insert into %s({}) values({})" % table
        key_sql = ','.join(list(items.keys()))
        values = list(items.values())
        value_sql = ''
        for value in values[0:-1]:
            if isinstance(value, int):
                value_sql += str(value) + ','
            else:
                value_sql += "'" + value + "',"
        if isinstance(values[-1], int):
            value_sql += str(values[-1])
        else:
            value_sql += "'" + values[-1] + "'"
        return self.__edit(base_sql.format(key_sql, value_sql))

    def find_many(self, table, fields=None, query=None):
        """select * form user where id < 5 """
        base_sql = "select {} from %s " % table
        if isinstance(fields, str):
            base_sql = base_sql.format(fields)
        elif fields and hasattr(fields, '__iter__'):
            base_sql = base_sql.format(','.join(fields))
        else:
            base_sql = base_sql.format('*')
        if query:
            base_sql += query
        return self.get_all(base_sql)

    def update(self, table, set_sql, condition):
        """ update users set username='xiaomaoyu' where id=3 """
        return self.__edit("update {} set {} where {}".format(table, set_sql, condition))

    def delete(self, table, condition):
        """ delete from users where id > 999 """
        return self.__edit("delete from {} where {}".format(table, condition))

