#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2021/10/12 14:17
# @Author : zyf
# @description :


# test_1.py 测试用例层代码

import pytest, os
from selenium import webdriver
import allure
import sys
import time


def test_login(driver):

    driver.get("https://qzone.qq.com/")
    driver.find_element_by_name("u").send_keys("admin")
    driver.find_element_by_name("p").send_keys("123456")
    driver.quit()






if __name__ == "__main__":
    pytest.main(['--alluredir', 'D:/pytestFrame/Reports/allure_data', 'test_2.py::test_login'])
    # allure转换成---html并打开测试报告
    os.system('cd D:/se_frame/Reports/allure_data')
    os.system('allure generate D:/se_frame/Reports/allure_data -o D:/se_frame/Reports/html --clean')
