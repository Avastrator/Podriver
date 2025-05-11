"""
LGK_Podriver_UI_Main:
Longecko Podriver Main UI
By Avastrator
2025-03-23 10:39:50
"""

import flet as ft
import flet_map as map
import asyncio
from datetime import datetime

import LGK_Podriver_Args as a
from LGK_Podriver_Utils import safe_exit

c = a.get("config")
l = a.get("lang")

def app(page: ft.Page):
    # Vars
    ipconfig = a.get("ipconfig")
    right_control_width = c["ui"]["eqhistory_control_width"]
    
    # MapRef
    ref_map_eqr_marks_layer = ft.Ref[map.MarkerLayer]()
    a.set("ref_map_eqr_marks_layer", ref_map_eqr_marks_layer)
    
    ref_map_eqr_areaint_layer = ft.Ref[map.MarkerLayer]()
    a.set("ref_map_eqr_areaint_layer", ref_map_eqr_areaint_layer)

    ref_map_eew_areaint_layer = ft.Ref[map.MarkerLayer]()
    a.set("ref_map_eew_areaint_layer", ref_map_eew_areaint_layer)
    
    ref_map_esp_layer = ft.Ref[map.MarkerLayer]()
    a.set("ref_map_esp_layer", ref_map_esp_layer)
    
    ref_map_eew_wave_layer = ft.Ref[map.CircleLayer]()
    a.set("ref_map_eew_wave_layer", ref_map_eew_wave_layer)
    
    ref_map_eew_marks_layer = ft.Ref[map.MarkerLayer]()
    a.set("ref_map_eew_marks_layer", ref_map_eew_marks_layer)
    
    # ControlRef
    ref_eqlist_control = ft.Ref[ft.Column]()
    a.set("ref_eqlist_control", ref_eqlist_control)
    
    ref_map_control = ft.Ref[map.Map]()
    a.set("ref_map_control", ref_map_control)
    
    ref_eew_control = ft.Ref[ft.Column]()
    a.set("ref_eew_control", ref_eew_control)

    page.title = l["podriver"]
    page.fonts = {
        "harmony_bl": "fonts/HarmonyOS_Sans_SC_Black.ttf",
        "harmony_b": "fonts/HarmonyOS_Sans_SC_Bold.ttf",
        "harmony_m": "fonts/HarmonyOS_Sans_SC_Medium.ttf",
        "harmony_r": "fonts/HarmonyOS_Sans_SC_Regular.ttf",
        "harmony_l": "fonts/HarmonyOS_Sans_SC_Light.ttf",
        "harmony_t": "fonts/HarmonyOS_Sans_SC_Thin.ttf",
    }
    page.theme = ft.Theme(font_family="harmony_r", color_scheme_seed="white")
    page.dark_theme = ft.Theme(font_family="harmony_r", color_scheme_seed="GREY")
    page.theme_mode = ft.ThemeMode.DARK

    # Safe exit
    async def window_event(e):
        if e.data == "close":
            exiting = asyncio.create_task(asyncio.to_thread(safe_exit))
            await asyncio.wait_for(exiting, timeout=60)
            page.window.destroy()

    page.window.prevent_close = True
    page.window.on_event = window_event
    # AppBar
    page.appbar = ft.AppBar(
        title=ft.Text(
            f"{l["podriver"]} · {a.get('ipconfig')['region']}",
            size=25,
            font_family="harmony_b",
        ),
        actions=[
            ft.Text("0000-00-00 00:00:00", size=25, font_family="harmony_b"),
            ft.IconButton(
                icon="settings",
                icon_size=20,
                padding=15,
                tooltip=l["setting"],
            ),
        ],
    )

    async def appbar_handler(page: ft.Page):
        try:
            while True:
                    page.appbar.actions[0].update()
                    await asyncio.sleep(1)
                    if a.get("ws_retrytime") != 0:
                        page.appbar.actions[0].color = "red"
                        continue
                    page.appbar.actions[0].color = "white"
                    page.appbar.actions[0].value = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        except asyncio.CancelledError:
            return

    # Map
    def map_on_secondary_tap():
        ref_map_eqr_areaint_layer.current.markers.clear()
        ref_map_eqr_areaint_layer.current.update()
        map_control.center_on(map.MapLatitudeLongitude(ipconfig["location"][0], ipconfig["location"][1]), 4.2)

    map_control = map.Map(
        ref=ref_map_control,
        expand=True,
        initial_center=map.MapLatitudeLongitude(ipconfig["location"][0], ipconfig["location"][1]),
        initial_zoom=4.2,
        interaction_configuration=map.MapInteractionConfiguration(
            flags=map.MapInteractiveFlag.ALL,
            rotation_threshold=0,
        ),
        on_secondary_tap=lambda e: map_on_secondary_tap(),
        layers=[
            map.TileLayer(
                url_template=c["map_tile_server"],
                fallback_url=c["map_tile_server"],
                pan_buffer=1,
                keep_alive=True,
                keep_buffer=1000,
                max_zoom=16,
                max_native_zoom=16,
            ),
            # 地震速报区域烈度标记图层
            map.MarkerLayer(
                ref=ref_map_eqr_areaint_layer,
                markers=[],
            ),
            # 历史地震震中标记
            map.MarkerLayer(
                ref=ref_map_eqr_marks_layer,
                markers=[]
            ),
            # 摇晃感知烈度标记图层
            map.MarkerLayer(
                ref=ref_map_esp_layer,
                markers=[],
            ),
            # 地震预警区域烈度标记图层
            map.MarkerLayer(
                ref=ref_map_eew_areaint_layer,
                markers=[],
            ),
            # 地震预警地震波图层
            map.CircleLayer(
                ref=ref_map_eew_wave_layer,
                circles=[],
            ),
            # 地震预警震中标记
            map.MarkerLayer(
                ref=ref_map_eew_marks_layer,
                markers=[],
            ),
            # 常驻置顶标记图层
            map.MarkerLayer(
                markers=[
                    # 观测点标记
                    map.Marker(
                        content=ft.Image(
                            src="/map_icons/home.png",
                            height=20,
                            width=20,
                            tooltip=f"{l["ip_addr"]}: {ipconfig['address']}\n{l["ip_region"]}: {ipconfig['region']}\n{l['lat']}: {ipconfig['location'][0]}\n{l['lon']}: {ipconfig['location'][1]}",
                        ),
                        coordinates=map.MapLatitudeLongitude(ipconfig['location'][0], ipconfig['location'][1]),
                )],
            ),
        ],
    )

    # EEW Control
    eew_control = ft.Column(
        ref=ref_eew_control,
        spacing=10,
        controls=[],
        alignment=ft.MainAxisAlignment.START,
    )

    # Earthquake list
    eqlist_control = ft.Column(
        ref=ref_eqlist_control,
        spacing=10,
        controls=[],
        alignment=ft.MainAxisAlignment.START,
    )

    page.add(ft.Row(
        expand=True,
        vertical_alignment=ft.CrossAxisAlignment.START,
        controls=[
            map_control,
            ft.Column(
                width=right_control_width,
                scroll=ft.ScrollMode.AUTO,
                alignment=ft.MainAxisAlignment.START,
                controls=[
                    eew_control,
                    eqlist_control,
                    ]
                )
            ],
        )
    )

    
    # Update title time in real-time
    page.run_task(appbar_handler, page)
