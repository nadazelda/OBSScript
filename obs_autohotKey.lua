obs = obslua

local start_time = nil
local mark_start_time = nil
local log_path = os.getenv("USERPROFILE") .. "/Documents/OBS_timestamps.txt"

-- 녹화 시작 시간 기록
function on_event(event)
    if event == obs.OBS_FRONTEND_EVENT_RECORDING_STARTED then
        mark_start_time = os.time()
        print("녹화 시작 시간 기록됨: " .. os.date("%X", mark_start_time))
    elseif event == obs.OBS_FRONTEND_EVENT_RECORDING_STOPPED then
        mark_start_time = nil
        print("녹화 종료됨")
    end
end

-- 경과시간 포맷터
function get_elapsed_time()
    if not mark_start_time then return "00:00:00" end
    local elapsed = os.time() - mark_start_time
    local h = math.floor(elapsed / 3600)
    local m = math.floor((elapsed % 3600) / 60)
    local s = elapsed % 60
    return string.format("%02d:%02d:%02d", h, m, s)
end

-- F3: 시작 타임 마킹
function on_hotkey_start()
    start_time = get_elapsed_time()
    print("Start marked: " .. start_time)
end

-- F4: 종료 타임 마킹 & 저장
function on_hotkey_end()
    if not start_time then return end
    local end_time = get_elapsed_time()

    local file = io.open(log_path, "a")
    if file then
		file:write(start_time .. " ~ " .. end_time .. "\n")
		file:close()
		print("Saved: " .. start_time .. " ~ " .. end_time)
	else
		print("⚠️ 로그 파일 열기 실패: " .. log_path)
	end

    print("Saved: " .. start_time .. " ~ " .. end_time)
    start_time = nil
end

-- 단축키 등록
function script_load(settings)
    obs.obs_frontend_add_event_callback(on_event)

    hotkey_start_id = obs.obs_hotkey_register_frontend("mark_start", "Mark Start Time (F3)", on_hotkey_start)
    hotkey_end_id = obs.obs_hotkey_register_frontend("mark_end", "Mark End Time (F4)", on_hotkey_end)

    local hk1 = obs.obs_data_get_array(settings, "mark_start")
    local hk2 = obs.obs_data_get_array(settings, "mark_end")
    obs.obs_hotkey_load(hotkey_start_id, hk1)
    obs.obs_hotkey_load(hotkey_end_id, hk2)
    obs.obs_data_array_release(hk1)
    obs.obs_data_array_release(hk2)
end

function script_save(settings)
    local hk1 = obs.obs_hotkey_save(hotkey_start_id)
    local hk2 = obs.obs_hotkey_save(hotkey_end_id)
    obs.obs_data_set_array(settings, "mark_start", hk1)
    obs.obs_data_set_array(settings, "mark_end", hk2)
    obs.obs_data_array_release(hk1)
    obs.obs_data_array_release(hk2)
end

function script_description()
    return "녹화 중 F3/F4로 구간 타임스탬프 기록 (00:00:00 ~ 00:00:00 형식)"
end
