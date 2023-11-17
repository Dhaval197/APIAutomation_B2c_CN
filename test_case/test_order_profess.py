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
    return sign


class TestOrderProfess(object):
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
    @pytest.mark.parametrize("get_load_data, get_url", [((path, current_file), '')],
                             indirect=["get_load_data", "get_url"])
    def test_001_user_Login(self, get_load_data, get_url, i=0):
        """用户登录接口"""
        allure.dynamic.title(get_load_data[i][0])
        logger.info('用例名称：' + get_load_data[i][0])  # 用例名称
        url = get_url + get_load_data[i][1]  # 接口请求uri
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data[i][-1])  # 参数类型为dict
        payload['password'] = get_sign(payload['password'])
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

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data, get_url", [((path, current_file), '')],
                             indirect=["get_load_data", "get_url"])
    def test_002_create_Token(self, get_load_data, get_url, i=1):
        """创建订单Token接口"""
        allure.dynamic.title(get_load_data[i][0])
        logger.info('用例名称：' + get_load_data[i][0])  # 用例名称
        url = get_url + URLConf.PREFIX_ORDER.value + get_load_data[i][1]  # 接口请求uri
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['hmac'] = get_v8_hmac(payload)
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)  # 发送get请求
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in ResCode.res_mapping.value.get('success'), '验证通过'
        assert response.json().get('data') is not None  # 断言响应token字段值不为空
        globals()['token'] = response.json().get('data')

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data, get_url", [((path, current_file), '')],
                             indirect=["get_load_data", "get_url"])
    def test_003_create_Order(self, get_load_data, get_url, i=2):
        """创建订单接口"""
        allure.dynamic.title(get_load_data[i][0])
        logger.info('用例名称：' + get_load_data[i][0])  # 用例名称
        url = get_url + URLConf.PREFIX_ORDER.value + get_load_data[i][1]  # 接口请求uri
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data[i][-1])  # 参数类型为dict
        payload['token'] = globals()['token']
        payload['userid'] = globals()['userId']
        payload['hmac'] = get_v8_hmac(payload)
        headers = {'Connection': 'close'}
        response = requests.post(url, headers=headers, data=payload)  # 发送post请求
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求状态码为 200
        assert response.json().get('code') in ResCode.res_mapping.value.get('success'), '验证通过'  # 断言响应code为 20000
        assert response.json().get('data').get('orderCode') is not None  # 断言响应orderCode字段值不为空
        globals()['orderCode'] = response.json().get('data').get('orderCode')

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data, get_url", [((path, current_file), '')],
                             indirect=["get_load_data", "get_url"])
    def test_036_isCanPayOrder(self, get_load_data, get_url, i=35):
        '''查询用户是否可以支付订单'''
        allure.dynamic.title(get_load_data[i][0])
        url = get_url + URLConf.PREFIX_ORDER.value + get_load_data[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['orderCode'] = globals()['orderCode']
        payload['hmac'] = get_v8_hmac(payload)
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)  # 发送get请求
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') == 20000

    @pytest.mark.cn
    @pytest.mark.parametrize("get_load_data, get_url", [((path, current_file), '')],
                             indirect=["get_load_data", "get_url"])
    def test_004_query_initialCode(self, get_load_data, get_url, i=3):
        """查询初始化 订单状态接口 10"""
        allure.dynamic.title(get_load_data[i][0])
        logger.info('用例名称：' + get_load_data[i][0])  # 用例名称
        url = get_url + URLConf.PREFIX_ORDER.value + get_load_data[i][1]  # 接口请求uri
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data[i][-1])  # 参数类型为dict
        # 更新请求原数据的code值
        payload['code'] = globals()['orderCode']
        payload['userid'] = globals()['userId']
        payload['hmac'] = get_v8_hmac(payload)
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)
        logger.info('响应结果为：' + response.text)  # 打印响应结果
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in ResCode.res_mapping.value.get('success'), '验证通过'  # 断言响应code为 20000
        assert response.json().get('data') in [10, '10'], '订单状态为 未支付 10'  # 断言响应status为 10

    # discript = ['10-支付宝', '20-微信', '30-paypal', '31-paypal自动续费', '32-信用卡', '40-apple', '41-apple自动续费', '50-充值卡',
    #             '60-免费', '70-stripe订阅']
    discript_cn = ['10-支付宝', '20-微信', '40-apple', '41-apple自动续费', '50-充值卡', '60-免费', '70-stripe订阅']
    ids = [f'payTpye={p}' for p in discript_cn]  # => 生成与数据值相同的名称列表

    @pytest.mark.cn  # 该用例国内执行
    @pytest.mark.parametrize('payType_cn', [10, 20, 40, 41, 50, 60, 70], ids=ids)  # 支付类型参数化
    @pytest.mark.parametrize("get_load_data, get_url", [((path, current_file), '')],
                             indirect=["get_load_data", "get_url"])
    def test_005_editPayStatus_Order_cn(self, get_load_data, get_url, payType_cn, i=4):
        """同步返回修改支付状态为支付中 20"""
        logger.info('用例名称：' + get_load_data[i][0])  # 用例名称
        url = get_url + URLConf.PREFIX_ORDER.value + get_load_data[i][1]  # 接口请求uri
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data[i][-1])  # 参数类型为dict
        payload['payType'] = payType_cn  # 更新请求原数据的code值
        payload['userid'] = globals()['userId']
        payload['orderCode'] = globals()['orderCode']  # 更新请求原数据的orderCode值
        payload['hmac'] = get_v8_hmac(payload)
        headers = {'Connection': 'close'}
        response = requests.post(url, headers=headers, data=payload)
        logger.info('响应结果为：' + response.text)  # 打印响应结果
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in ResCode.res_mapping.value.get('success'), '验证通过'  # 断言响应code为 20000

    discript_hw = ['30-paypal', '31-paypal自动续费', '32-信用卡', '40-apple', '41-apple自动续费', '50-充值卡', '60-免费', '70-stripe订阅']
    ids = [f'payTpye={p}' for p in discript_hw]  # => 生成与数据值相同的名称列表

    @pytest.mark.hw  # 该用例海外执行
    @pytest.mark.parametrize('payType_hw', [30, 31, 32, 40, 41, 50, 60, 70], ids=ids)  # 支付类型参数化
    @pytest.mark.parametrize("get_load_data, get_url", [((path, current_file), '')],
                             indirect=["get_load_data", "get_url"])
    def test_005_editPayStatus_Order_hw(self, get_load_data, get_url, payType_hw, i=4):
        """同步返回修改支付状态为支付中 20 海外环境"""
        logger.info('用例名称：' + get_load_data[i][0])  # 用例名称
        url = get_url + URLConf.PREFIX_ORDER.value + get_load_data[i][1]  # 接口请求uri
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data[i][-1])  # 参数类型为dict
        payload['payType'] = payType_hw  # 更新请求原数据的code值
        payload['userid'] = globals()['userId']
        payload['orderCode'] = globals()['orderCode']  # 更新请求原数据的orderCode值
        payload['hmac'] = get_v8_hmac(payload)
        headers = {'Connection': 'close'}
        response = requests.post(url, headers=headers, data=payload)
        logger.info('响应结果为：' + response.text)  # 打印响应结果
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in ResCode.res_mapping.value.get('success'), '验证通过'  # 断言响应code为 20000

    @pytest.mark.cn  # 该用例国内执行
    @pytest.mark.parametrize("get_load_data, get_url", [((path, current_file), '')],
                             indirect=["get_load_data", "get_url"])
    def test_006_query_paymentCode(self, get_load_data, get_url, i=5):
        """查询支付中 订单状态接口 20"""
        allure.dynamic.title(get_load_data[i][0])
        logger.info('用例名称：' + get_load_data[i][0])  # 用例名称
        url = get_url + URLConf.PREFIX_ORDER.value + get_load_data[i][1]  # 接口请求uri
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['code'] = globals()['orderCode']  # 更新请求原数据的code值
        payload['hmac'] = get_v8_hmac(payload)
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)
        logger.info('响应结果为：' + response.text)  # 打印响应结果
        assert response.status_code == 200, '请求返回非200'  # 断言请求状态码为 200
        assert response.json().get('code') in ResCode.res_mapping.value.get('success'), '验证通过'  # 断言响应code为 20000
        assert response.json().get('data') in [20, '20'], '订单状态为支付中 20'  # 断言支付状态为 20

    @pytest.mark.cn
    @pytest.mark.parametrize("get_load_data, get_url", [((path, current_file), '')],
                             indirect=["get_load_data", "get_url"])
    def test_007_wxPay_Order(self, get_load_data, get_url, i=6):
        """微信客户端支付 接口"""
        allure.dynamic.title(get_load_data[i][0])
        logger.info('用例名称：' + get_load_data[i][0])  # 用例名称
        url = get_url + URLConf.PREFIX_ORDER.value + get_load_data[i][1]  # 接口请求uri
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['orderCode'] = globals()['orderCode']
        payload['hmac'] = get_v8_hmac(payload)
        headers = {'Connection': 'close'}
        response = requests.post(url, headers=headers, data=payload)
        logger.info('响应结果为：' + response.text)  # 打印响应结果
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in ResCode.res_mapping.value.get('success'), '验证通过'
        assert response.json().get('data') is not None  # 断言响应data字段值不为空

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data, get_url", [((path, current_file), '')],
                             indirect=["get_load_data", "get_url"])
    def test_008_userOrder_list(self, get_load_data, get_url, i=7):
        """用户订单列表 接口"""
        allure.dynamic.title(get_load_data[i][0])
        logger.info('用例名称：' + get_load_data[i][0])  # 用例名称
        url = get_url + URLConf.PREFIX_ORDER.value + get_load_data[i][1]  # 接口请求uri
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['hmac'] = get_v8_hmac(payload)
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)
        logger.info('响应结果为：' + response.text)  # 打印响应结果
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in ResCode.res_mapping.value.get('success'), '验证通过'
        assert response.json().get('data') is not None  # 断言响应data字段值不为空
        if response.json().get('data') is not None:
            records = response.json().get('data').get('records')
            globals()['user_records'] = [records[i]['code'] for i in range(len(records))]
        logger.info('用户订单号为：' + str(globals()['user_records']))

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data, get_url", [((path, current_file), '')],
                             indirect=["get_load_data", "get_url"])
    def test_009_userOrder_detail(self, get_load_data, get_url, i=8):
        """用户订单详情 接口"""
        allure.dynamic.title(get_load_data[i][0])
        logger.info('用例名称：' + get_load_data[i][0])  # 用例名称
        url = get_url + URLConf.PREFIX_ORDER.value + get_load_data[i][1]  # 接口请求uri
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['orderCode'] = globals()['user_records'][0]
        payload['hmac'] = get_v8_hmac(payload)
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)
        logger.info('响应结果为：' + response.text)  # 打印响应结果
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in ResCode.res_mapping.value.get('success'), '验证通过'
        assert response.json().get('data') is not None  # 断言响应data字段值不为空

    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data, get_url", [((path, current_file), '')],
                             indirect=["get_load_data", "get_url"])
    def test_010_userOrderPay_history(self, get_load_data, get_url, i=9):
        """用户订单支付历史 接口"""
        allure.dynamic.title(get_load_data[i][0])
        logger.info('用例名称：' + get_load_data[i][0])  # 用例名称
        url = get_url + URLConf.PREFIX_ORDER.value + get_load_data[i][1]  # 接口请求uri
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['orderCode'] = globals()['user_records'][0]
        payload['hmac'] = get_v8_hmac(payload)
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)
        logger.info('响应结果为：' + response.text)  # 打印响应结果
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in ResCode.res_mapping.value.get('success'), '验证通过'

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data, get_url", [((path, current_file), '')],
                             indirect=["get_load_data", "get_url"])
    def test_011_Get_Trail(self, get_load_data, get_url, i=10):
        """是否是新用户 接口"""
        allure.dynamic.title(get_load_data[i][0])
        logger.info('用例名称：' + get_load_data[i][0])  # 用例名称
        url = get_url + URLConf.PREFIX_ORDER.value + get_load_data[i][1]  # 接口请求uri
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['hmac'] = get_v8_hmac(payload)
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)
        logger.info('响应结果为：' + response.text)  # 打印响应结果
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in ResCode.res_mapping.value.get('success'), '验证通过'
        assert response.json().get('data').get('trial') in [0, 1]  # 0为新用户；1为老用户

    @pytest.mark.cn
    @pytest.mark.parametrize("get_load_data, get_url", [((path, current_file), '')],
                             indirect=["get_load_data", "get_url"])
    def test_012_Order_Exists(self, get_load_data, get_url, i=11):
        """是否有云服务 接口"""
        allure.dynamic.title(get_load_data[i][0])
        logger.info('用例名称：' + get_load_data[i][0])  # 用例名称
        url = get_url + URLConf.PREFIX_ORDER.value + get_load_data[i][1]  # 接口请求uri
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['hmac'] = get_v8_hmac(payload)
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)
        logger.info('响应结果为：' + response.text)  # 打印响应结果
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in ResCode.res_mapping.value.get('success'), '验证通过'
        assert response.json().get('data') in [0, 1]  # 0没有；1为有云服务

    @pytest.mark.cn
    @pytest.mark.parametrize("get_load_data, get_url", [((path, current_file), '')],
                             indirect=["get_load_data", "get_url"])
    def test_013_Renew_Order(self, get_load_data, get_url, i=12):
        """一键续费 接口"""
        allure.dynamic.title(get_load_data[i][0])
        logger.info('用例名称：' + get_load_data[i][0])  # 用例名称
        url = get_url + URLConf.PREFIX_ORDER.value + get_load_data[i][1]  # 接口请求uri
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['beforeOrderCode'] = globals()['user_records'][0]
        payload['hmac'] = get_v8_hmac(payload)
        headers = {'Connection': 'close'}
        response = requests.post(url, headers=headers, data=payload)
        logger.info('响应结果为：' + response.text)  # 打印响应结果
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in ResCode.res_mapping.value.get('success'), '验证通过'  # 订单支付成功后才可续费
        assert response.json().get('data') is not None  # 断言data不为空

    @pytest.mark.cn  # 该用例国内执行
    @pytest.mark.hw  # 该用例海外执行
    @pytest.mark.parametrize("get_load_data, get_url", [((path, current_file), '')],
                             indirect=["get_load_data", "get_url"])
    def test_014_edit_OrderInfo(self, get_load_data, get_url, i=13):
        """oms系统修改订单时间接口"""
        allure.dynamic.title(get_load_data[i][0])
        logger.info('用例名称：' + get_load_data[i][0])  # 用例名称
        url = get_url + URLConf.PREFIX_ORDER.value + get_load_data[i][1]  # 接口请求uri
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data[13][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['orderCode'] = globals()['user_records'][0]
        payload['hmac'] = get_v8_hmac(payload)
        headers = {'Connection': 'close'}
        response = requests.post(url, headers=headers, json=payload)
        logger.info('响应结果为：' + response.text)  # 打印响应结果
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.text in ResCode.res_mapping.value.get('success')

    @pytest.mark.cn  # 该用例国内执行
    @pytest.mark.hw  # 该用例海外执行
    @pytest.mark.parametrize("get_load_data, get_url", [((path, current_file), '')],
                             indirect=["get_load_data", "get_url"])
    def test_015_selectId_Orderstatus(self, get_load_data, get_url, i=14):
        """根据用户id获取用户订单信息"""
        allure.dynamic.title(get_load_data[i][0])
        logger.info('用例名称：' + get_load_data[i][0])  # 用例名称
        url = get_url + URLConf.PREFIX_ORDER.value + get_load_data[i][1]  # 接口请求uri
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['hmac'] = get_v8_hmac(payload)
        headers = {'Connection': 'close'}
        response = requests.post(url, headers=headers, json=payload)
        logger.info('响应结果为：' + response.text)  # 打印响应结果
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in ResCode.res_mapping.value.get('success'), '验证通过'
        assert response.json().get('data') is not None  # 断言data不为空

    @pytest.mark.cn  # 该用例国内执行
    @pytest.mark.hw  # 该用例海外执行
    @pytest.mark.skip('接口在国内没有返回，暂时跳过')
    @pytest.mark.parametrize("get_load_data, get_url", [((path, current_file), '')],
                             indirect=["get_load_data", "get_url"])
    def test_016_nearly_seven_dayOrder(self, get_load_data, get_url, i=15):
        """获取用户近7天过期订单"""
        allure.dynamic.title(get_load_data[i][0])
        logger.info('用例名称：' + get_load_data[i][0])  # 用例名称
        url = get_url + URLConf.PREFIX_ORDER.value + get_load_data[i][1]  # 接口请求uri
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['hmac'] = get_v8_hmac(payload)
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)
        logger.info('响应结果为：' + response.text)  # 打印响应结果
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in [20000, 60204, 60134], '验证通过'
        # 60204/60134--表示该用户近7天没有过期的订单

    @pytest.mark.hw  # 该用例海外执行
    @pytest.mark.parametrize("get_load_data, get_url", [((path, current_file), '')],
                             indirect=["get_load_data", "get_url"])
    def test_018_Order_E911Service(self, get_load_data, get_url, i=17):
        """是否有e911服务"""
        allure.dynamic.title(get_load_data[i][0])
        logger.info('用例名称：' + get_load_data[i][0])  # 用例名称
        url = get_url + URLConf.PREFIX_ORDER.value + get_load_data[i][1]  # 接口请求uri
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['hmac'] = get_v8_hmac(payload)
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)
        logger.info('响应结果为：' + response.text)  # 打印响应结果
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in ResCode.res_mapping.value.get('success'), '验证通过'

    @pytest.mark.hw  # 该用例海外执行
    @pytest.mark.parametrize("get_load_data, get_url", [((path, current_file), '')],
                             indirect=["get_load_data", "get_url"])
    def test_019_Order_Quarterscreen(self, get_load_data, get_url, i=18):
        """用户的下的订单是否支持四分屏"""
        allure.dynamic.title(get_load_data[i][0])
        logger.info('用例名称：' + get_load_data[i][0])  # 用例名称
        url = get_url + URLConf.PREFIX_ORDER.value + get_load_data[i][1]  # 接口请求uri
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['hmac'] = get_v8_hmac(payload)
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)
        logger.info('响应结果为：' + response.text)  # 打印响应结果
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in ResCode.res_mapping.value.get('success'), '验证通过'
        assert response.json().get('data') is not None

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data, get_url", [((path, current_file), '')],
                             indirect=["get_load_data", "get_url"])
    def test_020_product_cloudAndAlarmList(self, get_load_data, get_url, i=20):
        """云存+报警服务组合套餐产品sku列表"""
        allure.dynamic.title(get_load_data[i][0])
        logger.info('用例名称：' + get_load_data[i][0])  # 用例名称
        url = get_url + URLConf.PREFIX_ORDER.value + get_load_data[i][1]  # 接口请求uri
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['hmac'] = get_v8_hmac(payload)
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)
        logger.info('响应结果为：' + response.text)  # 打印响应结果
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in ResCode.res_mapping.value.get('success'), '验证通过'
        assert response.json().get('data') is not None

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data, get_url", [((path, current_file), '')],
                             indirect=["get_load_data", "get_url"])
    def test_021_cloud_deviceList(self, get_load_data, get_url, i=17):
        """通过用户id获取云存设备列表"""
        allure.dynamic.title(get_load_data[i][0])
        url = get_url + URLConf.PREFIX_VAS.value + get_load_data[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['hmac'] = get_v8_hmac(payload)
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)  # 发送get请求
        logger.info('响应结果为：' + response.text)
        data = response.json().get('data')
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in ResCode.res_mapping.value.get('success')
        globals()['devUid'] = data[0]['deviceCloudStatus']['devUid']

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data, get_url", [((path, current_file), '')],
                             indirect=["get_load_data", "get_url"])
    def test_022_product_ListV4(self, get_load_data, get_url, i=21):
        """购买页4.0"""
        allure.dynamic.title(get_load_data[i][0])
        url = get_url + URLConf.PREFIX_ORDER.value + get_load_data[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['uid'] = globals()['devUid']
        payload['hmac'] = get_v8_hmac(payload)
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)  # 发送get请求
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') == 20000
        assert response.json().get('data') is not None

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data, get_url", [((path, current_file), '')],
                             indirect=["get_load_data", "get_url"])
    def test_023_order_detail(self, get_load_data, get_url, i=22):
        '''用户订单详情'''
        allure.dynamic.title(get_load_data[i][0])
        url = get_url + URLConf.PREFIX_ORDER.value + get_load_data[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['orderCode'] = globals()['orderCode']
        payload['hmac'] = get_v8_hmac(payload)
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)  # 发送get请求
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') == 20000
        assert response.json().get('data') is not None

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data, get_url", [((path, current_file), '')],
                             indirect=["get_load_data", "get_url"])
    def test_024_order_getUserSuffix(self, get_load_data, get_url, i=23):
        '''查询配置对应策略的尾号'''
        allure.dynamic.title(get_load_data[i][0])
        url = get_url + URLConf.PREFIX_ORDER.value + get_load_data[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['hmac'] = get_v8_hmac(payload)
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)  # 发送get请求
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') == 20000
        assert response.json().get('data') is not None

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data, get_url", [((path, current_file), '')],
                             indirect=["get_load_data", "get_url"])
    def test_025_getCloudBuyPopWindow(self, get_load_data, get_url, i=24):
        '''进入云存购买页待支付订单>取消自动续费弹窗展示'''
        allure.dynamic.title(get_load_data[i][0])
        url = get_url + URLConf.PREFIX_ORDER.value + get_load_data[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['hmac'] = get_v8_hmac(payload)
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)  # 发送get请求
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') == 20000

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data, get_url", [((path, current_file), '')],
                             indirect=["get_load_data", "get_url"])
    def test_026_batchDevice_list(self, get_load_data, get_url, i=19):
        '''批量设备购买产品列表接口'''
        allure.dynamic.title(get_load_data[i][0])
        url = get_url + URLConf.PREFIX_ORDER.value + get_load_data[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['hmac'] = get_v8_hmac(payload)
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)  # 发送get请求
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') == 20000
        assert response.json().get('data') is not None

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data, get_url", [((path, current_file), '')],
                             indirect=["get_load_data", "get_url"])
    def test_027_product_alarm_list(self, get_load_data, get_url, i=18):
        '''报警产品sku列表'''
        allure.dynamic.title(get_load_data[i][0])
        url = get_url + URLConf.PREFIX_ORDER.value + get_load_data[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['hmac'] = get_v8_hmac(payload)
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)  # 发送get请求
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') == 20000
        assert response.json().get('data') is not None

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data, get_url", [((path, current_file), '')],
                             indirect=["get_load_data", "get_url"])
    def test_028_order_Repurchase_RemindPopWindow(self, get_load_data, get_url, i=25):
        '''复购回流首页弹窗'''
        allure.dynamic.title(get_load_data[i][0])
        url = get_url + URLConf.PREFIX_ORDER.value + get_load_data[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['hmac'] = get_v8_hmac(payload)
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)  # 发送get请求
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') == 20000

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data, get_url", [((path, current_file), '')],
                             indirect=["get_load_data", "get_url"])
    def test_029_product_getManualRenewalSkuInfo(self, get_load_data, get_url, i=26):
        '''获取手动续订sku'''
        allure.dynamic.title(get_load_data[i][0])
        url = get_url + URLConf.PREFIX_ORDER.value + get_load_data[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['hmac'] = get_v8_hmac(payload)
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)  # 发送get请求
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') == 20000
        assert response.json().get('data') is not None

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data, get_url", [((path, current_file), '')],
                             indirect=["get_load_data", "get_url"])
    def test_030_cloudorder_getbanner(self, get_load_data, get_url, i=27):
        '''云服务购买页4.0更多操作下拉弹窗'''
        allure.dynamic.title(get_load_data[i][0])
        url = get_url + URLConf.PREFIX_ORDER.value + get_load_data[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['hmac'] = get_v8_hmac(payload)
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)  # 发送get请求
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') == 20000
        assert response.json().get('data') is not None

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data, get_url", [((path, current_file), '')],
                             indirect=["get_load_data", "get_url"])
    def test_031_SD_bannerisshow(self, get_load_data, get_url, i=28):
        '''查询SD卡格式化失败与损坏ABTEST解决方案按钮是否展示'''
        allure.dynamic.title(get_load_data[i][0])
        url = get_url + URLConf.PREFIX_ORDER.value + get_load_data[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['hmac'] = get_v8_hmac(payload)
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)  # 发送get请求
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') == 20000
        assert response.json().get('data') is not None

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data, get_url", [((path, current_file), '')],
                             indirect=["get_load_data", "get_url"])
    def test_032_SD_jumptosevenday(self, get_load_data, get_url, i=29):
        '''查询SD卡格式化失败与损坏ABTEST是否跳转7天免费页'''
        allure.dynamic.title(get_load_data[i][0])
        url = get_url + URLConf.PREFIX_ORDER.value + get_load_data[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['hmac'] = get_v8_hmac(payload)
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)  # 发送get请求
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') == 20000
        assert response.json().get('data') is not None

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data, get_url", [((path, current_file), '')],
                             indirect=["get_load_data", "get_url"])
    def test_033_isDeviceHasPayOrder(self, get_load_data, get_url, i=30):
        '''查询SD卡格式化失败与损坏ABTEST是否跳转7天免费页'''
        allure.dynamic.title(get_load_data[i][0])
        url = get_url + URLConf.PREFIX_ORDER.value + get_load_data[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['hmac'] = get_v8_hmac(payload)
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)  # 发送get请求
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') == 20000
        assert response.json().get('data') is not None

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data, get_url", [((path, current_file), '')],
                             indirect=["get_load_data", "get_url"])
    def test_034_openSmartAlarmFunction(self, get_load_data, get_url, i=31):
        '''查询用户是否开放智能报警功能'''
        allure.dynamic.title(get_load_data[i][0])
        url = get_url + URLConf.PREFIX_ORDER.value + get_load_data[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['hmac'] = get_v8_hmac(payload)
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)  # 发送get请求
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') == 20000
        assert response.json().get('data') is not None

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data, get_url", [((path, current_file), '')],
                             indirect=["get_load_data", "get_url"])
    def test_035_getProductListV4Banner(self, get_load_data, get_url, i=32):
        '''获取云回放页4.0配置banner的图片和Url'''
        allure.dynamic.title(get_load_data[i][0])
        url = get_url + URLConf.PREFIX_ORDER.value + get_load_data[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['hmac'] = get_v8_hmac(payload)
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)  # 发送get请求
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') == 20000
        assert response.json().get('data') is not None

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data, get_url", [((path, current_file), '')],
                             indirect=["get_load_data", "get_url"])
    def test_035_getCloudPageOptimizationConfig(self, get_load_data, get_url, i=33):
        '''云回放页面优化人群配置'''
        allure.dynamic.title(get_load_data[i][0])
        url = get_url + URLConf.PREFIX_ORDER.value + get_load_data[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['hmac'] = get_v8_hmac(payload)
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)  # 发送get请求
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') == 20000
        assert response.json().get('data') is not None

    @pytest.mark.cn
    @pytest.mark.hw
    # @pytest.mark.skip('暂时跳过')
    @pytest.mark.parametrize("get_load_data, get_url", [((path, current_file), '')],
                             indirect=["get_load_data", "get_url"])
    def test_035_getCloudPageOptimizationConfig(self, get_load_data, get_url, i=34):
        '''订单挽留页用户领取优惠券'''
        allure.dynamic.title(get_load_data[i][0])
        url = get_url + URLConf.PREFIX_ORDER.value + get_load_data[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['orderCode'] = globals()['orderCode']
        payload['hmac'] = get_v8_hmac(payload)
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.post(url, headers=headers, data=payload)
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        # assert response.json().get('code') == 20000
        # assert response.json().get('data') is not None
