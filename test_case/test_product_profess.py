# !/usr/bin/python3
# -*- coding: utf-8 -*-
import os

import allure
import pytest
import logging
import requests
from fixture.get_hmac_fixture import *
from config.url_config import URLConf
from config.response_code import ResCode
from fixture.connect_mysql import get_czkPw

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
    print(sign, 99)
    return sign


class TestProductProfess(object):
    @pytest.fixture(scope='function', autouse=True)
    def setup_teardown(self):
        """
        此方法包括了前置和后置，可以传入参数
        :param sn:
        :return:
        """
        logger.info('\n===============setup===============')
        yield
        logger.info('\n===============teardown============')

    @pytest.mark.cn
    @pytest.mark.hw
    # @pytest.mark.parametrize("get_load_data_product, get_url", [((path, current_file), '')],
    #                          indirect=["get_load_data_product", "get_url"])    测试环境
    @pytest.mark.parametrize("get_load_data_product, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_product", "get_url"])    #生产环境
    def test_001_user_Login(self, get_load_data_product, get_url, i=0):
        """用户登录接口"""
        allure.dynamic.title(get_load_data_product[i][0])
        logger.info('用例名称：' + get_load_data_product[i][0])  # 用例名称
        url = get_url + get_load_data_product[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_product[i][-1])  # 参数类型为dict
        payload['password'] = get_sign(payload['password'])
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)  # 发送get请求
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功


    @pytest.mark.cn
    @pytest.mark.parametrize('channel_cn', ['870'])
    @pytest.mark.parametrize("get_load_data_product, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_product", "get_url"])
    def test_002_Product_List_cn(self, get_load_data_product, get_url, channel_cn, i=1):
        """产品列表接口"""
        allure.dynamic.title(get_load_data_product[i][0])
        logger.info('用例名称：' + get_load_data_product[i][0])  # 用例名称
        url = get_url + URLConf.PREFIX_ORDER.value + get_load_data_product[i][1]  # 接口请求uri
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_product[i][-1])  # 参数类型为dict
        payload['channel'] = channel_cn
        payload['userid'] = globals()['userId']
        payload['hmac'] = get_v8_hmac(payload)
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)  # 发送get请求
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功


    @pytest.mark.hw
    @pytest.mark.parametrize('channel_hw', ['96', '144'])
    @pytest.mark.parametrize("get_load_data_product, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_product", "get_url"])
    def test_002_Product_List_hw(self, get_load_data_product, get_url, channel_hw, i=1):
        """产品列表接口"""
        allure.dynamic.title(get_load_data_product[i][0])
        logger.info('用例名称：' + get_load_data_product[i][0])  # 用例名称
        url = get_url + URLConf.PREFIX_ORDER.value + get_load_data_product[i][1]  # 接口请求uri
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_product[1][-1])  # 参数类型为dict
        payload['channel'] = channel_hw
        payload['userid'] = globals()['userId']
        payload['hmac'] = get_v8_hmac(payload)
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)  # 发送get请求
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功



