import logging

"""
日志 Tag 定义
- start-up：程序启动
- obs-update：Observer 有信息更新
- act-done：Action 完成
- shutdown：程序终止
"""


six_logger = logging.getLogger("six")
for handler in six_logger.handlers:
    if not isinstance(handler, logging.FileHandler):
        handler.setLevel(logging.ERROR)

logger = logging.getLogger("ddt")
logger.setLevel(logging.INFO)
# create file handler which logs even debug messages
fh = logging.FileHandler("ddt.log")
fh.setLevel(logging.INFO)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)
