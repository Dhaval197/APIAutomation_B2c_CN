# !/usr/bin/python3
# -*- coding: utf-8 -*-
import base64
import hashlib
import hmac
import os
import allure
import pytest
import logging
import requests
from xml.dom.minidom import parse
import xml.dom.minidom
from config.response_code import ResCode
from config.url_config import URLConf
from fixture.get_hmac_fixture import get_sign
from alipay import *

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


@allure.story('微信购买购买云存服务')
@pytest.mark.flaky(reruns=3, reruns_delay=1)
# 使用微信客户端支付，创建订单全流程
class TestWXpayProfess(object):
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

    @pytest.mark.run(order=1)
    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_oms", [(path, current_file)], indirect=["get_load_data_oms"])
    def test_001_oauth_token(self, get_load_data_oms, eurl, i=0):
        """获取 access_token"""
        allure.dynamic.title('01' + get_load_data_oms[i][0])  # allure动态获取 用例名称
        # url = get_load_data_oms[i][1]
        if eurl == 'cn_test':
            url = 'http://oms-oauth.sh-test.xiaoyi.com/oauth/token'
        else:
            url = 'http://47.88.29.148:38080/oauth/token'

        logger.info('请求地址为：'+ url)
        payload = eval(get_load_data_oms[i][-1])  # 参数类型为dict
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.post(url, headers=headers, data=payload)  # 发送post请求
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('access_token') is not None
        globals()['access_token'] = response.json().get('access_token')
        logger.info('access_token为：' + globals()['access_token'])

    @pytest.mark.run(order=2)
    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_oms", [(path, current_file)], indirect=["get_load_data_oms"])
    def test_002_oms_users_current(self, get_load_data_oms, eurl, i=1):
        """根据access_token获取 当前登录用户"""
        allure.dynamic.title('02' + get_load_data_oms[i][0])  # allure动态获取 用例名称

        if eurl == 'cn_test':
            oms_url = "http://oms-service.sh-test.xiaoyi.com"
        else:
            oms_url = "http://47.88.29.148:38081"

        url = oms_url + get_load_data_oms[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_oms[i][-1])  # 参数类型为dict
        payload['access_token'] = globals()['access_token']
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)  # 发送get请求
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in ResCode.res_mapping.value.get('success')  # 断言响应code=20000
        # assert response.json().get('data').get('username') == 'dong.yu'  # 断言用户名是否为预期值
        assert response.json().get('data').get('username') == 'zhang.yongfeng'  # 断言用户名是否为预期值

    @pytest.mark.run(order=4)
    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_oms", [(path, current_file)], indirect=["get_load_data_oms"])
    def test_004_oms_getSkuChannelPage(self, get_load_data_oms, eurl, i=3):
        """分页查询skuChannel列表(即：查询新建channel ID)"""
        allure.dynamic.title('04' + get_load_data_oms[i][0])  # allure动态获取 用例名称
        if eurl == 'cn_test':  # 测试地址
            oms_url = "http://oms-service.sh-test.xiaoyi.com"
        else:
            oms_url = "http://47.88.29.148:38081"
        url = oms_url + get_load_data_oms[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_oms[i][-1])  # 参数类型为dict
        logger.info('请求参数为：' + str(payload))
        headers = {'Authorization': 'Bearer ' + globals()['access_token']}
        for m in range(1, 3):
            falg = 0
            try:
                payload['page'] = m
                # logger.info('翻页 '+ str(m)+' 请求参数为：' +  str(payload))
                logger.info('翻页 {} 请求参数为：{}'.format(m, payload))
                response = requests.get(url, headers=headers, params=payload)  # 发送get请求
                logger.info('响应结果为：' + response.text)
                assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
                assert response.json().get('code') in ResCode.res_mapping.value.get('success')  # 断言响应code=20000
                res_data = response.json().get('data').get('records')
                if res_data:  # 断言响应data字段值不为空
                    globals()['channel_id'] = [i['id'] for i in res_data if i['name'] == 'auto_test5']
                    logger.info(globals()['channel_id'][0])
            except Exception as e:
                logger.info('报错信息 {}'.format(e))
                falg = 1
            if falg == 0:
                break

    # @pytest.mark.run(order=4)
    # @pytest.mark.cn
    # @pytest.mark.hw
    # @pytest.mark.parametrize("get_load_data_oms", [(path, current_file)], indirect=["get_load_data_oms"])
    # def test_004_oms_getSkuChannelPage(self, get_load_data_oms, eurl, i=3):
    #     """分页查询skuChannel列表(即：查询新建channel ID)"""
    #     allure.dynamic.title('04' + get_load_data_oms[i][0])  # allure动态获取 用例名称
    #     if eurl == 'cn_test':  # 测试地址
    #         oms_url = "http://oms-service.sh-test.xiaoyi.com"
    #     else:
    #         oms_url = "http://47.88.29.148:38081"
    #     url = oms_url + get_load_data_oms[i][1]
    #     logger.info('请求地址为：' + url)
    #     payload = eval(get_load_data_oms[i][-1])  # 参数类型为dict
    #     logger.info('请求参数为：' + str(payload))
    #     headers = {'Authorization': 'Bearer ' + globals()['access_token']}
    #     response = requests.get(url, headers=headers, params=payload)  # 发送get请求
    #     logger.info('响应结果为：' + response.text)
    #     assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
    #     assert response.json().get('code') in ResCode.res_mapping.value.get('success')  # 断言响应code=20000
    #     res_data = response.json().get('data').get('records')
    #     if res_data:  # 断言响应data字段值不为空
    #         globals()['channel_id'] = [i['id'] for i in res_data if i['name'] == 'auto_test5']
    #         logger.info(globals()['channel_id'][0])

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
    #     payload['id'] = globals()['channel_id'][0]
    #     logger.info('请求参数为：' + str(payload))
    #     headers = {'Authorization': 'Bearer ' + globals()['access_token']}
    #     response = requests.get(url, headers=headers, params=payload)  # 发送get请求
    #     logger.info('响应结果为：' + response.text)
    #     assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
    #     assert response.json().get('code') in ResCode.res_mapping.value.get('success')  # 断言响应code=20000
    #     res_data = response.json().get('data')
    #     assert res_data['id'] == globals()['channel_id'][0]
    #     assert res_data['name'] == 'auto_test5'
    #     assert res_data['status'] in [0, 1]  #
    #     assert res_data['appSystem'] in [1, 2, 3]  #

    # @pytest.mark.run(order=6)
    # @pytest.mark.cn
    # @pytest.mark.hw
    # @pytest.mark.parametrize("get_load_data_oms", [(path, current_file)], indirect=["get_load_data_oms"])
    # def test_006_oms_channel_edit(self, get_load_data_oms, i=5):
    #     """更新channel信息(name、Region、Status、Description)"""
    #     allure.dynamic.title(get_load_data_oms[i][0])  # allure动态获取 用例名称
    #     url = oms_url + get_load_data_oms[i][1]
    #     logger.info('请求地址为：' + url)
    #     payload = eval(get_load_data_oms[i][-1])  # 参数类型为dict
    #     payload['id'] = globals()['channel_id'][0]
    #     payload['status'] = 1  # 1-有效，0-无效
    #     logger.info('请求参数为：' + str(payload))
    #     headers = {'Authorization': 'Bearer ' + globals()['access_token']}
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
    #     allure.dynamic.title('07'+get_load_data_oms[i][0])  # allure动态获取 用例名称
    #     url = oms_url + get_load_data_oms[i][1]
    #     logger.info('请求地址为：' + url)
    #     payload = eval(get_load_data_oms[i][-1])  # 参数类型为dict
    #     payload['id'] = globals()['channel_id'][0]
    #     logger.info('请求参数为：' + str(payload))
    #     headers = {'Authorization': 'Bearer ' + globals()['access_token']}
    #     response = requests.get(url, headers=headers, params=payload)  # 发送get请求
    #     logger.info('响应结果为：' + response.text)
    #     assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
    #     assert response.json().get('code') in ResCode.res_mapping.value.get('success')  # 断言响应code=20000
    #     res_data = response.json().get('data')
    #     assert res_data['id'] == globals()['channel_id'][0]
    #     assert res_data['status'] == 1

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
    #     headers = {'Authorization': 'Bearer ' + globals()['access_token']}
    #     response = requests.get(url, headers=headers, params=payload)  # 发送get请求
    #     logger.info('响应结果为：' + response.text)
    #     assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
    #     assert response.json().get('code') in ResCode.res_mapping.value.get('success')  # 断言响应code=20000
    #     res_data = response.json().get('data').get('records')
    #     # if res_data:  # 断言响应data字段值不为空
    #     #     globals()['sku_id'] = [i['id'] for i in res_data if i['skuName'] == 'auto_test5']
    #     #     logger.info(globals()['sku_id'][0])

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
    #     headers = {'Authorization': 'Bearer ' + globals()['access_token']}
    #     response = requests.get(url, headers=headers, params=payload)  # 发送get请求
    #     logger.info('响应结果为：' + response.text)
    #     assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
    #     assert response.json().get('code') in ResCode.res_mapping.value.get('success')  # 断言响应code=20000
    #     res_data = response.json().get('data')
    #     assert res_data['id'] == 1353
    #     assert res_data['skuName'] == eval(get_load_data_oms[6][-1])['skuName']
    #     assert res_data['status'] == eval(get_load_data_oms[6][-1])['status']
    #     assert res_data['appSystem'] == eval(get_load_data_oms[6][-1])['appSystem']  #
    #     # assert res_data['price'] == eval(get_load_data_oms[6][-1])['price']

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
    #     payload['channelId'] = globals()['channel_id'][0]
    #     logger.info('请求参数为：' + str(payload))
    #     headers = {'Authorization': 'Bearer ' + globals()['access_token']}
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
        allure.dynamic.title('13' + get_load_data_oms[i][0])
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
            globals()['sign_value'] = response.json().get('data').get('token') + '&' \
                                      + response.json().get('data').get('token_secret')
            globals()['userId'] = response.json().get('data').get('userid')

    @pytest.mark.run(order=14)
    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_oms, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_oms", "get_url"])
    def test_014_Product_List_cn(self, get_load_data_oms, get_url, i=12):
        """查询产品列表信息"""
        allure.dynamic.title('14' + get_load_data_oms[i][0])  # allure动态获取 用例名称
        url = get_url + URLConf.PREFIX_ORDER.value + get_load_data_oms[i][1]  # 接口请求uri
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_oms[i][-1])  # 参数类型为dict
        payload['channel'] = globals()['channel_id'][0]
        payload['userid'] = globals()['userId']
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
            globals()['prod_skuid_value'] = [[productsDtos[i]['skuId'], productsDtos[i]['price']] for i in
                                             range(len(productsDtos))]
            # print(globals()['prod_skuid_value'])

    @pytest.mark.run(order=15)
    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_oms, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_oms", "get_url"])
    def test_015_create_Token(self, get_load_data_oms, get_url, i=13):
        """创建订单Token接口"""
        allure.dynamic.title('15' + get_load_data_oms[i][0])
        url = get_url + URLConf.PREFIX_ORDER.value + get_load_data_oms[i][1]  # 接口请求uri
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_oms[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['hmac'] = get_v8_hmac(payload)
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)  # 发送get请求
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in ResCode.res_mapping.value.get('success'), '验证通过'
        assert response.json().get('data') is not None  # 断言响应token字段值不为空
        globals()['token'] = response.json().get('data')

    @pytest.mark.run(order=16)
    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_oms, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_oms", "get_url"])
    def test_016_create_Order(self, get_load_data_oms, get_url, i=14):
        """创建订单接口"""
        allure.dynamic.title('16' + get_load_data_oms[i][0])
        url = get_url + URLConf.PREFIX_ORDER.value + get_load_data_oms[i][1]  # 接口请求uri
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_oms[i][-1])  # 参数类型为dict
        payload['token'] = globals()['token']
        payload['userid'] = globals()['userId']
        payload['channel'] = globals()['channel_id'][0]
        payload['skuId'] = globals()['prod_skuid_value'][0][0]
        payload['hmac'] = get_v8_hmac(payload)
        headers = {'Connection': 'close'}
        response = requests.post(url, headers=headers, data=payload)  # 发送post请求
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求状态码为 200
        assert response.json().get('code') in ResCode.res_mapping.value.get('success'), '验证通过'  # 断言响应code为 20000
        assert response.json().get('data').get('orderCode') is not None  # 断言响应orderCode字段值不为空
        globals()['orderCode'] = response.json().get('data').get('orderCode')

    @pytest.mark.run(order=17)
    @pytest.mark.cn
    @pytest.mark.parametrize("get_load_data_oms, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_oms", "get_url"])
    def test_017_query_initialCode(self, get_load_data_oms, get_url, i=15):
        """查询初始化 订单状态接口 10"""
        allure.dynamic.title('17' + get_load_data_oms[i][0])
        url = get_url + URLConf.PREFIX_ORDER.value + get_load_data_oms[i][1]  # 接口请求uri
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_oms[i][-1])  # 参数类型为dict
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

    @pytest.mark.run(order=18)
    @pytest.mark.cn
    @pytest.mark.parametrize("get_load_data_oms, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_oms", "get_url"])
    def test_018_wxPay_Order(self, get_load_data_oms, get_url, i=16):
        """微信客户端支付 接口"""
        allure.dynamic.title('18' + get_load_data_oms[i][0])
        url = get_url + URLConf.PREFIX_ORDER.value + get_load_data_oms[i][1]  # 接口请求uri
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_oms[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['orderCode'] = globals()['orderCode']
        payload['hmac'] = get_v8_hmac(payload)
        headers = {'Connection': 'close'}
        response = requests.post(url, headers=headers, data=payload)
        logger.info('响应结果为：' + response.text)  # 打印响应结果
        globals()['sign'] = response.json().get('data').get('sign')
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in ResCode.res_mapping.value.get('success'), '验证通过'
        assert response.json().get('data') is not None  # 断言响应data字段值不为空

    @pytest.mark.run(order=19)
    @pytest.mark.flaky(reruns=5, reruns_delay=3)
    @pytest.mark.cn
    @pytest.mark.parametrize("get_load_data_oms, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_oms", "get_url"])
    def test_019_wxPay_callback(self, get_load_data_oms, get_url, eurl):
        """微信回调"""
        allure.dynamic.title("19微信回调")

        body_xml = r'body1.xml'
        # 打开xml文档 , 修改指定标签的内容
        dom = xml.dom.minidom.parse(body_xml)
        # 打开xml文档,修改sign信息
        cc = dom.getElementsByTagName('sign')
        c1 = cc[0]
        c1.firstChild.data = globals()['sign']
        # 修改 out_trade_no 的信息为 orderCode
        bb = dom.getElementsByTagName('out_trade_no')
        b1 = bb[0]
        b1.firstChild.data = globals()['orderCode']

        with open(body_xml, 'w') as fh:
            dom.writexml(fh)

        #  重新读取xml 文档
        with open(body_xml, encoding='utf-8') as fp:
            body = fp.read()

        headers = {'Content-Type': 'text/xml'}

        if eurl == 'cn_test':
            url = "https://openapi-cn-test.xiaoyi.com/orderpay/v8/wx/pay/callback"  # 直接调用微信的，不走网关 ,测试环境
        else:
            url = "https://open-gw.xiaoyi.com/orderpay/v8/wx/pay/callback"  # 直接调用微信的，不走网关 ，正式环境
        logger.info('重新配置的地址：' + url)
        response = requests.post(url, headers=headers, data=body.encode("utf-8"))  # 发送post请求
        logger.info('响应结果为：' + response.text)  # 打印响应结果
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功

    @pytest.mark.flaky(reruns=3, reruns_delay=1)  # reruns表示失败后执行几次，reruns_delay表示失败后等待几秒后，在重新执行
    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_oms, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_oms", "get_url"])
    def test_021_userOrder_detail(self, get_load_data_oms, get_url, i=18):
        """用户订单详情 接口"""
        allure.dynamic.title('21' + get_load_data_oms[i][0])
        url = get_url + URLConf.PREFIX_ORDER.value + get_load_data_oms[i][1]  # 接口请求uri
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_oms[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['orderCode'] = globals()['orderCode']
        payload['hmac'] = get_v8_hmac(payload)
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)
        logger.info('响应结果为：' + response.text)  # 打印响应结果
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in ResCode.res_mapping.value.get('success'), '验证通过'
        res_data = response.json().get('data')
        if res_data:
            assert res_data['code'] == globals()['orderCode']
            assert res_data['payStatus'] == 30  # 30-支付成功状态
            assert res_data['payType'] == 20  # 20-表示微信支付
            assert res_data['payAmount'] == 201  # 201-表示支付金额

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_oms, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_oms", "get_url"])
    def test_022_cloud_serviceByOrderCode(self, get_load_data_oms, get_url, i=20):
        """通过订单号查询-云存服务"""
        allure.dynamic.title('22' + get_load_data_oms[i][0])
        url = get_url + URLConf.PREFIX_VAS.value + get_load_data_oms[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_oms[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['orderCode'] = globals()['orderCode']
        payload['hmac'] = get_v8_hmac(payload)
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)  # 发送get请求
        logger.info('响应结果为：' + response.text)
        res = response.json().get('data')
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in ResCode.res_mapping.value.get('success'), '验证通过'
        if res:  # 断言响应data字段值不为空
            assert res[0]['orderCode'] in globals()['orderCode']
        globals()['businessOrderCode'] = res[0]['businessOrderCode']  # 10020210326143139934757816

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
    #     payload['userid'] = globals()['userId']
    #     payload['hmac'] = get_v8_hmac(payload)
    #     logger.info('请求参数为：' + str(payload))
    #     headers = {'Connection': 'close'}
    #     response = requests.get(url, headers=headers, params=payload)  # 发送get请求
    #     logger.info('响应结果为：' + response.text)
    #     data = response.json().get('data')
    #     assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
    #     assert response.json().get('code') in ResCode.res_mapping.value.get('success')
    #     globals()['devUid'] = data[0]['eiNumber']

    # @pytest.mark.cn
    # @pytest.mark.hw
    # @pytest.mark.parametrize("get_load_data_oms, get_url", [((path, current_file), '')],
    #                          indirect=["get_load_data_oms", "get_url"])
    # def test_024_cloud_setBind(self, get_load_data_oms, get_url, i=22):
    #     """设备绑定/解绑业务订单-从Url获取参数"""
    #     allure.dynamic.title('24'+get_load_data_oms[i][0])
    #     url = get_url + URLConf.PREFIX_VAS.value + get_load_data_oms[i][1]
    #     logger.info('请求地址为：' + url)
    #     payload = eval(get_load_data_oms[i][-1])  # 参数类型为dict
    #     payload['userid'] = globals()['userId']
    #     payload['businessOrderCode'] = globals()['businessOrderCode']
    #     payload['devUid'] = globals()['devUid']
    #     payload['hmac'] = get_v8_hmac(payload)
    #     logger.info('请求参数为：' + str(payload))
    #     headers = {'Connection': 'close'}
    #     response = requests.put(url, headers=headers, data=payload)  # 发送get请求
    #     logger.info('响应结果为：' + response.text)
    #     assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
    #     assert response.json().get('code') in ResCode.res_mapping.value.get('success')  # 断言响应code==20000
    #
    # @pytest.mark.cn
    # @pytest.mark.hw
    # @pytest.mark.parametrize("get_load_data_oms, get_url", [((path, current_file), '')],
    #                          indirect=["get_load_data_oms", "get_url"])
    # def test_025_cloud_deviceStatus(self, get_load_data_oms, get_url, i=23):
    #     """设备状态"""
    #     allure.dynamic.title('25'+get_load_data_oms[i][0])
    #     url = get_url + URLConf.PREFIX_VAS.value + get_load_data_oms[i][1]
    #     logger.info('请求地址为：' + url)
    #     payload = eval(get_load_data_oms[i][-1])  # 参数类型为dict
    #     payload['userid'] = globals()['userId']
    #     payload['uid'] = globals()['devUid']
    #     payload['hmac'] = get_v8_hmac(payload)
    #     logger.info('请求参数为：' + str(payload))
    #     headers = {'Connection': 'close'}
    #     response = requests.get(url, headers=headers, params=payload)  # 发送get请求
    #     logger.info('响应结果为：' + response.text)
    #     assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
    #     assert response.json().get('code') in ResCode.res_mapping.value.get('success')  # 断言响应code==20000
    #
    # @pytest.mark.cn
    # @pytest.mark.hw
    # @pytest.mark.parametrize("get_load_data_oms, get_url", [((path, current_file), '')],
    #                          indirect=["get_load_data_oms", "get_url"])
    # def test_026_cloud_status(self, get_load_data_oms, get_url, i=24):
    #     """设备云存订单状态（业务订单状态、设备设置状态）"""
    #     allure.dynamic.title('26'+get_load_data_oms[i][0])
    #     url = get_url + URLConf.PREFIX_VAS.value + get_load_data_oms[i][1]
    #     logger.info('请求地址为：' + url)
    #     payload = eval(get_load_data_oms[i][-1])  # 参数类型为dict
    #     payload['userid'] = globals()['userId']
    #     payload['uid'] = globals()['devUid']
    #     payload['hmac'] = get_v8_hmac(payload)
    #     logger.info('请求参数为：' + str(payload))
    #     headers = {'Connection': 'close'}
    #     response = requests.get(url, headers=headers, params=payload)  # 发送get请求
    #     logger.info('响应结果为：' + response.text)
    #     assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
    #     assert response.json().get('code') in ResCode.res_mapping.value.get('success')
    #     res = response.json().get('data')
    #     if res:
    #         assert res['orderCode'] == globals()['orderCode']
    #         assert res['businessType'] in [1, 2]  # 云存订单-1,
    #         assert res['state'] in [1, 2]  # 绑定-1, 解绑-2


if __name__ == '__main__':
    pytest.main(['-v', '-s'])
