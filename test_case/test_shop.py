# !/usr/bin/python3
# -*- coding: utf-8 -*-
import datetime
import os
import time
import allure
import logging
import pytest
import requests

from common.base_func import Base_func
from fixture.get_hmac_fixture import *
from config.url_config import URLConf
from config.response_code import ResCode

logger = logging.getLogger(__name__)
# test_data所在路径 如：D:\yi_api_test_profess\test_data
path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'test_data')
current_file = os.path.basename(__file__)  # 当前文件名称 如: test_order_profess.py
data_folder = os.path.join(path, current_file.strip('.py'))  # 当前文件对应的数据文件的目录名称


def get_v8_hmac(params):
    """SHA1加密
    return:加密结果转成16进制字符串形式
    """
    str1 = ["{0}={1}".format(k, v) for k, v in params.items()]  # 使用 = 拼接dict数据（key,values）
    str1.sort()  # 按照字母序进行排序
    res = "&".join(str1)  # 使用 & 拼接数据
    message = res.encode('utf-8')
    key = globals()['sign_value'].encode('utf-8')
    sign1 = hmac.new(key, message, digestmod=hashlib.sha1)  # 使用sha1进行加密
    sign = base64.b64encode(sign1.digest()).decode()  # 使用base64进行转码
    return sign


def days_age30():
    threeDayAgo = datetime.datetime.today() - datetime.timedelta(30)
    time1 = threeDayAgo.strftime("%Y-%m-%d %H:%M:%S")
    # 转为时间数组
    timeArray = time.strptime(time1, "%Y-%m-%d %H:%M:%S")
    # 转为时间戳
    timeStamp = int(time.mktime(timeArray))
    return timeStamp


def get_notv8_hmac(params):
    """SHA1加密
    return:加密结果转成16进制字符串形式
    """
    str1 = ["{0}={1}".format(k, v) for k, v in params.items()]  # 使用 = 拼接dict数据（key,values）
    # str1.sort()  # 按照字母序进行排序
    res = "&".join(str1)  # 使用 & 拼接数据
    message = res.encode('utf-8')
    key = globals()['sign_value'].encode('utf-8')
    sign1 = hmac.new(key, message, digestmod=hashlib.sha1)  # 使用sha1进行加密
    sign = base64.b64encode(sign1.digest()).decode()  # 使用base64进行转码
    return sign


@allure.story('云存服务信息')
@pytest.mark.flaky(reruns=3, reruns_delay=2)
class TestCloudProfess(object):
    @pytest.fixture(scope='function', autouse=True)
    def setup_teardown(self):
        """
        此方法包括了前置和后置，可以传入参数
        :param:
        :return:
        """
        logger.info('='*90)
        yield
        logger.info('='*90)

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_001_user_Login(self, get_load_data_cloud, get_url, i=0):
        """用户登录接口"""
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + get_load_data_cloud[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['password'] = get_sign(payload['password'])
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)  # 发送get请求
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in ResCode.res_mapping.value.get('success'), '验证通过'
        assert response.json().get('data') is not None
        if response.json().get('code') in ResCode.res_mapping.value.get('success'):
            globals()['sign_value'] = response.json().get('data').get('token') + '&' \
                                      + response.json().get('data').get('token_secret')
            globals()['userId'] = response.json().get('data').get('userid')