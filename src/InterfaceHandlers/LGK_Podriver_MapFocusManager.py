"""
LGK_Podriver_MapFocusManager:
Longecko Podriver Interface Map Focuses Manager
By Avastrator
2025-03-30 09:46:20
"""
import flet_map as map
import asyncio

import LGK_Podriver_Args as a

c = a.get("config")

a.set("map_focus_list", [])

async def manager():
    try:
        while True:
            await asyncio.sleep(0.05)
            for i in a.get("map_focus_list")[:]:
                await asyncio.sleep(float(c["eew"]["epicenters_alternate_display_interval"]))
                if i not in a.get("map_focus_list"):
                    continue
                a.get("ref_map_control").current.center_on(map.MapLatitudeLongitude(i[0][0],i[0][1]), i[1])
    except asyncio.CancelledError as e:
        return