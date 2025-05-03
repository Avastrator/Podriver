"""
LGK_Podriver_UI_OOBE:
Longecko Podriver Main UI
By Avastrator
2025-03-23 10:39:50
"""
import flet as ft
import time

def oobe_app(page: ft.Page):
    page.title = "Podriver"
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
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    
    c = ft.Text(
        "Hello, Flet!",
        size=30,
        color="blue",
        offset=ft.transform.Offset(-2, 0),
        animate_offset=ft.animation.Animation(1000, curve="decelerate"),
    )

    def animate():
        c.offset = ft.transform.Offset(0, 0)
        c.update()

    page.add(
        c,
        ft.ElevatedButton("Reveal!"),
    )
    page.update()
    animate()