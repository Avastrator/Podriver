"""
LGK_Podriver_Receiver:
Longecko Podriver intelligence Receiver
By Avastrator
2025-03-23 11:57:05
"""
import websockets
import base64
import json
import brotli
import asyncio
import time
import socket

import LGK_Podriver_Args as a
import InterfaceHandlers.LGK_Podriver_EQRHandler as eqr
import InterfaceHandlers.LGK_Podriver_ESPHandler as esp
import InterfaceHandlers.LGK_Podriver_EEWHandler as eew

c = a.get("config")
output = a.get("logger")

a.set("eew_handlers", {})
a.set("eew_handler_queues", {})

# Get IP address
try:
    ip_address = socket.gethostbyname(c["podris_server"]["host"])
    output.info(f"Podris Server [{c["podris_server"]["host"]}] IP address: {ip_address}")
except socket.gaierror as e:
    output.error(f"Failed to get Podris Server [{c["podris_server"]["host"]}] IP address: {e}")
    raise e

ws_url = f"ws://{ip_address}:{str(c["podris_server"]["port"])}"

async def handler_manager(data):
    """
    Dispatch messages to corresponding handling functions
    """
    async def eew_handler_manager(data):
        global eew_tasks
        if data["event_id"] in a.get("eew_handlers"): # Already have a corresponding processing task
            a.get("eew_handler_queues")[data["event_id"]].put_nowait(data)
        else:
            # Create a new handler task
            a.get("eew_handler_queues")[data["event_id"]] = asyncio.Queue()
            a.get("eew_handler_queues")[data["event_id"]].put_nowait(data)
            a.get("eew_handlers")[data["event_id"]] = asyncio.create_task(eew.handler(data["event_id"]))
    if isinstance(data, list):
        await eqr.eqlist_handler(data)  # 直接 await 异步函数
    elif any(i in data.get("event_source", "") for i in c["source_filter"]) and c["source_filter_type"] == "blacklist":
        return
    elif any(i not in data.get("event_source", "") for i in c["source_filter"]) and c["source_filter_type"] == "whitelist":
        return
    elif data["event_type"] == "EQR":
        asyncio.create_task(eqr.handler(data))
    elif data["event_type"] == "EEW" and data["report_final"] == True:
        await eew_handler_manager(data)
        asyncio.create_task(eqr.handler(data))
    elif data["event_type"] == "EEW" and data["report_final"] == False:
        await eew_handler_manager(data)
    elif data["event_type"] == "ESP":
        asyncio.create_task(esp.handler(data))
    else:
        return

async def receiver():
    a.set("ws_retrytime", 0)
    def decoder(data):
        return json.loads(str(brotli.decompress(base64.b64decode(data)).decode("utf-8")))

    while True:
        try:
            while a.get("ref_eqlist_control") == None: # Wait for app launch
                await asyncio.sleep(0.05)
                continue
            async with websockets.connect(ws_url, additional_headers=[("Authorization", f"Bearer {c["podris_server"]["token"]}")]) as websocket:
                # Handshake
                message = await websocket.recv()
                data = decoder(message)
                if "ver" in data:
                    output.info(f"Connected to Podris Server! Server Version: {data['ver']}, latency: {str((time.time_ns() // 1000000) - data["time"])}ms")
                    a.set("ws_retrytime", 0) # Reset retry time
                    for i in data["active_eew"]:
                        asyncio.create_task(handler_manager(i))
                    await websocket.send("get_eqlist")
                    data = decoder(await websocket.recv())
                    asyncio.create_task(handler_manager(data))
                else:
                    raise Exception("Handshake failed!")
                while True:
                    message = await websocket.recv()
                    data = decoder(message)
                    asyncio.create_task(handler_manager(data))
        except asyncio.CancelledError:
            # Cancelled by the main task
            break
        except Exception as e:
            # Exponential backoff handling connection errors
            retry_time = a.get("ws_retrytime")
            if a.get("ws_retrytime") < 8:  # Maximum tolerated errors
                a.set("ws_retrytime", retry_time + 1)
                retry_time = a.get("ws_retrytime")
                output.error(f"WebSocket connection error: {str(e)} {str(retry_time)} Retrying in {2 ** retry_time} seconds")
            else:
                # Maximum tolerated errors reached
                output.error(f"WebSocket connection error and maximum tolerated errors reached: {str(e)} {str(retry_time)} Retrying in {2 ** retry_time} seconds")
            await asyncio.sleep(2 ** retry_time)
