# !/usr/bin/python3
# -*- coding: utf-8 -*-
import logging
import oss2

logger = logging.getLogger(__name__)


class Base_func(object):
    def log_info(self, get_load_data_cloud, get_url, url, response, i):
        logger.info('用例名称：' + get_load_data_cloud[i][0])
        logger.info('环境地址为：' + get_url)
        logger.info('请求地址为：' + url)
        logger.info('响应结果为：' + response.text)

    def cloud_oss(self, bucket_file, file):
        """
         # 阿里云账号AccessKey拥有所有API的访问权限，风险很高。强烈建议您创建并使用RAM用户进行API访问或日常运维，请登录RAM控制台创建RAM用户。
        :param file:
        :return:
        """
        # bucket:  'xiaoyi-css-cn-7d',  file: 'TNPCHNG-492868-HRCJK/20210520/8560209/'
        auth = oss2.Auth('Pa0tZniM9vyAqqMn', 'SNRE7QOjLURKIjg9rZjatz0HInJxh3')
        # Endpoint以杭州为例，其它Region请按实际情况填写。
        bucket = oss2.Bucket(auth, 'https://oss-cn-shanghai.aliyuncs.com', bucket_file)
        # 列举fun文件夹下的所有文件，包括子目录下的文件。
        image_list = []
        for obj in (oss2.ObjectIterator(bucket, prefix=file)):
            image_list.append(obj.key)
        return image_list


if __name__ == '__main__':
    b = Base_func()
    print(b.cloud_oss('xiaoyi-css-cn-7d', 'TNPCHNG-492868-HRCJK/20210520/8560209'))
