"""
LGK_Podriver_Audio:
Longecko Podriver Interface Audio
By Avastrator
2025-03-30 10:04:19
"""
import asyncio
import os
import time
import edge_tts
from playsound import playsound

import LGK_Podriver_Utils as u
import LGK_Podriver_Args as a

output = a.get("logger")
c = a.get("config")
l = a.get("lang")
t = a.get("tmp_path")
ass_path = a.get("ass_path")

tts_lock = asyncio.Lock()

# Make sure the cache directory for TTS exists
if not os.path.exists(os.path.join(t, "TTS")):
    os.makedirs(os.path.join(t, "TTS"))

# Audios
audios = {
    "eew": {
        "weak": os.path.join(ass_path, "audio/eew_weak.wav"),
        "small": os.path.join(ass_path, "audio/eew_small.wav"),
        "medium": os.path.join(ass_path, "audio/eew_medium.wav"),
        "large": os.path.join(ass_path, "audio/eew_large.wav"),
        "severe": os.path.join(ass_path, "audio/eew_severe.wav"),
        "update": os.path.join(ass_path, "audio/eew_update.wav"),
        "countdown": os.path.join(ass_path, "audio/countdown.wav"),
        "arrived": os.path.join(ass_path, "audio/s_wave_arrived.wav"),
    },
    "eqr": {
        "normal": os.path.join(ass_path, "audio/eqr_normal.wav"),
        "medium": os.path.join(ass_path, "audio/eqr_medium.wav"),
        "large": os.path.join(ass_path, "audio/eqr_large.wav"),
    },
    "esp": {
        "weak": os.path.join(ass_path, "audio/esp_weak.wav"),
        "felt": os.path.join(ass_path, "audio/esp_small.wav"),
        "medium": os.path.join(ass_path, "audio/esp_medium.wav"),
        "strong": os.path.join(ass_path, "audio/esp_large.wav"),
        "severe": os.path.join(ass_path, "audio/esp_severe.wav"),
    },
    "tnm": {
        "low": os.path.join(ass_path, "audio/tnm_medium.wav"),
        "medium": os.path.join(ass_path, "audio/tnm_large.wav"),
        "severe": os.path.join(ass_path, "audio/tnm_severe.wav"),
    },
    "cancel": os.path.join(ass_path, "audio/cancelation.wav"),
}

async def get_tts(data: dict):
    if "datas" in data:
        return None
    # 生成TTS文字
    if data["event_type"] == "EEW":
        if data["int_type"] in ["CSIS", "MMI"]:
            int_type = "fc_max_intensity"
        else:
            int_type = "fc_max_shindo"
        voice = "zh-CN-XiaoyiNeural"
        final_report = l["final_report"] if data["report_final"] else ""
        text = f'{data["event_source"]}{l["eew"]}{l["report_num"].replace("[num]", str(data["report_num"]))}{final_report}, {data["region"]} {l["magnitude_num"].replace("[num]", str(data["magnitude"]))}, {l[int_type]}{u.shindo_to_cn(data["intensity"])}'
    elif data["event_type"] == "EQR":
        if data["int_type"] in ["CSIS", "MMI"]:
            int_type = "max_intensity"
        else:
            int_type = "max_shindo"
        if l["lang"] == "cn":
            voice = "zh-CN-XiaoyiNeural"
            text = f'{data["event_source"]}{l["eqr"]}, {data["region"]}{l["magnitude_num"].replace("[num]", str(data["magnitude"]))}, {l["depth"]}{data["depth"]}{l["km"]}, {l[int_type]}{u.shindo_to_cn(data["intensity"])}'
        elif l["lang"] == "en":
            # Not done yet
            return None
        else:
            return None
    else:
        return None
    ad_path = os.path.join(t, "TTS", f"{str(time.time())}_TTS.mp3")
    # 生成TTS
    for _ in range(3):
        try:
            tts = edge_tts.Communicate(text, voice)
            output.info(f"Generating TTS: {text}")
            await tts.save(ad_path)
            break
        except Exception as e:
            output.error(f"TTS error: {str(e)}")
    return ad_path

def get_sound(data):
    """
    Get sound effect by data
    """
    if isinstance(data, str):
        return data
    if data["event_type"] == "EEW":
        if data["int_type"] in ["CSIS", "MMI"]:
            if data["intensity"] <= 2:
                return audios["eew"]["weak"]
            elif data["intensity"] <= 4:
                return audios["eew"]["small"]
            elif data["intensity"] <= 6:
                return audios["eew"]["medium"]
            elif data["intensity"] <= 8:
                return audios["eew"]["large"]
            else:
                return audios["eew"]["severe"]
        elif data["int_type"] in ["JMA", "CWASIS"]:
            if data["intensity"] <= 2:
                return audios["eew"]["weak"]
            elif data["intensity"] <= 3:
                return audios["eew"]["small"]
            elif data["intensity"] <= 5:
                return audios["eew"]["medium"]
            elif data["intensity"] <= 6:
                return audios["eew"]["large"]
            else:
                return audios["eew"]["severe"]
        else:
            output.warn(f"Unknown EEW intensity type: {data['int_type']}")
            return None
    elif data["event_type"] == "EQR":
        if data["intensity"] <= 4.5:
            return audios["eqr"]["normal"]
        elif data["intensity"] < 6:
            return audios["eqr"]["medium"]
        else:
            return audios["eqr"]["large"]
    elif data["event_type"] == "ESP":
        data = data["list"][0]
        if data["int_type"] in ["CSIS", "MMI"]:
            if data["intensity"] <= 2:
                return audios["esp"]["weak"]
            elif data["intensity"] <= 4:
                return audios["esp"]["felt"]
            elif data["intensity"] <= 6:
                return audios["esp"]["medium"]
            elif data["intensity"] <= 8:
                return audios["esp"]["strong"]
            else:
                return audios["esp"]["severe"]
        elif data["int_type"] in ["JMA", "CWASIS"]:
            if data["intensity"] <= 2:
                return audios["esp"]["weak"]
            elif data["intensity"] <= 3:
                return audios["esp"]["felt"]
            elif data["intensity"] <= 5:
                return audios["esp"]["medium"]
            elif data["intensity"] <= 6:
                return audios["esp"]["strong"]
            else:
                return audios["esp"]["severe"]
        else:
            output.warn(f"Unknown EEW intensity type: {data['int_type']}")
            return None
    elif data["event_type"] == "CAN":
        return audios["cancel"]
    else:
        output.warn(f"Unknown event type: {data['event_type']}")
        return None

async def audio_player(path: str, lock=False):
    """
    Play audio
    """
    if lock:
        await tts_lock.acquire()
    try:
        audio_task = asyncio.create_task(asyncio.to_thread(playsound, path))
        await asyncio.wait_for(audio_task, timeout=60)
    except Exception as e:
        output.error(f"Audio player error: {str(e)}")
    finally:
        if lock:
            tts_lock.release()

async def player(data: dict, effect: bool, tts: bool, eew_update: bool):
    # play sound effect
    if effect and c["audio"]["play_effect"]:
        sound_path = get_sound(data)
        if sound_path:
            asyncio.create_task(audio_player(sound_path, False))
    if tts and c["audio"]["play_tts"]:
        tts_path = await get_tts(data)
        if tts_path:
            asyncio.create_task(audio_player(tts_path, True))
    if eew_update:
        asyncio.create_task(audio_player(audios["eew"]["update"], False))