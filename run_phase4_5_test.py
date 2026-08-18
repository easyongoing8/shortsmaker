from media_engine import SRTGenerator, VideoRenderEngine, CapCutGuideExporter

# 1. K03 규격 자막 데이터 (손예진 롱폼 대본)
cues_data = [
    {"cue_id": 1, "start_ms": 135000, "end_ms": 138500, "text": "제가 진짜 10년째 아무한테도 안 알려준 비밀 향수가 있거든요."},
    {"cue_id": 2, "start_ms": 139000, "end_ms": 142000, "text": "스태프들도 매일 뭐 뿌렸냐고 물어보는데 절대 안 알려줬어요."},
    {"cue_id": 3, "start_ms": 142500, "end_ms": 145500, "text": "이거 뿌리고 나가면 다들 어디 거냐고 물어봐요. 오늘 처음 공개해요."},
    {"cue_id": 4, "start_ms": 146000, "end_ms": 149000, "text": "바로 산타마리아노벨라 프리지아 향수예요. 세 병째 쓰고 있어요."}
]

# 2. SRT 자막 파일 생성
SRTGenerator.export_srt(cues_data, "output.srt")
print("✓ [K03] 표준 자막 파일 'output.srt' 생성 완료")

# 3. K05 20초 편집 EDL 클립 (0~3초 최강 훅 전면 배치 및 재배열)
edl_clips_sample = [
    {"src_start_ms": 139000, "src_end_ms": 142000, "text": "스태프들도 매일 뭐 뿌렸냐고 물어보는데 절대 안 알려줬어요."},
    {"src_start_ms": 135000, "src_end_ms": 138000, "text": "제가 진짜 10년째 아무한테도 안 알려준 비밀 향수거든요."},
    {"src_start_ms": 142500, "src_end_ms": 145500, "text": "뿌리고 나가면 다들 어디 거냐고 물어봐요. 오늘 처음 공개해요."},
    {"src_start_ms": 146000, "src_end_ms": 148500, "text": "바로 산타마리아노벨라 프리지아 향수예요."},
    {"src_start_ms": 148500, "src_end_ms": 150000, "text": "세 병째 쓰고 있어요. (실제 분사 모습)"}
]

# 4. FFmpeg 렌더 매니페스트 생성
manifest = VideoRenderEngine.build_render_manifest(
    source_video_path="source.mp4",
    edl_clips=edl_clips_sample,
    top_caption_1="10년째 비밀 유지",
    top_caption_2="손예진 원픽 향수",
    output_video_path="shorts_final_20s.mp4"
)
print(f"✓ [K05/K08] 렌더 매니페스트 생성 완료 (예상 길이: {manifest['expected_duration_sec']} / 20초 이하 검증: {manifest['is_under_20s']})")

# 5. CapCut 편집 가이드 내보내기
CapCutGuideExporter.export_guide(
    project_name="손예진_비밀향수",
    edl_clips=edl_clips_sample,
    tts1="대체 뭐길래 10년 동안 숨겼을까요?",
    tts2="세 병째 비웠다면 설명 끝났습니다.",
    output_path="capcut_edit_guide.txt"
)
print("✓ [K05] CapCut 편집 가이드 'capcut_edit_guide.txt' 저장 완료")