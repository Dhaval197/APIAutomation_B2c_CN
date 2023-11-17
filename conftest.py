# !/usr/bin/python3
# -*- coding: utf-8 -*-
import json
import os
import time
import sys

import pytest

import allure
import os
import platform

import requests
from selenium import webdriver

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
    parser.addoption(
        "--eurl", action="store", default="cn_test",
        choices=["cn_test", "cn_prod"],
        help="将命令行参数 ’--eurl' 添加到 pytest 配置中"
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


# 使用request.config.getoption("--命令行")获取命令行参数的值
@pytest.fixture(scope='session')
def eurl(request):
    """从配置对象中读取自定义参数的值"""
    return request.config.getoption('--eurl')


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


driver = None

def sendMsg(count_all, passed, failed, error, skipped, dutation, reportUrl='http://192.168.1.105:63342/yiHome_yiIot_api/report/allure_report/index.html'):
    """
    reportUrl 本地报告服务地址，不同机器注意替换
    """
    # 企微群webhook地址
    url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=d50f8468-f817-4cd6-a946-409a5bffdc2c1'
    header = {'Content-Type': 'application/json'}
    # 报告内容
    Data = {
        "msgtype": "markdown",
        "markdown": {
            'content': '本次执行情况如下：\n'
                       '总用例数为：{}\n'
                       '通过用例数：<font color=\\"info\\">{}条</font>\n'
                       '失败用例数：<font color=\\"warning\\">{}条</font>\n'
                       '错误用例数：{}\n'
                       '跳过用例数：{}\n'
                       '用时：{}s\n'
                       '报告地址： {}'
            .format(count_all, passed, failed, error, skipped, dutation, reportUrl)
            # 下方代码在群里@相应的人员，注意需要使用userid，就是用户名，不是中文名称，是企业微信通讯录中的“帐号”，这里不用修改，只需要知道账号就可以了。
            # "mentioned_list": ["@all"],
            # "mentioned_list" :[User,"@all"],
            # 下方代码可使用手机号进行提示，本示例中并未示例
            # "mentioned_mobile_list" : ["13800000000","@all"]
        }
    }
    res = requests.post(url=url, headers=header, data=json.dumps(Data), verify=False)
    if res.status_code == 200:
        print('报告发送成功')


def pytest_terminal_summary(terminalreporter):
    print("total：", terminalreporter._numcollected)
    print('passed：', len([i for i in terminalreporter.stats.get('passed', []) if i.when != 'teardown']))
    print('failed：', len([i for i in terminalreporter.stats.get('failed', []) if i.when != 'teardown']))
    print('error：', len([i for i in terminalreporter.stats.get('error', []) if i.when != 'teardown']))
    print('skipped：', len([i for i in terminalreporter.stats.get('skipped', []) if i.when != 'teardown']))
    print('成功率：%.2f' % (len(terminalreporter.stats.get('passed', [])) / terminalreporter._numcollected * 100) + '%')
    # terminalreporter._sessionstarttime 会话开始时间
    duration = time.time() - terminalreporter._sessionstarttime
    print('total times：', round(duration,2), 'seconds')
    sendMsg(terminalreporter._numcollected, len(terminalreporter.stats.get('passed', [])),
            len(terminalreporter.stats.get('failed', [])), len(terminalreporter.stats.get('error', [])),
            len(terminalreporter.stats.get('skipped', [])), round(duration,2))

# 用例失败后自动截图
# @pytest.hookimpl(tryfirst=True, hookwrapper=True)
# def pytest_runtest_makereport(item, call):
#     """
#     获取用例执行结果的钩子函数
#     :param item:
#     :param call:
#     :return:
#     """
#     outcome = yield
#     report = outcome.get_result()
#     if report.when == "call" and report.failed:
#         mode = "a" if os.path.exists("failures") else "w"
#         with open("failures", mode)as f:
#             if "tmpir" in item.fixturenames:
#                 extra = " (%s)" % item.funcargs["tmpdir"]
#             else:
#                 extra = ""
#                 f.write(report.nodeid + extra + "\n")
#             with allure.step('添加失败截图...'):
#                 allure.attach(driver.get_screenshot_as_png(), "失败截图", allure.attachment_type.PNG)


# sys_platform = platform.system()


# @pytest.fixture(scope='session', autouse=True)
# def driver():
#     """
#     定义一个总的调用driver的方法，用例中直接调用 driver
#     # 定义一个总的调用driver的方法，用例中直接调用browser
#     :return:
#     """
#     global driver
#     if "Windows" in sys_platform:
#         driver = webdriver.Chrome(r"C:\Program Files\Google\Chrome\Application\chromedriver.exe")
#     else:
#         # firefox
#         time.sleep(2)
#         # options = webdriver.FirefoxOptions()
#         # options.add_argument('--headless')
#         # options.add_argument('--no-sandbox')
#         # options.add_argument('--disable-dev-shm-usage')
#         # driver = webdriver.Firefox(options=options)
#         driver = webdriver.Chrome()
#
#     return driver


