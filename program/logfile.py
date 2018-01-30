# -*- encoding:utf-8 -*-
import logging

import logging

 # 创建一个logger
logger = logging.getLogger('logging')
logger.setLevel(logging.DEBUG)

 # 创建一个handler，用于写入日志文件
fh = logging.FileHandler('classification.log')
fh.setLevel(logging.DEBUG)

 # 再创建一个handler，用于输出到控制台
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

 # 定义handler的输出格式
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

 # 给logger添加handler
logger.addHandler(fh)
logger.addHandler(ch)

