import logging
from loguru import logger

# 配置 Loguru
logger.add("logs/{time:YYYY-MM-DD}.log", rotation="1 day", retention="7 days", level="INFO", encoding="utf-8")

# 为了兼容标准的 logging 模块，你可以使用以下代码将 loguru logger 适配为标准的 logging logger
class InterceptHandler(logging.Handler):
    def emit(self, record):
        # 获取调用者的文件名和行号
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1
        log = logger.bind(depth=depth, module=record.module)
        log_opt = log.opt(exception=record.exc_info)
        log_opt.log(record.levelname, record.getMessage())

logging.basicConfig(handlers=[InterceptHandler()], level=logging.INFO)

# 如果需要在项目的其他部分使用标准的 logging
logging.getLogger().handlers = [InterceptHandler()]


__all__ = ["logger"]




"""
logging的使用
在当前项目的任何地方，你都可以使用 logger 对象来记录日志。例如：

from windsummary.logging_config import logger

logger.info("This is an info message")

或者使用标准的 logging 模块：

import logging
# 获取日志记录器
log = logging.getLogger(__name__)  # __name__ 是当前模块的名称
log.info("This is an info message")

logging.getLogger(__name__) 是标准 Python logging 模块中的一个常用模式，用来获取一个与当前模块（或文件）关联的日志记录器（logger）实例。
"""