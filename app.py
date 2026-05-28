import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import streamlit as st


APP_NAME = "SIGVARIS Prompt Builder"
DEFAULT_MODEL = "gpt-4.1-mini"


PRODUCT_BLOCKS = {
    "무릎형": "종아리부터 무릎 아래까지 탄탄하게 잡아주는 클래식 무릎형 압박스타킹. 종아리 라인과 발목 압박 설계가 잘 보이도록 표현한다.",
    "허벅지형": "허벅지까지 올라오는 실루엣이 자연스럽게 표현된 허벅지형 압박스타킹. 허벅지 마감선과 전체 다리 라인이 자연스럽고 고급스럽게 보이도록 한다.",
    "팬티스타킹형": "허리부터 발끝까지 연결되는 팬티스타킹형 압박스타킹. 전체적인 핏과 다리 라인이 자연스럽고 균형 있게 보이도록 표현한다.",
    "임산부용": "임산부도 편안하게 착용할 수 있는 압박스타킹 콘셉트. 편안함, 안정감, 부드러운 일상 무드를 반영한다.",
}

PURPOSE_BLOCKS = {
    "패션 화보": "프리미엄 패션 에디토리얼 화보처럼 연출하되, 제품이 가장 돋보이게 한다.",
    "상세페이지 첫 화면": "모바일 상세페이지 첫 화면에서 3초 안에 제품 신뢰감과 핵심 포인트가 전달되도록 구성한다.",
    "광고 배너": "클릭과 구매 전환을 고려한 광고 비주얼로 구성한다. 핵심 제품과 혜택 전달력이 좋아야 한다.",
    "SNS 콘텐츠": "모바일 화면에서 시선을 빠르게 끌 수 있게 감도 있고 선명한 비주얼로 구성한다.",
    "리뷰/후기형": "실제 착용 후기 같은 신뢰감 있는 무드로 구성하되, 지나치게 꾸민 느낌은 줄인다.",
}

SCENE_BLOCKS = {
    "고급 리조트 라운지": "고급 리조트 라운지 인테리어 배경, 조용하고 럭셔리한 분위기, 따뜻한 자연광이 은은하게 들어오는 공간.",
    "여름 호텔 풀사이드": "여름의 시원함이 느껴지는 고급 호텔 풀사이드 또는 서머 리조트 무드. 밝고 청량하지만 프리미엄한 분위기.",
    "조용한 병실/클리닉": "깔끔하고 밝은 병실 또는 클리닉 공간. 의료 신뢰감은 있으나 차갑지 않고 편안한 톤.",
    "오피스/데일리 라이프": "출근과 일상에 자연스럽게 녹아드는 깔끔한 오피스 또는 라이프스타일 공간.",
    "미니멀 스튜디오": "제품과 모델이 가장 잘 보이는 밝고 미니멀한 스튜디오. 군더더기 없는 상업용 촬영 무드.",
}

MODEL_BLOCKS = {
    "한국인 여성": "우아하고 세련된 한국인 여성 모델.",
    "한국인 남성": "깔끔하고 현실적인 한국인 남성 모델.",
    "부부/커플": "자연스럽고 현실적인 분위기의 한국인 커플 모델.",
    "얼굴 비노출 모델": "얼굴은 거의 나오지 않거나 프레임 밖으로 두어 제품에 시선이 집중되게 한다.",
}

COMPOSITION_BLOCKS = {
    "전신": "모델 전신이 자연스럽게 보이는 구도.",
    "무릎 아래 중심": "무릎 아래부터 발끝까지 제품이 중심이 되는 구도.",
    "앉은 포즈": "자연스럽게 앉아 있는 포즈, 억지스럽지 않은 여성스럽고 세련된 자세.",
    "서있는 포즈": "자연스럽게 서 있는 포즈, 제품 라인이 잘 보이도록 정돈된 자세.",
    "다리 중심 클로즈업": "다리와 압박스타킹 텍스처가 잘 보이는 클로즈업 중심 구도.",
}

ASPECT_RATIOS = ["1:1", "4:5", "9:16", "16:9", "3:4", "4:3", "1414:1000", "1000:1414"]

DEFAULT_MOOD = "고급스럽고 조용한 럭셔리 무드, 여름의 시원함, 실사 화보 느낌"
DEFAULT_COLOR_TONE = "화이트, 베이지, 아이보리 중심의 밝고 프리미엄한 톤"
DEFAULT_MUST_HAVE = """제품 변형 금지
원단 질감 강조
실사 느낌
자연스러운 다리 비율
고급스럽고 상업용으로 완성도 높은 분위기"""
DEFAULT_MUST_AVOID = """과한 피부 보정
왜곡된 발가락
저해상도
싸보이는 분위기"""
DEFAULT_EXTRA_REQUEST = "제품이 가장 돋보이되, 전체 무드는 세련되고 AI 느낌이 없었으면 좋겠다."


SYSTEM_PROMPT = """당신은 SIGVARIS 압박스타킹 전용 이미지 프롬프트 설계 전문가입니다.

역할:
- 사용자의 입력을 분석해 SIGVARIS 압박스타킹 이미지 제작에 최적화된 고품질 한국어 프롬프트를 생성한다.
- 상업용 광고, 상세페이지, SNS, 화보, 후기형 콘텐츠에 맞게 실무적으로 작성한다.
- 제품 형태 정확성, 발끝 디테일, 원단 질감, 실사감, 프리미엄 무드를 최우선으로 한다.

반드시 강하게 반영할 품질 규칙:
1. 제품 변형 금지.
2. AI 느낌 금지.
3. 다리/발/발가락/손가락 해부학적 왜곡 금지.
4. 압박스타킹 원단 질감과 압박감 있는 밀착 표현 강조.
5. 실제 카메라로 촬영한 듯한 포토리얼 결과를 지향.
6. 상업용으로 바로 사용할 수 있을 정도의 깔끔한 완성도.
7. 의료용/압박 제품 특성상 과장된 의학적 표현은 지양하고, 신뢰감과 프리미엄 무드를 강조.

발끝 디테일 관련 핵심 규칙(오픈토 옵션이 켜져 있으면 반드시 반영):
- 흰색 스타킹 발부분에 오픈토 구조.
- 앞부분에 검정색의 둥근 밴드/테두리 마감.
- 자연스럽게 보이는 발가락.
- 신발, 슬리퍼, 샌들, 토삭스처럼 보이면 안 됨.
- 발끝 개구부의 스타킹 원단 경계가 자연스럽게 보여야 함.

반드시 JSON만 반환하라. 마크다운/코드블록 금지.
스키마:
{
  "summary": "요약",
  "recommended_aspect_ratio": "추천 비율",
  "main_prompt": "메인 프롬프트",
  "negative_prompt": "네거티브 프롬프트",
  "edit_prompt": "참고 이미지 편집용 프롬프트",
  "variants": [
    {"name": "A", "purpose": "", "prompt": ""},
    {"name": "B", "purpose": "", "prompt": ""},
    {"name": "C", "purpose": "", "prompt": ""}
  ],
  "must_check": ["체크포인트1", "체크포인트2", "체크포인트3"],
  "input_summary": {
    "product_type": "",
    "purpose": "",
    "scene": "",
    "model": "",
    "toe_style": ""
  }
}"""


def load_dotenv_if_exists() -> None:
    """Small .env loader so the app can use environment values without extra dependencies."""
    env_path = Path(".env")
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def get_config_value(key: str, default: str = "") -> str:
    env_value = os.getenv(key)
    if env_value:
        return env_value

    try:
        secret_value = st.secrets.get(key)
    except Exception:
        secret_value = None

    if secret_value:
        return str(secret_value)
    return default


def split_lines(text: str) -> List[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


def dedupe(items: List[str]) -> List[str]:
    seen = set()
    result = []
    for item in items:
        normalized = re.sub(r"\s+", " ", item.strip())
        if normalized and normalized not in seen:
            seen.add(normalized)
            result.append(normalized)
    return result


def build_quality_rules(open_toe: bool) -> List[str]:
    rules = [
        "초고해상도 포토리얼 이미지",
        "실제 촬영한 패션 에디토리얼 또는 상업 광고 사진 느낌",
        "85mm 렌즈 촬영 느낌, 얕은 심도, 자연스러운 아웃포커싱",
        "피부결, 원단 조직감, 압박스타킹 텍스처까지 사실적으로 표현",
        "자연스러운 인체 비율과 현실적인 관절 표현",
        "상업용으로 바로 사용할 수 있는 깔끔하고 고급스러운 완성도",
        "제품 변형 금지",
        "AI 느낌 금지",
    ]

    if open_toe:
        rules.extend(
            [
                "발끝은 흰색 오픈토 의료용 압박스타킹 구조",
                "검정색 둥근 밴드 마감",
                "자연스럽게 보이는 발가락",
                "신발처럼 보이지 않는 스타킹 원단 구조",
            ]
        )

    return rules


def build_negative_rules(open_toe: bool, must_avoid: str) -> List[str]:
    rules = [
        "AI 느낌",
        "플라스틱 같은 피부",
        "비현실적인 다리 길이",
        "왜곡된 무릎",
        "이상한 손가락",
        "부자연스러운 발 형태",
        "제품 형태 변형",
        "저해상도",
        "과한 광택",
        "흐릿한 제품 표현",
        "과장된 포즈",
    ]

    if open_toe:
        rules.extend(
            [
                "신발처럼 보이는 발끝",
                "슬리퍼/샌들 같은 형태",
                "토삭스처럼 분리된 발가락",
                "검정 밴드 누락",
                "오픈토 구조 누락",
            ]
        )

    rules.extend(split_lines(must_avoid))
    return dedupe(rules)


def build_text_rule(text_in_image: bool, text_content: str) -> str:
    if text_in_image:
        cleaned = text_content.strip()
        if cleaned:
            return f'이미지 안에 문구 "{cleaned}"를 자연스럽게 포함하되, 오탈자 없이 읽기 쉬운 광고 타이포그래피로 배치한다.'
        return "이미지 안에 짧고 읽기 쉬운 광고 문구를 포함하되, 오탈자 없이 자연스럽게 배치한다."
    return "이미지 내부에는 문구나 타이포그래피를 넣지 않는다. 필요한 문구는 후편집에서 올릴 수 있게 깨끗한 여백을 남긴다."


def build_payload(raw_input: Dict[str, Any]) -> Dict[str, Any]:
    product_type = raw_input["product_type"]
    purpose = raw_input["purpose"]
    scene = raw_input["scene"]
    model = raw_input["model"]
    composition = raw_input["composition"]
    open_toe = raw_input["open_toe"]

    return {
        "input": raw_input,
        "blocks": {
            "product": PRODUCT_BLOCKS[product_type],
            "purpose": PURPOSE_BLOCKS[purpose],
            "scene": SCENE_BLOCKS[scene],
            "model": MODEL_BLOCKS[model],
            "composition": COMPOSITION_BLOCKS[composition],
        },
        "quality_rules": build_quality_rules(open_toe),
        "negative_rules": build_negative_rules(open_toe, raw_input["must_avoid"]),
        "text_rule": build_text_rule(raw_input["text_in_image"], raw_input["text_content"]),
    }


def build_main_prompt(payload: Dict[str, Any]) -> str:
    user_input = payload["input"]
    blocks = payload["blocks"]
    must_have = split_lines(user_input["must_have"])
    quality_rules = payload["quality_rules"]

    parts = [
        "초고해상도 포토리얼 라이프스타일 사진.",
        "실제 촬영한 패션 에디토리얼 또는 상업 광고 사진 느낌.",
        blocks["purpose"],
        blocks["product"],
        blocks["scene"],
        blocks["model"],
        blocks["composition"],
        f"무드와 분위기: {user_input['mood']}.",
        f"컬러 톤: {user_input['color_tone']}.",
        "밝고 자연스러운 조명, 실제 카메라 촬영 같은 원근감과 그림자 표현.",
        "다리와 스타킹이 중심이 되는 구도.",
        f"반드시 포함/강조할 요소: {', '.join(must_have)}.",
        f"핵심 품질 규칙: {', '.join(quality_rules)}.",
        payload["text_rule"],
        f"추가 요청: {user_input['extra_request'].strip()}",
        f"이미지 비율: {user_input['aspect_ratio']}.",
    ]
    return "\n".join(part for part in parts if part.strip())


def build_edit_prompt(payload: Dict[str, Any]) -> str:
    user_input = payload["input"]
    product_type = user_input["product_type"]
    product_block = payload["blocks"]["product"]
    parts = [
        "업로드한 참고 이미지를 기반으로 SIGVARIS 압박스타킹 이미지로 자연스럽게 보정한다.",
        f"제품 타입은 {product_type}이며, {product_block}",
        "기존 구도와 분위기를 최대한 살리면서 제품 형태와 원단 질감을 정확하게 유지한다.",
        "다리 비율, 발, 발가락, 손가락 왜곡을 자연스럽게 수정한다.",
    ]

    if user_input["open_toe"]:
        parts.append(
            "발끝은 흰색 오픈토 구조, 검정색 둥근 밴드 마감, 자연스럽게 보이는 발가락, 신발처럼 보이지 않는 스타킹 발부분으로 만든다."
        )

    parts.append("AI 느낌이 나지 않게, 실사 화보처럼 정리한다.")
    return "\n".join(parts)


def fallback_generate(payload: Dict[str, Any]) -> Dict[str, Any]:
    user_input = payload["input"]
    main_prompt = build_main_prompt(payload)
    negative_prompt = ", ".join(payload["negative_rules"])
    edit_prompt = build_edit_prompt(payload)

    variants = [
        {
            "name": "A",
            "purpose": "프리미엄 화보형",
            "prompt": f"{main_prompt}\n여백과 고급 무드를 충분히 살린 프리미엄 화보형으로 연출한다.",
        },
        {
            "name": "B",
            "purpose": "전환형 광고 비주얼",
            "prompt": f"{main_prompt}\n제품이 한눈에 잘 보이게 하며, 모바일 광고에서 시선이 바로 꽂히도록 대비와 시각 집중도를 높인다.",
        },
        {
            "name": "C",
            "purpose": "상세페이지/제품 설명형",
            "prompt": f"{main_prompt}\n제품 특징이 명확히 전달되도록 제품 노출도와 설명 친화적인 구성을 우선한다.",
        },
    ]

    must_check = [
        "제품 길이/형태가 실제 의도한 타입(무릎형/허벅지형/팬티스타킹형)과 맞는지",
        "발끝 디테일이 신발처럼 보이지 않고 자연스러운 스타킹 구조인지",
        "다리 비율, 무릎, 발목, 발가락에 왜곡이 없는지",
        "원단 질감과 압박감 있는 핏이 잘 보이는지",
        "AI 느낌 없이 실제 촬영한 사진처럼 보이는지",
    ]

    toe_style = "오픈토 + 검정색 둥근 밴드 마감" if user_input["open_toe"] else "기본 발끝 표현"
    summary = (
        f"{user_input['scene']} 배경에서 {user_input['model']} 모델이 착용한 "
        f"SIGVARIS {user_input['product_type']} 압박스타킹을 {user_input['purpose']} 목적에 맞게 표현합니다."
    )

    return {
        "summary": summary,
        "recommended_aspect_ratio": user_input["aspect_ratio"],
        "main_prompt": main_prompt,
        "negative_prompt": negative_prompt,
        "edit_prompt": edit_prompt,
        "variants": variants,
        "must_check": must_check,
        "input_summary": {
            "product_type": user_input["product_type"],
            "purpose": user_input["purpose"],
            "scene": user_input["scene"],
            "model": user_input["model"],
            "toe_style": toe_style,
        },
    }


def extract_response_text(response: Any) -> str:
    output_text = getattr(response, "output_text", None)
    if output_text:
        return output_text

    try:
        data = response.model_dump()
    except AttributeError:
        try:
            data = json.loads(response.model_dump_json())
        except Exception:
            data = response

    if isinstance(data, dict):
        direct_text = data.get("output_text")
        if isinstance(direct_text, str) and direct_text.strip():
            return direct_text

        collected = []
        for output_item in data.get("output", []) or []:
            for content_item in output_item.get("content", []) or []:
                text = content_item.get("text")
                if isinstance(text, str) and text.strip():
                    collected.append(text)
        if collected:
            return "\n".join(collected)

    collected_recursive: List[str] = []

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            text = node.get("text")
            if isinstance(text, str) and text.strip():
                collected_recursive.append(text)
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(data)
    if collected_recursive:
        return "\n".join(dedupe(collected_recursive))

    return str(response)


def strip_json_code_block(raw_text: str) -> str:
    text = raw_text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)

    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start : end + 1]
    return text


def normalize_result(result: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
    fallback = fallback_generate(payload)
    normalized = {**fallback, **result}

    if not isinstance(normalized.get("variants"), list) or len(normalized["variants"]) < 3:
        normalized["variants"] = fallback["variants"]
    else:
        normalized["variants"] = normalized["variants"][:3]

    if not isinstance(normalized.get("must_check"), list) or not normalized["must_check"]:
        normalized["must_check"] = fallback["must_check"]

    if not isinstance(normalized.get("input_summary"), dict):
        normalized["input_summary"] = fallback["input_summary"]

    for key in ["summary", "recommended_aspect_ratio", "main_prompt", "negative_prompt", "edit_prompt"]:
        if not isinstance(normalized.get(key), str) or not normalized[key].strip():
            normalized[key] = fallback[key]

    return normalized


def generate_with_openai(payload: Dict[str, Any], api_key: str, model: str) -> Dict[str, Any]:
    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    response = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    "아래 입력값과 내부 규칙을 바탕으로 SIGVARIS 전용 이미지 프롬프트 결과를 생성하라.\n"
                    "반드시 지정된 JSON 스키마만 반환하라.\n\n"
                    f"{json.dumps(payload, ensure_ascii=False, indent=2)}"
                ),
            },
        ],
    )

    raw_text = extract_response_text(response)
    parsed = json.loads(strip_json_code_block(raw_text))
    return normalize_result(parsed, payload)


def create_download_payload(raw_input: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "app": APP_NAME,
        "input": raw_input,
        "output": result,
    }


def init_session_state() -> None:
    if "result" not in st.session_state:
        st.session_state.result = None
    if "last_input" not in st.session_state:
        st.session_state.last_input = None
    if "result_source" not in st.session_state:
        st.session_state.result_source = None
    if "fallback_reason" not in st.session_state:
        st.session_state.fallback_reason = None


def inject_style() -> None:
    st.markdown(
        """
        <style>
        .main .block-container {
            padding-top: 2.2rem;
            padding-bottom: 2.5rem;
            max-width: 1440px;
        }
        h1 {
            letter-spacing: 0;
        }
        section[data-testid="stSidebar"] {
            background: #f7f8fa;
            border-right: 1px solid #e5e7eb;
        }
        div[data-testid="stMetric"] {
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 14px 16px;
        }
        div[data-testid="stTextInput"] input,
        div[data-testid="stTextArea"] textarea,
        div[data-testid="stSelectbox"] div {
            border-radius: 8px;
        }
        .stButton > button,
        .stDownloadButton > button {
            border-radius: 8px;
            font-weight: 700;
        }
        .tips-box {
            border-top: 1px solid #e5e7eb;
            margin-top: 1.5rem;
            padding-top: 1rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> Dict[str, str]:
    env_api_key = get_config_value("OPENAI_API_KEY", "")
    env_model = get_config_value("OPENAI_MODEL", DEFAULT_MODEL)

    with st.sidebar:
        st.header("생성 설정")
        mode = st.radio(
            "생성 모드",
            ["OpenAI API 사용", "기본 템플릿 사용"],
            index=0,
        )
        api_key = st.text_input(
            "OpenAI API Key",
            value=env_api_key,
            type="password",
            placeholder="sk-...",
            help="입력하지 않으면 기본 템플릿 fallback 모드로 생성됩니다.",
        )
        model = st.text_input(
            "모델명",
            value=env_model or DEFAULT_MODEL,
            help="예: gpt-4.1-mini",
        )

        st.divider()
        st.subheader("기본 반영 규칙")
        st.markdown(
            """
            - SIGVARIS 제품이 중심
            - 제품 변형 금지
            - 실사 화보 퀄리티 지향
            - 발끝 디테일(오픈토 + 검정 밴드) 반영 가능
            - 다리/발 왜곡 최소화
            """
        )

    return {"mode": mode, "api_key": api_key.strip(), "model": model.strip() or DEFAULT_MODEL}


def render_input_panel() -> Dict[str, Any]:
    st.subheader("입력 설정")
    product_type = st.selectbox("제품 타입", list(PRODUCT_BLOCKS.keys()), index=0)
    purpose = st.selectbox("사용 목적", list(PURPOSE_BLOCKS.keys()), index=0)
    scene = st.selectbox("배경/씬", list(SCENE_BLOCKS.keys()), index=0)
    model = st.selectbox("모델 타입", list(MODEL_BLOCKS.keys()), index=0)
    composition = st.selectbox("구도", list(COMPOSITION_BLOCKS.keys()), index=0)
    aspect_ratio = st.selectbox("비율", ASPECT_RATIOS, index=0)
    mood = st.text_input("무드 / 분위기", value=DEFAULT_MOOD)
    color_tone = st.text_input("컬러 톤", value=DEFAULT_COLOR_TONE)
    open_toe = st.checkbox("오픈토 발끝 디테일 사용", value=True)
    text_in_image = st.checkbox("이미지 안에 문구 포함", value=False)
    text_content = st.text_area(
        "이미지에 넣을 문구",
        value="",
        height=88,
        disabled=not text_in_image,
        placeholder="예: 하루 종일 편안한 프리미엄 압박",
    )
    must_have = st.text_area("반드시 포함/강조할 요소", value=DEFAULT_MUST_HAVE, height=140)
    must_avoid = st.text_area("절대 피할 요소", value=DEFAULT_MUST_AVOID, height=120)
    extra_request = st.text_area("추가 요청", value=DEFAULT_EXTRA_REQUEST, height=110)

    return {
        "product_type": product_type,
        "purpose": purpose,
        "scene": scene,
        "model": model,
        "composition": composition,
        "aspect_ratio": aspect_ratio,
        "mood": mood,
        "color_tone": color_tone,
        "text_in_image": text_in_image,
        "text_content": text_content if text_in_image else "",
        "open_toe": open_toe,
        "must_have": must_have,
        "must_avoid": must_avoid,
        "extra_request": extra_request,
    }


def handle_generation(raw_input: Dict[str, Any], settings: Dict[str, str]) -> None:
    payload = build_payload(raw_input)
    mode = settings["mode"]
    api_key = settings["api_key"]
    model = settings["model"]

    with st.spinner("SIGVARIS 전용 프롬프트를 생성하는 중입니다..."):
        if mode == "OpenAI API 사용" and api_key:
            try:
                result = generate_with_openai(payload, api_key=api_key, model=model)
                st.session_state.result_source = f"OpenAI API · {model}"
                st.session_state.fallback_reason = None
            except Exception as exc:
                result = fallback_generate(payload)
                st.session_state.result_source = "기본 템플릿 fallback"
                st.session_state.fallback_reason = f"OpenAI 호출 또는 JSON 파싱 중 문제가 발생해 fallback으로 생성했습니다: {exc}"
        else:
            result = fallback_generate(payload)
            st.session_state.result_source = "기본 템플릿 fallback"
            st.session_state.fallback_reason = (
                "API 키가 비어 있거나 기본 템플릿 사용 모드가 선택되어 fallback으로 생성했습니다."
            )

    st.session_state.result = result
    st.session_state.last_input = raw_input


def render_result_panel() -> None:
    st.subheader("생성 결과")

    result = st.session_state.result
    raw_input = st.session_state.last_input

    if not result:
        st.info("왼쪽에서 옵션을 설정하고 'SIGVARIS 프롬프트 생성' 버튼을 누르면 결과가 여기에 표시됩니다.")
        return

    st.success("SIGVARIS 이미지 프롬프트 생성이 완료되었습니다.")
    if st.session_state.result_source:
        st.caption(f"생성 방식: {st.session_state.result_source}")
    if st.session_state.fallback_reason:
        st.warning(st.session_state.fallback_reason)

    st.markdown("#### 요약")
    st.write(result.get("summary", ""))

    metric_cols = st.columns(3)
    input_summary = result.get("input_summary", {})
    metric_cols[0].metric("제품 타입", input_summary.get("product_type", raw_input.get("product_type", "-")))
    metric_cols[1].metric("목적", input_summary.get("purpose", raw_input.get("purpose", "-")))
    metric_cols[2].metric("추천 비율", result.get("recommended_aspect_ratio", raw_input.get("aspect_ratio", "-")))

    st.markdown("#### 메인 프롬프트")
    st.code(result.get("main_prompt", ""), language="text")

    st.markdown("#### 네거티브 프롬프트")
    st.code(result.get("negative_prompt", ""), language="text")

    st.markdown("#### 참고 이미지 편집용 프롬프트")
    st.code(result.get("edit_prompt", ""), language="text")

    st.markdown("#### 변형 버전 3개")
    for variant in result.get("variants", []):
        label = f"{variant.get('name', '')} · {variant.get('purpose', '변형 프롬프트')}"
        with st.expander(label, expanded=False):
            st.code(variant.get("prompt", ""), language="text")

    st.markdown("#### 최종 체크리스트")
    for item in result.get("must_check", []):
        st.markdown(f"- {item}")

    download_payload = create_download_payload(raw_input, result)
    json_text = json.dumps(download_payload, ensure_ascii=False, indent=2)

    st.markdown("#### JSON 출력")
    st.json(download_payload)
    st.download_button(
        "JSON 다운로드",
        data=json_text.encode("utf-8"),
        file_name=f"sigvaris_prompt_builder_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json",
        use_container_width=True,
    )


def render_tips() -> None:
    st.markdown(
        """
        <div class="tips-box">
        <strong>활용 팁</strong>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        1. 실제 제품 사진이 있으면 이미지 생성 시 참고 이미지로 함께 넣는 게 가장 좋습니다.
        2. 텍스트가 긴 광고소재는 비주얼만 생성한 뒤, 텍스트는 별도 편집툴에서 올리는 게 안정적입니다.
        3. 발끝 디테일이 중요한 이미지라면 오픈토 옵션을 켜고, 무릎 아래 중심 또는 다리 중심 클로즈업 구도를 추천합니다.
        4. 허벅지형/팬티스타킹형은 전신 또는 서있는 포즈가 제품 전달력이 좋습니다.
        """
    )


def main() -> None:
    load_dotenv_if_exists()
    st.set_page_config(page_title=APP_NAME, page_icon="🧦", layout="wide")
    init_session_state()
    inject_style()

    settings = render_sidebar()

    st.title("🧦 SIGVARIS 압박스타킹 전용 이미지 프롬프트 생성기")
    st.write("지금까지 작업한 방향을 반영해, SIGVARIS 전용 화보/광고/상세페이지 프롬프트를 바로 뽑아주는 앱입니다.")

    left_col, right_col = st.columns([0.95, 1.05], gap="large")

    with left_col:
        raw_input = render_input_panel()
        generate_clicked = st.button("SIGVARIS 프롬프트 생성", type="primary", use_container_width=True)
        if generate_clicked:
            handle_generation(raw_input, settings)

    with right_col:
        render_result_panel()

    render_tips()


if __name__ == "__main__":
    main()
