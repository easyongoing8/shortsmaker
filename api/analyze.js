// Vercel Serverless API Route: /api/analyze
export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method Not Allowed' });

  try {
    const { videoUrl, celebrity, productHint, transcript, apiKey, coupangId } = req.body;
    const geminiKey = apiKey || process.env.GEMINI_API_KEY;

    let videoId = "";
    const ytMatch = videoUrl ? videoUrl.match(/(?:v=|\/)([0-9A-Za-z_-]{11})/) : null;
    if (ytMatch) videoId = ytMatch;

    if (geminiKey) {
      const prompt = `
너는 한국 시장용 연예인 추천템 쇼핑 쇼츠 제작 최고 전문가다.
유튜브 링크: ${videoUrl || "없음"} (Video ID: ${videoId})
연예인 힌트: ${celebrity || "자동 탐지"}
제품 힌트: ${productHint || "자동 탐지"}
대본 내용: ${transcript || ""}

규칙:
1. 연예인이 실제 사용/추천한 찐 애정템 1개를 선정하고 100점 만점으로 채점해라.
2. 20초 이하(1.1배속 적용 기준 17~19초) 쇼츠 편집 타임라인(A:궁금증반전형, B:문제해결형, C:인물루틴형)을 작성해라.
3. TTS 내레이션 2개(각 2초 이내), 효과음 5개, 상단 2줄 자막(각 10자 이내), 유튜브 제목 5개를 작성해라.

반드시 아래 JSON 형식으로만 출력해라:
{
  "celebrity": "연예인 이름",
  "product": "제품명",
  "brand": "브랜드명",
  "score": 96,
  "grade": "S (즉시 제작)",
  "viralTypePrimary": "[A2] N병·N개 소진형",
  "viralTypeSecondary": "[A1] N년 사용형",
  "hookQuote": "가장 강한 3초 훅 대사",
  "top1": "상단 1줄 자막 (10자 이내)",
  "top2": "상단 2줄 자막 (10자 이내)",
  "tts1": "TTS 1 내레이션 (02.8초 배치)",
  "tts2": "TTS 2 내레이션 (12.5초 배치)",
  "scenes": [
    {"scene": "장면 1 (최강 훅)", "time": "0.0 ~ 2.8초", "srcTime": "02:19 ~ 02:22", "action": "대사 내용", "edit": "1.1배속 + 크롭", "sfx": "SFX 1: whoosh (전환)"},
    {"scene": "장면 2 (의문 제기)", "time": "2.8 ~ 5.5초", "srcTime": "02:15 ~ 02:18", "action": "비밀 발언", "edit": "1.1배속 + 줌", "sfx": "SFX 2: pop (질문)"},
    {"scene": "장면 3 (반응 공개)", "time": "5.5 ~ 9.0초", "srcTime": "02:22 ~ 02:25", "action": "주변 반응", "edit": "1.1배속 + 손동작", "sfx": "SFX 3: impact (강조)"},
    {"scene": "장면 4 (제품 정체)", "time": "9.0 ~ 12.5초", "srcTime": "02:26 ~ 02:28", "action": "제품 공개", "edit": "1.0배속 + 인서트", "sfx": "SFX 4: sparkle (공개)"},
    {"scene": "장면 5 (재구매 증거)", "time": "12.5 ~ 16.0초", "srcTime": "02:28 ~ 02:29", "action": "실제 분사", "edit": "1.1배속 + 분사컷", "sfx": "SFX 5: ding (신뢰)"},
    {"scene": "장면 6 (루프 엔딩)", "time": "16.0 ~ 18.5초", "srcTime": "02:15 ~ 02:16", "action": "엔딩 미소", "edit": "루프 연결", "sfx": "-"}
  ],
  "ytTitles": [
    "유튜브 업로드 제목 1",
    "유튜브 업로드 제목 2",
    "유튜브 업로드 제목 3",
    "유튜브 업로드 제목 4",
    "유튜브 업로드 제목 5"
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
        const cId = coupangId || "AF893214";
        resJson.coupangLink = `https://link.coupang.com/a/${cId}_${encodeURIComponent(resJson.product.replace(/\s+/g,''))}`;
        return res.status(200).json(resJson);
      }
    }

    // 기본 안전 응답
    const finalCeleb = celebrity || "손예진";
    const finalProduct = productHint || "프리지아 오 드 코롱";
    const cId = coupangId || "AF893214";
    return res.status(200).json({
      celebrity: finalCeleb,
      product: finalProduct,
      brand: "산타마리아노벨라",
      score: 96,
      grade: "S (즉시 제작)",
      viralTypePrimary: "[A2] N병·N개 소진형",
      viralTypeSecondary: "[A1] N년 사용형",
      hookQuote: "제가 진짜 10년째 아무한테도 안 알려준 비밀 향수가 있거든요.",
      top1: "10년째 비밀 유지",
      top2: `${finalCeleb} 원픽 향수`,
      tts1: `대체 뭐길래 ${finalCeleb}이 10년 동안 숨겼을까요?`,
      tts2: "세 병째 비웠다면 설명 끝났습니다.",
      scenes: [
        { scene: "장면 1 (최강 훅)", time: "0.0 ~ 2.8초", srcTime: "02:19 ~ 02:22", action: "스태프들도 매일 뭐 뿌렸냐고 물어보는데 절대 안 알려줬어요.", edit: "1.1배속 + 크롭", sfx: "SFX 1: whoosh" },
        { scene: "장면 2 (의문)", time: "2.8 ~ 5.5초", srcTime: "02:15 ~ 02:18", action: "제가 진짜 10년째 아무한테도 안 알려준 비밀 향수거든요.", edit: "1.1배속 + 줌", sfx: "SFX 2: pop" },
        { scene: "장면 3 (반응)", time: "5.5 ~ 9.0초", srcTime: "02:22 ~ 02:25", action: "뿌리고 나가면 다들 어디 거냐고 물어봐요. 오늘 처음 공개해요.", edit: "1.1배속 + 손동작", sfx: "SFX 3: impact" },
        { scene: "장면 4 (공개)", time: "9.0 ~ 12.5초", srcTime: "02:26 ~ 02:28", action: "바로 산타마리아노벨라 프리지아 향수예요.", edit: "1.0배속 + 인서트", sfx: "SFX 4: sparkle" },
        { scene: "장면 5 (증거)", time: "12.5 ~ 16.0초", srcTime: "02:28 ~ 02:29", action: "세 병째 쓰고 있어요.", edit: "1.1배속 + 분사컷", sfx: "SFX 5: ding" },
        { scene: "장면 6 (루프)", time: "16.0 ~ 18.5초", srcTime: "02:15 ~ 02:16", action: "10년째 비밀로 간직한 이유가 납득되는 미소", edit: "루프 연결", sfx: "-" }
      ],
      ytTitles: [
        `${finalCeleb}이 10년 동안 아무한테도 안 알려준 비밀 ${finalProduct} 정보`,
        `스태프들도 매일 물어봤는데 절대 안 알려줬다는 ${finalCeleb} ${finalProduct} ㄷㄷ`,
        `10년째 세 병 비웠으면 말 다 했죠.. ${finalCeleb} 찐 인생템 공개`,
        `뿌리고 나가면 다들 어디 거냐고 물어본다는 ${finalCeleb} 원픽`,
        `[${finalCeleb} 쇼츠] 10년 동안 숨겨온 가방 속 비밀의 정체`
      ],
      coupangLink: `https://link.coupang.com/a/${cId}_${encodeURIComponent(finalProduct.replace(/\s+/g,''))}`
    });
  } catch (err) {
    return res.status(500).json({ error: err.message });
  }
}