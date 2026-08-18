from upload_policy_engine import UploadPackageGenerator, PolicyValidator
import json

# 1. 업로드 패키지 생성 (K06 규격)
package = UploadPackageGenerator.generate_package(
    celebrity="손예진",
    product="프리지아 오 드 코롱",
    brand="산타마리아노벨라",
    relation_grade="REL-B",
    viral_type="[A2] N병·N개 소진형",
    coupang_url="https://link.coupang.com/a/sample_son_perfume",
    source_title="[MY VOGUE] 손예진 가방 속 아이템"
)

# 2. JSON 파일 저장 (M14)
with open("upload_package.json", "w", encoding="utf-8") as f:
    json.dump(package, f, indent=2, ensure_ascii=False)
print("✓ [K06] 'upload_package.json' 생성 완료")

# 3. 정책 및 컴플라이언스 무결성 검증 (M15)
transcript_text = "제가 진짜 10년째 아무한테도 안 알려준 비밀 향수가 있거든요. 세 병째 쓰고 있어요."
report = PolicyValidator.validate_package(package, transcript_text)
print("✓ [K01/K06] 'policy_report.json' 검증 완료:")
print(json.dumps(report, indent=2, ensure_ascii=False))