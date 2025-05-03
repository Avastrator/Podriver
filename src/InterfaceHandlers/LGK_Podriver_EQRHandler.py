"""
LGK_Podriver_EQRHandler:
Longecko Podriver Interface EarthQuakeReport Handler
By Avastrator
2025-03-23 12:15:52
"""
import flet as ft
import flet_map as map
import asyncio

import LGK_Podriver_Args as a
from InterfaceHandlers.LGK_Podriver_EEWHandler import get_epicenter_mark
from InterfaceHandlers.LGK_Podriver_Audio import player

l = a.get("lang")
c = a.get("config")
output = a.get("logger")
eqr_list = {}

def on_click(e, data: dict):
    def get_int_markers(data: dict):
        """
        获取烈度标记
        """
        markers = []
        for i in list(reversed(data["area_intensity"])):  # Flet的MarkerLayer的图层是越后的越下, 所以需要倒序
            if i["int_type"] in ["JMA", "CWASIS"]:
                intensity_image = f"/intensity_round_icons/shindo_{str(i["intensity"])}.png"
            else:
                intensity_image = f"/intensity_round_icons/intensity_{str(int(i["intensity"]))}.png"
            markers.append(
                map.Marker(
                    content=ft.Image(
                        src=intensity_image,
                        height=50,
                        width=50,
                        anti_alias=True,
                        tooltip=f"{data["region"]} {data["time"]}\n{str(i['region'])} {i["int_type"]} {str(i['intensity'])}",
                    ),
                    coordinates=map.MapLatitudeLongitude(i["location"][0], i["location"][1]),
                )
            )
        return markers
    lat, lon = data["location"]
    a.get("ref_map_control").current.center_on(map.MapLatitudeLongitude(lat, lon), 8)
    a.get("ref_map_eqr_areaint_layer").current.markers.clear()
    a.get("ref_map_eqr_areaint_layer").current.markers.extend(get_int_markers(data))
    if data["event_type"] == "EEW":
        a.get("ref_map_eqr_areaint_layer").current.markers.append(get_epicenter_mark(data))
    a.get("ref_map_eqr_areaint_layer").current.update()

def get_map_marker(data: dict):
    """
    获取地图标记
    """
    if "datas" in data: # 针对综合情报的处理
        data["event_source"] = l["reports"].replace("[num]", str(len(data["datas"])))
    return map.Marker(
        content=ft.Image(
            src="/map_icons/earthquake.png",
            height=data["magnitude"]*5,
            width=data["magnitude"]*5,
            anti_alias=True,
            tooltip=f"[{l["eqr"]}]\n{l["quake_time"]}: {data["time"]}\n{l["source"]}: {data['event_source']}\n{l["location"]}: {data['region']}\n{l['lat']}: {data['location'][0]}\n{l['lon']}: {data['location'][1]}\n{l["magnitude"]}: {data['mag_type']} {data['magnitude']}\n{l["depth"]}: {data['depth']}km\n{l["max_intensity"]}: {data["int_type"]} {data['intensity']}",
        ),
        coordinates=map.MapLatitudeLongitude(data["location"][0], data["location"][1]),
    )

def get_eqr_control(data: dict):
    """
    获取单个地震报告控件
    """
    return ft.Container(
        ink=True,
        on_click=lambda e, data=data: on_click(e, data),
        content=ft.Row(
            spacing=5,
            controls=[
                # 单个地震事件的左侧, 展示规模, 深度, 烈度
                ft.Column(
                    spacing=-5,
                    width=c["ui"]["eqhistory_control_width"] * 0.2,
                    controls=[
                        # 展示地震规模单位
                        ft.Text(data["mag_type"],font_family="harmony_b",size=18),
                        # 展示地震规模
                        ft.Text(data["magnitude"],font_family="harmony_bl",size=23),
                        # 展示震源深度
                        ft.Text(f"{str(data["depth"])}km", size=13, font_family="harmony_m"),
                        # 展示烈度
                        ft.Text(f"{str(data["int_type"])} {str(data["intensity"])}", size=12, font_family="harmony_m"),
                    ],
                ),
                # 单个地震事件的右侧, 展示数据源, 发生时间, 位置
                ft.Column(
                    spacing=-1,
                    wrap=True,
                    controls=[
                        # 展示地震事件的数据源
                        ft.Text(data["event_source"], size=13, overflow=ft.TextOverflow.ELLIPSIS, max_lines=2, width=c["ui"]["eqhistory_control_width"]*0.78),
                        # 展示震中位置
                        ft.Text(
                            data["region"],
                            size=20,
                            font_family="harmony_m",
                            width=c["ui"]["eqhistory_control_width"]*0.78,
                            overflow=ft.TextOverflow.ELLIPSIS,
                            max_lines=2,
                        ),
                        # 展示发生时间
                        ft.Text(data["time"], size=13),
                    ],
                ),
            ],
        ),
    )

def get_mix_control(data: dict):
    # 需要先生成被收起报告的控件
    reports_controls = []
    for report in data["datas"]:
        # 生成被收起报告的逻辑也与生成地震报告的差不多
        reports_controls.append(get_eqr_control(report))
    # 生成整个可展开控件
    return ft.ExpansionTile(
        controls=reports_controls,
        tile_padding=ft.padding.all(0),
        title=ft.Container(
                ink=True,
                on_click=lambda e, data=data: on_click(e, data),
                content=ft.Row(
                    spacing=5,
                    controls=[
                        ft.Column(
                            spacing=-5,
                            width=c["ui"]["eqhistory_control_width"] * 0.2,
                            controls=[
                                # 展示地震规模单位
                                ft.Text(data["mag_type"],font_family="harmony_b",size=18),
                                # 展示地震规模
                                ft.Text(data["magnitude"],font_family="harmony_bl",size=23),
                                # 展示震源深度
                                ft.Text(f"{str(data["depth"])}km", size=13, font_family="harmony_m"),
                                # 展示烈度
                                ft.Text(f"{str(data["int_type"])} {str(data["intensity"])}", size=12, font_family="harmony_m"),
                            ],
                        ),
                        ft.Column(
                            spacing=-1,
                            wrap=True,
                            controls=[
                                ft.Text(l["reports"].replace("[num]", str(len(data["datas"]))), size=13, overflow=ft.TextOverflow.ELLIPSIS, max_lines=2, width=c["ui"]["eqhistory_control_width"]*0.78),
                                ft.Text(
                                    data["region"],
                                    size=18,
                                    font_family="harmony_m",
                                    width=c["ui"]["eqhistory_control_width"]*0.78,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                    max_lines=2,
                                ),
                                ft.Text(data["time"], size=13),
                            ]
                        )
                    ]
                )
        )
    )

def get_eew_control(data: dict):
    """
    获取地震预警历史控件
    """
    # 先需要生成预警历史报的控件
    eew_reports_controls = []
    source = data["event_source"]
    data["report_history"].append(data) # 最后一报也需要生成
    for report in list(reversed(data["report_history"])): # 新报在前旧报在后
        # 生成历史报的逻辑与生成地震报告的差不多, 只是需要将其数据源改为"第X报"
        report["event_source"] = f"No.{str(report["report_num"])}"
        eew_reports_controls.append(get_eqr_control(report))
    # 生成这次预警的整个可展开控件
    return ft.ExpansionTile(
        controls=eew_reports_controls,
        tile_padding=ft.padding.all(0),
        title=ft.Container(
                ink=True,
                on_click=lambda e, data=data: on_click(e, data),
                content=ft.Row(
                    spacing=5,
                    controls=[
                        ft.Column(
                            spacing=-5,
                            width=c["ui"]["eqhistory_control_width"]*0.2,
                            controls=[
                                # 展示地震规模单位
                                ft.Text(data["mag_type"],font_family="harmony_b",size=18),
                                # 展示地震规模
                                ft.Text(data["magnitude"],font_family="harmony_bl",size=23),
                                # 展示震源深度
                                ft.Text(f"{str(data["depth"])}km", size=13, font_family="harmony_m"),
                                # 展示烈度
                                ft.Text(f"{str(data["int_type"])} {str(data["intensity"])}", size=12, font_family="harmony_m"),
                            ],
                        ),
                        ft.Column(
                            spacing=-1,
                            wrap=True,
                            controls=[
                                ft.Text(f"[EEW]{source} {str(data["report_num"])} corr.", size=13, overflow=ft.TextOverflow.ELLIPSIS, max_lines=2, width=c["ui"]["eqhistory_control_width"]*0.78),
                                ft.Text(
                                    data["region"],
                                    size=20,
                                    font_family="harmony_m",
                                    width=c["ui"]["eqhistory_control_width"]*0.78, 
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                    max_lines=2,
                                ),
                                ft.Text(data["time"], size=13),
                            ]
                        )
                    ]
                )
        )
    )

async def handler(data: dict, refresh=True):
    """
    处理地震报告
    """
    event_id = data["event_id"]
    if data["event_type"] == "EEW":
        event_id = f"{event_id}EEW"

    # 移除旧信息
    if event_id in eqr_list:
        if eqr_list[event_id]["map_marker"]:
            a.get("ref_map_eqr_marks_layer").current.markers.remove(eqr_list[event_id]["map_marker"])
        a.get("ref_eqlist_control").current.controls.remove(eqr_list[event_id]["control"])
        del eqr_list[event_id]

    if data["event_type"] == "EQR" and "datas" not in data: # 处理单个地震报告
        # 获取其在地图上的标记
        map_marker = get_map_marker(data)
        # 获取其在地震历史控件上的控件
        control = get_eqr_control(data)
        # 记录在表中
        if data["event_source"] not in ["中国地震台网[自动测定]", "GeoNet[Preliminary]", "GeoNet[Automatic]"]:
            eqr_list[data["event_id"]] = {"map_marker": map_marker, "control": control}
        # 应用控件
        a.get("ref_map_eqr_marks_layer").current.markers.append(map_marker)
    elif data["event_type"] == "EQR" and "datas" in data: # 处理综合情报
        # 获取其在地图上的标记
        map_marker = get_map_marker(data)
        # 获取其在地震历史控件上的控件
        control = get_mix_control(data)
        # 记录在表中
        eqr_list[data["event_id"]] = {"map_marker": map_marker, "control": control}
        # 应用控件
        a.get("ref_map_eqr_marks_layer").current.markers.append(map_marker)
    elif data["event_type"] == "EEW": # 处理地震预警最终报
        # 获取其在地震历史控件上的控件
        control = get_eew_control(data)
        # 记录在表中, EEW的ID需要加上EEW后缀, 避免与测定冲突
        eqr_list[event_id] = {"map_marker": None, "control": control}
    else:
        # 卧槽给我干哪来了??这些类型都匹配不上那它传给我了个什么东西啊, 给个warn就算了
        output.warn(f"Unknown event: {str(data)}")
        return
    a.get("ref_eqlist_control").current.controls.insert(0, control)
    a.get("ref_eqlist_control").current.controls = a.get("ref_eqlist_control").current.controls[:50] # 仅保留最新50个报
    # 刷新
    if refresh:
        a.get("ref_map_control").current.center_on(map.MapLatitudeLongitude(data["location"][0], data["location"][1]), 8) # 聚焦地图中心
        on_click(None, data)
        a.get("ref_eqlist_control").current.update()
        a.get("ref_map_eqr_marks_layer").current.update()
        asyncio.create_task(player(data, True, True, False))
    return

async def eqlist_handler(data: list):
    """
    处理地震历史列表
    """
    a.get("ref_eqlist_control").current.controls.clear() # 所有地震信息都会重新创建, 需要删除当前所有已展示的地震信息
    a.get("ref_map_eqr_marks_layer").current.markers.clear()
    a.get("ref_eqlist_control").current.controls.clear()
    eqr_list.clear()
    for eq in list(reversed(data)): # 地震会从前到后依次插入到第一个, 需要反转才能得到正确顺序
        await handler(eq, False)
    a.get("ref_eqlist_control").current.update()
    a.get("ref_map_control").current.update()
    a.get("ref_map_control").current.center_on(
        map.MapLatitudeLongitude(
            a.get("ref_map_control").current.initial_center,
            a.get("ref_map_control").current.initial_zoom
        ),
        4.2
    )
    return