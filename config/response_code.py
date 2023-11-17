# !/usr/bin/python3
# -*- coding: utf-8 -*-
import enum


class ResCode(enum.Enum):
    """
    环境配置枚举类
    """
    res_mapping = {
        'success': [20000, '20000'],  # 接口响应成功code值
        'error': [99999, '99999']  # 接口响应失败code值
    }
