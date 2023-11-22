#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2023/11/21 13:23
# @Author  : qwj
# @Site    : 
# @File    : global_val.py
# @Software: PyCharm
"""全局公共变量"""
import logging

from common.base_func import logger


class GlobalValueHelper:
    _global_dict = {}

    def __init__(self):
        """初始化"""
        pass

    def set_value(self, key: str, value, desc=""):
        """
        定义一个全局变量
        Args:
            key: 索引
            value: 值
            desc: 描述信息

        Returns:

        """
        self._global_dict[key] = value, desc

    def get_value(self, key: str, def_value=None):
        """获得全局变量，不存在则返回默认值"""
        try:
            return self._global_dict[key][0]
        except KeyError:
            logging.error(f"全局变量中不包含 key：{key}")
            return def_value

    def get_keys_desc(self):
        """
        获取所有的key信息和描述信息
        Returns:

        """
        dic = {}
        for k, v in self._global_dict.items():
            dic[k] = v[1]
        return dic

    def get_key_by_value(self, value):
        """根据value获取key的值"""
        try:
            key = list(self._global_dict.keys())[[i[0] for i in list(self._global_dict.values())].index(value)]
            return key
        except KeyError:
            logging.error(f"根据value{value}获取Key的值，没有对应的K值")
            return "没有的对应的key"
        except Exception as e:
            logging.error(f"根据value获取key的值失败，错误信息{str(e)}")
