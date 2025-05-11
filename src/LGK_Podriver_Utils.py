"""
LGK_Podriver_Utils:
Longecko Podriver Utils
By Avastrator
2025-04-19 10:27:40
"""
import os
import time

import LGK_Podriver_Args as a
output = a.get("logger")
c = a.get("config")
stg_path = a.get("stg_path")
tmp_path = a.get("tmp_path")

def shindo_to_cn(i: float):
    intensity_cases = {
        0.0: "零",
        1.0: "一",
        2.0: "二",
        3.0: "三",
        4.0: "四",
        4.75: "五弱",
        5.25: "五强",
        5.75: "六弱",
        6.25: "六强",
        7: "七"
    }
    return intensity_cases.get(float(i), str(i))

def shindo_to_en(i: float):
    intensity_cases = {
        0.0: "zero",
        1.0: "one",
        2.0: "two",
        3.0: "three",
        4.0: "four",
        4.75: "five lower",
        5.25: "five upper",
        5.75: "six lower",
        6.25: "six upper",
        7: "seven"
    }
    return intensity_cases.get(float(i), str(i))

def cache_clean():
    cache_size = 0
    # 清空TTS文件
    try:
        for filename in os.listdir(os.path.join(tmp_path, "TTS")):
            if filename.endswith(".mp3"):
                file_path = os.path.join(tmp_path, "TTS", filename)
                # 记录大小
                cache_size += os.path.getsize(file_path)
                os.remove(file_path)
    except FileNotFoundError:
        pass
    return cache_size / 1024 / 1024 # 返回清理的MB值


def safe_exit():
    if c["clear_cache"] == True:
        cache_size = cache_clean()
        output.info(f"Cache cleared, size: {round(cache_size, 2)}MB")
    if c["save_log"] == True:
        try:
            with open(os.path.join(tmp_path, "console.log"), "rb") as src, open(os.path.join(stg_path, f"{str(time.time())}.log"), "wb") as dst:
                data = src.read()
                dst.write(data)
            output.info("LOG SAVED")
        except Exception as e:
            output.warn(f"Failed to save log: [{str(e)}]")