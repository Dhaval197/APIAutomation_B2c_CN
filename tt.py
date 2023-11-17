#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2023/11/15 14:03
# @Author  : qwj
# @Site    : 
# @File    : tt.py
# @Software: PyCharm
import ast

aa= """{
 "uids": '',
 "userid": "3206905"
}"""
b = ast.literal_eval(aa)
print(b)