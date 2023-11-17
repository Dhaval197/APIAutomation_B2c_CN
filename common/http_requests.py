# !/usr/bin/python3
# -*- coding: utf-8 -*-
import requests


# 定义一个HttpRequests的类
class HttpRequests(object):
    """
    :param url: 接口请求地址
    :param method: 接口请求方法：get/post或其他
    :param params: url额外参数，字典或字节流格式（多用于字典格式，字节流的话，多用于文件操作）
    :param data:   字典、字节序列或文件对象（多用于字典）
    :param headers: 请求头信息，字典形式
    :param json:    JSON格式的数据，作为参数传递
    :param cookies:  cookies信息，str类型
    :param  timeout:   设定超时时间，秒为单位
    """
    def __init__(self, url):
        self.url = url
        self.req = requests.session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/84.0.4147.125 Safari/537.36 '
        }

    # 封装get请求
    def get(self, uri='', params='', data='', headers=None, cookies=None):
        url = self.url + uri
        response = self.req.get(url, params=params, data=data, headers=headers, cookies=cookies)
        return response

    # 封装post方法
    def post(self, uri='', params='', data='', headers=None, cookies=None):
        url = self.url + uri
        response = self.req.post(url, params=params, data=data, headers=headers, cookies=cookies)
        return response

    # 封装put方法
    def put(self, uri='', params='', data='', headers=None, cookies=None):
        url = self.url + uri
        response = self.req.put(url, params=params, data=data, headers=headers, cookies=cookies)
        return response

    # 封装delete方法
    def delete(self, uri='', params='', data='', headers=None, cookies=None):
        url = self.url + uri
        response = self.req.delete(url, params=params, data=data, headers=headers, cookies=cookies)
        return response
