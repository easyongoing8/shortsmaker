import json
from typing import Dict, Any

# =====================================================================
# K07: M16 성과 지표 수집기 & M17 성과 진단 및 피드백 엔진
# =====================================================================
class PerformanceAnalyzer:
    """K07 규칙: 24h/7d/28d 성과 진단, 3분류 문제 진단, 6단 개선안 및 알고리즘 피드백"""

    @classmethod
    def analyze_performance(cls, analytics_data: Dict[str, Any], project_meta: Dict[str, Any]) -> Dict[str, Any]:
        timeframe = analytics_data.get("timeframe", "24h")  # 24h, 7d, 28d
        views = analytics_data.get("views", 0)
        retention_pct = analytics_data.get("avg_percentage_viewed", 0.0)  # 평균 완주율 (%)
        swipe_away_pct = analytics_data.get("swipe_away_rate", 0.0)      # 스와이프 이탈률 (%)
        shopping_clicks = analytics_data.get("shopping_clicks", 0)
        likes = analytics_data.get("likes", 0)
        comments = analytics_data.get("comments", 0)

        diagnostics = []

        # 1. 24시간 진단: 초반 훅 및 스와이프 이탈률 (기준: 스와이프 이탈률 > 35% 시 경고)
        if swipe_away_pct > 35.0:
            diagnostics.append({
                "category": "A. 영상 자체 (초반 훅)",
                "problem": "초반 0~2초 스와이프 이탈률 과다",
                "evidence": f"스와이프 이탈률 {swipe_away_pct}% (채널 목표 기준 30% 이하 초과)",
                "immediate_fix": "대표 썸네일 프레임 및 상단 1줄 자막을 더 자극적인 행동/숫자형으로 교체",
                "next_video_rule": "0~1.5초 구간에 설명 대사를 빼고 '스태프 뺏김' 등 즉각적인 제3자 리액션 컷을 0.0초에 바로 배치",
                "target_metric": "초반 3초 유지율 70% 이상 달성",
                "warning": "근거 없는 허위 과장 텍스트는 시청자 신뢰도를 떨어뜨리므로 실제 대사 기반 유지"
            })
        else:
            diagnostics.append({
                "category": "A. 영상 자체 (초반 훅)",
                "problem": "초반 후킹력 우수",
                "evidence": f"스와이프 이탈률 {swipe_away_pct}% (양호)",
                "immediate_fix": "현재 훅 구조 유지",
                "next_video_rule": "동일한 오프닝 템플릿(Whoosh + 표정 클로즈업) 지속 적용",
                "target_metric": "유지율 지속 유지",
                "warning": "없음"
            })

        # 2. 7일 진단: 완주율 및 제품 등장 타이밍 (기준: 완주율 < 80% 시 구조 점검)
        if retention_pct < 80.0:
            diagnostics.append({
                "category": "B. 콘텐츠 구조 및 제품 등장 타이밍",
                "problem": "영상 중반부 완주율 저하",
                "evidence": f"평균 완주율 {retention_pct}% (목표 85% 미달)",
                "immediate_fix": "해당 영상 고정댓글로 시청자 질문을 유도하여 체류시간 방어",
                "next_video_rule": "제품 정체 공개 시점을 기존 12초에서 8~9초대로 3초 이상 앞당김 (reveal_target_sec 조정)",
                "target_metric": "평균 완주율 85% 이상",
                "warning": "너무 일찍 제품명을 밝히면 궁금증이 해소되어 즉시 이탈할 수 있으므로 '이유'를 뒤에 배치"
            })

        # 3. 28일 진단: 쇼핑 전환 및 외부 전략 (CTR 검사)
        shopping_ctr = (shopping_clicks / max(1, views)) * 100
        if shopping_ctr < 1.0:
            diagnostics.append({
                "category": "C. 영상 밖 전략 (쇼핑 전환)",
                "problem": "쇼핑 링크 클릭률(CTR) 저조",
                "evidence": f"쇼핑 클릭수 {shopping_clicks}회 (조회수 대비 CTR {shopping_ctr:.2f}%)",
                "immediate_fix": "고정댓글 첫 줄을 '최저가 바로가기 👉' 형태로 가시성 높은 이모지와 함께 수정",
                "next_video_rule": "영상 엔딩 16초 지점에 '제품 정보는 댓글/쇼핑태그 확인' 유도 자막 추가",
                "target_metric": "쇼핑 CTR 2.0% 이상",
                "warning": "본문 전체를 링크 도배로 만들지 않고 깔끔한 1줄 링크 유지"
            })

        # 4. K07 차기 리서치 가중치 피드백 (Pattern Feedback Loop)
        feedback_weights = {
            "primary_viral_type_tested": project_meta.get("viral_type", "A2"),
            "feedback_action": "가중치 유지 및 reveal_target_sec = 8.5초로 고정" if retention_pct >= 80 else "A2 유형 점수 보정 및 오프닝 훅 강도 +5점 반영",
            "recommended_next_type": "D1 (다른 연예인이 탐낸형) 우선 리서치 권장"
        }

        report = {
            "project_id": project_meta.get("project_id", "PROJ_001"),
            "video_id": analytics_data.get("video_id", "VIDEO_001"),
            "timeframe": timeframe,
            "metrics_summary": {
                "views": views,
                "avg_percentage_viewed": f"{retention_pct}%",
                "swipe_away_rate": f"{swipe_away_pct}%",
                "shopping_clicks": shopping_clicks,
                "likes": likes,
                "comments": comments
            },
            "diagnostics_6_step": diagnostics,
            "feedback_weights": feedback_weights
        }

        # JSON 리포트 파일 저장
        with open("performance_analysis_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        return report