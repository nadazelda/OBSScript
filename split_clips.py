import os
import subprocess

# 현재 스크립트의 경로 기준으로 설정
script_dir = os.path.dirname(os.path.abspath(__file__))

# 경로 설정
input_txt = os.path.join(script_dir, "OBS_timestamps.txt")
input_video = os.path.join(script_dir, "a.mp4")
output_folder = os.path.join(script_dir, "clips")

# 출력 폴더가 없으면 생성
os.makedirs(output_folder, exist_ok=True)

# 타임라인 파일 읽기
with open(input_txt, "r", encoding="utf-8") as file:
    lines = file.readlines()

# 각 줄을 처리
for idx, line in enumerate(lines, 1):
    parts = line.strip().split("|")
    if len(parts) != 3:
        print(f"잘못된 형식: {line.strip()}")
        continue

    start_time = parts[0].strip()
    end_time = parts[1].strip()
    label = parts[2].strip().replace(" ", "_")  # 파일명에 공백 없애기

    output_file = os.path.join(output_folder, f"{idx}_{label}.mp4")

    # ffmpeg 명령어 생성 및 실행
    command = [
        "ffmpeg",
        "-i", input_video,
        "-ss", start_time,
        "-to", end_time,
        "-c:v", "libx264",
        "-c:a", "aac",
        "-strict", "experimental",
        "-y", output_file
    ]

    print(f"클립 저장 중: {output_file}")
    subprocess.run(command)

print("🎬 모든 클립이 성공적으로 저장되었습니다!")
