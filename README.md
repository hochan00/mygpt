# mygpt

나만의 한국어 GPT를 직접 구현하고, RAG 파이프라인과 FastAPI로 서빙하는 프로젝트

## 주요 기능

### 1. 텍스트 생성

- **모델**: EleutherAI/polyglot-ko-1.3b
- 사용자가 문장을 입력하면 이어지는 텍스트를 생성합니다.
- temperature, top-k 파라미터로 생성 다양성을 조절할 수 있습니다.

### 2. RAG (문서 기반 질의응답)

- **LLM**: Google Gemini 2.5 Flash
- **임베딩**: jhgan/ko-sroberta-multitask
- **벡터 DB**: ChromaDB (로컬 파일 기반)
- **프레임워크**: LangChain
- 텍스트 문서를 업로드하면 분할 후 벡터화하여 ChromaDB에 저장합니다.
- 질문이 들어오면 관련 문서를 검색하고, Gemini가 문서를 참고하여 답변을 생성합니다.

### 3. LangSmith 트레이싱

- RAG 체인 실행이 LangSmith에 자동으로 기록됩니다.
- `.env` 환경변수 설정만으로 동작합니다.

## 기술 스택

| 분류 | 기술 |
|------|------|
| 언어 | Python 3.13 |
| 프레임워크 | FastAPI |
| 텍스트 생성 | PyTorch, Transformers (polyglot-ko-1.3b) |
| RAG | LangChain, ChromaDB, Gemini API |
| 임베딩 | sentence-transformers (ko-sroberta-multitask) |
| 모니터링 | LangSmith |
| 패키지 관리 | uv |

## 프로젝트 구조

```
mygpt/
├── api/
│   ├── main.py                  # FastAPI 앱 진입점
│   ├── router.py                # API 엔드포인트 정의
│   ├── schema.py                # 요청/응답 Pydantic 모델
│   ├── core/
│   │   ├── config.py            # 환경변수 관리 (pydantic-settings)
│   │   └── llm.py               # LLM, 임베딩, 토크나이저 초기화
│   ├── prompts/
│   │   └── rag.yaml             # RAG 프롬프트 템플릿
│   └── services/
│       ├── generate_service.py  # 텍스트 생성 로직
│       └── rag_service.py       # RAG 문서 등록 및 질의 로직
├── model/                       # GPT 모델 구현
├── train/                       # 학습 스크립트
├── eval/                        # 평가
├── tokenizer/                   # BPE 토크나이저
├── configs/
│   └── default.yaml             # 하이퍼파라미터 설정
└── data/                        # 데이터셋, ChromaDB 저장소
```

## 설치 및 실행

### 1. 패키지 설치

```bash
uv sync
```

### 2. 환경변수 설정

`.env` 파일을 프로젝트 루트에 생성합니다.

```env
# LangSmith
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=your_langsmith_api_key
LANGSMITH_PROJECT=mygpt

# Google Gemini
GOOGLE_API_KEY=your_google_api_key
```

### 3. 서버 실행

```bash
uv run uvicorn api.main:app --reload
```

서버가 실행되면 `http://localhost:8000/docs`에서 Swagger UI를 통해 API를 테스트할 수 있습니다.

## API

### `GET /`

헬스 체크

### `POST /api/generate`

텍스트 생성

```json
// Request
{
  "prompt": "오늘 날씨가",
  "max_length": 128,
  "temperature": 0.8,
  "top_k": 50
}

// Response
{
  "prompt": "오늘 날씨가",
  "generated_text": "좋아서 산책을 나갔습니다..."
}
```

### `POST /api/documents`

RAG 검색 대상 문서 등록 (텍스트 파일 업로드)

```json
// Response
{
  "message": "'document.txt' 문서가 등록되었습니다.",
  "chunks": 5
}
```

### `POST /api/rag`

등록된 문서 기반 질의응답

```json
// Request
{
  "question": "이 문서의 핵심 내용이 뭐야?"
}

// Response
{
  "question": "이 문서의 핵심 내용이 뭐야?",
  "answer": "이 문서의 핵심 내용은...",
  "sources": ["document.txt"]
}
```
