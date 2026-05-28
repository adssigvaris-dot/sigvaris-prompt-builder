# SIGVARIS Prompt Builder

SIGVARIS 압박스타킹 전용 이미지 프롬프트 생성기입니다.  
제품 타입, 사용 목적, 배경, 모델, 구도, 비율, 무드, 컬러톤, 필수 요소, 금지 요소를 입력하면 상업용 이미지 제작에 바로 활용할 수 있는 한국어 프롬프트 세트를 생성합니다.

## 주요 특징

- SIGVARIS 압박스타킹 전용 프롬프트 생성
- OpenAI Responses API 기반 생성 지원
- API 키가 없거나 호출 오류가 발생하면 기본 템플릿 fallback 모드로 자동 생성
- 메인 프롬프트, 네거티브 프롬프트, 참고 이미지 편집용 프롬프트 생성
- 프리미엄 화보형, 전환형 광고 비주얼, 상세페이지/설명형 변형 프롬프트 3종 생성
- 최종 체크리스트 제공
- 전체 결과를 JSON으로 확인하고 다운로드 가능
- 한국어 UI 기반의 실무형 Streamlit 앱

## 파일 구조

```text
SIGVARIS Prompt Builder/
├─ app.py
├─ requirements.txt
├─ .env.example
└─ README.md
```

## 설치 방법

Python 3.10 이상 사용을 권장합니다.

```bash
python -m venv .venv
```

Windows PowerShell:

```bash
.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

필수 패키지를 설치합니다.

```bash
pip install -r requirements.txt
```

## 환경변수 설정

OpenAI API를 사용할 경우 `.env.example` 파일을 복사해 `.env` 파일을 만들고 값을 입력합니다.

```bash
cp .env.example .env
```

`.env` 예시:

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4.1-mini
```

환경변수를 설정하지 않아도 앱은 실행됩니다. API 키가 없으면 기본 템플릿 사용 모드로 동작합니다.

## 실행 방법

```bash
streamlit run app.py
```

실행 후 브라우저에서 Streamlit이 안내하는 주소로 접속합니다. 일반적으로 아래 주소입니다.

```text
http://localhost:8501
```

## 사용 방법

1. 사이드바에서 생성 모드를 선택합니다.
   - `OpenAI API 사용`: 입력한 API 키와 모델명으로 OpenAI Responses API를 호출합니다.
   - `기본 템플릿 사용`: API 없이 앱 내부 템플릿으로 결과를 생성합니다.
2. OpenAI API를 사용할 경우 API Key를 입력합니다.
3. 모델명을 확인합니다. 기본값은 `gpt-4.1-mini`입니다.
4. 왼쪽 입력 영역에서 제품 타입, 사용 목적, 배경, 모델, 구도, 비율, 무드, 컬러톤을 설정합니다.
5. 오픈토 발끝 디테일 사용 여부와 이미지 안 문구 포함 여부를 선택합니다.
6. 반드시 포함할 요소, 절대 피할 요소, 추가 요청을 입력합니다.
7. `SIGVARIS 프롬프트 생성` 버튼을 누릅니다.
8. 오른쪽 결과 영역에서 생성된 프롬프트와 JSON 결과를 확인합니다.
9. 필요한 경우 `JSON 다운로드` 버튼으로 결과를 저장합니다.

## 생성되는 결과

앱은 아래 결과를 자동으로 생성합니다.

- 요약
- 제품 타입, 목적, 추천 비율 metric
- 메인 프롬프트
- 네거티브 프롬프트
- 참고 이미지 편집용 프롬프트
- 변형 버전 3개
  - 프리미엄 화보형
  - 전환형 광고 비주얼
  - 상세페이지/설명형
- 최종 체크리스트
- JSON 출력
- JSON 다운로드 파일

## OpenAI API 동작 방식

앱은 `openai` 패키지의 최신 클라이언트 방식으로 Responses API를 호출합니다.

- `from openai import OpenAI`
- `client = OpenAI(api_key=api_key)`
- `client.responses.create(...)`

응답에서는 `output_text`를 우선 사용합니다.  
`output_text`가 없을 경우 `output`, `content`, `text` 구조에서 텍스트를 추출한 뒤 JSON으로 파싱합니다.  
응답이 코드블록으로 감싸져 있어도 자동으로 제거하고 파싱합니다.

## fallback 모드

아래 상황에서는 자동으로 `fallback_generate()` 함수가 실행됩니다.

- API 키가 비어 있는 경우
- 사용자가 `기본 템플릿 사용` 모드를 선택한 경우
- OpenAI API 호출 중 오류가 발생한 경우
- OpenAI 응답 JSON 파싱에 실패한 경우

fallback 모드에서도 아래 구조의 결과를 동일하게 반환합니다.

- `summary`
- `recommended_aspect_ratio`
- `main_prompt`
- `negative_prompt`
- `edit_prompt`
- `variants`
- `must_check`
- `input_summary`

## 실무 활용 팁

1. 실제 제품 사진이 있으면 이미지 생성 시 참고 이미지로 함께 넣는 게 가장 좋습니다.
2. 텍스트가 긴 광고소재는 비주얼만 생성한 뒤, 텍스트는 별도 편집툴에서 올리는 게 안정적입니다.
3. 발끝 디테일이 중요한 이미지라면 오픈토 옵션을 켜고, 무릎 아래 중심 또는 다리 중심 클로즈업 구도를 추천합니다.
4. 허벅지형/팬티스타킹형은 전신 또는 서있는 포즈가 제품 전달력이 좋습니다.

## 참고

SIGVARIS 제품 이미지는 제품 형태 정확성이 중요합니다.  
특히 오픈토 옵션을 사용할 때는 흰색 스타킹 발부분, 검정색 둥근 밴드 마감, 자연스러운 발가락, 신발처럼 보이지 않는 스타킹 구조가 결과물에 반영되는지 확인하는 것이 좋습니다.
