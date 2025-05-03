"""
LGK_Podris_IO_Logger:
Longecko ProjectPodris Input&Output Logger
By Avastrator
2024-12-01 10:35:19
"""
import atexit
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from queue import Queue

class logger:
    """
    一个日志记录器
    Args:
        comp (str): 组件名
        level (str): 需要写入到本地的日志级别，支持 "INFO", "WARN", "ERROR", "NONE"
        log_file (str): 日志文件的完整路径
    """
    LEVEL_ORDER = {"NONE": 0, "INFO": 1, "WARN": 2, "ERROR": 3}

    def __init__(self, comp, level, log_file):
        self.comp = comp
        self.save_level = level.upper()  # 使用字符串初始化日志级别
        self.log_file = log_file  # 直接使用指定的文件路径
        self.log_queue = Queue()
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.executor.submit(self._process_queue)
        atexit.register(self.close)  # 注册 close 方法在程序退出时调用

    def _process_queue(self):
        """后台线程处理日志队列"""
        while True:
            log = self.log_queue.get()
            if log is None:
                break
            with open(self.log_file, 'a', encoding="utf-8") as f:
                f.write(log + "\n")
            self.log_queue.task_done()

    def _log(self, level, content):
        """通用日志记录方法"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        string = f"[{timestamp}][{level}][{self.comp}] {content}"
        print(string)
        if self._should_save(level):
            self.log_queue.put(string)

    def _should_save(self, level):
        """判断是否需要保存日志"""
        return (self.save_level != "NONE" and 
                self.LEVEL_ORDER[self.save_level] <= self.LEVEL_ORDER[level])

    def info(self, content):
        """记录 INFO 级别的日志"""
        self._log("INFO", content)

    def warn(self, content):
        """记录 WARN 级别的日志"""
        self._log("WARN", content)

    def error(self, content):
        """记录 ERROR 级别的日志"""
        self._log("ERROR", content)

    def close(self):
        """关闭日志记录器，停止后台线程"""
        self.log_queue.put(None)  # 停止队列处理
        self.executor.shutdown(wait=True)  # 等待线程池中的任务完成
