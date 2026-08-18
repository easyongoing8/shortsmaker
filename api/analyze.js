// Vercel Serverless API Route: /api/analyze
export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method Not Allowed' });

  try {
    const { videoUrl, apiKey, coupangId } = req.body;
    const geminiKey = apiKey || process.env.GEMINI_API_KEY;
    const cId = coupangId || "AF893214";

    let videoId = "";
    const ytMatch = videoUrl ? videoUrl.match(/(?:v=|\/)([0-9A-Za-z_-]{11})/) : null;
    if (ytMatch) videoId = ytMatch;

    if (geminiKey) {
      const prompt = `
너는 한국 시장용 연예인 추천템 쇼핑 쇼츠 제작 최고 전문가다.
유튜브 링크: ${videoUrl || "없음"} (Video ID: ${videoId})

규칙:
1. 영상에서 출연 연예인을 파악하고, 영상에 등장하는 '실제 사용/추천 제품들'을 2~3개 추출해라.
2. 각 제품마다 100점 채점, 바이럴 유형, 해당 제품이 나오는 원본 대본 타임코드(시작~종료 대사)를 작성해라.
3. 각 제품마다 20초 이하 3가지 편집안(A:궁금증·반전형, B:문제·해결형, C:인물·루틴·신뢰형)과 TTS 2개, 효과음 5개, 상단 2줄 자막, 유튜브 제목 5개를 작성해라.

반드시 아래 JSON 포맷으로만 응답해라:
{
  "celebrity": "연예인 이름",
  "products": [
    {
      "id": "PROD_01",
      "product": "1위 제품명",
      "brand": "브랜드명",
      "score": 96,
      "grade": "S (즉시 제작)",
      "viralTypePrimary": "[A2] N병·N개 소진형",
      "viralTypeSecondary": "[A1] N년 사용형",
      "hookQuote": "가장 강한 3초 훅 대사",
      "transcriptText": "[02:15 ~ 02:18] 대사 1\\n[02:19 ~ 02:22] 대사 2...",
      "variants": {
        "A": {
          "name": "궁금증·반전형 (A안)",
          "duration": "18.5초",
          "durNum": 18.5,
          "top1": "상단 1줄 자막 (10자 이내)",
          "top2": "상단 2줄 자막 (10자 이내)",
          "tts1": "TTS 1 내레이션 (02.8초)",
          "tts2": "TTS 2 내레이션 (12.5초)",
          "sfx": "0.0초: whoosh | 2.8초: pop | 5.5초: impact | 9.0초: sparkle | 12.5초: ding",
          "scenes": [
            {"scene": "장면 1 (최강 훅)", "time": "0.0 ~ 2.8초", "srcTime": "02:19 ~ 02:22", "action": "대사", "edit": "1.1배속 + 크롭", "sfx": "SFX 1: whoosh"}
          ]
        },
        "B": {
          "name": "문제·해결형 (B안)",
          "duration": "18.2초",
          "durNum": 18.2,
          "top1": "상단 1줄 자막",
          "top2": "상단 2줄 자막",
          "tts1": "TTS 1 내레이션",
          "tts2": "TTS 2 내레이션",
          "sfx": "0.0초: whoosh | 3.0초: impact | 6.5초: sparkle | 10.5초: pop | 14.0초: ding",
          "scenes": [
            {"scene": "장면 1 (문제 제기)", "time": "0.0 ~ 3.0초", "srcTime": "02:15 ~ 02:18", "action": "대사", "edit": "1.1배속", "sfx": "SFX 1: whoosh"}
          ]
        },
        "C": {
          "name": "인물·루틴·신뢰형 (C안)",
          "duration": "18.0초",
          "durNum": 18.0,
          "top1": "상단 1줄 자막",
          "top2": "상단 2줄 자막",
          "tts1": "TTS 1 내레이션",
          "tts2": "TTS 2 내레이션",
          "sfx": "0.0초: whoosh | 2.5초: pop | 6.5초: impact | 10.5초: sparkle | 13.5초: ding",
          "scenes": [
            {"scene": "장면 1 (루틴 공개)", "time": "0.0 ~ 2.5초", "srcTime": "02:28 ~ 02:29", "action": "대사", "edit": "1.1배속", "sfx": "SFX 1: whoosh"}
          ]
        }
      },
      "ytTitles": [ "제목 1", "제목 2", "제목 3", "제목 4", "제목 5" ]
    }
  ]
}
`;

      const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${geminiKey}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contents: [{ parts: [{ text: prompt }] }],
          generationConfig: { responseMimeType: "application/json" }
        })
      });

      if (response.ok) {
        const data = await response.json();
        const resJson = JSON.parse(data.candidates[0].content.parts[0].text);
        if (resJson.products) {
          resJson.products.forEach(p => {
            p.coupangLink = `https://link.coupang.com/a/${cId}_${encodeURIComponent(p.product.replace(/\s+/g,''))}`;
          });
        }
        return res.status(200).json(resJson);
      }
    }

    // 기본 모의 데이터 (API 미입력 시 2개 제품 & A/B/C안 자동 제공)
    return res.status(200).json({
      celebrity: "손예진",
      products: [
        {
          id: "PROD_01",
          product: "프리지아 오 드 코롱 (향수)",
          brand: "산타마리아노벨라",
          score: 96,
          grade: "S (즉시 제작)",
          viralTypePrimary: "[A2] N병·N개 소진형",
          viralTypeSecondary: "[A1] N년 사용형",
          hookQuote: "제가 진짜 10년째 아무한테도 안 알려준 비밀 향수가 있거든요.",
          transcriptText: "[02:15.0 ~ 02:18.5] 제가 진짜 10년째 아무한테도 안 알려준 비밀 향수가 있거든요.\n[02:19.0 ~ 02:22.0] 스태프들도 매일 뭐 뿌렸냐고 물어보는데 절대 안 알려줬어요.\n[02:22.5 ~ 02:25.5] 이거 뿌리고 나가면 다들 어디 거냐고 물어봐요. 오늘 처음 공개해요.\n[02:26.0 ~ 02:29.0] 바로 산타마리아노벨라 프리지아 향수예요. 세 병째 쓰고 있어요.",
          variants: {
            A: {
              name: "궁금증·반전형 (A안 - 강력 추천)",
              duration: "18.5초",
              durNum: 18.5,
              top1: "10년째 비밀 유지",
              top2: "손예진 원픽 향수",
              tts1: "대체 뭐길래 손예진이 10년 동안 숨겼을까요?",
              tts2: "세 병째 비웠다면 설명 끝났습니다.",
              sfx: "0.0초: whoosh | 2.8초: pop | 5.5초: impact | 9.0초: sparkle | 12.5초: ding",
              scenes: [
                { scene: "장면 1 (최강 훅)", time: "0.0 ~ 2.8초", srcTime: "02:19 ~ 02:22", action: "스태프들도 매일 뭐 뿌렸냐고 물어보는데 절대 안 알려줬어요.", edit: "1.1배속 + 크롭", sfx: "SFX 1: whoosh" },
                { scene: "장면 2 (의문 제기)", time: "2.8 ~ 5.5초", srcTime: "02:15 ~ 02:18", action: "제가 진짜 10년째 아무한테도 안 알려준 비밀 향수거든요.", edit: "1.1배속 + 줌", sfx: "SFX 2: pop" },
                { scene: "장면 3 (반응 공개)", time: "5.5 ~ 9.0초", srcTime: "02:22 ~ 02:25", action: "뿌리고 나가면 다들 어디 거냐고 물어봐요. 오늘 처음 공개해요.", edit: "1.1배속 + 손동작", sfx: "SFX 3: impact" },
                { scene: "장면 4 (제품 정체)", time: "9.0 ~ 12.5초", srcTime: "02:26 ~ 02:28", action: "바로 산타마리아노벨라 프리지아 향수예요.", edit: "1.0배속 + 인서트", sfx: "SFX 4: sparkle" },
                { scene: "장면 5 (재구매 증거)", time: "12.5 ~ 16.0초", srcTime: "02:28 ~ 02:29", action: "세 병째 쓰고 있어요.", edit: "1.1배속 + 분사컷", sfx: "SFX 5: ding" },
                { scene: "장면 6 (루프 엔딩)", time: "16.0 ~ 18.5초", srcTime: "02:15 ~ 02:16", action: "10년째 비밀로 간직한 이유가 납득되는 미소", edit: "루프 연결", sfx: "-" }
              ]
            },
            B: {
              name: "문제·해결형 (B안)",
              duration: "18.2초",
              durNum: 18.2,
              top1: "흔하지 않은 향기",
              top2: "손예진 정착템",
              tts1: "남들과 겹치지 않는 인생 향수를 찾는다면?",
              tts2: "손예진이 10년째 정착한 이유가 확실하네요.",
              sfx: "0.0초: whoosh | 3.0초: impact | 6.5초: sparkle | 10.5초: pop | 14.0초: ding",
              scenes: [
                { scene: "장면 1 (문제 제기)", time: "0.0 ~ 3.0초", srcTime: "02:15 ~ 02:18", action: "10년 동안 하나만 고집해 온 비밀 향수", edit: "1.1배속 + 질문자막", sfx: "SFX 1: whoosh" },
                { scene: "장면 2 (공감 반응)", time: "3.0 ~ 6.5초", srcTime: "02:22 ~ 02:25", action: "뿌리고 나가면 다들 어디 거냐고 물어보는 반응", edit: "1.1배속 + 리액션", sfx: "SFX 2: impact" },
                { scene: "장면 3 (해결 정체)", time: "6.5 ~ 10.5초", srcTime: "02:26 ~ 02:28", action: "산타마리아노벨라 프리지아 정체 공개", edit: "1.0배속 + 라벨줌", sfx: "SFX 3: sparkle" },
                { scene: "장면 4 (재구매 증거)", time: "10.5 ~ 14.5초", srcTime: "02:28 ~ 02:29", action: "이미 세 병째 비우고 있는 실제 재구매 증거", edit: "1.1배속 + 폰트바운스", sfx: "SFX 4: pop" },
                { scene: "장면 5 (결론 루프)", time: "14.5 ~ 18.2초", srcTime: "02:19 ~ 02:22", action: "스태프에게도 안 알려주던 원픽 향수", edit: "마무리 루프", sfx: "SFX 5: ding" }
              ]
            },
            C: {
              name: "인물·루틴·신뢰형 (C안)",
              duration: "18.0초",
              durNum: 18.0,
              top1: "배우 손예진의 루틴",
              top2: "10년 찐 애정템",
              tts1: "톱배우가 10년 동안 한 가지만 썼다면?",
              tts2: "은은하고 고급스러운 분위기의 비결입니다.",
              sfx: "0.0초: whoosh | 2.5초: pop | 6.5초: impact | 10.5초: sparkle | 13.5초: ding",
              scenes: [
                { scene: "장면 1 (루틴 공개)", time: "0.0 ~ 2.5초", srcTime: "02:28 ~ 02:29", action: "세 병째 쓰고 있는 손예진의 찐 애정템", edit: "1.1배속 + 분사컷", sfx: "SFX 1: whoosh" },
                { scene: "장면 2 (비밀 사연)", time: "2.5 ~ 6.5초", srcTime: "02:15 ~ 02:18", action: "10년 동안 아무에게도 안 알려준 비밀", edit: "1.1배속 + 대화자막", sfx: "SFX 2: pop" },
                { scene: "장면 3 (주변 반응)", time: "6.5 ~ 10.5초", srcTime: "02:19 ~ 02:22", action: "스태프들도 매일 물어보던 그 향기", edit: "1.1배속 + 제3자강조", sfx: "SFX 3: impact" },
                { scene: "장면 4 (제품 공개)", time: "10.5 ~ 14.5초", srcTime: "02:26 ~ 02:28", action: "산타마리아노벨라 프리지아 향수", edit: "1.0배속 + 룩북연출", sfx: "SFX 4: sparkle" },
                { scene: "장면 5 (엔딩 마무리)", time: "14.5 ~ 18.0초", srcTime: "02:22 ~ 02:25", action: "오늘 처음 공개한 손예진의 시그니처 향", edit: "1.1배속 + 엔딩루프", sfx: "SFX 5: ding" }
              ]
            }
          },
          ytTitles: [
            "손예진이 10년 동안 아무한테도 안 알려준 비밀 향수 정보",
            "스태프들도 매일 물어봤는데 절대 안 알려줬다는 손예진 향수 ㄷㄷ",
            "10년째 세 병 비웠으면 말 다 했죠.. 손예진 찐 애정템 공개",
            "뿌리고 나가면 다들 어디 거냐고 물어본다는 손예진 원픽 향수",
            "[손예진 쇼츠] 10년 동안 숨겨온 가방 속 비밀 아이템의 정체"
          ],
          coupangLink: `https://link.coupang.com/a/${cId}_프리지아향수`
        },
        {
          id: "PROD_02",
          product: "엑스트라 립 틴트 (립밤)",
          brand: "바비브라운",
          score: 89,
          grade: "S (즉시 제작)",
          viralTypePrimary: "[A2] N병·N개 소진형",
          viralTypeSecondary: "[A4] 없으면 안 되는형",
          hookQuote: "건조할 때마다 바르면 바로 촉촉해져서 5통째 비운 제품이에요.",
          transcriptText: "[05:10.0 ~ 05:13.5] 그리고 이건 제가 가방에 매일 넣고 다니는 립밤이에요.\n[05:14.0 ~ 05:17.0] 건조할 때마다 바르면 바로 촉촉해져서 5통째 비운 제품이에요.\n[05:17.5 ~ 05:20.5] 입술에 닿자마자 자연스럽게 생기가 돌아서 민낯에도 꼭 발라요.",
          variants: {
            A: {
              name: "궁금증·반전형 (A안)",
              duration: "18.0초",
              durNum: 18.0,
              top1: "가방 속 필수 립밤",
              top2: "손예진 5통 비움",
              tts1: "손예진이 5통이나 비운 립밤의 정체는?",
              tts2: "바르는 순간 생기가 도는 이유가 있습니다.",
              sfx: "0.0초: whoosh | 2.5초: pop | 5.5초: impact | 9.0초: sparkle | 12.0초: ding",
              scenes: [
                { scene: "장면 1 (최강 훅)", time: "0.0 ~ 3.0초", srcTime: "05:14 ~ 05:17", action: "5통째 비운 제품이라고 공개하는 장면", edit: "1.1배속 + 크롭", sfx: "SFX 1: whoosh" },
                { scene: "장면 2 (일상 필수)", time: "3.0 ~ 6.5초", srcTime: "05:10 ~ 05:13", action: "가방에 매일 넣고 다닌다는 애장 발언", edit: "1.1배속 + 줌", sfx: "SFX 2: pop" },
                { scene: "장면 3 (정체 공개)", time: "6.5 ~ 11.0초", srcTime: "05:17 ~ 05:20", action: "바비브라운 엑스트라 립 틴트 정체 공개", edit: "1.0배속 + 인서트", sfx: "SFX 3: sparkle" },
                { scene: "장면 4 (사용 효능)", time: "11.0 ~ 15.0초", srcTime: "05:14 ~ 05:17", action: "건조할 때마다 즉시 촉촉해지는 보습 효과", edit: "1.1배속 + 자막", sfx: "SFX 4: impact" },
                { scene: "장면 5 (루프 엔딩)", time: "15.0 ~ 18.0초", srcTime: "05:10 ~ 05:13", action: "민낯 필수템으로 추천하는 미소", edit: "루프 연결", sfx: "SFX 5: ding" }
              ]
            },
            B: {
              name: "문제·해결형 (B안)",
              duration: "18.2초",
              durNum: 18.2,
              top1: "입술 각질 고민 끝",
              top2: "손예진 생기 립밤",
              tts1: "입술 건조함과 칙칙함이 고민이라면?",
              tts2: "손예진의 5통 찐후기가 증명하네요.",
              sfx: "0.0초: whoosh | 3.0초: impact | 6.5초: sparkle | 10.5초: pop | 14.0초: ding",
              scenes: [
                { scene: "장면 1 (고민 공감)", time: "0.0 ~ 3.0초", srcTime: "05:14 ~ 05:17", action: "건조할 때마다 즉각 해결하는 립밤", edit: "1.1배속 + 자막", sfx: "SFX 1: whoosh" },
                { scene: "장면 2 (정착 이유)", time: "3.0 ~ 7.0초", srcTime: "05:10 ~ 05:13", action: "매일 가방에 넣고 다니는 찐템", edit: "1.1배속 + 리액션", sfx: "SFX 2: impact" },
                { scene: "장면 3 (제품 공개)", time: "7.0 ~ 11.5초", srcTime: "05:17 ~ 05:20", action: "바비브라운 립 틴트 정체 공개", edit: "1.0배속 + 제품줌", sfx: "SFX 3: sparkle" },
                { scene: "장면 4 (재구매 증거)", time: "11.5 ~ 15.0초", srcTime: "05:14 ~ 05:17", action: "벌써 5통째 비웠다는 확실한 사용 증거", edit: "1.1배속 + 바운스", sfx: "SFX 4: pop" },
                { scene: "장면 5 (결론 루프)", time: "15.0 ~ 18.2초", srcTime: "05:17 ~ 05:20", action: "민낯에도 자연스러운 립케어 완료", edit: "마무리 루프", sfx: "SFX 5: ding" }
              ]
            },
            C: {
              name: "인물·루틴·신뢰형 (C안)",
              duration: "18.0초",
              durNum: 18.0,
              top1: "손예진 민낯 비결",
              top2: "가방 속 5통 립밤",
              tts1: "손예진의 파우치 속 1위 필수템은?",
              tts2: "촉촉함과 자연스러운 혈색의 정답입니다.",
              sfx: "0.0초: whoosh | 2.5초: pop | 6.5초: impact | 10.5초: sparkle | 13.5초: ding",
              scenes: [
                { scene: "장면 1 (루틴 공개)", time: "0.0 ~ 2.5초", srcTime: "05:10 ~ 05:13", action: "손예진이 매일 챙기는 립밤 루틴", edit: "1.1배속 + 클로즈업", sfx: "SFX 1: whoosh" },
                { scene: "장면 2 (애용 사연)", time: "2.5 ~ 6.5초", srcTime: "05:14 ~ 05:17", action: "5통째 비울 만큼 없으면 안 되는 아이템", edit: "1.1배속 + 텍스트줌", sfx: "SFX 2: pop" },
                { scene: "장면 3 (발색 반응)", time: "6.5 ~ 10.5초", srcTime: "05:17 ~ 05:20", action: "자연스럽게 차오르는 입술 생기", edit: "1.1배속 + 발색컷", sfx: "SFX 3: impact" },
                { scene: "장면 4 (제품 공개)", time: "10.5 ~ 14.5초", srcTime: "05:10 ~ 05:13", action: "바비브라운 엑스트라 립 틴트", edit: "1.0배속 + 인서트", sfx: "SFX 4: sparkle" },
                { scene: "장면 5 (엔딩 루프)", time: "14.5 ~ 18.0초", srcTime: "05:17 ~ 05:20", action: "손예진 표정 루프", edit: "엔딩 루프", sfx: "SFX 5: ding" }
              ]
            }
          },
          ytTitles: [
            "손예진이 5통째 비웠다는 가방 속 찐 립밤 정보",
            "민낯에도 자연스러운 혈색! 손예진 원픽 립틴트",
            "건조할 때마다 바르는 손예진 5통 립밤 ㄷㄷ",
            "[손예진 쇼츠] 파우치 속 없으면 불안한 립밤 공개",
            "손예진이 매일 챙겨 바르는 립밤의 정체"
          ],
          coupangLink: `https://link.coupang.com/a/${cId}_립밤`
        }
      ]
    });

  } catch (err) {
    return res.status(500).json({ error: err.message });
  }
}