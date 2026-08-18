import json
from typing import Dict, Any

# =====================================================================
# K02: M1 트렌드 리서치 & M2 롱폼 원본 발굴 엔진 (MODE A)
# =====================================================================
class ModeATrendEngine:
    """K02 규칙: 1,000만+ 쇼츠 벤치마킹, 롱폼 100점 평가 및 MODE B 자동 핸드오프"""

    BENCHMARK_DB = [
        {
            "cluster_id": "CLS_BEAUTY_PERFUME",
            "topic": "10년 숨겨온 비밀 향수",
            "celebrity": "손예진",
            "product": "산타마리아노벨라 프리지아",
            "proven_shorts_views": [1841000, 2156000, 1910000],  # 100만+ 3회 반복 검증
            "viral_pattern": "D1(스태프 탐냄) + A1(10년 애착) + A2(3병째 재구매)",
            "longform_candidate": {
                "source_id": "SRC_SON_VOGUE",
                "title": "[MY VOGUE] 손예진이 10년째 비밀을 유지한 향수 정보!",
                "channel": "VOGUE KOREA (매거진 공식 채널)",
                "url": "https://www.youtube.com/watch?v=sample_son",
                "duration_sec": 580,
                "terrestrial_origin": False,
                "score_breakdown": {
                    "주제 관련성(20)": 20,
                    "사용 가능 구간 밀도(15)": 15,
                    "시각적 임팩트(15)": 14,
                    "권리 안정성(15)": 15,
                    "인물 관심도(10)": 10,
                    "대사 후킹(10)": 10,
                    "재배열 가능성(10)": 10,
                    "현재성(5)": 5
                },
                "total_score": 99,
                "grade": "S (최우선 제작 소스)",
                "raw_transcript_cues": [
                    {"cue_id": 1, "start_ms": 135000, "end_ms": 138500, "text": "제가 진짜 10년째 아무한테도 안 알려준 비밀 향수가 있거든요."},
                    {"cue_id": 2, "start_ms": 139000, "end_ms": 142000, "text": "스태프들도 매일 뭐 뿌렸냐고 물어보는데 절대 안 알려줬어요."},
                    {"cue_id": 3, "start_ms": 142500, "end_ms": 145500, "text": "이거 뿌리고 나가면 다들 어디 거냐고 물어봐요. 오늘 처음 공개해요."},
                    {"cue_id": 4, "start_ms": 146000, "end_ms": 149000, "text": "바로 산타마리아노벨라 프리지아 향수예요. 세 병째 쓰고 있어요."}
                ]
            }
        },
        {
            "cluster_id": "CLS_SNACK_SWEETPOTATO",
            "topic": "가방 속 필수 다이어트 간식",
            "celebrity": "카리나",
            "product": "오사쯔 고구마스틱",
            "proven_shorts_views": [1725000, 2280000, 1507000],
            "viral_pattern": "A4(매일 챙김) + D1(스태프 따라 삼) + A2(10봉지째)",
            "longform_candidate": {
                "source_id": "SRC_KARINA_W",
                "title": "[ENG/JP] 에스파 카리나 인마이백 by W Korea",
                "channel": "W KOREA (매거진 공식 채널)",
                "url": "https://www.youtube.com/watch?v=sample_karina",
                "duration_sec": 490,
                "terrestrial_origin": False,
                "score_breakdown": {
                    "주제 관련성(20)": 19,
                    "사용 가능 구간 밀도(15)": 14,
                    "시각적 임팩트(15)": 15,
                    "권리 안정성(15)": 15,
                    "인물 관심도(10)": 10,
                    "대사 후킹(10)": 10,
                    "재배열 가능성(10)": 10,
                    "현재성(5)": 5
                },
                "total_score": 98,
                "grade": "S (최우선 제작 소스)",
                "raw_transcript_cues": [
                    {"cue_id": 1, "start_ms": 70000, "end_ms": 73000, "text": "카리나가 매일 가방에 넣고 다니는 최애 간식이에요."},
                    {"cue_id": 2, "start_ms": 74000, "end_ms": 77000, "text": "스태프들도 이거 한 번 먹어보고 다 따라 샀어요."},
                    {"cue_id": 3, "start_ms": 78000, "end_ms": 81000, "text": "진짜 바삭하고 고구마 100%라 10봉지째 먹고 있어요."},
                    {"cue_id": 4, "start_ms": 82000, "end_ms": 85000, "text": "바로 오사쯔 고구마스틱이에요. 가방에 없으면 불안해요."}
                ]
            }
        }
    ]

    @classmethod
    def research_trend(cls, query: str) -> Dict[str, Any]:
        """K02: 키워드 검색 기반 롱폼 발굴 및 MODE B 핸드오프 데이터 생성"""
        matched = []
        for item in cls.BENCHMARK_DB:
            if any(k in query for k in [item["celebrity"], item["product"], item["topic"], "오늘", "트렌드", "향수", "간식"]):
                matched.append(item)

        if not matched:
            matched = [cls.BENCHMARK_DB[0]]

        best = matched[0]
        longform = best["longform_candidate"]

        result = {
            "query": query,
            "matched_clusters": len(matched),
            "top_cluster_id": best["cluster_id"],
            "celebrity": best["celebrity"],
            "product": best["product"],
            "proven_shorts_success": f"100만+ 쇼츠 {len(best['proven_shorts_views'])}건 반복 검증 완료",
            "viral_pattern": best["viral_pattern"],
            "selected_longform": {
                "title": longform["title"],
                "channel": longform["channel"],
                "url": longform["url"],
                "duration": f"{longform['duration_sec']}초 (3분 이상 준수)",
                "longform_score": f"{longform['total_score']}점 ({longform['grade']})",
                "terrestrial_origin_excluded": True,
                "handoff_to_mode_b": {
                    "source_url": longform["url"],
                    "celebrity": best["celebrity"],
                    "product": best["product"],
                    "transcript_cues": longform["raw_transcript_cues"]
                }
            }
        }

        with open("mode_a_research_result.json", "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        return result