# !/usr/bin/python3
# -*- coding: utf-8 -*-
import pymysql
import pandas as pd
import numpy as np

# 连接MySQL数据库
db = pymysql.connect(host='47.116.15.142',  # 数据库地址
                     port=3306,  # 数据库端口
                     user='iot',  # 数据库登录用户名
                     passwd='jjker1314',  # 数据库登录密码
                     db='iot_order_db',  # 需要连接的库
                     charset='utf8')  # 需要查询中文时指定编码格式

# 连接MySQL数据库
db1 = pymysql.connect(host='47.116.15.142',  # 数据库地址
                     port=3306,  # 数据库端口
                     user='iot',  # 数据库登录用户名
                     passwd='jjker1314',  # 数据库登录密码
                     db='iot_order_db',  # 需要连接的库
                     charset='utf8')  # 需要查询中文时指定编码格式

# 获取充值卡密码
def get_czkPw():
    sqlcheck = "select pw, sku_id from tb_virtual_card_detail where used = 0 and expired_time > NOW() limit 5"
    df1 = pd.read_sql(sqlcheck, db)
    df2 = np.array(df1)  # 使用array()将DataFrame转换一下
    df3 = df2.tolist()  # 将数据用tolist()转成列表
    return df3


# 更新订单状态为 30-支付成功(微信)
def edit_orderStatus(aa, bb):
    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()
    # SQL 更新语句
    sql = "update tb_order_info set pay_status = 30 where user_id = '%s'" % aa + " and code = '%s'" % bb
    try:
        # 执行SQL语句
        cursor.execute(sql)
        # 提交到数据库执行
        db.commit()
    except:
        # 发生错误时回滚
        db.rollback()
    # 关闭数据库连接
    db.close()


# 更新订单状态为 30-支付成功(支付宝)
def edit_orderStatus1(aa, bb):
    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor1 = db1.cursor()
    # SQL 更新语句
    sql1 = "update tb_order_info set pay_status = 30 where user_id = '%s'" % aa + " and code = '%s'" % bb
    try:
        # 执行SQL语句
        cursor1.execute(sql1)
        # 提交到数据库执行
        db1.commit()
    except:
        # 发生错误时回滚
        db1.rollback()
    # 关闭数据库连接
    db1.close()


if __name__ == '__main__':
    print(edit_orderStatus())
