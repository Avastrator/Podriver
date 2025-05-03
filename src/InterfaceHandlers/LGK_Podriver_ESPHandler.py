"""
LGK_Podriver_ESPHandler:
Longecko Podriver Interface EarthquakeShakingPerception Handler
By Avastrator
2025-03-23 12:15:52
"""
import flet as ft
import flet_map as map

import LGK_Podriver_Args as a
from InterfaceHandlers.LGK_Podriver_WaveHandler import *
from InterfaceHandlers.LGK_Podriver_Audio import player

output = a.get("logger")
l = a.get("lang")

max_intensity = 0
max_shindo = 0

img = {
    "intensity": {
        0: ft.Image(src= "/station_icons/intensity_0.png", width=23, height=23),
        1: ft.Image(src= "/station_icons/intensity_1.png", width=23, height=23),
        2: ft.Image(src= "/station_icons/intensity_2.png", width=23, height=23),
        3: ft.Image(src= "/station_icons/intensity_3.png", width=23, height=23),
        4: ft.Image(src= "/station_icons/intensity_4.png", width=23, height=23),
        5: ft.Image(src= "/station_icons/intensity_5.png", width=23, height=23),
        6: ft.Image(src= "/station_icons/intensity_6.png", width=23, height=23),
        7: ft.Image(src= "/station_icons/intensity_7.png", width=23, height=23),
        8: ft.Image(src= "/station_icons/intensity_8.png", width=23, height=23),
        9: ft.Image(src= "/station_icons/intensity_9.png", width=23, height=23),
        10: ft.Image(src= "/station_icons/intensity_10.png", width=23, height=23),
        11: ft.Image(src= "/station_icons/intensity_11.png", width=23, height=23),
        12: ft.Image(src= "/station_icons/intensity_12.png", width=23, height=23),
    },
    "shindo": {
        0: ft.Image(src= "/station_icons/shindo_0.png", width=23, height=23),
        1: ft.Image(src= "/station_icons/shindo_1.png", width=23, height=23),
        2: ft.Image(src= "/station_icons/shindo_2.png", width=23, height=23),
        3: ft.Image(src= "/station_icons/shindo_3.png", width=23, height=23),
        4: ft.Image(src= "/station_icons/shindo_4.png", width=23, height=23),
        4.75: ft.Image(src= "/station_icons/shindo_4.75.png", width=23, height=23),
        5.25: ft.Image(src= "/station_icons/shindo_5.25.png", width=23, height=23),
        5.75: ft.Image(src= "/station_icons/shindo_5.75.png", width=23, height=23),
        6.25: ft.Image(src= "/station_icons/shindo_6.25.png", width=23, height=23),
        7: ft.Image(src= "/station_icons/shindo_7.png", width=23, height=23),
    }
}

esp_marks = {}
esp_lock = asyncio.Lock()

async def handler(data):
    global max_intensity, max_shindo
    # Remove old markers
    async with esp_lock:
        if esp_marks.get(data["event_source"], []) != []:
            for mark in esp_marks[data["event_source"]]:
                try:
                    a.get("ref_map_esp_layer").current.markers.remove(mark)
                except:
                    pass
            esp_marks[data["event_source"]] = []
        # Add new markers
        marks = []
        for i in data["list"]:
            if i["int_type"] in ["JMA", "CWASIS"]:
                intensity_image = f"/station_icons/shindo_{str(i["intensity"])}.png"
                op = i["intensity"] / 7
            else:
                intensity_image = f"/station_icons/intensity_{str(int(i["intensity"]))}.png"
                op = i["intensity"] / 12
            marks.append(
                map.Marker(
                    content=ft.Image(
                        src=intensity_image,
                        height=22,
                        width=22,
                        opacity=op,
                        anti_alias=True,
                        tooltip=f"{l["esp"]} {str(i['region'])} {i["int_type"]} {str(i['intensity'])}",
                    ),
                    coordinates=map.MapLatitudeLongitude(i["location"][0], i["location"][1]),
                )
            )
            a.get("ref_map_esp_layer").current.markers.append(marks[-1])
        esp_marks[data["event_source"]] = marks
        # Apply changes
        a.get("ref_map_esp_layer").current.update()
        if not len(data["list"]) == 0:
            data = data["list"][0]
            a.get("ref_map_control").current.center_on(map.MapLatitudeLongitude(data["location"][0], data["location"][1]), 9)
            if data["int_type"] in ["JMA", "CWASIS"]:
                if data["intensity"] <= max_shindo:
                    return
                else:
                    max_shindo = data["intensity"]
                    asyncio.create_task(player(data, True, True, False))
            else:
                if data["intensity"] <= max_intensity:
                    return
                else:
                    max_intensity = data["intensity"]
                    asyncio.create_task(player(data, True, True, False))
        else:
            max_shindo, max_intensity = 0, 0
