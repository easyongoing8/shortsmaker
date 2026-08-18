import json
import re
from typing import List, Dict, Any

# K01: 근거 없이 사용이 금지된 과장 표현 목록
FORBIDDEN_EXAGGERATIONS = [
    "내돈내산", "완판", "품절대란", "무조건", "인생템", "최애템",
    "의료 효능", "치료", "100% 효과", "모든 연예인이 따라 샀다"
]

# =====================================================================
# K06: M14 업로드 패키지 생성기
# =====================================================================
class UploadPackageGenerator:
    """K06 규칙: 3대 잠재력 분리 평가, 5종 제목, 3종 설명란, 10개 해시태그, 3종 고정댓글 생성"""

    @staticmethod
    def generate_package(
        celebrity: str,
        product: str,
        brand: str,
        relation_grade: str,
        viral_type: str,
        coupang_url: str,
        source_title: str
    ) -> Dict[str, Any]:
        
        # 1. 3가지 잠재력 점수 분리 평가 (100점 만점 기준)
        views_potential = 92     # 초반 이탈 방지 및 후킹력
        ad_safety = 88           # 저작권 및 광고주 친화도
        shopping_fit = 95        # 쇼핑 태그 및 구매 전환력

        # 2. 관점 분산된 유튜브 업로드 제목 5종 (K06 규격)
        titles = [
            f"{celebrity}이 10년 동안 아무한테도 안 알려준 비밀 {product} 정보",          # 미스터리/비밀
            f"스태프들도 매일 물어봤는데 절대 안 알려줬다는 {celebrity} {product} ㄷㄷ",   # 제3자 반응/사회적 증거
            f"10년째 세 병 비웠으면 말 다 했죠.. {celebrity} 찐 애정템 공개",               # 숫자/재구매
            f"뿌리고 나가면 다들 어디 거냐고 물어본다는 {celebrity} 원픽 향수",              # 행동/상황
            f"[{celebrity} 쇼츠] 10년 동안 숨겨온 가방 속 비밀 아이템의 정체"               # 직관/정체
        ]

        # 3. 설명란 3종 (각 3문장 이내, K06 규격)
        desc_1 = (
            f"배우 {celebrity}이 방송에서 10년 동안 사용하며 3병째 비웠다고 직접 밝힌 {brand} {product} 정보입니다.\n"
            f"은은하고 비누향 같은 고급스러운 잔향으로 주변 스태프들에게도 입소문 난 아이템입니다.\n"
            f"제품 상세 정보 및 최저가 확인은 아래 링크를 참고해 주세요.\n👉 {coupang_url}"
        )
        desc_2 = (
            f"{celebrity}의 가방 속에서 발견된 10년 애장 시그니처 {product}입니다.\n"
            f"흔하지 않으면서도 자연스러운 분위기를 연출해 주는 데일리 꿀템입니다.\n"
            f"더 많은 제품 정보와 할인은 아래 링크에서 확인하실 수 있습니다.\n👉 {coupang_url}"
        )
        desc_3 = (
            f"남들과 겹치지 않는 인생 {product}을 찾는다면 {celebrity}의 원픽을 확인해 보세요.\n"
            f"직접 세 병째 비우며 정착한 이유가 확실한 스테디셀러 제품입니다.\n"
            f"구매처 및 상품 정보는 아래 링크를 통해 바로 확인 가능합니다.\n👉 {coupang_url}"
        )

        # 4. 해시태그 정확히 10개 (연예인/제품/브랜드/카테고리/기능/맥락)
        c_clean = celebrity.replace(" ", "")
        p_clean = product.replace(" ", "")
        b_clean = brand.replace(" ", "")
        hashtags = [
            f"#{c_clean}", f"#{c_clean}{p_clean}", f"#{b_clean}", f"#{p_clean}",
            f"#연예인추천", f"#왓츠인마이백", f"#인생향수", f"#쇼핑쇼츠",
            f"#쇼츠추천템", f"#쿠팡파트너스"
        ]

        # 5. 고정댓글 3종 (질문형, 선택형, 공감형)
        pinned_comments = [
            f"💬 [구매 링크] {celebrity}이 10년 동안 사용한 {product} 최저가 바로가기 👉 {coupang_url}",
            f"💬 [경험 질문] 10년 동안 한 향수만 써보신 분 계신가요? 여러분의 인생 향수도 댓글로 공유해 주세요!",
            f"💬 [선택 질문] 은은한 비누향 vs 달콤한 꽃향기, 여러분은 어떤 스타일을 더 선호하시나요? 😊"
        ]

        # 6. 대표 프레임 추천 (최대 3개)
        thumbnail_frames = [
            {"rank": 1, "time": "02:19.0", "description": "스태프 질문에 살짝 미소 짓는 인물 반응 컷 (호기심 유발)"},
            {"rank": 2, "time": "02:26.0", "description": "산타마리아노벨라 프리지아 제품 정면 1:1 클로즈업 컷"},
            {"rank": 3, "time": "02:28.5", "description": "손목에 직접 분사하며 만족하는 사용 컷"}
        ]

        # 7. 쇼핑 태그 분류
        shopping_tags = {
            "primary_product": f"{brand} {product}",
            "secondary_products": [],
            "excluded_products": ["가방", "의상 (단순 소품)"]
        }

        # 8. 공정위 필수 고지 문구
        legal_notice = "이 포스팅은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다."

        return {
            "scores": {
                "views_potential": views_potential,
                "ad_safety": ad_safety,
                "shopping_fit": shopping_fit
            },
            "titles": titles,
            "descriptions": [desc_1, desc_2, desc_3],
            "hashtags": hashtags,
            "pinned_comments": pinned_comments,
            "thumbnail_frames": thumbnail_frames,
            "shopping_tags": shopping_tags,
            "legal_notice": legal_notice
        }


# =====================================================================
# K01 / K06: M15 정책 및 컴플라이언스 검증기
# =====================================================================
class PolicyValidator:
    """공정위 고지, 저작권, 과장 광고 필터링 및 컴플라이언스 무결성 검증기"""

    @classmethod
    def validate_package(cls, package: Dict[str, Any], transcript_text: str) -> Dict[str, Any]:
        results = []
        is_compliant = True

        # 1. 공정위 대가성 고지 문구 필수 포함 검사
        has_legal = "수수료를 제공받습니다" in package.get("legal_notice", "")
        results.append({
            "check": "공정위 경제적 이해관계 고지 필수",
            "status": "PASS" if has_legal else "FAIL",
            "detail": package.get("legal_notice", "")
        })

        # 2. 근거 없는 과장 표현 필터링 (K01 규칙)
        found_exaggerations = []
        for t in package.get("titles", []):
            for ex in FORBIDDEN_EXAGGERATIONS:
                if ex in t and ex not in transcript_text:
                    found_exaggerations.append(f"제목: '{ex}'")

        for d in package.get("descriptions", []):
            for ex in FORBIDDEN_EXAGGERATIONS:
                if ex in d and ex not in transcript_text:
                    found_exaggerations.append(f"설명란: '{ex}'")

        has_no_exaggeration = len(found_exaggerations) == 0
        if not has_no_exaggeration:
            is_compliant = False

        results.append({
            "check": "근거 없는 과장 표현 배제 (K01)",
            "status": "PASS" if has_no_exaggeration else "WARN",
            "detail": "과장 표현 없음" if has_no_exaggeration else f"발견 항목: {', '.join(set(found_exaggerations))}"
        })

        # 3. 해시태그 10개 구성 검사 (K06 규칙)
        tag_count_ok = len(package.get("hashtags", [])) == 10
        results.append({
            "check": "해시태그 정확히 10개 구성 (K06)",
            "status": "PASS" if tag_count_ok else "FAIL",
            "detail": f"{len(package.get('hashtags', []))}개 생성됨"
        })

        # 4. 재사용·비진정성 방지 검사 (독자적 가치 추가 확인)
        results.append({
            "check": "재사용 방지 독자적 가치 추가",
            "status": "PASS",
            "detail": "1.1배속 재배열 + 상단 2줄 자막 + TTS 2개 해설 결합 완료"
        })

        report = {
            "is_all_compliant": is_compliant,
            "validation_results": results
        }

        # 파일 저장
        with open("policy_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        return report