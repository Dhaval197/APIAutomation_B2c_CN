# !/usr/bin/python3
# -*- coding: utf-8 -*-

import enum


class URLConf(enum.Enum):
    """
    环境配置枚举类
    """
    url_mapping = {
        'cn_test': 'https://gw-test.xiaoyi.com/',
        'cn_prod': 'https://gw.xiaoyi.com/',
        'hw_test': 'http://test-api.us.xiaoyi.com/',
        'us_prod': 'https://gw-us.xiaoyi.com/',
        'sg_prod': 'https://gw-sg.xiaoyi.com/',
        'eu_prod': 'https://gw-eu.xiaoyi.com/'
    }

    # 订单路由
    PREFIX_ORDER = 'orderpay/'
    # 云存路由
    PREFIX_VAS = 'vas/'
    wx_url = {
        # 微信支付的url 不需要网关的 ，这里的网关都可以关系了 ，以下连个都直接配置到程序中了
        'test_url': 'https://openapi-cn-test.xiaoyi.com/orderpay/v8/wx/pay/callback',  # 直接调用微信的，不走网关
        'pro_url': 'https://open-gw.xiaoyi.com/orderpay/v8/wx/pay/callback'  # 直接调用微信的，不走网关
    }
