# #!/usr/bin/python3
# # -*- coding:utf-8 -*-
#
# """
# @author:
# @file: alipay_ui.py
# @time: 2021/6/3 16:27
# @desc:
# """
# import time
# from alipay import *
# from selenium import webdriver
#
# # 沙箱环境中 app 私钥
# app_private_key_string = open('app_private_key.pem').read()
#
# # alipay_public_key.pem   支付宝公钥
# alipay_public_key_string = open('alipay_public_key.pem').read()
#
#
# # 支付应用
# def get_alipay_url():
#     alipay = AliPay(
#         appid="2016102400750431",  # 创建的沙箱环境的appid
#         app_notify_url='https://openapi-cn-test.xiaoyi.com/orderpay/v8/ali/pay/callback',  # 设置为后台回调地址
#         app_private_key_string=app_private_key_string,  # 支付宝的公钥，验证支付宝回传消息使用,不是你自己的公钥
#         alipay_public_key_string=app_private_key_string,
#         sign_type="RSA",  # RSA 或者 RSA2
#         debug=True,  # 默认False,我们是沙箱，所以改成True(让访问沙箱环境支付宝地址)
#     )
#
#     # 电脑网站支付，需要跳转到https://openapi.alipay.com/gateway.do? + order_string
#     order_string = alipay.api_alipay_trade_page_pay(
#         out_trade_no="21060110187623",  # 订单id，应该从前端获取
#         total_amount=str(201),  # 订单总金额
#         subject="高级_连续包月",  # 付款标题信息
#         return_url=None,  # 付款成功回调地址(可以为空)
#         notify_url=None  # 付款成功后异步通知地址（可以为空）
#     )
#     pay_url = "https://openapi.alipaydev.com/gateway.do?" + order_string
#     print(pay_url)  # 将这个url复制到浏览器，就会打开支付宝支付页面
#     # 实例化浏览器
#     driver = webdriver.Chrome()
#     # 请求支付网站
#     driver.get(pay_url)
#     time.sleep(1)
#     # 输入账号
#     driver.find_element_by_xpath('//*[@id="J_tLoginId"]').send_keys('meassh9032@sandbox.com')
#     time.sleep(1)
#     # 输入密码
#     driver.find_element_by_xpath('//*[@id="payPasswd_rsainput"]').send_keys('111111')
#     time.sleep(1)
#     # 点击下一步
#     driver.find_element_by_xpath('//*[@id="J_newBtn"]/span').click()
#     time.sleep(5)
#     # 获取所有的窗口句柄
#     handles = driver.window_handles
#     # 切换到最新打开的窗口
#     driver.switch_to.window(handles[-1])
#     # search_window = driver.current_window_handle  # 此行代码用来定位当前页面
#     time.sleep(3)
#     # 输入支付宝支付密码
#     driver.find_element_by_id('payPassword_rsainput').send_keys('111111')
#     time.sleep(1)
#     # 点击确认按钮
#     driver.find_element_by_xpath('//*[@id="J_authSubmit"]').click()
#     time.sleep(1)
#     # # 判断是否登录成功
#     # try:
#     #     element = '//*[@id="header_user_right"]'
#     #     WebDriverWait(driver, 10, 0.5).until(EC.visibility_of_element_located((By.XPATH, element)))
#     #     print('！')
#     # except Exception as msg:
#     #     driver.get_screenshot_as_file('123.png')
#     #     print('')
#
#
# if __name__ == '__main__':
#     get_alipay_url()
