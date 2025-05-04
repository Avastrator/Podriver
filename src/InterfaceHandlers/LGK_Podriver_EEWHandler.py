"""
LGK_Podriver_EEWHandler:
Longecko Podriver Interface EarthquakeEarlyWarning Handler
By Avastrator
2025-03-23 12:15:52
"""
import math
import flet as ft
import flet_map as map

import LGK_Podriver_Args as a
from InterfaceHandlers.LGK_Podriver_WaveHandler import *
from InterfaceHandlers.LGK_Podriver_Audio import player

output = a.get("logger")
l = a.get("lang")
c = a.get("config")
ipconfig = a.get("ipconfig")

eew_area_int_list = {}

def get_eew_control(data: dict, local_int: int):
    """
    获取地震预警控件
    """
    if data["int_type"] in ["JMA", "CWASIS"]:
        max_intensity_text = l["fc_max_shindo"]
        intensity_image = f"/intensity_icons/shindo_{str(data["intensity"])}.png"
    else:
        max_intensity_text = l["fc_max_intensity"]
        intensity_image = f"/intensity_icons/intensity_{str(int(data["intensity"]))}.png"
    if local_int < 3:
        int_tip = l["local_int_weak"]
    elif local_int < 5:
        int_tip = l["local_int_small"]
    elif local_int < 7:
        int_tip = l["local_int_medium"]
    elif local_int < 9:
        int_tip = l["local_int_strong"]
    else:
        int_tip = l["local_int_severe"]
    if data["report_final"] == True:
        final_tip = l["final_report"]
    else:
        final_tip = ""
    return ft.Container(
    border_radius=10,
    border=ft.border.all(5,"#009199"),
    bgcolor="#00ACB5",
    alignment=ft.alignment.top_left,
    padding=1,
    on_click=lambda e, lat=data["location"][0], lon=data["location"][1]: a.get("ref_map_control").current.center_on(map.MapLatitudeLongitude(lat, lon), 7.5),
    content=ft.Column(
        alignment=ft.MainAxisAlignment.START,
        spacing=5,
        controls=[
            ft.Container(
                border=ft.border.all(1,"#009199"),
                margin=-1,
                content=ft.Row(
                    controls=[
                        ft.Text(
                            data["event_source"],
                            size=18,
                            font_family="harmony_m",
                            color="white",
                        ),
                        ft.Text(
                            f"{str(data["report_num"])} Rev.{final_tip}",
                            size=18,
                            font_family="harmony_m",
                            color="white",
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                bgcolor="#009199",
            ),
            ft.Row(
                spacing=5,
                controls=[
                    ft.Column(
                        spacing=-1,
                        controls=[
                            ft.Text(
                                max_intensity_text,
                                size=12,
                                font_family="harmony_m",
                                color="white",
                            ),
                            ft.Image(
                                src=intensity_image,
                                height=73,
                                width=73,
                            ),
                        ]  
                    ),
                    ft.Column(
                        width=c["ui"]["eqhistory_control_width"] - 90,
                        spacing=-1,
                        controls=[
                            ft.Text(
                                data["region"],
                                size=20,
                                font_family="harmony_b",
                                overflow=ft.TextOverflow.ELLIPSIS,
                                max_lines=1,
                                color="white",
                            ),
                            ft.Text(
                                data["time"],
                                size=11,
                                font_family="harmony_r",
                                color="white",
                            ),
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Text(
                                        f"{data["mag_type"]} {str(data["magnitude"])}",
                                        size=18,
                                        font_family="harmony_b",
                                        color="white",
                                    ),
                                    ft.Text(
                                        f"{str(int(data["depth"]))} km",
                                        size=18,
                                        font_family="harmony_b",
                                        color="white",
                                    ),
                                ],
                            ),
                            ft.Text(
                                f"{l["local_int"]}: {str(local_int)}, {int_tip}",
                                size=12,
                                font_family="harmony_r",
                                color="white",
                            ),
                        ],
                    ),
                ],
            )
        ]
    )
)

def get_int_map_marks(data: dict):
    """
    获取地震预警区域标记
    """
    markers = []
    for i in list(reversed(data["area_intensity"])): # Flet的MarkerLayer的图层是越后的越下, 所以需要倒序
        if i["int_type"] in ["JMA", "CWASIS"]:
            intensity_image = f"/intensity_icons/shindo_{str(i["intensity"])}.png"
            op = i["intensity"] / data["intensity"]
        else:
            intensity_image = f"/intensity_icons/intensity_{str(int(i["intensity"]))}.png"
            op = i["intensity"] / data["intensity"]
        markers.append([
            map.Marker(
                content=ft.Image(
                    src=intensity_image,
                    height=27,
                    width=27,
                    opacity=op,
                    anti_alias=True,
                    tooltip=f"{str(i['region'])} {i["int_type"]} {str(i['intensity'])}",
                ),
                coordinates=map.MapLatitudeLongitude(i["location"][0], i["location"][1]),
            ),
            i["region"],
            i["intensity"],
            i["int_type"]
        ])
    return markers

def get_epicenter_mark(data: dict):
    """
    获取震中地图标记
    """
    return map.Marker(
        content=ft.Image(
            src="/map_icons/epicenter.png",
            height=120,
            width=120,
            anti_alias=True,
            tooltip=f"[{l["eew"]}]\n{l["quake_time"]}: {data["time"]}\n{l["source"]}: {data['event_source']}\n{l["location"]}: {data['region']}\n{l['lat']}: {data['location'][0]}\n{l['lon']}: {data['location'][1]}\n{l["magnitude"]}: {data['mag_type']} {data['magnitude']}\n{l["depth"]}: {data['depth']}km\n{l["fc_max_intensity"]}: {data["int_type"]} {data['intensity']}",
        ),
        coordinates=map.MapLatitudeLongitude(data["location"][0], data["location"][1]),
    )

async def handler(event_id: int):
    """
    Handle EEW data
    """
    # Eathquake Informations
    last_data = {} # last EEW data
    dist = 0 # local epicenter distance
    i = 0 # local intensity
    timeout = 30 # active time
    zoom = 7.5 # map zoom
    location = [] # epicenter location
    wave = None # wave task
    control = None
    marks = []
    epicenter_mark = None
    while True:
        # Wait for new data or timeout
        try:
            data = await asyncio.wait_for(a.get("eew_handler_queues")[event_id].get(), timeout)
        except asyncio.TimeoutError:
            # EXIT
            output.info(f"Handler EEW data timeout: {data}")
            # Stop wave drawing
            wave.cancel()
            try:
                await wave
            except asyncio.CancelledError:
                pass
            # Remove UI controls
            a.get("ref_eew_control").current.controls.remove(control)
            a.get("ref_map_eew_marks_layer").current.markers.remove(epicenter_mark)
            for mark in marks:
                try:
                    current_markers = a.get("ref_map_eew_areaint_layer").current.markers
                    # 通过工具提示查找实际存在的标记
                    target_tooltip = mark[0].content.tooltip
                    existing_marker = next(
                        (m for m in current_markers 
                         if m.content.tooltip == target_tooltip), 
                        None
                    )
                    if existing_marker is not None:
                        current_markers.remove(existing_marker)
                        eew_area_int_list.pop(mark[1])
                except (ValueError, StopIteration):
                    continue
            # Apply
            a.get("ref_eew_control").current.update()
            a.get("ref_map_eew_marks_layer").current.update()
            a.get("ref_map_eew_areaint_layer").current.update()
            # Remove focus
            a.get("map_focus_list").remove(location)
            # Remove self
            a.get("eew_handlers").pop(event_id)
            return
        output.info(f"Handler Got EEW data: {data}")
        # Update informations
        lat1, lon1, lat2, lon2 = data["location"][0], data["location"][1], ipconfig["location"][0], ipconfig["location"][1]
        dist = 6371 * 2 * math.asin(math.sqrt(math.sin(math.radians(lat2 - lat1) / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(math.radians(lon2 - lon1) / 2)**2))
        i = int(round(2.941 + 1.363 * data["magnitude"] - 1.494 * math.log(dist + 7), 0)) # 计算本地烈度(ICL算法)
        i = i if i < 12 else 12
        i = i if i > 0 else 0
        timeout = get_earthquake_active_time(data) + c["eew"]["eew_display_time_delay"]
        if timeout > 0:
            timeout = timeout if timeout <= c["eew"]["eew_display_time_delay"] else timeout * 2 / 3 + c["eew"]["eew_display_time_delay"]
        else:
            output.warn(f"Handler EEW data timeout suddenly: {data}")
            a.get("eew_handlers").pop(event_id)
            return # 过去的地震
        # Get new UI controls
        new_control = get_eew_control(data, i)
        new_marks = get_int_map_marks(data)
        new_epicenter_mark = get_epicenter_mark(data)
        # Remove old UI controls
        if not control == None:
            a.get("ref_eew_control").current.controls.remove(control)
        if not epicenter_mark == None:
            a.get("ref_map_eew_marks_layer").current.markers.remove(epicenter_mark)
        if not wave == None:
            wave.cancel()
        for mark in marks:
            try:
                target_tooltip = mark[0].content.tooltip
                existing_marker = next(
                    (m for m in a.get("ref_map_eew_areaint_layer").current.markers
                     if m.content.tooltip == target_tooltip), 
                    None
                )
                if existing_marker is not None:
                    a.get("ref_map_eew_areaint_layer").current.markers.remove(existing_marker)
                    eew_area_int_list.pop(mark[1])
            except (ValueError, StopIteration):
                continue
        # Add new UI controls
        a.get("ref_eew_control").current.controls.append(new_control)
        control = new_control
        a.get("ref_map_eew_marks_layer").current.markers.append(new_epicenter_mark)
        epicenter_mark = new_epicenter_mark
        for mark in new_marks:
            if not mark[1] in eew_area_int_list:
                # 该地没有烈度标记, 添加
                a.get("ref_map_eew_areaint_layer").current.markers.append(mark[0])
            elif not mark[3] == eew_area_int_list[mark[1]][3]:
                # 新烈度类型不同, 替换
                a.get("ref_map_eew_areaint_layer").current.markers.remove(eew_area_int_list[mark[1]][0])
                a.get("ref_map_eew_areaint_layer").current.markers.append(mark[0])
            elif mark[2] > eew_area_int_list[mark[1]][2]:
                # 新烈度更大, 替换
                a.get("ref_map_eew_areaint_layer").current.markers.remove(eew_area_int_list[mark[1]][0])
                a.get("ref_map_eew_areaint_layer").current.markers.append(mark[0])
            else:
                # 新烈度更小, 不替换
                pass
            eew_area_int_list[mark[1]] = mark
        marks = new_marks
        # Apply
        a.get("ref_map_eew_marks_layer").current.update()
        a.get("ref_map_eew_areaint_layer").current.update()
        a.get("ref_eew_control").current.update()
        # Launch wave drawing
        wave = asyncio.create_task(wave_handler(data))
        # Set map control focus
        zoom = max(min(8.2 - math.log(data["impact_radius"] / 100 + 1), 15), 4)
        a.get("ref_map_control").current.center_on(map.MapLatitudeLongitude(data["location"][0], data["location"][1]), zoom)
        if not location == []:
            a.get("map_focus_list").remove(location)
        a.get("map_focus_list").append([data["location"], zoom])
        location = [data["location"], zoom]
        # Play audio
        if data["intensity"] == last_data.get("intensity", 0):
            asyncio.create_task(player(data, False, False, True))
        else:
            asyncio.create_task(player(data, True, True, False))
        last_data = data
