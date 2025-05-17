"""
LGK_Podriver_UI_Main:
Longecko Podriver Main UI
By Avastrator
2025-03-23 10:39:50
"""

import flet as ft
import flet_map as map
import asyncio
import os
import json
import time
from datetime import datetime

import LGK_Podriver_Args as a
import LGK_Podriver_Utils as utils

c = a.get("config")
l = a.get("lang")
output = a.get("logger")

stg_path = a.get("stg_path")
tmp_path = a.get("tmp_path")
ass_path = a.get("ass_path")

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
            exiting_dialog = ft.AlertDialog(modal=True, title=ft.Text(l["shuting_down"]))
            page.open(exiting_dialog)
            exiting = asyncio.create_task(asyncio.to_thread(utils.safe_exit))
            await asyncio.wait_for(exiting, timeout=60)
            page.window.destroy()

    page.window.prevent_close = True
    page.window.on_event = window_event

    # AppBar
    def always_on_top_changed(e):
        e.control.checked = not e.control.checked
        page.window.always_on_top = e.control.checked
        page.update()

    page.appbar = ft.AppBar(
        title=ft.Text(
            f"{l["podriver"]} · {a.get('ipconfig')['region']}",
            size=25,
            font_family="harmony_b",
        ),
        actions=[
            ft.Text("0000-00-00 00:00:00", size=25, font_family="harmony_b"),
            ft.PopupMenuButton(
                tooltip=l["config"],
                items=[
                    ft.PopupMenuItem(icon="PUSH_PIN", text=l["always_on_top"], checked=False, on_click=lambda e: always_on_top_changed(e)),
                    ft.PopupMenuItem(),
                    ft.PopupMenuItem(icon="settings", text=l["settings"], on_click=lambda e: page.open(settings_dialog))
                ]
            )
        ],
    )

    # Settings
    field_width = 400
    def validate_required_text_field(e):
        if e.control.value.replace(" ", "") == "":
            e.control.error_text = l["field_required"]
            e.control.update()
        else:
            e.control.error_text = None
            e.control.update()
    def on_settings_save(e):
        global c
        try:
            output.info(f"Saving configuration...: {str(c)}")
            a.set("config", c)
            with open(os.path.join(stg_path, "config.conf"), "w", encoding="utf-8") as f:
                json.dump(c, f, ensure_ascii=False, indent=4)
        except Exception as e:
            output.error(f"Failed to save configuration: {str(e)}")
            fail_alert = ft.AlertDialog(
                modal=True,
                title=ft.Text(l["fail"]),
                content=ft.Text(str(e), size=16, font_family="harmony_m"),
                actions=[
                    ft.TextButton(l["confirm"], on_click=lambda e: page.close(fail_alert))
                ],
            )
            page.open(fail_alert)
            return
        page.close(settings_dialog)
        success_alert = ft.AlertDialog(
            modal=True,
            title=ft.Text(l["success"]),
            content=ft.Text(l["config_saved_restart_required"], size=16, font_family="harmony_m"),
            actions=[
                ft.TextButton(l["confirm"], on_click=lambda e: page.close(success_alert))
            ]
        )
        page.open(success_alert)
    def on_give_up_settings(e):
        a.set("config", json.load(open(os.path.join(stg_path, "config.conf"), "r", encoding="utf-8"))) # Reload config
        page.close(settings_dialog)
    def on_clean_cache(e):
        cache_size = utils.cache_clean()
        e.control.text = f"{l['cache_cleared']} ({round(cache_size, 2)}MB)"
        e.control.icon = "done"
        e.control.disabled = True
        e.control.update()
        time.sleep(2)
        e.control.text = l["clean_cache_now"]
        e.control.icon = None
        e.control.disabled = False
        e.control.update()

    settings_dialog = ft.AlertDialog(
        # NOTE: 哎我操lambda函数内不能直接进行赋值操作，只能通过exec函数来实现咯
        modal=True,
        title=ft.Text(l["settings"]),
        content=ft.Column(
            alignment=ft.MainAxisAlignment.START,
            scroll=ft.ScrollMode.AUTO,
            spacing=15,
            controls=[
                ft.Text(l["podris_server_config"], size=20, font_family="harmony_m"),
                ft.TextField(
                    expand=True,
                    label=l["podris_server_host"],
                    prefix=ft.Text(value="ws:// ", size=16, font_family="harmony_r"),
                    value=c["podris_server"]["host"],
                    on_change=lambda e: exec('c["podris_server"]["host"] = e.control.value', {'c': c, 'e': e}),
                    width=field_width,
                    on_blur=validate_required_text_field,
                ),
                ft.TextField(
                    expand=True,
                    label=l["podris_server_port"],
                    value=str(c["podris_server"]["port"]),
                    on_change=lambda e: exec('c["podris_server"]["port"] = int(e.control.value)', {'c': c, 'e': e}),
                    width=field_width,
                    input_filter=ft.NumbersOnlyInputFilter(),
                    on_blur=validate_required_text_field,
                ),
                ft.TextField(
                    expand=True,
                    password=True,
                    can_reveal_password=True,
                    label=l["podris_server_token"],
                    value=c["podris_server"]["token"],
                    on_change=lambda e: exec('c["podris_server"]["token"] = e.control.value', {'c': c, 'e': e}),
                    width=field_width,
                    on_blur=validate_required_text_field,
                ),
                ft.TextField(
                    expand=True,
                    label=f"{l["source_filter_separated_by_commas"]} ({l["field_optional"]})",
                    value=",".join(c["source_filter"]),
                    on_change=lambda e: exec('c["source_filter"] = e.control.value.split(",")', {'c': c, 'e': e}),
                    width=field_width,
                ),
                ft.Row(
                    alignment=ft.MainAxisAlignment.START,
                    spacing=10,
                    controls=[
                        ft.Text(f"{l["source_filter_mode"]}:", size=18, font_family="harmony_l"),
                        ft.SegmentedButton(
                            on_change=lambda e: exec('c["source_filter_type"] = list(e.control.selected)[0]', {'c': c, 'e': e}),
                            selected_icon=ft.Icon("check"),
                            selected={"blacklist"},
                            allow_multiple_selection=False,
                            segments=[
                                ft.Segment(
                                    label=ft.Text(l["blacklist"], size=14),
                                    value="blacklist"
                                ),
                                ft.Segment(
                                    label=ft.Text(l["whitelist"], size=14),
                                    value="whitelist"
                                )
                            ],
                        ),
                    ]
                ),
                ft.Text(l["map_config"], size=20, font_family="harmony_m"),
                ft.TextField(
                    expand=True,
                    label=l["map_tile_server"],
                    value=c["map_tile_server"],
                    on_change=lambda e: exec('c["map_tile_server"] = e.control.value', {'c': c, 'e': e}),
                    width=field_width,
                    on_blur=validate_required_text_field,
                ),
                ft.Text(l["ip_config"], size=20, font_family="harmony_m"),
                ft.TextField(
                    expand=True,
                    label=f"{l["ip_addr"]} ({l["field_optional"]})",
                    value=c["ipconfig"]["address"],
                    on_change=lambda e: exec('c["ipconfig"]["address"] = e.control.value', {'c': c, 'e': e}),
                    width=field_width,
                ),
                ft.TextField(
                    expand=True,
                    label=l["ip_region"],
                    value=c["ipconfig"]["region"],
                    on_change=lambda e: exec('c["ipconfig"]["region"] = e.control.value', {'c': c, 'e': e}),
                    width=field_width,
                    on_blur=validate_required_text_field,
                ),
                ft.TextField(
                    expand=True,
                    label=l["ip_latitude"],
                    value=str(int(c["ipconfig"]["location"][0])),
                    on_change=lambda e: exec('c["ipconfig"]["location"][0] = float(e.control.value)', {'c': c, 'e': e}),
                    width=field_width,
                    input_filter=ft.NumbersOnlyInputFilter(),
                    on_blur=validate_required_text_field,
                ),
                ft.TextField(
                    expand=True,
                    label=l["ip_longitude"],
                    value=str(int(c["ipconfig"]["location"][1])),
                    on_change=lambda e: exec('c["ipconfig"]["location"][1] = float(e.control.value)', {'c': c, 'e': e}),
                    width=field_width,
                    input_filter=ft.NumbersOnlyInputFilter(),
                    on_blur=validate_required_text_field,
                ),
                ft.Checkbox(label=l["force_use_custom_config"], value=c["ipconfig"]["force_use"], on_change=lambda e: exec('c["ipconfig"]["force_use"] = e.control.value', {'c': c, 'e': e})),
                ft.Text(l["ui_config"], size=20, font_family="harmony_m"),
                ft.TextField(
                    expand=True,
                    label=l["eqhistory_control_width"],
                    value=str(c["ui"]["eqhistory_control_width"]),
                    on_change=lambda e: exec('c["ui"]["eqhistory_control_width"] = int(e.control.value)', {'c': c, 'e': e}),
                    width=field_width,
                    input_filter=ft.NumbersOnlyInputFilter(),
                    on_blur=validate_required_text_field,
                ),
                ft.Text(l["storage_config"], size=20, font_family="harmony_m"),
                ft.Row(
                    alignment=ft.MainAxisAlignment.START,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10,
                    controls=[
                        ft.FilledTonalButton(
                            l["open_storage_folder"],
                            on_click=lambda e: os.startfile(stg_path)
                        ),
                        ft.FilledTonalButton(
                            l["open_cache_folder"],
                            on_click=lambda e: os.startfile(tmp_path)
                        ),
                        ft.FilledTonalButton(
                            l["open_assets_folder"],
                            on_click=lambda e: os.startfile(ass_path)
                        )
                    ]
                ),
                ft.OutlinedButton(text=l["clean_cache_now"], on_click=lambda e: on_clean_cache(e)),
                ft.Checkbox(label=l["auto_clean_cache"], value=c["clear_cache"], on_change=lambda e: exec('c["clear_cache"] = e.control.value', {'c': c, 'e': e})),
                ft.Text(l["debug_config"], size=20, font_family="harmony_m"),
                ft.Checkbox(label=l["save_log"], value=c["save_log"], on_change=lambda e: exec('c["save_log"] = e.control.value', {'c': c, 'e': e})),
                ft.Divider(thickness=1),
                ft.Image(src="PoweredbyProjectPodris.png", width=250, fit=ft.ImageFit.CONTAIN),
                ft.Text(f"Config Version: {c["config_version"]}", size=12, font_family="harmony_l"),
                ft.Text(f"Language: {l["lang"]}", size=12, font_family="harmony_l"),
                ft.Text(f"Podriver Version: {a.get("ver")}", size=12, font_family="harmony_l"),
            ]
        ),
        actions=[
            ft.TextButton(l["cancel"], on_click=lambda e: on_give_up_settings(e)),
            ft.TextButton(l["save"], on_click=lambda e: on_settings_save(e)),
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
