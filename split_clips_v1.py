import os
import subprocess

# 🔹 스크립트 위치 기준
script_dir = os.path.dirname(os.path.abspath(__file__))

# 🔹 경로 설정
input_txt = os.path.join(script_dir, "OBS_timestamps.txt")
output_folder = os.path.join(script_dir, "clips")

os.makedirs(output_folder, exist_ok=True)

clip_index = 1

# 🔹 타임라인 읽기
with open(input_txt, "r", encoding="utf-8") as file:
    lines = file.readlines()

for line in lines:
    line = line.strip()
    if not line:
        continue

    parts = [p.strip() for p in line.split("|")]
    if len(parts) < 4:
        print(f"⚠️ 잘못된 형식: {line}")
        continue

    input_video, start_time, end_time, label = parts

    # 파일 경로 (py 파일과 같은 폴더에 영상이 있다고 가정)
    input_video_path = os.path.join(script_dir, input_video)

    if not os.path.exists(input_video_path):
        print(f"❌ 영상 파일 없음: {input_video_path}")
        continue

    label = label.replace(" ", "_") if label else "clip"

    output_file = os.path.join(
        output_folder,
        f"{clip_index:03d}_{label}.mp4"
    )

    command = [
        "ffmpeg",
        "-y",
        "-i", input_video_path,
        "-ss", start_time,
        "-to", end_time,
        "-c:v", "libx264",
        "-c:a", "aac",
        output_file
    ]

    print(f"✂️ 클립 생성: {output_file}")
    subprocess.run(command)

    clip_index += 1

print("\n🎬 모든 클립 생성 완료!")
