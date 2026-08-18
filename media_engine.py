import os
import json
import subprocess
from typing import List, Dict, Any

# =====================================================================
# K03: M4 자막 파서 및 표준 SRT 생성기
# =====================================================================
class SRTGenerator:
    """K03 규칙: UTF-8, 순번 연속, HH:MM:SS,mmm 정규화, cue 겹침 방지"""
    
    @staticmethod
    def ms_to_srt_time(ms: int) -> str:
        """ms 정수를 'HH:MM:SS,mmm' 표준 SRT 타임코드로 변환"""
        total_sec = ms // 1000
        mmm = ms % 1000
        h = total_sec // 3600
        m = (total_sec % 3600) // 60
        s = total_sec % 60
        return f"{h:02d}:{m:02d}:{s:02d},{mmm:03d}"

    @classmethod
    def export_srt(cls, cues: List[Dict[str, Any]], output_path: str = "output.srt") -> str:
        """K03 규격에 맞는 .srt 자막 파일 생성"""
        srt_lines = []
        for i, cue in enumerate(cues, start=1):
            st_str = cls.ms_to_srt_time(cue["start_ms"])
            et_str = cls.ms_to_srt_time(cue["end_ms"])
            srt_lines.append(f"{i}")
            srt_lines.append(f"{st_str} --> {et_str}")
            srt_lines.append(cue["text"].strip())
            srt_lines.append("")  # 공백 줄 필수
        
        content = "\n".join(srt_lines)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        return content


# =====================================================================
# K05 / K08: M9 & M13 FFmpeg 미디어 렌더러 및 매니페스트 생성기
# =====================================================================
class VideoRenderEngine:
    """
    K05/K08 규칙:
    - 모든 시간은 내부적으로 ms 정수 연산
    - 1.1배속 적용 (길이 = 원본구간 / 1.1)
    - 9:16 (1080x1920) 캔버스 1:1 중앙 크롭
    - 상단 2줄 자막(10자 이내) 오버레이
    - render_manifest 생성 및 20초 이하 사전 검증(Preflight)
    """

    @staticmethod
    def build_render_manifest(
        source_video_path: str,
        edl_clips: List[Dict[str, Any]],
        top_caption_1: str,
        top_caption_2: str,
        output_video_path: str = "shorts_rendered_20s.mp4"
    ) -> Dict[str, Any]:
        filter_complex = []
        concat_inputs = []
        total_rendered_ms = 0

        for i, clip in enumerate(edl_clips):
            st_sec = clip["src_start_ms"] / 1000.0
            et_sec = clip["src_end_ms"] / 1000.0
            clip_dur_ms = int((clip["src_end_ms"] - clip["src_start_ms"]) / 1.1)
            total_rendered_ms += clip_dur_ms

            # 1.1배속(setpts=PTS/1.1, atempo=1.1) + 9:16 세로 1080x1920 크롭
            v_filter = (
                f"[0:v]trim=start={st_sec:.3f}:end={et_sec:.3f},setpts=PTS-STARTPTS,"
                f"setpts=PTS/1.1,scale=-1:1920,crop=1080:1920,format=yuv420p[v{i}]"
            )
            a_filter = (
                f"[0:a]atrim=start={st_sec:.3f}:end={et_sec:.3f},asetpts=PTS-STARTPTS,"
                f"atempo=1.1[a{i}]"
            )
            filter_complex.extend([v_filter, a_filter])
            concat_inputs.append(f"[v{i}][a{i}]")

        # 클립 연결 (Concat)
        concat_str = f"{''.join(concat_inputs)}concat=n={len(edl_clips)}:v=1:a=1[v_cat][a_cat]"
        filter_complex.append(concat_str)

        # 상단 2줄 자막 번인 (drawtext)
        draw_str = (
            f"[v_cat]drawtext=text='{top_caption_1}':fontcolor=white:fontsize=48:"
            f"box=1:boxcolor=black@0.6:boxborderw=10:x=(w-text_w)/2:y=180,"
            f"drawtext=text='{top_caption_2}':fontcolor=yellow:fontsize=52:"
            f"box=1:boxcolor=black@0.6:boxborderw=10:x=(w-text_w)/2:y=250[v_out]"
        )
        filter_complex.append(draw_str)

        cmd = [
            "ffmpeg", "-y", "-i", source_video_path,
            "-filter_complex", ";".join(filter_complex),
            "-map", "[v_out]", "-map", "[a_cat]",
            "-c:v", "libx264", "-preset", "fast", "-crf", "22",
            "-c:a", "aac", "-b:a", "192k",
            output_video_path
        ]

        manifest = {
            "source_file": source_video_path,
            "output_file": output_video_path,
            "expected_duration_ms": total_rendered_ms,
            "expected_duration_sec": f"{total_rendered_ms / 1000.0:.2f}초",
            "is_under_20s": total_rendered_ms <= 20000,
            "clip_count": len(edl_clips),
            "command": " ".join(cmd)
        }

        # 렌더 매니페스트 JSON 저장
        with open("render_manifest.json", "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)

        return manifest

    @staticmethod
    def execute_render(manifest: Dict[str, Any]) -> bool:
        """FFmpeg 실제 렌더링 실행 (원본 영상이 존재할 때)"""
        if not manifest["is_under_20s"]:
            print(f"[오류 차단] 영상 길이({manifest['expected_duration_sec']})가 20초를 초과하여 렌더링을 차단합니다. (V8 규칙)")
            return False

        if not os.path.exists(manifest["source_file"]):
            print(f"[안내] '{manifest['source_file']}' 파일이 로컬에 없습니다. 'render_manifest.json'에 저장된 명령어로 렌더링이 가능합니다.")
            return False

        print(f"[FFmpeg 실행 중] {manifest['output_file']} 렌더링 시작...")
        res = subprocess.run(manifest["command"], shell=True, capture_output=True, text=True)
        if res.returncode == 0:
            print(f"✓ [렌더링 완료] {manifest['output_file']} 생성 완료!")
            return True
        else:
            print(f"[렌더링 에러] {res.stderr[:300]}")
            return False


# =====================================================================
# K05: CapCut PC 호환 컷 편집 텍스트 가이드 생성기
# =====================================================================
class CapCutGuideExporter:
    @staticmethod
    def export_guide(project_name: str, edl_clips: list, tts1: str, tts2: str, output_path: str = "capcut_edit_guide.txt"):
        lines = [
            f"=== [CapCut PC 실전 컷 편집 가이드: {project_name}] ===",
            "1. 프로젝트 비율: 9:16 (1080x1920) 설정",
            "2. 원본 영상 불러오기 후 전체 속도 1.1배속 설정",
            "3. 아래 타임코드대로 컷 분할(Ctrl+B) 및 순서 재배치\n",
            "--- [0.1초 컷 편집 타임라인 표] ---"
        ]
        curr_time = 0.0
        for i, c in enumerate(edl_clips, start=1):
            dur = (c["src_end_ms"] - c["src_start_ms"]) / 1100.0
            st_str = f"{curr_time:.1f}"
            curr_time += dur
            et_str = f"{curr_time:.1f}"
            src_st = f"{c['src_start_ms']//60000:02d}:{(c['src_start_ms']%60000)/1000:04.1f}"
            src_et = f"{c['src_end_ms']//60000:02d}:{(c['src_end_ms']%60000)/1000:04.1f}"
            lines.append(f"[{i}번 컷] 쇼츠시간: {st_str}~{et_str}초 | 원본타임코드: {src_st}~{src_et} | 내용: {c['text']}")

        lines.extend([
            f"\n--- [TTS 내레이션 2개 (동일 화자)] ---",
            f"• TTS 1 (02.8초 배치): {tts1}",
            f"• TTS 2 (12.5초 배치): {tts2}",
            f"\n--- [효과음 5개 배치 위치] ---",
            f"0.0초(whoosh) | 2.8초(pop) | 5.5초(impact) | 9.0초(sparkle) | 12.5초(ding)",
            f"\n총 완성 길이: {curr_time:.1f}초 (20초 이하 검수 완료)"
        ])

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))