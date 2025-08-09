# 기술 스택 및 아키텍처 설계 문서

## 기술 스택 선택

### 언어 및 프레임워크

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

CSV 파일을 처리해야하는 요구사항에서 CSV 파일 처리에 특화된 Pandas 라이브러리가 가장 먼저 생각났습니다. 또한, 대용량 CSV 파일 분류 작업이 요구 될 경우 높은 부하가 동반된다고 판단했기에 API
서버와 분류 작업 서버를 분리하는 것이 바람직하다고 생각했습니다.

따라서, MSA 구조와 Pandas를 활용 가능한 Python 언어를 고려해 FastAPI를 선택했습니다.

### 데이터베이스

![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)

PostgreSQL은 Python 환경에서 높은 성능과 안정성을 제공하며 asyncpg의 높은 성능의 비동기 라이브러리를 제공하기때문에 PostgreSQL을 선택했습니다.
또한, 보안 부분에서도 세밀한 설정이 가능하며 RLS를 지원해 특정 사용자에 대한 접근 제어를 Row 단위로 할 수 있습니다.

### 메시지 큐

![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)

API 서버와 분류 작업 서버간의 결합도를 낮추기 위해 작업 전달용 메시지 브로커로서 Redis를 도입했습니다.

## 아키텍처 설계

### 시스템 아키텍처

큰 규모의 회사의 경우 대용량 거래 내역을 보유하고 있을 수 있기 때문에 API 서버와 분류 작업 서버를 분리하는 것이 합리적이라고 생각했습니다.
특히, Python 언어의 특성 상 CPU-intensive 한 작업에 매우 불리하기 때문에 분류 작업은 별도의 작업 서버에서 처리하도록 설계했습니다.

![architecture.png](assets%2Farchitecture.png)

### 클린 아키텍처

확장성과 유지보수성 그리고 유연성을 위해 클린아키텍처 패턴을 도입했습니다.

```
┌─────────────────────────────────────────────┐
│             Presentation Layer              │
│               (Controllers)                 │
├─────────────────────────────────────────────┤
│              Application Layer              │
│                 (Services)                  │
├─────────────────────────────────────────────┤
│               Domain Layer                  │
│                (Entities)                   │
├─────────────────────────────────────────────┤
│             Infrastructure Layer            │
│           (Repositories, Database)          │
└─────────────────────────────────────────────┘
```

### 한계

- 별도의 서버가 아닌 Container 로서 실행되며 독립적인 app 으로 동작합니다
- 외부 스토리지가 아닌 로컬 저장소를 사용합니다


