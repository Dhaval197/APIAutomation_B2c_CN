import pytest
from loguru import logger


@pytest.fixture(scope='session')
def log_info(get_load_data_cloud, get_url, url, response, i):
    logger.info('用例名称：' + get_load_data_cloud[i][0])
    logger.info('环境地址为：' + get_url)
    logger.info('请求地址为：' + url)
    logger.info('响应结果为：' + response.text)
