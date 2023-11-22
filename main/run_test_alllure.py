import pytest
import threading
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')
from common.report import Report

project_root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
report_dir = os.path.join(project_root, 'report')
result_dir = os.path.join(report_dir, 'allure_result')
allure_report = os.path.join(report_dir, 'allure_report')

report = Report()

print(__file__)
# 进入test_case目录

os.chdir('../test_case')

# 定义标签，按照指定标签过滤运行用例
tag = "cn"


def run_pytest():
    # params = ['test_cloud_profess.py', 'test_order_profess.py', "--env=cn_prod"]
    # params = ['test_cloud_profess.py', "--env=cn_prod"]
    params = ['test_order_profess.py', "--env=cn_prod"]
    # pytest.main(['-v', '-s', f'--alluredir={result_dir}'])
    # pytest.main(['test_cloud_profess.py', 'test_order_profess.py', '-vs', "-m", f"{tag}",
    #              f'--alluredir={result_dir}'])

    # pytest.main(['test_smoke.py','-vs', "-m", f"{tag}","--env=hw_test",f'--alluredir={result_dir}'])
    # pytest.main(['test_product_profess.py','-vs', "-m", f"{tag}","--env=hw_test",f'--alluredir={result_dir}'])
    # pytest.main(['test_smoke.py','-vs', "-m", f"{tag}","-k","test_035_get_cloud_status_of_device", "--env=hw_test",
    #              f'--alluredir={result_dir}'])
    params.extend(['-vs', "-m", f"{tag}", f'--alluredir={result_dir}', '--clean-alluredir'])
    pytest.main(params)


def general_report():
    # cmd = "{} generate {} -o {} --clean".format(report.allure, result_dir, allure_report)
    # print(os.popen(cmd).read())
    os.system(f"allure generate {result_dir} -o {allure_report} --clean ")
    os.system(f"allure open {allure_report}")


if __name__ == '__main__':
    # run = threading.Thread(target=run_pytest)
    # gen = threading.Thread(target=general_report)
    # run.start()
    # run.join()
    # gen.start()
    # gen.join()
    run_pytest()
    general_report()
