#!/usr/bin/python3
# -*- coding:utf-8 -*-

"""
@author: 
@file: test_order_alipay.py
@time: 2021/6/4 14:12
@desc: 
"""
import base64
import hashlib
import hmac
import os
import time
import allure
import pytest
import logging
import requests
from alipay import *
from selenium import webdriver
import platform
sys = platform.system()
import time
from config.response_code import ResCode
from config.url_config import URLConf
from fixture.get_hmac_fixture import get_sign


logger = logging.getLogger(__name__)
# test_data所在路径 如：D:\yi_api_test_profess\test_data
path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'test_data')
current_file = os.path.basename(__file__)  # 当前文件名称 如: test_order_profess.py
data_folder = os.path.join(path, current_file.strip('.py'))  # 当前文件对应的数据文件的目录名称

oms_url = "http://47.116.14.210:8350"


def get_v8_hmac(params):
    """SHA1加密
    return:加密结果转成16进制字符串形式
    """
    str1 = ["{0}={1}".format(k, v) for k, v in params.items()]  # 使用 = 拼接dict数据（key,values）
    str1.sort()  # 按照字母序进行排序
    res = "&".join(str1)  # 使用 & 拼接数据
    message = res.encode('utf-8')
    key = globals()['sign_value1'].encode('utf-8')
    sign1 = hmac.new(key, message, digestmod=hashlib.sha1)  # 使用sha1进行加密
    sign = base64.b64encode(sign1.digest()).decode()  # 使用base64进行转码
    return sign


# 沙箱环境中 app 私钥
app_private_key_string = open('app_private_key.pem').read()

# alipay_public_key.pem   支付宝公钥
alipay_public_key_string = open('alipay_public_key.pem').read()

@allure.story('支付宝购买购买云存服务')
# 使用支付宝支付，创建订单全流程,放在类上面，失败重跑三次，间隔2s，如果成功了，则成功。
@pytest.mark.flaky(reruns=3, reruns_delay=2)
class TestZFBpayProfess(object):
    @pytest.fixture(scope='function', autouse=True)
    def setup_teardown(self):
        """
        此方法包括了前置和后置，可以传入参数
        :return:
        """
        logger.info('\n===============setup===============')
        yield
        logger.info('\n===============teardown============')

    @pytest.mark.run(order=1)
    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_oms", [(path, current_file)], indirect=["get_load_data_oms"])
    def test_001_oauth_token(self, get_load_data_oms, i=0):
        """获取 access_token"""
        allure.dynamic.title('01'+get_load_data_oms[i][0])  # allure动态获取 用例名称
        url = get_load_data_oms[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_oms[i][-1])  # 参数类型为dict
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.post(url, headers=headers, data=payload)  # 发送post请求
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('access_token') is not None
        globals()['access_token1'] = response.json().get('access_token')
        logger.info('access_token为：' + globals()['access_token1'])

    @pytest.mark.run(order=2)
    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_oms", [(path, current_file)], indirect=["get_load_data_oms"])
    def test_002_oms_users_current(self, get_load_data_oms, i=1):
        """根据access_token获取 当前登录用户"""
        allure.dynamic.title('02'+get_load_data_oms[i][0])  # allure动态获取 用例名称
        url = oms_url + get_load_data_oms[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_oms[i][-1])  # 参数类型为dict
        payload['access_token'] = globals()['access_token1']
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)  # 发送get请求
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in ResCode.res_mapping.value.get('success')  # 断言响应code=20000
        # assert response.json().get('data').get('username') in ['dong.yu']  # 断言用户名是否为预期值
        assert response.json().get('data').get('username') in ['zhang.yongfeng']  # 断言用户名是否为预期值

    # @pytest.mark.skip
    # @pytest.mark.run(order=3)
    # @pytest.mark.cn
    # @pytest.mark.parametrize("get_load_data_oms", [(path, current_file)], indirect=["get_load_data_oms"])
    # def test_003_oms_addSkuChannel(self, get_load_data_oms, i=2):
    #     """创建channel, 状态为有效(1-有效，0-无效)"""
    #     allure.dynamic.title(get_load_data_oms[i][0])  # allure动态获取 用例名称
    #     url = oms_url + get_load_data_oms[i][1]
    #     logger.info('请求地址为：' + url)
    #     payload = eval(get_load_data_oms[i][-1])  # 参数类型为dict
    #     payload['name'] = 'auto_test4'
    #     logger.info('请求参数为：' + str(payload))
    #     headers = {'Authorization': 'Bearer ' + globals()['access_token1']}
    #     response = requests.post(url, headers=headers, json=payload)  # 发送post请求
    #     logger.info('响应结果为：' + response.text)
    #     assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
    #     assert response.json().get('code') in ResCode.res_mapping.value.get('success')  # 断言响应code=20000

    @pytest.mark.run(order=4)
    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_oms", [(path, current_file)], indirect=["get_load_data_oms"])
    def test_004_oms_getSkuChannelPage(self, get_load_data_oms, i=3):
        """分页查询skuChannel列表(即：查询新建channel ID)"""
        allure.dynamic.title('04'+get_load_data_oms[i][0])  # allure动态获取 用例名称
        url = oms_url + get_load_data_oms[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_oms[i][-1])  # 参数类型为dict
        logger.info('请求参数为：' + str(payload))
        headers = {'Authorization': 'Bearer ' + globals()['access_token1']}
        response = requests.get(url, headers=headers, params=payload)  # 发送get请求
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in ResCode.res_mapping.value.get('success')  # 断言响应code=20000
        res_data = response.json().get('data').get('records')
        if res_data:  # 断言响应data字段值不为空
            globals()['channel_id1'] = [i['id'] for i in res_data if i['name'] == 'auto_test5']
            logger.info(globals()['channel_id1'][0])

    # @pytest.mark.run(order=5)
    # @pytest.mark.cn
    # @pytest.mark.hw
    # @pytest.mark.parametrize("get_load_data_oms", [(path, current_file)], indirect=["get_load_data_oms"])
    # def test_005_oms_channel_detail(self, get_load_data_oms, i=4):
    #     """查看指定channel详情(按channel id查询)"""
    #     allure.dynamic.title('05'+get_load_data_oms[i][0])  # allure动态获取 用例名称
    #     url = oms_url + get_load_data_oms[i][1]
    #     logger.info('请求地址为：' + url)
    #     payload = eval(get_load_data_oms[i][-1])  # 参数类型为dict
    #     payload['id'] = globals()['channel_id1'][0]
    #     logger.info('请求参数为：' + str(payload))
    #     headers = {'Authorization': 'Bearer ' + globals()['access_token1']}
    #     response = requests.get(url, headers=headers, params=payload)  # 发送get请求
    #     logger.info('响应结果为：' + response.text)
    #     assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
    #     assert response.json().get('code') in ResCode.res_mapping.value.get('success')  # 断言响应code=20000
    #     res_data = response.json().get('data')
    #     assert res_data['id'] == globals()['channel_id1'][0]
    #     assert res_data['name'] == 'auto_test5'
    #     assert res_data['status'] in [0, 1]  #
    #     assert res_data['appSystem'] in [1, 2, 3]  #

    # @pytest.mark.run(order=6)
    # @pytest.mark.cn
    # @pytest.mark.hw
    # @pytest.mark.parametrize("get_load_data_oms", [(path, current_file)], indirect=["get_load_data_oms"])
    # def test_006_oms_channel_edit(self, get_load_data_oms, i=5):
    #     """更新channel信息(name、Region、Status、Description)"""
    #     allure.dynamic.title('06'+get_load_data_oms[i][0])  # allure动态获取 用例名称
    #     url = oms_url + get_load_data_oms[i][1]
    #     logger.info('请求地址为：' + url)
    #     payload = eval(get_load_data_oms[i][-1])  # 参数类型为dict
    #     payload['id'] = globals()['channel_id1'][0]
    #     payload['status'] = 1  # 1-有效，0-无效
    #     logger.info('请求参数为：' + str(payload))
    #     headers = {'Authorization': 'Bearer ' + globals()['access_token1']}
    #     response = requests.post(url, headers=headers, json=payload)  # 发送post请求
    #     logger.info('响应结果为：' + response.text)
    #     assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
    #     assert response.json().get('code') in ResCode.res_mapping.value.get('success')  # 断言响应code=20000

    # @pytest.mark.run(order=7)
    # @pytest.mark.cn
    # @pytest.mark.hw
    # @pytest.mark.parametrize("get_load_data_oms", [(path, current_file)], indirect=["get_load_data_oms"])
    # def test_007_oms_channel_EditDetail(self, get_load_data_oms, i=4):
    #     """查看指定channel的更新信息(按channel id查询)"""
    #     allure.dynamic.title(get_load_data_oms[i][0])  # allure动态获取 用例名称
    #     url = oms_url + get_load_data_oms[i][1]
    #     logger.info('请求地址为：' + url)
    #     payload = eval(get_load_data_oms[i][-1])  # 参数类型为dict
    #     payload['id'] = globals()['channel_id1'][0]
    #     logger.info('请求参数为：' + str(payload))
    #     headers = {'Authorization': 'Bearer ' + globals()['access_token1']}
    #     response = requests.get(url, headers=headers, params=payload)  # 发送get请求
    #     logger.info('响应结果为：' + response.text)
    #     assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
    #     assert response.json().get('code') in ResCode.res_mapping.value.get('success')  # 断言响应code=20000
    #     res_data = response.json().get('data')
    #     assert res_data['id'] == globals()['channel_id1'][0]
    #     assert res_data['status'] == 1

    # @pytest.mark.skip
    # @pytest.mark.run(order=8)
    # @pytest.mark.cn
    # @pytest.mark.parametrize("get_load_data_oms", [(path, current_file)], indirect=["get_load_data_oms"])
    # def test_008_oms_addSku(self, get_load_data_oms, i=6):
    #     """创建sku信息, 状态为有效(1-有效，0-无效)"""
    #     allure.dynamic.title(get_load_data_oms[i][0])  # allure动态获取 用例名称
    #     url = oms_url + get_load_data_oms[i][1]
    #     logger.info('请求地址为：' + url)
    #     payload = eval(get_load_data_oms[i][-1])  # 参数类型为dict
    #     payload['skuName'] = 'auto_test4'
    #     logger.info('请求参数为：' + str(payload))
    #     headers = {'Authorization': 'Bearer ' + globals()['access_token1']}
    #     response = requests.post(url, headers=headers, json=payload)  # 发送post请求
    #     logger.info('响应结果为：' + response.text)
    #     assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
    #     assert response.json().get('code') in ResCode.res_mapping.value.get('success')  # 断言响应code=20000
    # @pytest.mark.skip
    # @pytest.mark.run(order=9)
    # @pytest.mark.cn
    # @pytest.mark.hw
    # @pytest.mark.parametrize("get_load_data_oms", [(path, current_file)], indirect=["get_load_data_oms"])
    # def test_009_oms_skus(self, get_load_data_oms, i=7):
    #     """分页查询产品sku列表(即：查询新建sku ID)"""
    #     allure.dynamic.title('09'+get_load_data_oms[i][0])  # allure动态获取 用例名称
    #     url = oms_url + get_load_data_oms[i][1]
    #     logger.info('请求地址为：' + url)
    #     payload = eval(get_load_data_oms[i][-1])  # 参数类型为dict
    #     logger.info('请求参数为：' + str(payload))
    #     headers = {'Authorization': 'Bearer ' + globals()['access_token1']}
    #     response = requests.get(url, headers=headers, params=payload)  # 发送get请求
    #     logger.info('响应结果为：' + response.text)
    #     assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
    #     assert response.json().get('code') in ResCode.res_mapping.value.get('success')  # 断言响应code=20000
    #     # res_data = response.json().get('data').get('records')
    #     # if res_data:  # 断言响应data字段值不为空
    #     #     globals()['sku_id1'] = [i['id'] for i in res_data if i['skuName'] == 'auto_test5']
    #     #     logger.info(globals()['sku_id1'][0])

    # @pytest.mark.skip
    # @pytest.mark.run(order=10)
    # @pytest.mark.cn
    # @pytest.mark.hw
    # @pytest.mark.parametrize("get_load_data_oms", [(path, current_file)], indirect=["get_load_data_oms"])
    # def test_010_oms_getProductSkuDetail(self, get_load_data_oms, i=8):
    #     """查看指定sku详情(按sku id查询)"""
    #     allure.dynamic.title('10'+get_load_data_oms[i][0])  # allure动态获取 用例名称
    #     url = oms_url + get_load_data_oms[i][1]
    #     logger.info('请求地址为：' + url)
    #     payload = eval(get_load_data_oms[i][-1])  # 参数类型为dict
    #     payload['skuId'] = 1353
    #     logger.info('请求参数为：' + str(payload))
    #     headers = {'Authorization': 'Bearer ' + globals()['access_token1']}
    #     response = requests.get(url, headers=headers, params=payload)  # 发送get请求
    #     logger.info('响应结果为：' + response.text)
    #     assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
    #     assert response.json().get('code') in ResCode.res_mapping.value.get('success')  # 断言响应code=20000
    #     res_data = response.json().get('data')
    #     assert res_data['id'] == 1353
    #     assert res_data['skuName'] == eval(get_load_data_oms[6][-1])['skuName']
    #     assert res_data['status'] == 1  # 上架-1, 下架-0
    #     assert res_data['appSystem'] == eval(get_load_data_oms[6][-1])['appSystem']  #
    #     # assert res_data['price'] == eval(get_load_data_oms[6][-1])['price']

    # @pytest.mark.skip
    # @pytest.mark.run(order=11)
    # @pytest.mark.cn
    # @pytest.mark.parametrize("get_load_data_oms", [(path, current_file)], indirect=["get_load_data_oms"])
    # def test_011_oms_sku_change(self, get_load_data_oms, i=9):
    #     """channel下sku变更(添加/移除)"""
    #     allure.dynamic.title(get_load_data_oms[i][0])  # allure动态获取 用例名称
    #     url = oms_url + get_load_data_oms[i][1]
    #     logger.info('请求地址为：' + url)
    #     payload = eval(get_load_data_oms[i][-1])  # 参数类型为dict
    #     payload['skuIds'] = globals()['sku_id1']
    #     payload['channelId'] = globals()['channel_id1'][0]
    #     payload['changer'] = 1  # changer(0-移除，1-添加)
    #     logger.info('请求参数为：' + str(payload))
    #     headers = {'Authorization': 'Bearer ' + globals()['access_token1']}
    #     response = requests.post(url, headers=headers, json=payload)  # 发送post请求
    #     logger.info('响应结果为：' + response.text)
    #     assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
    #     assert response.json().get('code') in ResCode.res_mapping.value.get('success')  # 断言响应code=20000

    # @pytest.mark.skip
    # @pytest.mark.run(order=12)
    # @pytest.mark.cn
    # @pytest.mark.hw
    # @pytest.mark.parametrize("get_load_data_oms", [(path, current_file)], indirect=["get_load_data_oms"])
    # def test_012_oms_Cskus(self, get_load_data_oms, i=10):
    #     """查询channel下sku信息"""
    #     allure.dynamic.title('12'+get_load_data_oms[i][0])  # allure动态获取 用例名称
    #     url = oms_url + get_load_data_oms[i][1]
    #     logger.info('请求地址为：' + url)
    #     payload = eval(get_load_data_oms[i][-1])  # 参数类型为dict
    #     payload['channelId'] = globals()['channel_id1'][0]
    #     logger.info('请求参数为：' + str(payload))
    #     headers = {'Authorization': 'Bearer ' + globals()['access_token1']}
    #     response = requests.get(url, headers=headers, params=payload)  # 发送get请求
    #     logger.info('响应结果为：' + response.text)
    #     assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
    #     assert response.json().get('code') in ResCode.res_mapping.value.get('success')  # 断言响应code=20000

    @pytest.mark.run(order=13)
    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_oms, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_oms", "get_url"])
    def test_013_user_Login(self, get_load_data_oms, get_url, i=11):
        """用户登录接口"""
        allure.dynamic.title('13'+get_load_data_oms[i][0])
        url = get_url + get_load_data_oms[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_oms[i][-1])  # 参数类型为dict
        payload['password'] = get_sign(payload['password'])
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)  # 发送get请求
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in ResCode.res_mapping.value.get('success'), '验证通过'
        assert response.json().get('data') is not None
        if response.json().get('code') in ResCode.res_mapping.value.get('success'):
            globals()['sign_value1'] = response.json().get('data').get('token') + '&' \
                                       + response.json().get('data').get('token_secret')
            globals()['userId1'] = response.json().get('data').get('userid')

    @pytest.mark.run(order=14)
    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_oms, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_oms", "get_url"])
    def test_014_Product_List_cn(self, get_load_data_oms, get_url, i=12):
        """查询产品列表信息"""
        allure.dynamic.title('14'+get_load_data_oms[i][0])  # allure动态获取 用例名称
        url = get_url + URLConf.PREFIX_ORDER.value + get_load_data_oms[i][1]  # 接口请求uri
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_oms[i][-1])  # 参数类型为dict
        payload['channel'] = globals()['channel_id1'][0]
        payload['userid'] = globals()['userId1']
        payload['hmac'] = get_v8_hmac(payload)
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)  # 发送get请求
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in ResCode.res_mapping.value.get('success')  # 断言响应code=20000
        res_data = response.json().get('data')
        if res_data:
            productsDtos = res_data['productsDtos']
            globals()['prod_skuid_value1'] = [[productsDtos[i]['skuId'], productsDtos[i]['price']] for i in
                                              range(len(productsDtos))]
            # print(globals()['prod_skuid_value'])

    @pytest.mark.run(order=15)
    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_oms, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_oms", "get_url"])
    def test_015_create_Token(self, get_load_data_oms, get_url, i=13):
        """创建订单Token接口"""
        allure.dynamic.title('15'+get_load_data_oms[i][0])
        url = get_url + URLConf.PREFIX_ORDER.value + get_load_data_oms[i][1]  # 接口请求uri
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_oms[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId1']
        payload['hmac'] = get_v8_hmac(payload)
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)  # 发送get请求
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in ResCode.res_mapping.value.get('success'), '验证通过'
        assert response.json().get('data') is not None  # 断言响应token字段值不为空
        globals()['token1'] = response.json().get('data')

    @pytest.mark.run(order=16)
    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_oms, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_oms", "get_url"])
    def test_016_create_Order(self, get_load_data_oms, get_url, i=14):
        """创建订单接口"""
        allure.dynamic.title('16'+get_load_data_oms[i][0])
        url = get_url + URLConf.PREFIX_ORDER.value + get_load_data_oms[i][1]  # 接口请求uri
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_oms[i][-1])  # 参数类型为dict
        payload['token'] = globals()['token1']
        payload['userid'] = globals()['userId1']
        payload['channel'] = globals()['channel_id1'][0]
        payload['skuId'] = globals()['prod_skuid_value1'][0][0]
        payload['hmac'] = get_v8_hmac(payload)
        headers = {'Connection': 'close'}
        response = requests.post(url, headers=headers, data=payload)  # 发送post请求
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求状态码为 200
        assert response.json().get('code') in ResCode.res_mapping.value.get('success'), '验证通过'  # 断言响应code为 20000
        assert response.json().get('data').get('orderCode') is not None  # 断言响应orderCode字段值不为空
        globals()['orderCode1'] = response.json().get('data').get('orderCode')

    @pytest.mark.run(order=17)
    @pytest.mark.cn
    @pytest.mark.parametrize("get_load_data_oms, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_oms", "get_url"])
    def test_017_query_initialCode(self, get_load_data_oms, get_url, i=15):
        """查询初始化 订单状态接口 10"""
        allure.dynamic.title('17'+get_load_data_oms[i][0])
        url = get_url + URLConf.PREFIX_ORDER.value + get_load_data_oms[i][1]  # 接口请求uri
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_oms[i][-1])  # 参数类型为dict
        # 更新请求原数据的code值
        payload['code'] = globals()['orderCode1']
        payload['userid'] = globals()['userId1']
        payload['hmac'] = get_v8_hmac(payload)
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)
        logger.info('响应结果为：' + response.text)  # 打印响应结果
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in ResCode.res_mapping.value.get('success'), '验证通过'  # 断言响应code为 20000
        assert response.json().get('data') in [10, '10'], '订单状态为 未支付 10'  # 断言响应status为 10

    @pytest.mark.run(order=18)
    @pytest.mark.cn
    @pytest.mark.parametrize("get_load_data_oms, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_oms", "get_url"])
    def test_018_zfbPay_Order(self, get_load_data_oms, get_url, i=19):
        """支付宝支付接口"""
        allure.dynamic.title('18'+get_load_data_oms[i][0])
        url = get_url + URLConf.PREFIX_ORDER.value + get_load_data_oms[i][1]  # 接口请求uri
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_oms[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId1']
        payload['orderCode'] = globals()['orderCode1']
        payload['hmac'] = get_v8_hmac(payload)
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)
        logger.info('响应结果为：' + response.text)  # 打印响应结果
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in ResCode.res_mapping.value.get('success'), '验证通过'


    @pytest.mark.cn
    @pytest.mark.run(order=-3)
    @pytest.mark.flaky(reruns=5, reruns_delay=3)
    @pytest.mark.parametrize("get_load_data_oms, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_oms", "get_url"])
    def test_019_alipay(self,get_load_data_oms, get_url, i=19):
        """支付宝支付"""
        allure.dynamic.title("19选择支付宝支付")
        alipay = AliPay(
            appid="2016102400750431",  # 创建的沙箱环境的appid
            app_notify_url='https://openapi-cn-test.xiaoyi.com/orderpay/v8/ali/pay/callback',  # 设置为后台回调地址
            app_private_key_string=app_private_key_string,  # 支付宝的公钥，验证支付宝回传消息使用,不是你自己的公钥
            alipay_public_key_string=app_private_key_string,
            sign_type="RSA",  # RSA 或者 RSA2
            debug=True,  # 默认False,我们是沙箱，所以改成True(让访问沙箱环境支付宝地址)
        )

        # 电脑网站支付，需要跳转到https://openapi.alipay.com/gateway.do? + order_string
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=globals()['orderCode1'],  # 订单id，应该从前端获取
            total_amount=str(2.01),  # 订单总金额 支付宝 是 2.01
            subject="高级_连续包月",  # 付款标题信息
            return_url=None,  # 付款成功回调地址(可以为空)
            notify_url=None  # 付款成功后异步通知地址（可以为空）
        )
        pay_url = "https://openapi.alipaydev.com/gateway.do?" + order_string
        print(pay_url)  # 将这个url复制到浏览器，就会打开支付宝支付页面
        # 实例化浏览器
        if "Windows" in sys:
            driver = webdriver.Chrome()
        else:
            # firefox
            time.sleep(2)
            options = webdriver.FirefoxOptions()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            driver = webdriver.Firefox(options=options)
            # chrome
            # driver = webdriver.ChromeOptions()
            # # driver.add_argument('headless')   #设置无界面 ，
            # driver.add_argument('no-sandbox')
            # driver.add_argument('disable-dev-shm-usage')
            # driver = webdriver.Chrome('/usr/bin/chromedriver', options=driver)
        # 请求支付网站
        driver.get(pay_url)
        time.sleep(5)
        # 输入账号
        driver.find_element_by_xpath('//*[@id="J_tLoginId"]').send_keys('meassh9032@sandbox.com')
        time.sleep(1)
        # 输入密码
        driver.find_element_by_xpath('//*[@id="payPasswd_rsainput"]').send_keys('111111')
        time.sleep(1)
        # 点击下一步
        driver.find_element_by_xpath('//*[@id="J_newBtn"]/span').click()
        time.sleep(5)
        # 获取所有的窗口句柄
        handles = driver.window_handles
        # 切换到最新打开的窗口
        driver.switch_to.window(handles[-1])
        # search_window = driver.current_window_handle  # 此行代码用来定位当前页面
        time.sleep(3)
        # 输入支付宝支付密码
        driver.find_element_by_id('payPassword_rsainput').send_keys('111111')
        time.sleep(3)
        # 点击确认按钮
        driver.find_element_by_xpath('//*[@id="J_authSubmit"]').click()
        time.sleep(5)

    # @pytest.mark.run(order=20)
    # @pytest.mark.cn  # 该用例国内执行
    # @pytest.mark.hw  # 该用例海外执行
    # @pytest.mark.parametrize("get_load_data_oms, get_url", [((path, current_file), '')],
    #                          indirect=["get_load_data_oms", "get_url"])
    # def test_020_edit_OrderInfo(self, get_load_data_oms, get_url, i=17):
    #     """oms系统修改订单结束时间，同步给vas服务"""
    #     allure.dynamic.title(get_load_data_oms[i][0])
    #     url = get_url + URLConf.PREFIX_ORDER.value + get_load_data_oms[i][1]  # 接口请求uri
    #     logger.info('请求地址为：' + url)
    #     payload = eval(get_load_data_oms[i][-1])  # 参数类型为dict
    #     payload['userid'] = globals()['userId1']
    #     payload['orderCode'] = globals()['orderCode1']
    #     payload['hmac'] = get_v8_hmac(payload)
    #     headers = {'Connection': 'close'}
    #     response = requests.post(url, headers=headers, json=payload)
    #     logger.info('响应结果为：' + response.text)  # 打印响应结果
    #     assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
    #     assert response.text in ResCode.res_mapping.value.get('success')


    @pytest.mark.flaky(reruns=3, reruns_delay=1)
    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_oms, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_oms", "get_url"])
    def test_021_userOrder_detail(self, get_load_data_oms, get_url, i=18):
        """用户订单详情 接口"""
        allure.dynamic.title('21'+get_load_data_oms[i][0])
        url = get_url + URLConf.PREFIX_ORDER.value + get_load_data_oms[i][1]  # 接口请求uri
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_oms[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId1']
        payload['orderCode'] = globals()['orderCode1']
        payload['hmac'] = get_v8_hmac(payload)
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)
        logger.info('响应结果为：' + response.text)  # 打印响应结果
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in ResCode.res_mapping.value.get('success'), '验证通过'
        res_data = response.json().get('data')
        if res_data:
            assert res_data['code'] == globals()['orderCode1']
            assert res_data['payStatus'] == 30  # 30-支付成功状态
            assert res_data['payType'] == 10  # 10-表示支付宝支付
            assert res_data['payAmount'] == 201  # 201-表示支付金额

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_oms, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_oms", "get_url"])
    def test_022_cloud_serviceByOrderCode(self, get_load_data_oms, get_url, i=20):
        """通过订单号查询-云存服务"""
        allure.dynamic.title('22'+get_load_data_oms[i][0])
        url = get_url + URLConf.PREFIX_VAS.value + get_load_data_oms[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_oms[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId1']
        payload['orderCode'] = globals()['orderCode1']
        payload['hmac'] = get_v8_hmac(payload)
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)  # 发送get请求
        logger.info('响应结果为：' + response.text)
        res = response.json().get('data')
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in ResCode.res_mapping.value.get('success'), '验证通过'
        if res:  # 断言响应data字段值不为空  ,此处开始的订单是在订单号码中存在
            assert res[0]['orderCode'] in globals()['orderCode1']
        globals()['businessOrderCode1'] = res[0]['businessOrderCode']  # 10020210326143139934757816

    # @pytest.mark.cn
    # @pytest.mark.hw
    # @pytest.mark.parametrize("get_load_data_oms, get_url", [((path, current_file), '')],
    #                          indirect=["get_load_data_oms", "get_url"])
    # def test_023_cloud_deviceList(self, get_load_data_oms, get_url, i=21):
    #     """通过用户id获取云存设备列表"""
    #     allure.dynamic.title('23'+get_load_data_oms[i][0])
    #     url = get_url + URLConf.PREFIX_VAS.value + get_load_data_oms[i][1]
    #     logger.info('请求地址为：' + url)
    #     payload = eval(get_load_data_oms[i][-1])  # 参数类型为dict
    #     payload['userid'] = globals()['userId1']
    #     payload['hmac'] = get_v8_hmac(payload)
    #     logger.info('请求参数为：' + str(payload))
    #     headers = {'Connection': 'close'}
    #     response = requests.get(url, headers=headers, params=payload)  # 发送get请求
    #     logger.info('响应结果为：' + response.text)
    #     data = response.json().get('data')
    #     assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
    #     assert response.json().get('code') in ResCode.res_mapping.value.get('success')
    #     globals()['devUid1'] = data[0]['eiNumber']

    # @pytest.mark.skip
    # @pytest.mark.cn
    # @pytest.mark.hw
    # @pytest.mark.parametrize("get_load_data_oms, get_url", [((path, current_file), '')],
    #                          indirect=["get_load_data_oms", "get_url"])
    # def test_024_cloud_setBind(self, get_load_data_oms, get_url, i=22):
    #     """设备绑定/解绑业务订单-从Url获取参数"""
    #     allure.dynamic.title(get_load_data_oms[i][0])
    #     url = get_url + URLConf.PREFIX_VAS.value + get_load_data_oms[i][1]
    #     logger.info('请求地址为：' + url)
    #     payload = eval(get_load_data_oms[i][-1])  # 参数类型为dict
    #     payload['userid'] = globals()['userId1']
    #     payload['businessOrderCode'] = globals()['businessOrderCode1']
    #     payload['devUid'] = globals()['devUid1']
    #     payload['hmac'] = get_v8_hmac(payload)
    #     logger.info('请求参数为：' + str(payload))
    #     headers = {'Connection': 'close'}
    #     response = requests.put(url, headers=headers, data=payload)  # 发送get请求
    #     logger.info('响应结果为：' + response.text)
    #     assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
    #     assert response.json().get('code') in ResCode.res_mapping.value.get('success')  # 断言响应code==20000
    #
    # @pytest.mark.skip
    # @pytest.mark.cn
    # @pytest.mark.hw
    # @pytest.mark.parametrize("get_load_data_oms, get_url", [((path, current_file), '')],
    #                          indirect=["get_load_data_oms", "get_url"])
    # def test_025_cloud_deviceStatus(self, get_load_data_oms, get_url, i=23):
    #     """设备状态"""
    #     allure.dynamic.title(get_load_data_oms[i][0])
    #     url = get_url + URLConf.PREFIX_VAS.value + get_load_data_oms[i][1]
    #     logger.info('请求地址为：' + url)
    #     payload = eval(get_load_data_oms[i][-1])  # 参数类型为dict
    #     payload['userid'] = globals()['userId1']
    #     payload['uid'] = globals()['devUid1']
    #     payload['hmac'] = get_v8_hmac(payload)
    #     logger.info('请求参数为：' + str(payload))
    #     headers = {'Connection': 'close'}
    #     response = requests.get(url, headers=headers, params=payload)  # 发送get请求
    #     logger.info('响应结果为：' + response.text)
    #     assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
    #     assert response.json().get('code') in ResCode.res_mapping.value.get('success')  # 断言响应code==20000
    #
    # @pytest.mark.skip
    # @pytest.mark.cn
    # @pytest.mark.hw
    # @pytest.mark.parametrize("get_load_data_oms, get_url", [((path, current_file), '')],
    #                          indirect=["get_load_data_oms", "get_url"])
    # def test_026_cloud_status(self, get_load_data_oms, get_url, i=24):
    #     """设备云存订单状态（业务订单状态、设备设置状态）"""
    #     allure.dynamic.title(get_load_data_oms[i][0])
    #     url = get_url + URLConf.PREFIX_VAS.value + get_load_data_oms[i][1]
    #     logger.info('请求地址为：' + url)
    #     payload = eval(get_load_data_oms[i][-1])  # 参数类型为dict
    #     payload['userid'] = globals()['userId1']
    #     payload['uid'] = globals()['devUid1']
    #     payload['hmac'] = get_v8_hmac(payload)
    #     logger.info('请求参数为：' + str(payload))
    #     headers = {'Connection': 'close'}
    #     response = requests.get(url, headers=headers, params=payload)  # 发送get请求
    #     logger.info('响应结果为：' + response.text)
    #     assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
    #     assert response.json().get('code') in ResCode.res_mapping.value.get('success')
    #     res = response.json().get('data')
    #     if res:
    #         assert res['businessOrderCode'] == globals()['businessOrderCode1']
    #         assert res['businessType'] in [1, 2]  # 云存订单-1,
    #         assert res['state'] in [1, 2]  # 绑定-1, 解绑-2

    #  最后三条 case


if __name__ == '__main__':
    pytest.main(['-v', '-s'])
