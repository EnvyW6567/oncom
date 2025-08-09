# 실행 및 테스트 가이드

### 포트 사용 현황

- `8000` : API 서버 (FastAPI)
- `5432` : PostgreSQL 데이터베이스
- `6379` : Redis (작업 큐)

### 1. 저장소 클론

```
git clone https://github.com/EnvyW6567/oncom.git oncom
cd oncom
```

### 2. 도커 실행

```
docker-compose up --build
```

### 3. API 문서

```
localhost:8000/docs
```

[![API Docs](https://img.shields.io/badge/API%20Docs-Swagger-85EA2D?style=for-the-badge&logo=swagger&logoColor=black)
](http://localhost:8000/docs)

[![swagger.png](assets%2Fswagger.png)](http://localhost:8000/docs)
