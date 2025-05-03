ver = 0.1

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

from LGK_Podris_IO_Logger import logger

# Envionment variables
import LGK_Podriver_Args as a
a._init()
stg_path = os.getenv("FLET_APP_STORAGE_DATA")
tmp_path = os.getenv("FLET_APP_STORAGE_TEMP")
if os.getenv("FLET_PLATFORM") == "windows":
    ass_path = os.path.join(os.getenv("PYTHONPATH").split(";")[0], "assets") # Windows端的FLET_ASSETS_DIR被狗吃了
else:
    ass_path = os.getenv("FLET_ASSETS_DIR")
if stg_path is None or ass_path is None or tmp_path is None:
    raise Exception(f"Environment variables ERROR: [{str(os.environ)}]")
a.set("ver", ver)
a.set("stg_path", stg_path)
a.set("ass_path", ass_path)
a.set("tmp_path", tmp_path)

# Configuration
try:
    c = json.load(open(os.path.join(stg_path, "config.conf"), "r", encoding="utf-8"))
except FileNotFoundError:
    c = json.load(open(os.path.join(ass_path, "config.example"), "r", encoding="utf-8"))
    with open(os.path.join(stg_path, "config.conf"), "w", encoding="utf-8") as f:
        json.dump(c, f, ensure_ascii=False, indent=4)
l = json.load(open(os.path.join(ass_path, "lang.json"), "r", encoding="utf-8"))
a.set("config", c)
a.set("lang", l)

# Logger
output = logger(f"PODRIVER_{ver}", c["log_level"], os.path.join(stg_path, "output.log"))
a.set("logger", output)

# Initialization
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

# Modules
from LGK_Podriver_UI_OOBE import oobe_app
from LGK_Podriver_UI_Main import app
from LGK_Podriver_Receiver import receiver
import InterfaceHandlers.LGK_Podriver_MapFocusManager as mfm

async def main():
    # launch modules
    rev_task = asyncio.create_task(receiver())
    mfm_task = asyncio.create_task(mfm.manager())
    # launch flet app
    await ft.app_async(target=app)
    # shutdown
    rev_task.cancel()
    mfm_task.cancel()
    output.close()

asyncio.run(main())  # 启动事件循环并运行主协程
