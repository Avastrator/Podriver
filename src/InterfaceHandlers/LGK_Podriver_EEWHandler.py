"""
LGK_Podriver_EEWHandler:
Longecko Podriver Interface EarthquakeEarlyWarning Handler
By Avastrator
2025-03-23 12:15:52
"""
import math
import flet as ft
import flet_map as map
import asyncio
from datetime import datetime, timedelta

import LGK_Podriver_Args as a
from InterfaceHandlers.LGK_Podriver_WaveHandler import *
from InterfaceHandlers.LGK_Podriver_Audio import player

output = a.get("logger")
l = a.get("lang")
c = a.get("config")
ipconfig = a.get("ipconfig")

eew_area_int_list = {}
"""
该表用于管理地图上预估烈度点, 具体复杂点在处理多震中
这个表看起来是这样的:
{
    地名: {
        "active": {
            "mark": 地图标记本体, 
            "int": 烈度, 
            "type": 烈度单位, 
            "id": 地震编号
            }, 
        "inactive": [
            {
                "mark": 地图标记本体, 
                "int": 烈度, 
                "type": 烈度单位, 
                "id": 地震编号
            }, 
            {
                "mark": 地图标记本体, 
                "int": 烈度, 
                "type": 烈度单位, 
                "id": 地震编号
            },
            ...
        ]
    }
}
"""

def get_eew_control(data: dict, local_int: int, countdown_ref=ft.Ref[ft.Text]()):
    ""
    """
    获取地震预警控件
    """
    if data["int_type"] in ["JMA", "CWASIS"]:
        intensity_image = f"/intensity_icons/shindo_{str(data["intensity"])}.png"
    else:
        intensity_image = f"/intensity_icons/intensity_{str(int(data["intensity"]))}.png"
    local_intensity_image = f"/intensity_icons/intensity_{str(local_int)}.png"
    if data["report_final"] == True:
        report_status = l["final_report"]
    else:
        report_status = str(l["final_report"]).replace("[num]", str(data["report_num"]))
    return ft.Container(
    border=ft.Border(ft.BorderSide(4, "#009199", -1), ft.BorderSide(4, "#009199", -1), ft.BorderSide(4, "#009199", -1), ft.BorderSide(4, "#009199", -1)),
    border_radius=3,
    bgcolor="#00ACB5",
    alignment=ft.Alignment(-1.0, -1.0),
    padding=1,
    on_click=lambda e, lat=data["location"][0], lon=data["location"][1]: a.get("ref_map_control").current.center_on(map.MapLatitudeLongitude(lat, lon), 7.5),
    content=ft.Column(
        alignment=ft.MainAxisAlignment.START,
        spacing=0,
        controls=[
            ft.Row(
                alignment=ft.MainAxisAlignment.START,
                expand=True,
                controls=[
                    ft.Column( # 上左部分
                        alignment=ft.MainAxisAlignment.START,
                        spacing=0,
                        controls=[
                            ft.Text(
                                value="MAX INTENSITY",
                                font_family="harmony_l",
                                size=11,
                                color="white",
                            ),
                            ft.Image(
                                src=intensity_image,
                                height=80,
                                width=80,
                            )
                        ]
                    ),
                    ft.Column( # 上右部分
                        alignment=ft.MainAxisAlignment.START,
                        spacing=3,
                        expand=True,
                        controls=[
                            ft.Row( # 报数与最终报
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                expand=True,
                                controls=[
                                    ft.Text(
                                        value=f"FROM: {data['event_source']}",
                                        size=15,
                                        font_family="harmony_m",
                                        color="white",
                                    ),
                                    ft.Text(
                                        value=report_status,
                                        size=14,
                                        font_family="harmony_m",
                                        color="white",
                                    ),
                                ]
                            ),
                            ft.Text( # 震中名
                                value=data["region"],
                                size=27,
                                font_family="harmony_b",
                                color="white",
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                            ft.Text( # 发震时间
                                value=data["time"],
                                size=18,
                                font_family="harmony_m",
                                color="white",
                            ),
                        ]
                    )
                ]
            ),
            ft.Row( # 下排部分
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                expand=True,
                controls=[
                    ft.Text(
                        value=f"{data["mag_type"]} {str(data["magnitude"])}",
                        size=23,
                        font_family="harmony_m",
                        color="white",
                    ),
                    ft.Text(
                        value=f"{str(data["depth"])}km",
                        size=23,
                        font_family="harmony_m",
                        color="white",
                    ),
                    ft.Row( # 本地烈度
                        alignment=ft.MainAxisAlignment.START,
                        spacing=3,
                        controls=[
                            ft.Image(
                                src=local_intensity_image,
                                height=28,
                                width=28,
                            ),
                            ft.Text(
                                ref=countdown_ref,
                                value="00:00",
                                size=23,
                                font_family="harmony_m",
                                color="white",
                            )
                        ]
                    )
                ]
            )
        ]
    )
)

async def handle_eew_countdown(ref: ft.Ref[ft.Text], eqtime: str, arrive_time: int):
    """
    处理地震预警倒计时
    """
    eqtime = datetime.strptime(eqtime, "%Y-%m-%d %H:%M:%S")
    try:
        while True:
            final_time_diff = eqtime + timedelta(seconds=arrive_time) - datetime.now()
            if final_time_diff.total_seconds() <= 10:
                ref.current.color = "red"
            if final_time_diff.total_seconds() <= 0:
                ref.current.value = "00:00"
                ref.current.update()
                return
            final_minutes, final_seconds = final_time_diff.seconds // 60, final_time_diff.seconds % 60
            ref.current.value = f"{final_minutes:02d}:{final_seconds:02d}"
            ref.current.update()
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        return

def get_int_map_marks(data: dict, id: int):
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
        markers.append({
            "region": i["region"],
            "mark": map.Marker(
                content=ft.Image(
                    src=intensity_image,
                    height=27,
                    width=27,
                    opacity=op,
                    border_radius=2,
                    anti_alias=True,
                    tooltip=f"{str(i['region'])} {i["int_type"]} {str(i['intensity'])}",
                ),
                coordinates=map.MapLatitudeLongitude(i["location"][0], i["location"][1]),
            ),
            "int": i["intensity"],
            "type": i["int_type"],
            "id": id
        })
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

def get_active_mark(ilist: list):
    """
    从不活跃的区域烈度标记列表中获取最新的活跃标记
    """
    # 先按烈度类型排
    shindo = []
    intensity = []
    for i in ilist:
        if i["type"] in ["JMA", "CWASIS"]:
            shindo.append(i)
        else:
            intensity.append(i)
    # 再按烈度大小排
    shindo = sorted(shindo, key=lambda x: x["int"], reverse=True)
    intensity = sorted(intensity, key=lambda x: x["int"], reverse=True)
    # 取第一个
    if len(shindo) > 0:
        return shindo[0]
    elif len(intensity) > 0:
        return intensity[0]
    else:
        return {}

async def handler(event_id: int):
    """
    Handle EEW data
    """
    # Eathquake Informations
    last_data = {} # last EEW data
    dist = 0 # local epicenter distance
    countdown = 0 # arrival time
    countdown_task = None # countdown task
    ref_countdown = ft.Ref[ft.Text]() # countdown text reference
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
            # Stop countdown
            countdown_task.cancel()
            try:
                await wave
            except asyncio.CancelledError:
                pass
            # Remove UI controls
            a.get("ref_eew_control").current.controls.remove(control)
            a.get("ref_map_eew_marks_layer").current.markers.remove(epicenter_mark)
            for mark in marks:
                region = mark.pop("region")
                if eew_area_int_list[region]["active"].get("id", -1) == event_id:
                    # 现在的活跃标记还是我的, 好耶
                    # 取将要替换的标记的所在位置
                    index = a.get("ref_map_eew_areaint_layer").current.markers.index(eew_area_int_list[region]["active"]["mark"])
                    # 上新标记
                    eew_area_int_list[region]["active"] = get_active_mark(eew_area_int_list[region]["inactive"])
                    if eew_area_int_list[region]["active"] != {}:
                        eew_area_int_list[region]["inactive"].remove(eew_area_int_list[region]["active"])
                        a.get("ref_map_eew_areaint_layer").current.markers[index] = eew_area_int_list[region]["active"]["mark"]
                    else:
                        a.get("ref_map_eew_areaint_layer").current.markers.pop(index)
                else:
                    # 标记不是active的, 取inactive里找
                    if mark in eew_area_int_list[region]["inactive"]:
                        eew_area_int_list[region]["inactive"].remove(mark)
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
        countdown = round(get_travel_time(data["time"], data["depth"], dist), 0)
        countdown = countdown if countdown > 0 else 0
        timeout = get_travel_time(data["time"], data["depth"], data["impact_radius"])
        if timeout + c["eew"]["eew_display_time_delay"] > 0:
            timeout = timeout * 5 / 2 + c["eew"]["eew_display_time_delay"] if timeout > 0 else timeout + c["eew"]["eew_display_time_delay"]
        else:
            output.warn(f"ID[{event_id}] EEW TIMEOUT: [{str(timeout)}]")
            a.get("eew_handlers").pop(event_id)
            return # 过去的地震
        
        # Get new UI controls
        new_control = get_eew_control(data, i, ref_countdown)
        new_marks = get_int_map_marks(data, event_id)
        new_epicenter_mark = get_epicenter_mark(data)

        # Remove old UI controls
        if not control == None:
            a.get("ref_eew_control").current.controls.remove(control)
        if not epicenter_mark == None:
            a.get("ref_map_eew_marks_layer").current.markers.remove(epicenter_mark)
        if not wave == None:
            wave.cancel()
        if not countdown_task == None:
            countdown_task.cancel()
        for mark in marks:
            region = mark.pop("region")
            if eew_area_int_list[region]["active"].get("id", -1) == event_id:
                # 现在的活跃标记还是我的, 好耶
                # 取将要替换的标记的所在位置
                index = a.get("ref_map_eew_areaint_layer").current.markers.index(eew_area_int_list[region]["active"]["mark"])
                # 上新标记
                eew_area_int_list[region]["active"] = get_active_mark(eew_area_int_list[region]["inactive"])
                if eew_area_int_list[region]["active"] != {}:
                    eew_area_int_list[region]["inactive"].remove(eew_area_int_list[region]["active"])
                    a.get("ref_map_eew_areaint_layer").current.markers[index] = eew_area_int_list[region]["active"]["mark"]
                else:
                    a.get("ref_map_eew_areaint_layer").current.markers.pop(index)
            else:
                # 标记不是active的, 取inactive里找
                if mark in eew_area_int_list[region]["inactive"]:
                    eew_area_int_list[region]["inactive"].remove(mark)

        # Add new UI controls
        control = new_control
        a.get("ref_eew_control").current.controls.append(new_control)
        countdown_task = asyncio.create_task(handle_eew_countdown(ref_countdown, data["time"], countdown))
        epicenter_mark = new_epicenter_mark
        a.get("ref_map_eew_marks_layer").current.markers.append(new_epicenter_mark)
        for mark in  [m.copy() for m in new_marks]:  # 创建列表副本，避免修改原始列表
            region = mark.pop("region")
            if eew_area_int_list.get(region, {"active": {}, "inactive": []}) == {"active": {}, "inactive": []}:
                # 该地没有烈度标记, 添加
                eew_area_int_list[region] = {
                    "active": mark,
                    "inactive": []
                }
                a.get("ref_map_eew_areaint_layer").current.markers.append(mark["mark"])
            elif eew_area_int_list[region]["active"]["type"] in ["JMA", "CWASIS"] and mark["type"] in ["JMA", "CWASIS"]:
                # 烈度类型都是震度, 比较震度大小
                if mark["int"] > eew_area_int_list[region]["active"]["int"]:
                    # 新震度更大, 替换
                    # 取将要替换的标记的所在位置
                    index = a.get("ref_map_eew_areaint_layer").current.markers.index(eew_area_int_list[region]["active"]["mark"])
                    # 移动当前标记到inactive
                    eew_area_int_list[region]["inactive"].append(eew_area_int_list[region]["active"])
                    # 上新标记
                    eew_area_int_list[region]["active"] = mark
                    a.get("ref_map_eew_areaint_layer").current.markers[index] = eew_area_int_list[region]["active"]["mark"]
                else:
                    # 新震度更小, 不替换
                    eew_area_int_list[region]["inactive"].append(mark)
            elif eew_area_int_list[region]["active"]["type"] in ["MMI", "CSIS"] and mark["type"] in ["MMI", "CSIS"]:
                # 烈度类型相同, 比较大小
                if mark["int"] > eew_area_int_list[region]["active"]["int"]:
                    # 新烈度更大, 替换
                    # 取将要替换的标记的所在位置
                    index = a.get("ref_map_eew_areaint_layer").current.markers.index(eew_area_int_list[region]["active"]["mark"])
                    # 移动当前标记到inactive
                    eew_area_int_list[region]["inactive"].append(eew_area_int_list[region]["active"])
                    # 上新标记
                    eew_area_int_list[region]["active"] = mark
                    a.get("ref_map_eew_areaint_layer").current.markers[index] = eew_area_int_list[region]["active"]["mark"]
                else:
                    # 新烈度更小, 不替换
                    eew_area_int_list[region]["inactive"].append(mark)
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
        a.get("ref_map_eqr_areaint_layer").current.markers.clear() # clear interface
        a.get("ref_map_eqr_areaint_layer").current.update()

        # Play audio
        if data["intensity"] != last_data.get("intensity", 0) or data["report_final"] == True:
            asyncio.create_task(player(data, True, True, False))
        else:
            asyncio.create_task(player(data, False, False, True))

        last_data = data
