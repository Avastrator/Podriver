ver = "1.0.0-alpha.6"

"""
Podriver
Practical Online Disaster Reduction Intelligence ViewER
By Avastrator
Powered By Flet & Project Podris
2025-01-27 19:28:55
"""
import flet as ft
import os
import json
import aiohttp
import asyncio

from LGK_Podriver_IO_Logger import logger

# Envionment variables
import LGK_Podriver_Args as a
a._init()
stg_path = os.getenv("FLET_APP_STORAGE_DATA", r"D:\Code\podriver\storage\data")
tmp_path = os.getenv("FLET_APP_STORAGE_TEMP", r"D:\Code\podriver\storage\temp")
if os.getenv("FLET_PLATFORM") == "windows":
    ass_path = os.path.join(os.getenv("PYTHONPATH").split(";")[0], "assets") # Windows端的FLET_ASSETS_DIR被狗吃了
else:
    ass_path = os.getenv("FLET_ASSETS_DIR")
ass_path = r"D:\Code\podriver\src\assets"
if stg_path is None or ass_path is None or tmp_path is None:
    raise Exception(f"Environment variables ERROR: [{str(os.environ)}]")
a.set("ver", ver)
a.set("stg_path", stg_path)
a.set("ass_path", ass_path)
a.set("tmp_path", tmp_path)

# Logger
output = logger(f"PODRIVER_{ver}")
a.set("logger", output)

# Configuration

eg_c = json.load(open(os.path.join(ass_path, "config.example"), "r", encoding="utf-8"))
try:
    c = json.load(open(os.path.join(stg_path, "config.conf"), "r", encoding="utf-8"))
    if c.get("config_version", None) != eg_c["config_version"]:
        output.warn(f"Configuration version mismatch, the configuration will be reset to the default configuration")
        os.rename(os.path.join(stg_path, "config.conf"), os.path.join(stg_path, "config.conf.INVAID"))
        raise FileNotFoundError
except FileNotFoundError:
    with open(os.path.join(stg_path, "config.conf"), "w", encoding="utf-8") as f:
        json.dump(eg_c, f, ensure_ascii=False, indent=4)
    c = eg_c
l = json.load(open(os.path.join(ass_path, "lang.json"), "r", encoding="utf-8"))
a.set("config", c)
a.set("lang", l)

# Initialization
from LGK_Podriver_Utils import cache_clean
async def get_ip_config():
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        for _ in range(3):
            try:
                async with session.get("https://uapis.cn/api/myip.php") as response:
                    r = await response.json()
                    output.info(f"Obtained IP info: {r}")
                    return {"address": r["ip"], "region": r["region"], "location": [float(r["latitude"]), float(r["longitude"])]}
            except Exception as e:
                output.warn(f"Failed to obtain IP info: [{str(e)}] Retrying...")
            output.warn(f"Failed to obtain IP info, The default configuration will be used")
            return c["ipconfig"] # Default configuration

if c["ipconfig"]["force_use"] == False:
    ipconfig = asyncio.run(get_ip_config())
    output.info(f"GOT IPCONFIG ONLINE: {str(ipconfig)}")
else:
    ipconfig = c["ipconfig"]
    output.info(f"GOT IPCONFIG LOCAL: {str(ipconfig)}")
a.set("ipconfig", ipconfig)

if c["clear_cache"] == True:
    cache_size = cache_clean()
    output.info(f"Cache cleared, size: {round(cache_size, 2)}MB")

# Modules
from LGK_Podriver_UI_OOBE import oobe_app
from LGK_Podriver_UI_Main import app
from LGK_Podriver_Receiver import receiver
import InterfaceHandlers.LGK_Podriver_MapFocusManager as mfm

async def main():
    # launch modules
    asyncio.create_task(receiver())
    asyncio.create_task(mfm.manager())
    # launch flet app
    await ft.app_async(target=app)

asyncio.run(main())  # 启动事件循环并运行主协程