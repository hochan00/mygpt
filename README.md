# notion-assistant

> LangGraph 기반 **Notion 개인 비서 에이전트** — 내 노션에서 정보를 찾아 종합해 답하고,
> 새 내용을 적절한 위치에 작성하고, 자연어로 일정을 등록해주는 tool-calling 에이전트

---

## 목차

- [핵심 아이디어](#핵심-아이디어)
- [사용 시나리오](#사용-시나리오)
- [아키텍처](#아키텍처)
  - [LangGraph 그래프 구조 — ReAct 루프](#langgraph-그래프-구조--react-루프)
  - [search_notion 내부 파이프라인](#search_notion-내부-파이프라인)
- [도구 목록](#도구-목록)
- [기술 스택](#기술-스택)
- [프로젝트 구조](#프로젝트-구조)
- [설치 및 실행](#설치-및-실행)
- [API](#api)
- [설계 결정](#설계-결정)

---

## 핵심 아이디어

노션을 오래 쓸수록 정보는 여러 페이지에 흩어집니다. 무언가를 다시 찾으려면 검색창에 키워드를
바꿔가며 넣어보고, 여러 페이지를 열어 읽고, 머릿속으로 종합해야 합니다.

이 프로젝트는 그 과정을 에이전트가 대신합니다 — **흩어진 노트를 찾아 하나의 답변으로 종합하고,
어느 페이지에서 가져온 내용인지 출처 페이지 링크와 함께 전달**합니다. 나아가 새 내용을 적을 때는
적절한 위치를 판단해서 작성하고, 자연어로 말한 일정을 캘린더에 등록합니다.

| 사람이 직접 하면 | 에이전트가 하면 |
|---|---|
| 검색창에 키워드를 넣고, 여러 페이지를 열어 읽고, 머릿속으로 종합 | 흩어진 노트를 찾아 종합한 답변을 **출처 페이지 링크와 함께** 전달 |
| 어느 페이지에 적을지 고민하고, 중복인지 기존 노트를 뒤져봄 | **관련 노트를 먼저 검색해서 "이어붙일지 / 새로 만들지" 판단** 후 확인을 구함 |
| 캘린더를 열고 날짜·시간을 클릭해 입력 | "다음주 화요일 3시 팀 미팅"이라는 **자연어를 해석**해 일정 항목 생성 |

구조는 **LLM이 매 턴 어떤 도구를 쓸지 스스로 결정하는 ReAct 루프**입니다. 요청마다 실제로 다른
경로(검색 / 작성 / 일정 / 그냥 대화)를 타기 때문에, 그래프 분기가 형식적이지 않고 실질적으로
동작합니다.

---

## 사용 시나리오

**A. 검색·질의응답** (도구: `search_notion`)

> "저번주에 진행한 프로젝트A 정리한 문서에서 어떤 내용 협의했는지 확인할 수 있나?"

관련 노트 검색 → 관련성 평가 → (실패 시 질의 재작성 후 재검색) → 여러 노트 종합 답변 → 근거 검증 →
"[프로젝트A 회의록] 페이지에 이렇게 정리되어 있어요: ..." + 원본 페이지 링크

**B. 노트 작성 — 신규 또는 병합** (도구: `write_note` + 승인)

> "오늘 인터뷰 스터디에서 STAR 기법 배웠어, 나중에 참고하게 적어줘"

관련 기존 노트 검색 → 없으면 "새 페이지로 만들까요?", 있으면 "[인터뷰 준비] 페이지에 이어붙일까요?" →
**사용자 승인 후** 실행

**C. 일정 등록** (도구: `create_event` + 승인)

> "다음주 화요일 3시에 팀 미팅 잡아줘"

자연어에서 날짜·시간·제목 해석 → "7/21(화) 15:00 '팀 미팅' 일정을 등록할까요?" → **승인 후**
캘린더 뷰로 사용 중인 노션 데이터베이스에 날짜 속성을 채운 페이지 생성

**D. 일반 대화** (도구 없음)

> "LangGraph에서 interrupt가 뭐야?"

검색·작성이 필요 없는 질문은 도구 호출 없이 바로 답변하고 종료 — LLM이 "도구가 필요 없다"고 판단하는
것 자체가 하나의 경로

---

## 아키텍처

### LangGraph 그래프 구조 — ReAct 루프

실선은 구현 완료, 점선은 구현 예정입니다.

```mermaid
flowchart TD
    START([START]) --> agent

    agent["agent<br/>Gemini가 도구 선택 또는 답변 생성"]
    tools["tools<br/>도구 실행 - ToolNode"]
    confirm["confirm_action<br/>사용자 승인 대기 - interrupt"]:::planned

    agent -->|도구 호출 없음 - 답변 완성| END([END])
    agent -->|도구 호출 있음| tools
    agent -.->|쓰기 도구 - 예정| confirm

    confirm -.->|승인| tools
    confirm -.->|거절 - 사유와 함께 재판단| agent

    tools -->|실행 결과를 메시지로 추가| agent

    classDef planned stroke-dasharray: 5 5,fill:#f5f5f5,color:#888;
```

**핵심 설계 포인트 1 — 조건부 엣지는 도구 개수만큼 늘어나지 않음**: "어떤 도구를 쓸지"는 그래프 엣지가
아니라 `agent` 노드 안에서 LLM(`bind_tools`)이 이미 결정합니다. 그래프가 판단하는 것은
"도구 호출이 있는가 / 그것이 쓰기 도구인가"라는 단순한 분기뿐이라, 도구가 늘어나도 그래프 구조는
그대로입니다.

**핵심 설계 포인트 2 — 쓰기만 승인을 받음**: 검색(읽기)은 실패해도 되돌릴 것이 없지만, 작성(쓰기)은
잘못되면 기존 노트를 오염시킵니다. 그래서 `write_note`·`create_event`만 `confirm_action`
(LangGraph `interrupt()` 기반 human-in-the-loop)을 거치고, 읽기 도구는 바로 실행합니다.

**핵심 설계 포인트 3 — 상태는 MessagesState 기반**: 비서는 여러 턴의 대화와 도구 호출 이력을
이어가야 하므로, 메시지 리스트를 누적(`add_messages` 리듀서)하는 `MessagesState` 기반 상태를
사용합니다. checkpointer가 `thread_id`별로 상태를 저장·복원해 멀티턴 대화를 지원합니다.

### search_notion 내부 파이프라인

> 구현 예정인 내부 설계입니다.

개인 노트는 LLM이 사전학습에서 전혀 본 적 없는 내용이라, **근거 검증 없이는 신뢰할 수 있는 답이
성립하지 않습니다.** 그래서 단순 "검색 → 생성"이 아니라 관련성 평가·질의 재작성·근거 검증을 거치는
파이프라인으로 구성합니다.

```mermaid
flowchart LR
    Q([검색 질의]) --> Retrieve["벡터 검색<br/>ChromaDB"]
    Retrieve --> Grade["grade_documents<br/>관련성 평가"]
    Grade -->|관련 있음| Gen["generate<br/>여러 노트 종합"]
    Grade -->|관련 없음| Transform["transform_query<br/>질의 재작성"]
    Transform --> Retrieve
    Gen --> Hallu["grade_hallucination<br/>근거 검증"]
    Hallu --> A([종합 답변 + 원본 페이지 링크])
```

---

## 도구 목록

> 현재는 ReAct 루프 검증용 더미 도구(`get_current_time`)만 연결되어 있으며, 아래 4개가 목표 도구입니다.

| 도구 | 역할 | 성격 | 승인(HITL) |
|------|------|------|:---:|
| `search_notion` | 내 노션 페이지를 검색해 근거 검증을 거친 종합 답변 생성 | 읽기 | ✕ |
| `web_search` | 노션에 없는 일반 지식·최신 정보 검색 | 읽기 | ✕ |
| `write_note` | 관련 기존 페이지를 먼저 검색해 "병합 / 신규" 판단 후 작성 | 쓰기 | ✓ |
| `create_event` | 자연어 일정을 해석해 캘린더 뷰 데이터베이스에 항목 생성 | 쓰기 | ✓ |

---

## 기술 스택

| 분류 | 기술 | 선택 이유 |
|------|------|----------|
| 언어 | Python 3.13 | — |
| 프레임워크 | FastAPI | 비동기 지원, 자동 Swagger 문서화 |
| 오케스트레이션 | LangChain · LangGraph | ReAct 루프 + human-in-the-loop(`interrupt`)를 상태 그래프로 표현 |
| LLM | Google Gemini 2.5 Flash | tool-calling 지원, instruction-following 우수, 무료 티어 제공 |
| 임베딩 | Qwen3-Embedding-0.6B (로컬) | 32K 토큰까지 처리 — 긴 노트도 잘림 없이 임베딩, 호출 비용 없음 |
| 벡터 DB | ChromaDB (로컬 파일) | 별도 서버 없이 파일 기반으로 영속화 |
| 외부 연동 | Notion API (`notion-client`) | 페이지 목록·본문 조회, 페이지 생성 — 무료, rate limit 3 req/s |
| 웹검색 | Tavily (예정) | RAG용으로 설계된 검색 API, 무료 티어 제공 |
| 모니터링 | LangSmith | 도구 선택·그래프 실행 과정 자동 트레이싱 |
| 패키지 관리 | uv | 빠른 의존성 해석, `pyproject.toml` + `uv.lock` |

---

## 프로젝트 구조

> ReAct 뼈대(agent ⇄ tools 루프, thread_id 기반 대화 API)는 구현 완료. 노션 연동 도구와
> 승인 노드는 구현 예정입니다.

```
langgraph-agent/
├── src/
│   ├── main.py                  # FastAPI 앱 진입점
│   │
│   ├── router/
│   │   └── agent_router.py      #   /agent — 비서 대화 엔드포인트 (thread_id 기반)
│   │
│   ├── schemas/
│   │   └── agent_schema.py      #   요청/응답 모델 (message, thread_id)
│   │
│   ├── core/
│   │   ├── config.py            #   pydantic-settings 기반 환경변수
│   │   └── llm.py               #   Gemini · 임베딩 모델 인스턴스
│   │
│   ├── graph/                   # LangGraph "조립/실행"만 담당
│   │   ├── state.py             #   AgentState (MessagesState 기반)
│   │   ├── nodes/
│   │   │   ├── agent.py         #     agent 노드 + 라우팅 함수 (bind_tools된 LLM 호출)
│   │   │   └── confirm.py       #     confirm_action — interrupt 기반 승인 (예정)
│   │   └── graph.py             #   StateGraph 조립 + checkpointer + compile
│   │
│   ├── tools/                   # 에이전트 도구 정의 (@tool)
│   │   ├── get_current_time.py  #   루프 검증용 더미 도구 (추후 삭제)
│   │   ├── search_notion.py     #   (예정)
│   │   ├── web_search.py        #   (예정)
│   │   ├── write_note.py        #   (예정)
│   │   └── create_event.py      #   (예정)
│   │
│   ├── services/                # 재사용 가능한 "부품"
│   │   ├── notion_client.py     #   Notion API 래핑 (예정)
│   │   ├── prompts.py           #   yaml → ChatPromptTemplate 로딩
│   │   └── utils.py
│   │
│   └── prompts/                 # 프롬프트 템플릿 (yaml)
│
└── data/
    └── chroma_db/               # 노션 페이지 벡터 인덱스 (git 제외)
```

**모듈 구성 원칙**

- `services/` — 누가 쓰든 상관없는 **재사용 부품**
- `graph/` — 노드를 어떤 **순서/조건**으로 실행할지만 담당
- `tools/` — `services/`의 부품을 조합해 에이전트에게 노출하는 **도구 인터페이스**

---

## 설치 및 실행

### 1. 패키지 설치

```bash
uv sync
```

### 2. 환경변수 설정

프로젝트 루트에 `.env` 파일을 생성합니다.

```env
# LangSmith
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=your_langsmith_api_key
LANGSMITH_PROJECT=notion-assistant

# Google Gemini
GOOGLE_API_KEY=your_google_api_key

# Notion — 내부 통합(internal integration) 토큰
NOTION_API_KEY=your_notion_integration_token

# 일정 등록 대상 데이터베이스 (캘린더 뷰로 사용 중인 DB)
NOTION_CALENDAR_DB_ID=your_database_id
```

> Notion 통합 토큰은 [notion.so/my-integrations](https://www.notion.so/my-integrations)에서 발급하고,
> 검색·작성 대상 페이지에 해당 통합을 **연결(connection 추가)** 해야 API로 접근할 수 있습니다.

### 3. 서버 실행

```bash
uv run uvicorn src.main:app --reload --reload-exclude "data/*" --reload-exclude ".git/*"
```

- Swagger UI: `http://localhost:8000/docs`

---

## API

### `POST /api/agent`

`thread_id`가 같으면 이전 대화에 이어서 응답합니다(멀티턴).

```json
// Request
{ "message": "지금 몇 시야?", "thread_id": "user-session-1" }

// Response
{ "message": "지금은 2026년 7월 21일 11시 48분 27초입니다." }
```

**승인 흐름 (구현 예정)** — 쓰기 도구는 실행 전에 그래프가 일시정지(`interrupt`)되고,
같은 `thread_id`로 승인 응답을 보내면 이어서 실행됩니다.

```json
// Request
{ "message": "다음주 화요일 3시에 팀 미팅 잡아줘", "thread_id": "user-session-1" }

// Response — 승인 대기
{ "status": "pending_confirmation", "message": "7/21(화) 15:00 '팀 미팅' 일정을 캘린더에 등록할까요?" }
```

---

## 설계 결정

<details>
<summary><b>왜 Notion AI를 쓰지 않고 직접 만드는가</b></summary>

Notion AI는 유료 구독(Business 플랜 이상)이지만, Notion의 일반 API는 무료입니다.
API 위에 Gemini(무료 티어)와 로컬 임베딩을 조합하면 구독료 없이 같은 목적을 달성할 수 있습니다.
다만 이 프로젝트의 주 목적은 비용 절감보다 **LangGraph 에이전트 패턴(ReAct 루프, HITL, 도구 설계)의
실습·포트폴리오**이며, Notion AI의 대체 상품이 아니라 개인 워크스페이스용 자동화 도구입니다.
(사내 자동화·개인 자동화는 Notion이 Developer Platform으로 공식 권장하는 사용 방식입니다.)
</details>

<details>
<summary><b>왜 고정 분기 그래프가 아니라 ReAct 루프인가</b></summary>

고정 분기 그래프는 모든 분기 경우의 수를 사람이 미리 설계해야 합니다. 흐름이 하나로 정해진
태스크에는 맞지만, 비서는 요청 유형(검색/작성/일정/잡담)이 매번 달라서 경우의 수를 미리 나열할 수
없습니다. ReAct 루프는 "어떤 도구를 쓸지"를 LLM의 tool-calling에 맡기고, 그래프는
"도구 호출 여부 / 쓰기 여부"라는 단순한 분기만 담당합니다.
`create_react_agent` 프리빌트를 쓰지 않고 StateGraph로 직접 조립하는 이유는, 쓰기 도구 앞에
**승인 노드(confirm_action)를 끼워 넣어야** 하기 때문입니다 — 프리빌트는 이 지점을 커스텀할 수 없습니다.
</details>

<details>
<summary><b>왜 write_note는 저장 전에 검색부터 하는가</b></summary>

"기존에 관련 페이지가 있는지"를 LLM 단독 판단에 맡기면 존재하지 않는 페이지를 있다고 착각할 수
있습니다. 검색 오류는 틀린 답을 주는 것에 그치지만, **쓰기 오류는 엉뚱한 페이지를 오염**시킵니다.
그래서 저장 전에 `search_notion`과 같은 검색 경로로 후보를 확보하고, 그 근거 위에서
"이어붙일지 / 새로 만들지"를 판단한 뒤, 최종 실행은 사용자 승인을 거칩니다.
</details>
