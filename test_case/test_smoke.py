# !/usr/bin/python3
# -*- coding: utf-8 -*-
import ast
import datetime
from dateutil.relativedelta import relativedelta
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


def get_v2_hmac(params):
    """SHA1加密
    return:加密结果转成16进制字符串形式
    """
    str1 = ["{0}={1}".format(k, v) for k, v in params.items()]  # 使用 = 拼接dict数据（key,values）
    # str1.sort()  # 按照字母序进行排序  #value = seq + userId + timestamp + webAuthFlow + appPlatform
    res = "&".join(str1)  # 使用 & 拼接数据
    message = res.encode('utf-8')
    key = (globals()['token'] + '&' + globals()['token_secret']).encode('utf-8')
    # print((globals()['token'] + '&' + globals()['token_secret']))
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


def months_age3(current_timestamp):
    """
    计算实际三个月之前的时间戳
    """
    # 计算三个月前的时间
    current_datetime = datetime.datetime.fromtimestamp(current_timestamp)
    three_months_ago = current_datetime - relativedelta(months=3)

    # 获取三个月前这个时间点的时间戳（以秒为单位）
    three_months_ago_timestamp = int(three_months_ago.timestamp())
    return three_months_ago_timestamp


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
        logger.info('=' * 90)
        yield
        logger.info('=' * 90)

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
            globals()['token'] = response.json().get('data').get('token')
            globals()['token_secret'] = response.json().get('data').get('token_secret')

    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_002_user_List(self, get_load_data_cloud, get_url, i=1):
        """用户订单列表 接口"""
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + URLConf.PREFIX_ORDER.value + get_load_data_cloud[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['hmac'] = get_v8_hmac(payload)
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)  # 发送get请求
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in ResCode.res_mapping.value.get('success'), '验证通过'
        assert response.json().get('data') is not None  # 断言响应token字段值不为空
        res = response.json().get('data').get('records')
        print(res[0]['code'])
        globals()['orderCode'] = res[0]['code']

    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_003_cloud_deviceList(self, get_load_data_cloud, get_url, i=2):
        """通过用户id获取云存设备列表"""
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + URLConf.PREFIX_VAS.value + get_load_data_cloud[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
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


    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_004_get_videos(self, get_load_data_cloud, get_url, i=3):
        """云存播放滚动条渲染_get"""
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + URLConf.PREFIX_VAS.value + get_load_data_cloud[i][1].strip()
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['uid'] = globals()['devUid']
        payload['end_time'] = int(time.time())
        payload['hmac'] = get_v8_hmac(payload)
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)  # 发送get请求
        res = response.json().get('msg')
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in ResCode.res_mapping.value.get('success'), '验证通过'
        assert res is not None, 'msg 有提示信息'  # 断言响应data字段值不为空,当get到信息时候，判断有以下信息


    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_005_post_videos(self, get_load_data_cloud, get_url, i=4):
        """云存播放滚动条渲染_post"""
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + URLConf.PREFIX_VAS.value + get_load_data_cloud[i][1].strip()
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['uid'] = globals()['devUid']
        payload['end_time'] = int(time.time())
        payload['hmac'] = get_v8_hmac(payload)
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.post(url, headers=headers, data=payload)  # 发送get请求
        res = response.json().get('msg')
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in [20000, 50013], '200000表示userid 下的 设备 id 是绑定的，50013 则不是。'
        assert res in ['success', '查看视频异常'], 'msg 有提示信息'  # 断言响应data字段值不为空,当get到信息时候，判断有以下信息


    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_006_del_videos(self, get_load_data_cloud, get_url, i=5):
        """删除云存播放信息-delete"""
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + URLConf.PREFIX_VAS.value + get_load_data_cloud[i][1].strip()
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['uid'] = globals()['devUid']
        payload['start_time'] = days_age30()  # 30天前的时间戳
        payload['end_time'] = int(time.time())  # 当前时间戳
        payload['hmac'] = get_v8_hmac(payload)
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.delete(url, headers=headers, params=payload)  # 发送del请求
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in ResCode.res_mapping.value.get('success'), '验证通过'


    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_007_cloud_service(self, get_load_data_cloud, get_url, i=6):
        """云存服务列表"""
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + URLConf.PREFIX_VAS.value + get_load_data_cloud[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['hmac'] = get_v8_hmac(payload)
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)  # 发送get请求
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in ResCode.res_mapping.value.get('success')  # 断言响应code==20000


    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_008_cloud_images(self, get_load_data_cloud, get_url, i=7):
        """云存播放信息-get"""
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + URLConf.PREFIX_VAS.value + get_load_data_cloud[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['uid'] = globals()['devUid']
        payload['end_time'] = int(time.time())
        payload['hmac'] = get_v8_hmac(payload)
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)  # 发送get请求
        res = response.json().get('data')
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in ResCode.res_mapping.value.get('success'), '验证通过'
        if res:  # 断言响应data字段值不为空,当get到信息时候，判断有以下信息
            assert 'viewUrl' in res.keys(), '结果中包含viewUrl'
            assert 'viewUrlImg' in res.keys(), '结果中包含viewUrlImg'


    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_009_register_user(self, get_load_data_cloud, get_url, i=8):
        """邮箱注册账号"""
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + get_load_data_cloud[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.put(url, headers=headers, params=payload)  # 发送get请求
        res = response.json().get('data')
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in ResCode.res_mapping.value.get('success'), '验证通过'


    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_010_login_facebook(self, get_load_data_cloud, get_url, i=9):
        """facebook登陆"""
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + get_load_data_cloud[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)  # 发送get请求
        res = response.json().get('data')
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in ResCode.res_mapping.value.get('success'), '验证通过'


    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_010_get_region(self, get_load_data_cloud, get_url, i=10):
        """get user region"""
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + get_load_data_cloud[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)  # 发送get请求
        res = response.json().get('data')
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in ResCode.res_mapping.value.get('success'), '验证通过'


    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_011_get_bindkey(self, get_load_data_cloud, get_url, i=11):
        """get hmac"""
        allure.dynamic.title(get_load_data_cloud[i][0])

        url = get_url + get_load_data_cloud[i][1].strip()
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['timestamp'] = int(time.time() * 1000)
        payload['hmac'] = get_v2_hmac(payload)
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)  # 发送get请求
        res = response.json().get('data')
        logger.info('响应结果为：' + response.text)
        globals()['bindkey'] = response.json().get('data').get('bindkey')
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in ResCode.res_mapping.value.get('success'), '验证通过'
        assert res is not None


    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_012_check_bindkey(self, get_load_data_cloud, get_url, i=12):
        """check bindkey"""
        allure.dynamic.title(get_load_data_cloud[i][0])

        url = get_url + get_load_data_cloud[i][1].strip()
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['timestamp'] = int(time.time() * 1000)
        payload['bindkey'] = globals()['bindkey']
        print(payload['bindkey'])
        payload['hmac'] = get_v2_hmac(payload)
        print(payload['hmac'])
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)  # 发送get请求
        res = response.json().get('data')
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in ResCode.res_mapping.value.get('success'), '验证通过'
        assert res is not None


    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_013_device_edit(self, get_load_data_cloud, get_url, i=13):
        """edit device"""
        allure.dynamic.title(get_load_data_cloud[i][0])

        url = get_url + get_load_data_cloud[i][1].strip()
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['token'] = globals()['token']
        payload['uid'] = globals()['devUid']
        payload['hmac'] = get_v2_hmac(payload)

        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)  # 发送get请求

        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in ResCode.res_mapping.value.get('success'), '验证通过'


    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_014_device_info(self, get_load_data_cloud, get_url, i=14):
        """get_device_info"""
        allure.dynamic.title(get_load_data_cloud[i][0])

        url = get_url + get_load_data_cloud[i][1].strip()
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['uid'] = globals()['devUid']
        payload['hmac'] = get_v2_hmac(payload)

        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)  # 发送get请求

        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in ResCode.res_mapping.value.get('success'), '验证通过'


    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_015_app_config(self, get_load_data_cloud, get_url, i=15):
        """get_app_config"""
        allure.dynamic.title(get_load_data_cloud[i][0])

        url = get_url + get_load_data_cloud[i][1].strip()
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']

        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)  # 发送get请求

        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in ResCode.res_mapping.value.get('success'), '验证通过'


    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_016_get_password(self, get_load_data_cloud, get_url, i=16):
        """Get the p2p password of camera"""
        allure.dynamic.title(get_load_data_cloud[i][0])

        url = get_url + get_load_data_cloud[i][1].strip()
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        # print(payload)
        payload['userid'] = globals()['userId']
        payload['uid'] = globals()['devUid']
        payload['hmac'] = get_v2_hmac(payload)
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)  # 发送get请求
        # res = response.json().get('data')[]
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in ResCode.res_mapping.value.get('success'), '验证通过'
        res = response.json().get('data')['password']
        assert res is not None


    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_017_get_message(self, get_load_data_cloud, get_url, i=17):
        """Get message(Show or hide red dot)"""
        allure.dynamic.title(get_load_data_cloud[i][0])

        url = get_url + get_load_data_cloud[i][1].strip()
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['user_id'] = globals()['userId']

        payload['end_time'] = int(time.time())
        payload['start_time'] = int(payload['end_time'] - 90 * 24 * 60 * 60)
        payload['hmac'] = get_v2_hmac(payload)
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)  # 发送get请求
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in ResCode.res_mapping.value.get('success'), '验证通过'


    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_018_get_invitations(self, get_load_data_cloud, get_url, i=18):
        """Get invitee message"""
        allure.dynamic.title(get_load_data_cloud[i][0])

        url = get_url + get_load_data_cloud[i][1].strip()
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['hmac'] = get_v2_hmac(payload)
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)  # 发送get请求
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in ResCode.res_mapping.value.get('success'), '验证通过'


    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_019_get_invitations(self, get_load_data_cloud, get_url, i=19):
        """Get login message"""
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + get_load_data_cloud[i][1].strip()
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['end_time'] = int(time.time())
        payload['start_time'] = months_age3(payload['end_time'])
        payload['start'] = '0'
        payload['row_count'] = '1'
        payload['hmac'] = get_v2_hmac(payload)
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)  # 发送get请求
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in ResCode.res_mapping.value.get('success'), '验证通过'


    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_020_get_user_extinfo(self, get_load_data_cloud, get_url, i=20):
        """Get user timezone/language/location"""
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + get_load_data_cloud[i][1].strip()
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['hmac'] = get_v2_hmac(payload)
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)  # 发送get请求
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in ResCode.res_mapping.value.get('success'), '验证通过'


    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_021_get_alert_list(self, get_load_data_cloud, get_url, i=21):
        """Get alert list"""
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + get_load_data_cloud[i][1].strip()
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['to'] = int(time.time())
        payload['from'] = payload['to'] - (7 * 24 * 60 * 60)
        payload['hmac'] = get_v2_hmac(payload)
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)  # 发送get请求
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in ResCode.res_mapping.value.get('success'), '验证通过'


    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_022_get_alert_del_list(self, get_load_data_cloud, get_url, i=22):
        """Get delete alerts"""
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + get_load_data_cloud[i][1].strip()
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['to'] = int(time.time())
        payload['from'] = payload['to'] - (30 * 24 * 60 * 60)
        payload['hmac'] = get_v2_hmac(payload)
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)  # 发送get请求
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in ResCode.res_mapping.value.get('success'), '验证通过'


    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_023_get_user_permissions(self, get_load_data_cloud, get_url, i=23):
        """Get expire time to delete expire alerts in app database without cloud plan"""
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + get_load_data_cloud[i][1].strip()
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['hmac'] = get_v2_hmac(payload)
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)  # 发送get请求
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in ResCode.res_mapping.value.get('success'), '验证通过'


    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_024_get_scenes_state(self, get_load_data_cloud, get_url, i=24):
        """Get scenes state"""
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + get_load_data_cloud[i][1].strip()
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['user_id'] = globals()['userId']
        payload['cur_time'] = int(time.time() * 1000)
        payload['hmac'] = get_v2_hmac(payload)
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)  # 发送get请求
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in ResCode.res_mapping.value.get('success'), '验证通过'


    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_025_get_scenes_devices(self, get_load_data_cloud, get_url, i=25):
        """Get devices set for Home/Away"""
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + get_load_data_cloud[i][1].strip()
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['user_id'] = globals()['userId']
        payload['cur_time'] = int(time.time() * 1000)
        payload['hmac'] = get_v2_hmac(payload)
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)  # 发送get请求
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in ResCode.res_mapping.value.get('success'), '验证通过'


    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_026_get_scenes_devices(self, get_load_data_cloud, get_url, i=26):
        """Get sensors state"""
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + get_load_data_cloud[i][1].strip()
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['timestamp'] = int(time.time())
        payload['hmac'] = get_v2_hmac(payload)
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)  # 发送get请求
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in ResCode.res_mapping.value.get('success'), '验证通过'


    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_027_get_alert_push(self, get_load_data_cloud, get_url, i=27):
        """Get device push info"""
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + get_load_data_cloud[i][1].strip()
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['uid'] = globals()['devUid']
        payload['hmac'] = get_v2_hmac(payload)
        print(payload)
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)  # 发送get请求
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in ResCode.res_mapping.value.get('success'), '验证通过'


    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_028_get_storage_status(self, get_load_data_cloud, get_url, i=28):
        """Get baby service status"""
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + get_load_data_cloud[i][1].strip()
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['timestamp'] = int(time.time() * 1000)
        payload['hmac'] = get_v8_hmac(payload)
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)  # 发送get请求
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in ResCode.res_mapping.value.get('success'), '验证通过'


    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_029_get_alert_push2(self, get_load_data_cloud, get_url, i=29):
        """Get device push info with inviter"""
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + get_load_data_cloud[i][1].strip()
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['uid'] = globals()['devUid']
        payload['inviterUserId'] = "3206905"
        payload['hmac'] = get_v2_hmac(payload)
        print(payload)
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)  # 发送get请求
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in ResCode.res_mapping.value.get('success'), '验证通过'


    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_030_get_banner_list(self, get_load_data_cloud, get_url, i=30):
        """Get banner list"""
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + get_load_data_cloud[i][1].strip()
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['hmac'] = get_v8_hmac(payload)
        print(payload)
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)  # 发送get请求
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in ResCode.res_mapping.value.get('success'), '验证通过'


    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_031_send_sharing_invite(self, get_load_data_cloud, get_url, i=31):
        """Send sharing invite"""
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + get_load_data_cloud[i][1].strip()
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['uids'] = globals()['devUid']
        payload['timestamp'] = int(time.time() * 1000)
        payload['hmac'] = get_v8_hmac(payload)
        print(payload)
        headers = {'Connection': 'close'}
        response = requests.post(url, headers=headers, json=payload)  # 发送get请求
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in ResCode.res_mapping.value.get('success'), '验证通过'


    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_032_get_sharing_invite(self, get_load_data_cloud, get_url, i=32):
        """Get sharing invite"""
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + get_load_data_cloud[i][1].strip()
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['timestamp'] = int(time.time() * 1000)
        payload['hmac'] = get_v8_hmac(payload)
        print(payload)
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)  # 发送get请求
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in ResCode.res_mapping.value.get('success'), '验证通过'
        globals()['shareId'] = response.json().get('data')[0].get('shareId')


    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_033_modify_sharing_invite(self, get_load_data_cloud, get_url, i=33):
        """Modify sharing invite"""
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + get_load_data_cloud[i][1].strip()
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['timestamp'] = int(time.time() * 1000)
        payload['shareId'] = globals()['shareId']
        payload['uids'] = globals()['devUid']
        payload['hmac'] = get_v8_hmac(payload)
        print(payload)
        headers = {'Connection': 'close'}
        response = requests.put(url, headers=headers, params=payload)  # 发送get请求
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in ResCode.res_mapping.value.get('success'), '验证通过'


    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_034_delete_sharing_invite(self, get_load_data_cloud, get_url, i=34):
        """Delete sharing invite"""
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + get_load_data_cloud[i][1].strip()
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['uid'] = globals()['devUid']
        payload['hmac'] = get_v8_hmac(payload)
        print(payload)
        headers = {'Connection': 'close'}
        response = requests.delete(url, headers=headers, params=payload)  # 发送get请求
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in ResCode.res_mapping.value.get('success'), '验证通过'

    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_035_get_cloud_status_of_device(self, get_load_data_cloud, get_url, i=35):
        """Get cloud status of device"""
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + URLConf.PREFIX_VAS.value + get_load_data_cloud[i][1].strip()
        logger.info('请求地址为：' + url)
        payload = ast.literal_eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['uid'] = globals()['devUid']
        payload['hmac'] = get_v8_hmac(payload)
        print(payload)
        headers = {'connection': 'Keep-Alive'}
        response = requests.get(url, headers=headers, params=payload)  # 发送get请求
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in ResCode.res_mapping.value.get('success'), '验证通过'

    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_036_get_cloud_free_info(self, get_load_data_cloud, get_url, i=36):
        """Get cloud free info"""
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + URLConf.PREFIX_ORDER.value + get_load_data_cloud[i][1].strip()
        logger.info('请求地址为：' + url)
        payload = ast.literal_eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['uid'] = globals()['devUid']
        payload['hmac'] = get_v8_hmac(payload)
        print(payload)
        headers = {'connection': 'Keep-Alive'}
        response = requests.get(url, headers=headers, params=payload)  # 发送get请求
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in ResCode.res_mapping.value.get('success'), '验证通过'

    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_037_get_cloud_trial(self, get_load_data_cloud, get_url, i=37):
        """Get cloud trial"""
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + URLConf.PREFIX_ORDER.value + get_load_data_cloud[i][1].strip()
        logger.info('请求地址为：' + url)
        payload = ast.literal_eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        # payload['uid'] = globals()['devUid']
        payload['hmac'] = get_v8_hmac(payload)
        print(payload)
        headers = {'connection': 'Keep-Alive'}
        response = requests.get(url, headers=headers, params=payload)  # 发送get请求
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in ResCode.res_mapping.value.get('success'), '验证通过'
