# !/usr/bin/python3
# -*- coding: utf-8 -*-
import hmac
import hashlib
import base64


# 登录密码进行加密
def get_sign(user_pwd):
    """
    HmacSHA256加密
    return:加密结果转成16进制字符串形式
    """
    message = user_pwd.encode('utf-8')
    key = "KXLiUdAsO81ycDyEJAeETC$KklXdz3AC".encode('utf-8')
    sign1 = hmac.new(key, message, digestmod=hashlib.sha256)  # 使用sha256进行加密
    sign = base64.b64encode(sign1.digest()).decode()  # 使用base64进行转码
    return sign

