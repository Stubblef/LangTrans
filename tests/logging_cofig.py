import logging
from loguru import logger

# 配置 Loguru
logger.add(
    "logs/{time:YYYY-MM-DD}.log", 
    rotation="1 week",  # 每周一个日志文件
    retention="2 weeks",  # 保留两周的日志文件
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    encoding="utf-8",
    compression="zip",  # 压缩旧的日志文件
    )

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