"""
LGK_Podriver_IO_Logger:
Longecko Podriver Input&Output Logger
By Avastrator
2024-12-01 10:35:19
"""
from datetime import datetime

class logger:
    """
    一个日志记录器(仅输出)
    Args:
        comp (str): 组件名
    """

    def __init__(self, comp):
        self.comp = comp

    def _log(self, level, content):
        """通用日志记录方法"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}][{level}][{self.comp}] {content}")

    def info(self, content):
        """记录 INFO 级别的日志"""
        self._log("INFO", content)

    def warn(self, content):
        """记录 WARN 级别的日志"""
        self._log("WARN", content)

    def error(self, content):
        """记录 ERROR 级别的日志"""
        self._log("ERROR", content)