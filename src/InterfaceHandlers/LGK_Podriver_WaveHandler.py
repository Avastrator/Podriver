"""
LGK_Podriver_WaveHandler:
Longecko Podriver Interface earthquakeWave Handler
By Avastrator
2025-03-23 12:15:52
"""
import json
import flet as ft
import flet_map as map
from datetime import datetime
import asyncio

import LGK_Podriver_Args as a

output = a.get("logger")
c = a.get("config")
ass_path = a.get("ass_path")

a.set("eew_area_int_list", {})

# import travel timetable
tt = json.load(open(f"{ass_path}/traveltimetable.json", "r", encoding="utf-8"))

frame = c["ui"]["wave_drawing_frame"]
sec_per_frame = 1 / frame
    
def get_travel_timetable(depth: int):
    # 匹配对应深度的走时表, tjma2011的标准: 0-50内偶数, 50-200公差为五的数. 200-700公差为十的数
    depth = int(float(depth))
    if depth <= 50:
        if depth % 2 == 0:
            depth = depth
        else:
            depth = depth - 1
    elif depth <= 200:
        depth = depth // 5 * 5
    elif depth <= 700:
        depth = depth // 10 * 10
    else:
        depth = 700
    return tt[str(depth)]

def get_travel_time(eqtime: str, depth: int, radius: int, wave_type: str = "s"):
    t = get_travel_timetable(depth)
    # 匹配对应半径, tjma2011的标准: 0-50内偶数, 50-200公差为五的数. 200-2000公差为十的数
    r = int(radius)
    if r <= 50:
        if r % 2 == 0:
            r = r
        else:
            r = r - 1
    elif r <= 200:
        r = r // 5 * 5
    elif r <= 2000:
        r = r // 10 * 10
    else:
        at = t[-1][2] + (r - 2000) / 4 # 超出走时表的粗略计算就行了
        nt = at - (datetime.now() - datetime.strptime(eqtime, "%Y-%m-%d %H:%M:%S")).total_seconds()
        return nt
    # 取表
    res = [sublist for sublist in t if sublist[0] == r]
    if wave_type == "s":
        at = res[0][2]
    else:
        at = res[0][1]
    nt = at - (datetime.now() - datetime.strptime(eqtime, "%Y-%m-%d %H:%M:%S")).total_seconds()
    return nt

async def pwave(tt: list, data: dict, cc_queue: asyncio.Queue):
    """
    P波输出
    """
    try:
        start_time = datetime.strptime(data["time"], "%Y-%m-%d %H:%M:%S")
        i = -1
        last_r = 0
        last_circle = None
        constant = False
        on_ground = True
        circle = map.CircleMarker(
            coordinates=map.MapLatitudeLongitude(data["location"][0], data["location"][1]),
            radius=0,
            use_radius_in_meter=True,
            color=ft.Colors.with_opacity(0.15, c["ui"]["p_wave_color"]),
            border_color=c["ui"]["p_wave_color"],
            border_stroke_width=c["ui"]["wave_border"],
        )
        while True:
            i += 1
            try:
                r, t  = tt[i][0] - last_r, tt[i][1] - (datetime.now() - start_time).total_seconds() # 获取当前走时半径与时间
            except IndexError:
                r, t = 7, 1 # 走时表已用完, 接下来按匀速7km/s绘制
                constant = True
            if t < 0: # 该走时已过时
                if on_ground == False: # 地表地震波
                    if r == 2:
                        last_r -= r # 刚到地表的那就把这段跳过距离算到下一次走时避免地震波是闪出来的
                        continue
                    elif last_r < 0: # 还是没追上
                        continue
                    else: # 已经追上地震波了
                        on_ground = True
                circle.radius += 1000 * r
                last_r = tt[i][0]
                continue
            if not constant:
                last_r = tt[i][0]
            if r == 0: # 地震波还没到地表
                on_ground = False
                r = t * 7
                t -= 1 # 抵消绘制中途的误差
                circle.radius, circle.color, circle.border_stroke_width = 1000 * r, ft.Colors.with_opacity(0.4, c["ui"]["p_wave_color"]), 0
                sr = 1000 * (r / (t // sec_per_frame + 1))
                for _ in range(int(t // sec_per_frame)):
                    circle.radius -= sr
                    await asyncio.sleep(sec_per_frame)
                    cc_queue.put_nowait([circle, last_circle])
                    last_circle = circle
                circle.radius, circle.color, circle.border_stroke_width = 0, ft.Colors.with_opacity(0.15, c["ui"]["p_wave_color"]), c["ui"]["wave_border"]
                await asyncio.sleep(t % sec_per_frame)
                cc_queue.put_nowait([circle, last_circle])
                last_circle = circle
                continue
            sr = 1000 * (r / (t // sec_per_frame + 1))
            for _ in range(int(t // sec_per_frame)):
                circle.radius += sr
                await asyncio.sleep(sec_per_frame)
                cc_queue.put_nowait([circle, last_circle])
                last_circle = circle
            circle.radius += sr
            await asyncio.sleep(t % sec_per_frame)
            cc_queue.put_nowait([circle, last_circle])
            last_circle = circle
    except asyncio.CancelledError:
        try:
            a.get("ref_map_eew_wave_layer").current.circles.remove(last_circle)
        except ValueError:
            pass
        return

async def swave(tt: list, data: dict, cc_queue: asyncio.Queue):
    """
    S波输出
    """
    try:
        start_time = datetime.strptime(data["time"], "%Y-%m-%d %H:%M:%S")
        i = -1
        last_r = 0
        last_circle = None
        constant = False
        on_ground = True
        circle = map.CircleMarker(
            coordinates=map.MapLatitudeLongitude(data["location"][0], data["location"][1]),
            radius=0,
            use_radius_in_meter=True,
            color=ft.Colors.with_opacity(0.15, c["ui"]["s_wave_color"]),
            border_color=c["ui"]["s_wave_color"],
            border_stroke_width=c["ui"]["wave_border"],
        )
        while True:
            i += 1
            try:
                r, t  = tt[i][0] - last_r, tt[i][2] - (datetime.now() - start_time).total_seconds()
            except IndexError:
                r, t = 4, 1 # 走时表已用完, 接下来按匀速4km/s绘制
                constant = True
            if t < 0: # 该走时已过时
                if on_ground == False: # 地表地震波
                    if r == 2:
                        last_r -= r # 刚到地表的那就把这段跳过距离算到下一次走时避免地震波是闪出来的
                        continue
                    elif last_r < 0: # 还是没追上
                        continue
                    else: # 已经追上地震波了
                        on_ground = True
                circle.radius += 1000 * r
                last_r = tt[i][0]
                continue
            if not constant:
                last_r = tt[i][0]
            if r == 0: # 地震波还没到地表
                on_ground = False
                r = t * 4
                t -= 1 # 抵消绘制中途的误差
                circle.radius, circle.color, circle.border_stroke_width = 1000 * r, ft.Colors.with_opacity(0.4, c["ui"]["s_wave_color"]), 0
                sr = 1000 * (r / (t // sec_per_frame + 1))
                for _ in range(int(t // sec_per_frame)):
                    circle.radius -= sr
                    await asyncio.sleep(sec_per_frame)
                    cc_queue.put_nowait([circle, last_circle])
                    last_circle = circle
                circle.radius, circle.color, circle.border_stroke_width = 0, ft.Colors.with_opacity(0.15, c["ui"]["s_wave_color"]), c["ui"]["wave_border"]
                await asyncio.sleep(t % sec_per_frame)
                cc_queue.put_nowait([circle, last_circle])
                last_circle = circle
                r = 0
                continue
            sr = 1000 * (r / (t // sec_per_frame + 1))
            for _ in range(int(t // sec_per_frame)):
                circle.radius += sr
                await asyncio.sleep(sec_per_frame)
                cc_queue.put_nowait([circle, last_circle])
                last_circle = circle
            circle.radius += sr
            await asyncio.sleep(t % sec_per_frame)
            cc_queue.put_nowait([circle, last_circle])
            last_circle = circle
    except asyncio.CancelledError:
        try:
            a.get("ref_map_eew_wave_layer").current.circles.remove(last_circle)
        except ValueError:
            pass
        return

async def wave_handler(data: dict):
    """
    Handle seismic wave visualization drawing
    """
    try:
        if data["depth"] > 700:
            return # 你妈了隔壁那么深画个P的地震波啊我操你妈
        wave_queue = asyncio.Queue()
        tt = get_travel_timetable(data["depth"])
        p_wave_task = asyncio.create_task(pwave(tt, data, wave_queue))
        s_wave_task = asyncio.create_task(swave(tt, data, wave_queue))
        # 接下来绘制P波和S波
        while True:
            circle, last_circle = await wave_queue.get()
            if not last_circle == None:
                a.get("ref_map_eew_wave_layer").current.circles = [circle if i == last_circle else i for i in a.get("ref_map_eew_wave_layer").current.circles]
            else:
                a.get("ref_map_eew_wave_layer").current.circles.append(circle)
            # 应用
            a.get("ref_map_eew_wave_layer").current.update()
    except asyncio.CancelledError:
        pass
    except Exception as e:
        output.error(f"Wave handler error: {str(e)}")
        return
    finally:
        p_wave_task.cancel()
        s_wave_task.cancel()
        try:
            await p_wave_task
        except asyncio.CancelledError:
            pass
        try:
            await s_wave_task
        except asyncio.CancelledError:
            pass
        a.get("ref_map_eew_wave_layer").current.update()
        return
