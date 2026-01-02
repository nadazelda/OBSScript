import obspython as obs
import os
import time
import tkinter as tk
from tkinter import simpledialog
from datetime import datetime

# === 전역 변수 선언 ===
start_time = None
record_start_time = None
log_path = os.path.expanduser("~/Documents/OBS_timestamps.txt")
hotkey_start_id = None
hotkey_end_id = None

# === OBS 이벤트 콜백 ===
def on_event(event):
    global record_start_time, current_recording_file

    if event == obs.OBS_FRONTEND_EVENT_RECORDING_STARTED:
        record_start_time = time.time()

        # 🔹 현재 녹화 파일 경로 가져오기
        output = obs.obs_frontend_get_recording_output()
        if output is not None:
            settings = obs.obs_output_get_settings(output)
            path = obs.obs_data_get_string(settings, "path")

            obs.obs_data_release(settings)
            obs.obs_output_release(output)

            # 파일명만 추출
            current_recording_file = os.path.basename(path)

        print(
            "[timestamp_logger.py] 녹화 시작:",
            current_recording_file,
            time.strftime("%X", time.localtime(record_start_time))
        )

    elif event == obs.OBS_FRONTEND_EVENT_RECORDING_STOPPED:
        record_start_time = None
        current_recording_file = None
        print("[timestamp_logger.py] 녹화 종료됨")


# === 경과 시간 계산 ===
def get_elapsed_time():
    if not record_start_time:
        return "00:00:00"
    elapsed = int(time.time() - record_start_time)
    h = elapsed // 3600
    m = (elapsed % 3600) // 60
    s = elapsed % 60
    return f"{h:02d}:{m:02d}:{s:02d}"

def get_elapsed_time_with_offset(offset_sec):
    if not record_start_time:
        return "00:00:00"
    elapsed = int(time.time() - record_start_time + offset_sec)
	# 🔒 음수 방지 (0초로 고정)
    if elapsed < 0:
        elapsed = 0
    h = elapsed // 3600
    m = (elapsed % 3600) // 60
    s = elapsed % 60
    return f"{h:02d}:{m:02d}:{s:02d}"

# === F3 단축키: 시작 시간 마킹 ===
def on_hotkey_start(pressed):
    global start_time
    if pressed:
        start_time = get_elapsed_time_with_offset(-10)
        print("[timestamp_logger.py] Start marked:", start_time)

# === F4 단축키: 종료 + 메모 입력 ===
def on_hotkey_end(pressed):
    global start_time
    if pressed and start_time:
        end_time = get_elapsed_time_with_offset(0)
        print("[timestamp_logger.py] End marked:", end_time)
        show_input_popup(start_time, end_time)
        start_time = None  # 초기화

# === 팝업 입력창 ===
def show_input_popup(start, end):
    root = tk.Tk()
    root.withdraw()  # 메인 창 숨기기

    try:
        user_input = simpledialog.askstring("메모 입력", f"{start} ~ {end} 구간에 대한 메모를 입력하세요:")
        if user_input:
            print(f"사용자 입력: {user_input}")
            write_to_log_file(start, end, user_input)
    finally:
        root.destroy()  # 창 닫기

# === 로그 파일 기록 ===
def write_to_log_file(start, end, memo):
    if not current_recording_file:
        print("[timestamp_logger.py] 녹화 파일 정보 없음, 기록 생략")
        return

    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"{current_recording_file} | {start} | {end} | {memo}\n")

        print(f"[timestamp_logger.py] 로그 기록 완료: {current_recording_file}")

    except Exception as e:
        print(f"[timestamp_logger.py] 파일 기록 실패: {e}")


# === OBS 스크립트 로딩 ===
def script_load(settings):
    global hotkey_start_id, hotkey_end_id

    obs.obs_frontend_add_event_callback(on_event)

    hotkey_start_id = obs.obs_hotkey_register_frontend("mark_start", "Mark Start Time (F3)", on_hotkey_start)
    hotkey_end_id = obs.obs_hotkey_register_frontend("mark_end", "Mark End Time + Memo (F4)", on_hotkey_end)

    hotkey_start = obs.obs_data_get_array(settings, "mark_start")
    hotkey_end = obs.obs_data_get_array(settings, "mark_end")

    obs.obs_hotkey_load(hotkey_start_id, hotkey_start)
    obs.obs_hotkey_load(hotkey_end_id, hotkey_end)

    obs.obs_data_array_release(hotkey_start)
    obs.obs_data_array_release(hotkey_end)

# === 단축키 저장 ===
def script_save(settings):
    global hotkey_start_id, hotkey_end_id

    if hotkey_start_id is None or hotkey_end_id is None:
        print("[timestamp_logger.py] 단축키 ID가 초기화되지 않았습니다. 저장을 건너뜁니다.")
        return

    start_keys = obs.obs_hotkey_save(hotkey_start_id)
    end_keys = obs.obs_hotkey_save(hotkey_end_id)

    obs.obs_data_set_array(settings, "mark_start", start_keys)
    obs.obs_data_set_array(settings, "mark_end", end_keys)

    obs.obs_data_array_release(start_keys)
    obs.obs_data_array_release(end_keys)

# === 설명 표시 ===
def script_description():
    return "녹화 중 F3/F4 단축키로 구간 타임스탬프 + 메모 기록 (파일 저장)"
