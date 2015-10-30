# encoding: utf-8
__author__ = 'zhanghe'

from psycopg2 import *
import json
from datetime import date, datetime


# 本地环境
db_config_local = {
    'database': '',
    'user': 'xxxx',
    'password': 'xxxxxxxx',
    'host': '192.168.1.1',
    'port': 3306
}

# 线上环境
db_config_online = {
    'database': '',
    'user': 'xxxx',
    'password': 'xxxxxxxx',
    'host': '192.168.1.2',
    'port': 3306
}

db_config_current = db_config_local


class Postgres(object):
    """
    自定义Postgres工具
    """
    def __init__(self, db_config, db_name=None):
        self.db_config = db_config
        if db_name is not None:
            self.db_config['database'] = db_name
        try:
            self.conn = connect(
                database=self.db_config['database'],
                user=self.db_config['user'],
                password=self.db_config['password'],
                host=self.db_config['host'],
                port=self.db_config['port']
            )
        except Exception, e:
            print e

    @staticmethod
    def __default(obj):
        """
        支持datetime的json encode
        TypeError: datetime.datetime(2015, 10, 21, 8, 42, 54) is not JSON serializable
        :param obj:
        :return:
        """
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        else:
            raise TypeError('%r is not JSON serializable' % obj)

    def is_conn_open(self):
        """
        检测连接是否打开
        :return:
        """
        if self.conn is None or self.conn.closed == 1:
            return False
        else:
            return True

    def close_conn(self):
        """
        关闭数据库连接
        :return:
        """
        if self.is_conn_open() is True:
            self.conn.close()

    def get_columns_name(self, table_name):
        """
        获取数据表的字段名称
        :param table_name:
        :return:
        """
        if self.is_conn_open() is False:
            print '连接已断开'
            return []
        try:
            # 参数判断
            if table_name is None:
                print '查询表名缺少参数'
                return []
            cursor = self.conn.cursor()
            sql = "select column_name from information_schema.columns where table_name = '%s'" % table_name
            print sql
            cursor.execute(sql)
            result = cursor.fetchall()
            row = [item[0] for item in result]
            cursor.close()
            return row
        except Exception, e:
            print e

    def get_row(self, table_name, condition=None):
        """
        获取单行数据
        :return:
        """
        if self.is_conn_open() is False:
            print '连接已断开'
            return None
        try:
            # 参数判断
            if table_name is None:
                print '查询表名缺少参数'
                return None
            if condition and not isinstance(condition, list):
                print '查询条件参数格式错误'
                return None
            # 组装查询条件
            if condition:
                sql_condition = 'where '
                sql_condition += ' and '.join(condition)
            else:
                sql_condition = ''
            sql = 'select * from %s %s limit 1' % (table_name, sql_condition)
            print sql
            cursor = self.conn.cursor()
            cursor.execute(sql)
            row = cursor.fetchone()
            cursor.close()
            return row
        except Exception, e:
            print e

    def get_rows(self, table_name, condition=None, limit='limit 10 offset 0'):
        """
        获取多行数据
        con_obj.get_rows('company', ["type='6'"], 'limit 10 offset 0')
        con_obj.get_rows('company', ["type='6'"], 'limit 10')
        """
        if self.is_conn_open() is False:
            print '连接已断开'
            return None
        try:
            # 参数判断
            if table_name is None:
                print '查询表名缺少参数'
                return None
            if condition and not isinstance(condition, list):
                print '查询条件参数格式错误'
                return None
            # 组装查询条件
            if condition:
                sql_condition = 'where '
                sql_condition += ' and '.join(condition)
            else:
                sql_condition = ''
            sql = 'select * from %s %s %s' % (table_name, sql_condition, limit)
            print sql
            cursor = self.conn.cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
            cursor.close()
            return rows
        except Exception, e:
            print e

    def get_count(self, table_name, condition=None):
        """
        获取记录总数
        :return:
        """
        if self.is_conn_open() is False:
            print '连接已断开'
            return 0
        try:
            # 参数判断
            if table_name is None:
                print '查询表名缺少参数'
                return 0
            if condition and not isinstance(condition, list):
                print '查询条件参数格式错误'
                return 0
            # 组装查询条件
            if condition:
                sql_condition = 'where '
                sql_condition += ' and '.join(condition)
            else:
                sql_condition = ''
            sql = 'select count(*) from %s %s' % (table_name, sql_condition)
            print sql
            cursor = self.conn.cursor()
            cursor.execute(sql)
            row = cursor.fetchone()
            count = row[0]
            cursor.close()
            return count
        except Exception, e:
            print e

    def output_row(self, table_name, condition=None, style=0):
        """
        格式化输出单个记录
        style=0 键值对齐风格
        style=1 JSON缩进风格
        """
        # 参数判断
        if not table_name:
            print '查询数据缺少参数'
            return None
        if condition and not isinstance(condition, list):
            print '查询条件参数格式错误'
            return None
        columns_name = self.get_columns_name(table_name)
        row = self.get_row(table_name, condition)
        if not columns_name:
            print '表名不存在'
            return None
        if not row:
            print '记录不存在'
            return None
        if style == 0:
            # 获取字段名称最大的长度值作为缩进依据
            max_len_column = max([len(each_column) for each_column in columns_name])
            str_format = '{0: >%s}' % max_len_column
            columns_name = [str_format.format(each_column) for each_column in columns_name]
            result = dict(zip(columns_name, row))
            print '**********  表名[%s]  **********' % table_name
            for key, item in result.items():
                print key, ':', item
        else:
            result = dict(zip(columns_name, row))
            print json.dumps(result, indent=4, ensure_ascii=False, default=self.__default)

    def output_rows(self, table_name, condition=None, limit='limit 10 offset 0', style=0):
        """
        格式化输出批量记录
        style=0 键值对齐风格
        style=1 JSON缩进风格
        """
        # 参数判断
        if not table_name:
            print '查询数据缺少参数'
            return None
        if condition and not isinstance(condition, list):
            print '查询条件参数格式错误'
            return None
        columns_name = self.get_columns_name(table_name)
        rows = self.get_rows(table_name, condition, limit)
        if not columns_name:
            print '表名不存在'
            return None
        if not rows:
            print '记录不存在'
            return None
        if style == 0:
            # 获取字段名称最大的长度值作为缩进依据
            max_len_column = max([len(each_column) for each_column in columns_name])
            str_format = '{0: >%s}' % max_len_column
            columns_name = [str_format.format(each_column) for each_column in columns_name]
            count = 0
            total = len(rows)
            for row in rows:
                result = dict(zip(columns_name, row))
                count += 1
                print '**********  表名[%s]  [%d/%d]  **********' % (table_name, count, total)
                for key, item in result.items():
                    print key, ':', item
        else:
            for row in rows:
                result = dict(zip(columns_name, row))
                print json.dumps(result, indent=4, ensure_ascii=False, default=self.__default)

    def update(self, table_name, update_field, condition=None):
        """
        更新数据
        con_obj.update('company', ["title='标题'", "flag='2'"], ["type='6'"])
        """
        if self.is_conn_open() is False:
            print '连接已断开'
            return False
        try:
            # 参数判断
            if not table_name or not update_field:
                print '更新数据缺少参数'
                return False
            if not isinstance(update_field, list) or (condition and not isinstance(condition, list)):
                print '更新数据参数格式错误'
                return False
            # 组装更新字段
            if update_field:
                sql_update_field = 'set '
                sql_update_field += ' and '.join(update_field)
            else:
                sql_update_field = ''
            # 组装更新条件
            if condition:
                sql_condition = 'where '
                sql_condition += ' and '.join(condition)
            else:
                sql_condition = ''
            # 拼接sql语句
            sql = 'update %s %s %s' % (table_name, sql_update_field, sql_condition)
            print sql
            cursor = self.conn.cursor()
            cursor.execute(sql)
            self.conn.commit()
            print '更新行数：%s' % cursor.rowcount
            cursor.close()
            return True
        except Exception, e:
            print e

    def delete(self, table_name, condition=None):
        """
        删除数据
        con_obj.delete('company', ["type='6'", "flag='2'"])
        """
        if self.is_conn_open() is False:
            print '连接已断开'
            return False
        try:
            # 参数判断
            if condition and not isinstance(condition, list):
                print '删除数据参数格式错误'
                return False
            # 组装删除条件
            if condition:
                sql_condition = 'where '
                sql_condition += ' and '.join(condition)
            else:
                sql_condition = ''
            # 拼接sql语句
            sql = 'delete from %s %s' % (table_name, sql_condition)
            print sql
            cursor = self.conn.cursor()
            cursor.execute(sql)
            self.conn.commit()
            print '删除行数：%s' % cursor.rowcount
            cursor.close()
            print '删除成功'
            return True
        except Exception, e:
            print e

    def query_by_sql(self, sql=None):
        """
        根据sql语句查询
        :return:
        """
        if self.is_conn_open() is False:
            print '连接已断开'
            return None
        if sql is None:
            print 'sql语句不能为空'
            return None
        # 安全性校验
        sql = sql.lower()
        if not sql.startswith('select'):
            print '未授权的操作'
            return None
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
            cursor.close()
            # print rows
            return rows
        except Exception, e:
            print e

    def update_by_sql(self, sql=None):
        """
        根据sql语句[增删改]
        :return:
        """
        if self.is_conn_open() is False:
            print '连接已断开'
            return False
        if sql is None:
            print 'sql语句不能为空'
            return False
        # 安全性校验
        sql = sql.lower()
        if not (sql.startswith('update') or sql.startswith('insert') or sql.startswith('delete')):
            print '未授权的操作'
            return False
        try:
            print sql
            cursor = self.conn.cursor()
            cursor.execute(sql)
            self.conn.commit()
            print '影响行数：%s' % cursor.rowcount
            cursor.close()
            print '执行成功'
            return True
        except Exception, e:
            print e


def test_51job():
    """
    测试51job
    """
    # 实例化wl_crawl库的连接
    wl_crawl = Postgres(db_config_current, 'wl_crawl')
    # 查询总数
    count = wl_crawl.get_count('origin_position', ['source_type=2'])
    print '51job职位 原始总记录数：%s\n' % count
    count = wl_crawl.get_count('origin_company', ['source_type=2'])
    print '51job公司 原始总记录数：%s\n' % count
    # 关闭数据库连接
    # wl_crawl.close_conn()
    # 查询单条记录
    # wl_crawl.output_row('origin_company', ['id=69011'])
    # 关闭数据库连接(测试再次关闭)
    wl_crawl.close_conn()


def test_china_hr():
    """
    测试china_hr
    """
    # 实例化wl_crawl库的连接
    wl_crawl = Postgres(db_config_current, 'wl_crawl')

    # 查询总数
    count = wl_crawl.get_count('origin_position', ['source_type=6'])
    print 'china_hr职位 原始总记录数：%s\n' % count
    count = wl_crawl.get_count('origin_company', ['source_type=6'])
    print 'china_hr公司 原始总记录数：%s\n' % count
    count = wl_crawl.get_count('online_position', ['source_type=6'])
    print 'china_hr职位 清洗总记录数：%s\n' % count
    count = wl_crawl.get_count('online_company', ['source_type=6'])
    print 'china_hr公司 清洗总记录数：%s\n' % count

    # 查询单条记录
    # wl_crawl.output_row('origin_company', ['source_type=6'])
    # wl_crawl.output_row('origin_position', ['source_type=6', 'id=157789'])
    # wl_crawl.output_row('online_position', ['source_type=6', 'id=157789'])
    # wl_crawl.output_rows('origin_position', ['source_type=6', 'clean_flag=0'])
    # wl_crawl.output_rows('online_position', ['source_type=6'])
    # wl_crawl.output_rows('origin_company', ['source_type=6'])
    # wl_crawl.output_rows('online_company', ['source_type=6', 'id=134064'])
    # wl_crawl.output_rows('online_company', ['source_type=6'])

    # 还原清洗状态
    if 0:
        wl_crawl.delete('online_position', ['source_type=6'])
        wl_crawl.update('origin_position', ['clean_flag=0'], ['source_type=6', 'clean_flag>0'])
        wl_crawl.delete('online_company', ['source_type=6'])
        wl_crawl.update('origin_company', ['clean_flag=0'], ['source_type=6', 'clean_flag>0'])

    # 还原数据导出状态
    if 0:
        wl_crawl.update('online_position', ['export_flag=0'])
    # 检查字段分类集合
    if 0:
        sql = 'select distinct(salary_from) from origin_position where source_type=6'
        result = wl_crawl.query_by_sql(sql)
        print json.dumps(result, indent=4, ensure_ascii=False)

    # 关闭数据库连接(测试再次关闭)
    wl_crawl.close_conn()


if __name__ == '__main__':
    # test_51job()
    test_china_hr()
