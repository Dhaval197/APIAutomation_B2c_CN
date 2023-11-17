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

    @pytest.mark.cn
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

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.skip('接口没有返回，暂时跳过')
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_003_cloud_serviceByOrderCode(self, get_load_data_cloud, get_url, i=2):
        """云存服务列表接口-通过订单号生成业务订单号"""
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + URLConf.PREFIX_VAS.value + get_load_data_cloud[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['orderCode'] = globals()['orderCode']
        payload['hmac'] = get_v8_hmac(payload)
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)  # 发送get请求
        logger.info('响应结果为：' + response.text)
        print(response.json())
        res = response.json().get('data')
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in ResCode.res_mapping.value.get('success'), '验证通过'
        assert res is not None  # 断言响应data字段值不为空
        print(res[0]['orderCode'])
        print(globals()['orderCode'])
        assert res[0]['orderCode'] in globals()['orderCode']
        globals()['businessOrderCode'] = res[0]['businessOrderCode']  # 10020210326143139934757816

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_004_cloud_deviceList(self, get_load_data_cloud, get_url, i=3):
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

    # @pytest.mark.cn
    # @pytest.mark.hw
    # @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
    #                          indirect=["get_load_data_cloud", "get_url"])
    # def test_005_cloud_setBind(self, get_load_data_cloud, get_url, i=4):
    #     """设备绑定/解绑业务订单-从Url获取参数"""
    #     allure.dynamic.title(get_load_data_cloud[i][0])
    #     url = get_url + URLConf.PREFIX_VAS.value + get_load_data_cloud[i][1]
    #     logger.info('请求地址为：' + url)
    #     payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
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

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_005_cloud_deviceStatus(self, get_load_data_cloud, get_url, i=5):
        """设备状态"""
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + URLConf.PREFIX_VAS.value + get_load_data_cloud[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['uid'] = globals()['devUid']
        payload['hmac'] = get_v8_hmac(payload)
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)  # 发送get请求
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in ResCode.res_mapping.value.get('success')  # 断言响应code==20000

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_006_cloud_service(self, get_load_data_cloud, get_url, i=6):
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

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_007_cloud_status(self, get_load_data_cloud, get_url, i=7):
        """设备云存订单状态（业务订单状态、设备设置状态）"""
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + URLConf.PREFIX_VAS.value + get_load_data_cloud[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['uid'] = globals()['devUid']
        payload['hmac'] = get_v8_hmac(payload)
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)  # 发送get请求
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in ResCode.res_mapping.value.get('success')  # 断言响应code==20000

    # @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.skip('接口没有返回，暂时跳过')
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_008_cloud_deleteOrderByBusiness(self, get_load_data_cloud, get_url, i=8):
        """通过订单CODE删除订单"""
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + URLConf.PREFIX_VAS.value + get_load_data_cloud[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['businessOrderCode'] = globals()['businessOrderCode']
        payload['hmac'] = get_v8_hmac(payload)
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)  # 发送get请求
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in ResCode.res_mapping.value.get('success')  # 断言响应code==20000

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_009_cloud_FileInfoController_GetListByRefId(self, get_load_data_cloud, get_url, i=9):
        """获取文件列表"""
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + URLConf.PREFIX_VAS.value + get_load_data_cloud[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['refId'] = '339'
        payload['hmac'] = get_v8_hmac(payload)
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)  # 发送get请求
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in ResCode.res_mapping.value.get('success')  # 断言响应code==20000

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_010_cloud_FileInfoController_GetUploadAddress(self, get_load_data_cloud, get_url, i=10):
        """获取上传地址"""
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

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_011_cloud_images(self, get_load_data_cloud, get_url, i=11):
        """云存AI检索"""
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
        assert res is not None  # 断言响应data字段值不为空
        # 通过接口获取当前的AI的视频，通过接口获取当前3天的视频，判断最后两条视频是在oss上存在。
        url_end = response.url.split('.com')[-1]
        #  切换到正式环境来 ，判断手机上的视频，在oss上有没有；
        url_full = 'https://gw.xiaoyi.com' + url_end
        response_image = requests.get(url_full, headers=headers)  # 发送get请求
        image = response_image.json().get('data').get('images')
        # 保证账号是绑定设备的，然后是ai有检测到信息，且是购买了运存服务的。
        if image:
            image_one = image[-2]['url'].split('?')[0].split('.com/')[1]  # 倒数第二个
            image_one_path = '/'.join(image_one.split('/')[:-1])
            image_last = image[-1]['url'].split('?')[0].split('.com/')[1]  # 倒数第一个
            image_laste_path = '/'.join(image_one.split('/')[:-1])
            b = Base_func()
            # 确定当前AI检索的在oss 中：
            result = bool(image_one in b.cloud_oss('xiaoyi-css-cn-1d', image_one_path)
                          and (image_last in b.cloud_oss('xiaoyi-css-cn-1d', image_laste_path))
                          or (image_one in b.cloud_oss('xiaoyi-css-cn-7d', image_one_path)
                              and (image_last in b.cloud_oss('xiaoyi-css-cn-7d', image_laste_path)))
                          or (image_one in b.cloud_oss('xiaoyi-css-cn-30d', image_one_path)
                              and (image_last in b.cloud_oss('xiaoyi-css-cn-30d', image_laste_path))))
            assert result is True  # 判断该视频存在oss中，否则失败

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_012_cloud_images(self, get_load_data_cloud, get_url, i=12):
        """Yihome_Api"""
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

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_013_get_videos(self, get_load_data_cloud, get_url, i=13):
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

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_014_post_videos(self, get_load_data_cloud, get_url, i=14):
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

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_015_del_videos(self, get_load_data_cloud, get_url, i=15):
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

    # @pytest.mark.cn
    # @pytest.mark.hw
    # @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
    #                          indirect=["get_load_data_cloud", "get_url"])
    # def test_017_cloud_STSToken(self, get_load_data_cloud, get_url, i=17):
    #     """IPC获取STSToken"""
    #     allure.dynamic.title(get_load_data_cloud[i][0])
    #     url = get_url + URLConf.PREFIX_VAS.value + get_load_data_cloud[i][1].strip()
    #     logger.info('请求地址为：' + url)
    #     payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
    #     payload['userid'] = globals()['userId']
    #     payload['hmac'] = get_notv8_hmac(payload)
    #     logger.info('请求参数为：' + str(payload))
    #     headers = {'Connection': 'close'}
    #     response = requests.put(url, headers=headers, data=payload)
    #     logger.info('响应结果为：' + response.text)
    #     assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
    #     assert response.json().get('code') == 20202, '验证表示当前的验签规则不能用普通的规则'

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_016_cloud_ipc(self, get_load_data_cloud, get_url, i=17):
        """IPC-云存开关状态"""
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + URLConf.PREFIX_VAS.value + get_load_data_cloud[i][1].strip()
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        # payload['uid'] = globals()['devUid']
        payload['timestamp'] = int(time.time())  # 获取当前时间戳到min
        payload['hmac'] = get_notv8_hmac(payload)
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)  # 发送get请求
        flag = response.json().get('flag')
        image_flag = response.json().get('image_flag')
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in ResCode.res_mapping.value.get('success'), '验证通过'
        assert flag == 1
        assert image_flag == 1

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_017_get_cloud(self, get_load_data_cloud, get_url, i=18):
        """云存开关状态  cloud get"""
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + URLConf.PREFIX_VAS.value + get_load_data_cloud[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['uid'] = globals()['devUid']
        payload['timestamp'] = int(time.time())  # 获取当前时间戳到min
        payload['hmac'] = get_v8_hmac(payload)
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)  # 发送get请求
        mode = response.json().get('data').get('mode')
        flag = response.json().get('data').get('flag')
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') in ResCode.res_mapping.value.get('success'), '验证通过'
        assert response.json().get('data') is not None  # 断言响应data字段值不为空
        assert mode == 0
        # assert flag == 0   # 1 是关闭 0是打开

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    @pytest.mark.parametrize('state', [1, 0])  # 给同一个case 传递参数，转化为多个case了
    def test_018_put_cloud(self, get_load_data_cloud, get_url, state, i=19):
        """云存开关状态  cloud put"""
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + URLConf.PREFIX_VAS.value + get_load_data_cloud[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['uid'] = globals()['devUid']
        payload['hmac'] = get_v8_hmac(payload)
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.put(url, headers=headers, data=payload)
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') == 20000, '验证通过,40402 表示服务过期'
        assert response.json().get('data') is None  # 断言响应data

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_019_equipment_list(self, get_load_data_cloud, get_url, i=21):
        """多个设备维度列表"""
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + URLConf.PREFIX_VAS.value + get_load_data_cloud[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['hmac'] = get_v8_hmac(payload)
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') == 20000, '验证通过,40402 表示服务过期'
        assert response.json().get('data') is not None  # 待确认

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_020_equipment_ForPay(self, get_load_data_cloud, get_url, i=22):
        """支付设备列表"""
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + URLConf.PREFIX_VAS.value + get_load_data_cloud[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['hmac'] = get_v8_hmac(payload)
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') == 20000, '验证通过,40402 表示服务过期'
        assert response.json().get('data') is not None  # 断言响应

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_021_get_DeviceList(self, get_load_data_cloud, get_url, i=23):
        """通过用户id获取绑定的报警设备列表"""
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + URLConf.PREFIX_VAS.value + get_load_data_cloud[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['hmac'] = get_v8_hmac(payload)
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') == 20000, '验证通过,40402 表示服务过期'
        assert response.json().get('data') is not None  # 断言响应

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_023_equipment_BannerList(self, get_load_data_cloud, get_url, i=24):
        """多个设备维度banner列表"""
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + URLConf.PREFIX_VAS.value + get_load_data_cloud[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['hmac'] = get_v8_hmac(payload)
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') == 20000, '验证通过,40402 表示服务过期'
        assert response.json().get('data') is not None  # 断言响应

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_024_equipment_play(self, get_load_data_cloud, get_url, i=25):
        """播放器下方广告位统一"""
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + URLConf.PREFIX_VAS.value + get_load_data_cloud[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['hmac'] = get_v8_hmac(payload)
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') == 20000, '验证通过,40402 表示服务过期'
        assert response.json().get('data') is not None  # 断言响应

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_025_equipment_cloudHock(self, get_load_data_cloud, get_url, i=26):
        """equipmentCloudHook"""
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + URLConf.PREFIX_VAS.value + get_load_data_cloud[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['uid'] = globals()['devUid']
        payload['hmac'] = get_v8_hmac(payload)
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') == 20000, '验证通过,40402 表示服务过期'

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_026_equipment_mainHock(self, get_load_data_cloud, get_url, i=27):
        """equipmentMainHook"""
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + URLConf.PREFIX_VAS.value + get_load_data_cloud[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['hmac'] = get_v8_hmac(payload)
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') == 20000, '验证通过,40402 表示服务过期'

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_027_equipment_appHock(self, get_load_data_cloud, get_url, i=28):
        """equipment appHock"""
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + URLConf.PREFIX_VAS.value + get_load_data_cloud[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['uid'] = globals()['devUid']
        payload['hmac'] = get_v8_hmac(payload)
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') == 20000, '验证通过,40402 表示服务过期'
        # assert response.json().get('data') is not None '已购买云存'

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_028_equipment_H5Hock(self, get_load_data_cloud, get_url, i=29):
        '''equipment h5Hock'''
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + URLConf.PREFIX_VAS.value + get_load_data_cloud[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['uid'] = globals()['devUid']
        payload['hmac'] = get_v8_hmac(payload)
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') == 20000, '验证通过,40402 表示服务过期'
        assert response.json().get('data') is not None

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_029_equipment_playHock(self, get_load_data_cloud, get_url, i=30):
        '''equipment playHock '''
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + URLConf.PREFIX_VAS.value + get_load_data_cloud[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['uid'] = globals()['devUid']
        payload['hmac'] = get_v8_hmac(payload)
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') == 20000, '验证通过,40402 表示服务过期'
        # assert response.json().get('data') is not None   '已购买云存'

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_030_equipment_banner3(self, get_load_data_cloud, get_url, i=31):
        '''单个设备banner列表03'''
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + URLConf.PREFIX_VAS.value + get_load_data_cloud[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['uid'] = globals()['devUid']
        payload['hmac'] = get_v8_hmac(payload)
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') == 20000, '验证通过,40402 表示服务过期'

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_031_orderPay_remind(self, get_load_data_cloud, get_url, i=32):
        '''云回放页订单状态提醒'''
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + URLConf.PREFIX_VAS.value + get_load_data_cloud[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['uid'] = globals()['devUid']
        payload['hmac'] = get_v8_hmac(payload)
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') == 20000, '验证通过,40402 表示服务过期'
        assert response.json().get('data') is not None

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_032_orderPay_remind(self, get_load_data_cloud, get_url, i=33):
        '''播放器下方广告位统一02'''
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + URLConf.PREFIX_VAS.value + get_load_data_cloud[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['hmac'] = get_v8_hmac(payload)
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') == 20000, '验证通过,40402 表示服务过期'
        assert response.json().get('data') is not None

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_033_orderPay_remind(self, get_load_data_cloud, get_url, i=34):
        '''云回放页提醒订单状态-关闭广告条'''
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + URLConf.PREFIX_VAS.value + get_load_data_cloud[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['uid'] = globals()['devUid']
        payload['hmac'] = get_v8_hmac(payload)
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.post(url, headers=headers, params=payload)
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') == 20000, '验证通过,40402 表示服务过期'

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_034_equipment_banner(self, get_load_data_cloud, get_url, i=35):
        '''单个设备banner列表'''
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + URLConf.PREFIX_VAS.value + get_load_data_cloud[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['uid'] = globals()['devUid']
        payload['hmac'] = get_v8_hmac(payload)
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') == 20000, '验证通过,40402 表示服务过期'

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_035_equipment_banner2(self, get_load_data_cloud, get_url, i=36):
        '''单个设备banner列表02'''
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + URLConf.PREFIX_VAS.value + get_load_data_cloud[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['uid'] = globals()['devUid']
        payload['hmac'] = get_v8_hmac(payload)
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') == 20000, '验证通过,40402 表示服务过期'

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_038_cloud_memomotion_pause(self, get_load_data_cloud, get_url, i=39):
        '''时光沙漏视频暂停'''
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + URLConf.PREFIX_VAS.value + get_load_data_cloud[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        # 加密字段排序
        request_data = {
            "seq": payload['seq'], "userid": globals()['userId'],
            "uid": globals()['devUid'], "state": payload['state'],
        }
        request_data['hmac'] = get_notv8_hmac(request_data)
        logger.info('请求参数为：' + str(request_data))
        headers = {'Connection': 'close'}
        response = requests.put(url, headers=headers, params=request_data)
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') == '20000', '验证通过,40402 表示服务过期'

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.skip('影响生产数据，暂时跳过')
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_039_cloud_memomotion_delete(self, get_load_data_cloud, get_url, i=38):
        '''时光沙漏视频删除'''
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + URLConf.PREFIX_VAS.value + get_load_data_cloud[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        # 加密字段排序
        request_data = {
            'seq': payload['seq'], 'userid': globals()['userId'], 'memoIds': globals()['memoIds']
        }
        request_data['hmac'] = get_notv8_hmac(request_data)
        logger.info('请求参数为：' + str(request_data))
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=request_data)
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') == 20000, '验证通过,40402 表示服务过期'

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_040_serviceListByOrderCode(self, get_load_data_cloud, get_url, i=41):
        '''通过订单号和业务类型获取业务订单'''
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + URLConf.PREFIX_VAS.value + get_load_data_cloud[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['orderCode'] = globals()['orderCode']
        payload['hmac'] = get_v8_hmac(payload)
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') == 20000, '验证通过,40402 表示服务过期'

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_041_equipmentPlay_removehook(self, get_load_data_cloud, get_url, i=42):
        '''equipmentPlayRemoveHook'''
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + URLConf.PREFIX_VAS.value + get_load_data_cloud[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['uid'] = globals()['devUid']
        payload['hmac'] = get_v8_hmac(payload)
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') == 20000, '验证通过,40402 表示服务过期'

    @pytest.mark.cn
    @pytest.mark.hw
    # @pytest.mark.xfail('card和device都没入库')
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_042_get4gInfo_old(self, get_load_data_cloud, get_url, i=43):
        '''老版获取4G卡内容，线上在用'''
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + URLConf.PREFIX_VAS.value + get_load_data_cloud[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        # 设备未确认前，使用固定参数传值
        # payload['userid'] = globals()['userId']
        # payload['uid'] = globals()['devUid']
        # payload['hmac'] = get_v8_hmac(payload)
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') == 20000, '验证通过,40402 表示服务过期'
        assert response.json().get('data') is not None

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_043_get4gInfo_new(self, get_load_data_cloud, get_url, i=44):
        '''新版获取4G卡内容'''
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + URLConf.PREFIX_VAS.value + get_load_data_cloud[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['uid'] = globals()['devUid']
        payload['hmac'] = get_v8_hmac(payload)
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') == 20000, '验证通过,40402 表示服务过期'
        assert response.json().get('data') is not None

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_044_equipmentMsg_removeHook(self, get_load_data_cloud, get_url, i=45):
        '''消息页关闭hook'''
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + URLConf.PREFIX_VAS.value + get_load_data_cloud[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['hmac'] = get_v8_hmac(payload)
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') == 20000, '验证通过,40402 表示服务过期'

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_045_equipment_removeHook(self, get_load_data_cloud, get_url, i=46):
        '''设备云回放页 关闭hook'''
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + URLConf.PREFIX_VAS.value + get_load_data_cloud[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['hmac'] = get_v8_hmac(payload)
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') == 20000, '验证通过,40402 表示服务过期'

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_046_equipment_removeHook(self, get_load_data_cloud, get_url, i=47):
        '''设备直播页 hook'''
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + URLConf.PREFIX_VAS.value + get_load_data_cloud[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['uid'] = globals()['devUid']
        payload['hmac'] = get_v8_hmac(payload)
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') == 20000, '验证通过,40402 表示服务过期'
        # assert response.json().get('data') is not None   '已购买云存'

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_047_equipment_removeHook(self, get_load_data_cloud, get_url, i=48):
        '''通过iccid或did查询卡状态'''
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + URLConf.PREFIX_VAS.value + get_load_data_cloud[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['hmac'] = get_v8_hmac(payload)
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') == 20000, '验证通过,40402 表示服务过期'
        assert response.json().get('data') is not None

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_048_equipment_orderPayMessageRemind(self, get_load_data_cloud, get_url, i=49):
        '''消息页新增订单创建未购买、订单临期未续费、订单到期未续费钩子'''
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + URLConf.PREFIX_VAS.value + get_load_data_cloud[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['uid'] = globals()['devUid']
        payload['hmac'] = get_v8_hmac(payload)
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') == 20000, '验证通过,40402 表示服务过期'
        assert response.json().get('data') is not None

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_049_equipment_orderPaySDRemind(self, get_load_data_cloud, get_url, i=50):
        '''SD卡回放页新增云存订单状态提醒'''
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + URLConf.PREFIX_VAS.value + get_load_data_cloud[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['uid'] = globals()['devUid']
        payload['hmac'] = get_v8_hmac(payload)
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') == 20000, '验证通过,40402 表示服务过期'
        assert response.json().get('data') is not None

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_050_equipment_closeSDCloudOrderPayBanner(self, get_load_data_cloud, get_url, i=51):
        '''SD卡回放页新增云存订单状态提醒关闭广告条'''
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + URLConf.PREFIX_VAS.value + get_load_data_cloud[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['uid'] = globals()['devUid']
        payload['hmac'] = get_v8_hmac(payload)
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.post(url, headers=headers, params=payload)
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') == 20000, '验证通过,40402 表示服务过期'

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_051_equipment_one(self, get_load_data_cloud, get_url, i=52):
        """单个设备维度列表"""
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + URLConf.PREFIX_VAS.value + get_load_data_cloud[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['uid'] = globals()['devUid']
        payload['hmac'] = get_v8_hmac(payload)
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') == 20000, '验证通过,40402 表示服务过期'
        assert response.json().get('data') is not None  # 断言响应data

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_052_equipment_one(self, get_load_data_cloud, get_url, i=53):
        """设备维度云存服务列表"""
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + URLConf.PREFIX_VAS.value + get_load_data_cloud[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['hmac'] = get_v8_hmac(payload)
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') == 20000, '验证通过,40402 表示服务过期'

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_053_getNoLockDays(self, get_load_data_cloud, get_url, i=54):
        """getNoLockDays"""
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + URLConf.PREFIX_VAS.value + get_load_data_cloud[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['hmac'] = get_v8_hmac(payload)
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') == 20000, '验证通过,40402 表示服务过期'

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_054_getEquipment_lastBusOrder(self, get_load_data_cloud, get_url, i=55):
        """'''获取用户wifi设备及其最后一笔服务'''"""
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + URLConf.PREFIX_VAS.value + get_load_data_cloud[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['hmac'] = get_v8_hmac(payload)
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') == 20000, '验证通过,40402 表示服务过期'
        assert response.json().get('data') is not None

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.skip('没有4g设备，暂时跳过')
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_055_cloud_4gStatus(self, get_load_data_cloud, get_url, i=56):
        """'''设备云存订单状态（业务订单状态、设备设置状态）'''"""
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + URLConf.PREFIX_VAS.value + get_load_data_cloud[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        # 需要绑定4G设备，设备未确定前使用固定参数
        # payload['userid'] = globals()['userId']
        # payload['uid'] = globals()['devUid']
        # payload['hmac'] = get_v8_hmac(payload)
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') == 20000, '验证通过,40402 表示服务过期'
        assert response.json().get('data') is not None

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_056_get_4gList(self, get_load_data_cloud, get_url, i=57):
        """'''获取4G列表'''"""
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + URLConf.PREFIX_VAS.value + get_load_data_cloud[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['hmac'] = get_v8_hmac(payload)
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') == 20000, '验证通过,40402 表示服务过期'
        # assert response.json().get('data') is not None           #需要绑定4G设备，否则响应data数据为空

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_057_AI_cloudImages(self, get_load_data_cloud, get_url, i=58):
        """'''云存AI检索'''"""
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + URLConf.PREFIX_VAS.value + get_load_data_cloud[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        # payload['userid'] = globals()['userId']
        # payload['hmac'] = get_v8_hmac(payload)
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') == 20000, '验证通过,40402 表示服务过期'
        assert response.json().get('data') is not None

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.xfail(reason='设备信息不存在')
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_058_get_OSSToken_V9(self, get_load_data_cloud, get_url, i=59):
        """'''getOSSTokenV9'''"""
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + URLConf.PREFIX_VAS.value + get_load_data_cloud[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['hmac'] = get_v8_hmac(payload)
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') == 20000, '设备不存在'

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_059_cloud_index(self, get_load_data_cloud, get_url, i=60):
        """'''云存储，获取m3u8文件'''"""
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + URLConf.PREFIX_VAS.value + get_load_data_cloud[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        # payload['hmac'] = get_v8_hmac(payload)
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_060_main_removeHook(self, get_load_data_cloud, get_url, i=61):
        """'''equipmentMainRemoveHook'''"""
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + URLConf.PREFIX_VAS.value + get_load_data_cloud[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['hmac'] = get_v8_hmac(payload)
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
        assert response.json().get('code') == 20000, '验证通过,40402 表示服务过期'
        assert response.json().get('data') is None

    @pytest.mark.cn
    @pytest.mark.hw
    @pytest.mark.parametrize("get_load_data_cloud, get_url", [((path, current_file), '')],
                             indirect=["get_load_data_cloud", "get_url"])
    def test_062_cloud_hlsKey(self, get_load_data_cloud, get_url, i=62):
        """'''m3u8文件解密地址'''"""
        allure.dynamic.title(get_load_data_cloud[i][0])
        url = get_url + URLConf.PREFIX_VAS.value + get_load_data_cloud[i][1]
        logger.info('请求地址为：' + url)
        payload = eval(get_load_data_cloud[i][-1])  # 参数类型为dict
        payload['userid'] = globals()['userId']
        payload['uid'] = globals()['devUid']
        logger.info('请求参数为：' + str(payload))
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, params=payload)
        logger.info('响应结果为：' + response.text)
        assert response.status_code == 200, '请求返回非200'  # 断言请求是否成功
