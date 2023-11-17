# !/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import pytest

from common.parse_excel import ParseExcel
from config.url_config import URLConf


def pytest_collection_modifyitems(items):
    """
    测试用例收集完成时，将收集到的item的name和nodeid的中文显示在控制台上
    :return:
    """
    for item in items:
        item.name = item.name.encode("utf-8").decode("unicode_escape")
        print(item.nodeid)
        item._nodeid = item.nodeid.encode("utf-8").decode("unicode_escape")


# 定义pytest_addoption方法注册 pytest命令行参数，函数名和参数保持一致
def pytest_addoption(parser):
    """注册自定义参数 env 到配置对象"""
    parser.addoption(
        "--env", action="store", default="cn_test",
        choices=["cn_test", "cn_prod", "hw_test", "us_prod", "sg_prod", "eu_prod"],
        help="将命令行参数 ’--env' 添加到 pytest 配置中"
    )


# 使用request.config.getoption("--命令行")获取命令行参数的值
@pytest.fixture(scope='session')
def get_env(request):
    """从配置对象中读取自定义参数的值"""
    return request.config.getoption('--env')


@pytest.fixture(scope='session')
def get_url(request):
    """获取不同环境对应的服务地址"""
    env = request.getfixturevalue("get_env")
    url_mapping = URLConf.url_mapping.value
    return url_mapping.get(env)


@pytest.fixture(scope='session')
def get_load_data(request):
    """获取不同环境对应的测试数据"""
    # 获取解析到的test_data所在的目录，以及调用test_data的文件，为环境归类
    data_folder, test_file = request.param
    env = request.getfixturevalue('get_env')
    env_folder = os.path.join(data_folder, env)
    # 根据传入的环境变量参数，计算出应该用那个环境下的数据文件
    data_file_name = test_file.replace('.py', '.xlsx')
    data_file = os.path.join(env_folder, data_file_name)  # .xlsx文件所在路径
    sheetName = 'order_api_v8_test_data'
    data = ParseExcel(data_file, sheetName)
    data_list1 = []
    # 按照需求提取Excel文件中的数据
    for i in data.getDatasFromSheet():
        testname = str(i[1])
        uri = str(i[3])
        method = i[5]
        params_tpye = str(i[-2])
        params = i[-1]
        data_list1.append(testname)
        data_list1.append(uri)
        data_list1.append(method)
        data_list1.append(params_tpye)
        data_list1.append(params)
    data_list = []
    # 提取到的数据处理成指定格式
    for j in range(len(data_list1) // 5):
        ret = data_list1[0:5]
        data_list.append(ret)
        for m in ret:
            data_list1.remove(m)
    return data_list


@pytest.fixture(scope='session')
def get_load_data_product(request):
    """获取不同环境对应的测试数据"""
    # 获取解析到的test_data所在的目录，以及调用test_data的文件，为环境归类
    data_folder, test_file = request.param
    env = request.getfixturevalue('get_env')
    env_folder = os.path.join(data_folder, env)
    # 根据传入的环境变量参数，计算出应该用那个环境下的数据文件
    data_file_name = test_file.replace('.py', '.xlsx')
    data_file = os.path.join(env_folder, data_file_name)  # .xlsx文件所在路径
    sheetName = 'product_api_v8_test_data'
    data = ParseExcel(data_file, sheetName)
    data_list1 = []
    # 按照需求提取Excel文件中的数据
    for i in data.getDatasFromSheet():
        testname = str(i[1])
        uri = str(i[3])
        method = i[5]
        params_tpye = str(i[-2])
        params = i[-1]
        data_list1.append(testname)
        data_list1.append(uri)
        data_list1.append(method)
        data_list1.append(params_tpye)
        data_list1.append(params)
    data_list = []
    # 提取到的数据处理成指定格式
    for j in range(len(data_list1) // 5):
        ret = data_list1[0:5]
        data_list.append(ret)
        for m in ret:
            data_list1.remove(m)
    return data_list


@pytest.fixture(scope='session')
def get_load_data_cloud(request):
    """获取不同环境对应的测试数据"""
    # 获取解析到的test_data所在的目录，以及调用test_data的文件，为环境归类
    data_folder, test_file = request.param
    env = request.getfixturevalue('get_env')
    env_folder = os.path.join(data_folder, env)
    # 根据传入的环境变量参数，计算出应该用那个环境下的数据文件
    data_file_name = test_file.replace('.py', '.xlsx')
    data_file = os.path.join(env_folder, data_file_name)  # .xlsx文件所在路径
    sheetName = 'cloud_api_v8_test_data'
    data = ParseExcel(data_file, sheetName)
    data_list1 = []
    # 按照需求提取Excel文件中的数据
    for i in data.getDatasFromSheet():
        testname = str(i[1])
        uri = str(i[3])
        method = i[5]
        params_tpye = str(i[-2])
        params = i[-1]
        data_list1.append(testname)
        data_list1.append(uri)
        data_list1.append(method)
        data_list1.append(params_tpye)
        data_list1.append(params)
    data_list = []
    # 提取到的数据处理成指定格式
    for j in range(len(data_list1) // 5):
        ret = data_list1[0:5]
        data_list.append(ret)
        for m in ret:
            data_list1.remove(m)
    return data_list


@pytest.fixture(scope='session')
def get_load_data_oms(request):
    """获取不同环境对应的测试数据"""
    # 获取解析到的test_data所在的目录，以及调用test_data的文件，为环境归类
    data_folder, test_file = request.param
    env = request.getfixturevalue('get_env')
    env_folder = os.path.join(data_folder, env)
    # 根据传入的环境变量参数，计算出应该用那个环境下的数据文件
    data_file_name = test_file.replace('.py', '.xlsx')
    data_file = os.path.join(env_folder, data_file_name)  # .xlsx文件所在路径
    sheetName = 'oms_api_test_data'
    data = ParseExcel(data_file, sheetName)
    data_list1 = []
    # 按照需求提取Excel文件中的数据
    for i in data.getDatasFromSheet():
        testname = str(i[1])
        uri = str(i[3])
        method = i[5]
        params_tpye = str(i[-2])
        params = i[-1]
        data_list1.append(testname)
        data_list1.append(uri)
        data_list1.append(method)
        data_list1.append(params_tpye)
        data_list1.append(params)
    data_list = []
    # 提取到的数据处理成指定格式
    for j in range(len(data_list1) // 5):
        ret = data_list1[0:5]
        data_list.append(ret)
        for m in ret:
            data_list1.remove(m)
    return data_list
