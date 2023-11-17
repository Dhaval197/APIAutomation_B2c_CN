# !/usr/bin/python3
# -*- coding: utf-8 -*-
import configparser
import os


class Readconfig:
    """定义一个读取配置文件的类"""

    def __init__(self, filepath=None):
        if filepath:
            configpath = filepath
        else:
            root_dir = os.path.dirname(os.path.abspath('.'))  # 获取当前文件所在目录的上一级目录，即项目所在目录D:\yi_api_test_profess
            configpath = os.path.join(root_dir, "config\config.ini")  # 拼接得到config.ini文件的路径
        self.cf = configparser.ConfigParser()  # 实例化configParser对象
        self.cf.read(configpath)  # 读取配置文件

    def get_login_data(self, param):
        value = self.cf.get("Login-Data", param)
        return value
