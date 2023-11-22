#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2023/11/21 11:24
# @Author  : qwj
# @Site    : 
# @File    : api_func.py
# @Software: PyCharm
import base64
import hashlib
import hmac

import requests

from lib.global_val import GlobalValueHelper


class EncryptFunc:
    @staticmethod
    def get_v8_hmac(params):
        """SHA1加密
        return:加密结果转成16进制字符串形式
        """
        str1 = ["{0}={1}".format(k, v) for k, v in params.items()]  # 使用 = 拼接dict数据（key,values）
        str1.sort()  # 按照字母序进行排序
        res = "&".join(str1)  # 使用 & 拼接数据
        message = res.encode('utf-8')
        key = GlobalValueHelper().get_value("sign_value").encode('utf-8')
        sign1 = hmac.new(key, message, digestmod=hashlib.sha1)  # 使用sha1进行加密
        sign = base64.b64encode(sign1.digest()).decode()  # 使用base64进行转码
        return sign


class APIFunc:
    """api公共方法"""

    @staticmethod
    def get_device_list(url, userid) -> list:
        """
        获取设备列表
        Args:
            url: 接口请求地址
            userid: 用户id

        Returns:
            返回接口返回设备json信息
        """

        payload = {
            "seq": "1",
            "userid": userid
        }
        _hmac = EncryptFunc().get_v8_hmac(payload)
        payload["hmac"] = _hmac
        response = requests.get(url + "/v4/devices/list", params=payload)
        return response.json()["data"]
