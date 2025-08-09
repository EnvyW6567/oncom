-- PostgreSQL 초기화 스크립트
-- UUID 확장 설치 (processing_jobs 테이블에서 사용)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. 회사 (companies) 테이블
CREATE TABLE companies
(
    company_id   VARCHAR(50) PRIMARY KEY,
    company_name VARCHAR(200) NOT NULL,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at   TIMESTAMP DEFAULT NULL
);

-- 회사명 중복 방지 (삭제되지 않은 것만)
CREATE UNIQUE INDEX idx_companies_name ON companies (company_name)
    WHERE deleted_at IS NULL;

-- 2. 카테고리 (categories) 테이블
CREATE TABLE categories
(
    category_id   VARCHAR(50) PRIMARY KEY,
    company_id    VARCHAR(50)  NOT NULL REFERENCES companies (company_id) ON DELETE CASCADE,
    category_name VARCHAR(200) NOT NULL,
    keywords      JSONB        NOT NULL DEFAULT '[]',
    created_at    TIMESTAMP             DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP             DEFAULT CURRENT_TIMESTAMP,
    deleted_at    TIMESTAMP             DEFAULT NULL
);

-- 복합 인덱스: 회사별 카테고리 조회 최적화 (삭제되지 않은 것만)
CREATE INDEX idx_categories_company_id ON categories (company_id)
    WHERE deleted_at IS NULL;

-- 회사 내 카테고리명 중복 방지 (삭제되지 않은 것만)
CREATE UNIQUE INDEX idx_categories_company_name ON categories (company_id, category_name)
    WHERE deleted_at IS NULL;

-- 3. 분류 작업 (processing_jobs) 테이블
CREATE TABLE processing_jobs
(
    job_id         UUID PRIMARY KEY     DEFAULT uuid_generate_v4(),
    status         VARCHAR(20) NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    csv_file_path  VARCHAR(500),
    rules_data     JSONB,
    total_rows     INTEGER              DEFAULT 0,
    processed_rows INTEGER              DEFAULT 0,
    error_message  TEXT,
    created_at     TIMESTAMP            DEFAULT CURRENT_TIMESTAMP,
    started_at     TIMESTAMP,
    completed_at   TIMESTAMP,
    deleted_at     TIMESTAMP            DEFAULT NULL
);

-- 상태별 작업 조회 최적화 (삭제되지 않은 것만)
CREATE INDEX idx_processing_jobs_status ON processing_jobs (status)
    WHERE deleted_at IS NULL;

-- 최근 작업 조회 최적화 (삭제되지 않은 것만)
CREATE INDEX idx_processing_jobs_created_at ON processing_jobs (created_at DESC)
    WHERE deleted_at IS NULL;

-- 4. 거래 내역 (transactions) 테이블
CREATE TABLE transactions
(
    transaction_id       BIGSERIAL PRIMARY KEY,
    job_id               UUID        NOT NULL REFERENCES processing_jobs (job_id) ON DELETE CASCADE,
    company_id           VARCHAR(50) REFERENCES companies (company_id) ON DELETE SET NULL,
    category_id          VARCHAR(50) REFERENCES categories (category_id) ON DELETE SET NULL,
    transaction_date     TIMESTAMP   NOT NULL,
    description          TEXT        NOT NULL,
    amount_in            INTEGER   DEFAULT 0,
    amount_out           INTEGER   DEFAULT 0,
    balance_after        INTEGER     NOT NULL,
    transaction_location VARCHAR(200),
    created_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at           TIMESTAMP DEFAULT NULL
);

-- 성능 최적화 인덱스 (삭제되지 않은 것만)
CREATE INDEX idx_transactions_company_id ON transactions (company_id)
    WHERE deleted_at IS NULL;

CREATE INDEX idx_transactions_job_id ON transactions (job_id)
    WHERE deleted_at IS NULL;

CREATE INDEX idx_transactions_date ON transactions (transaction_date)
    WHERE deleted_at IS NULL;

-- 복합 인덱스: 회사별 분류된 거래 조회 (삭제되지 않은 것만)
CREATE INDEX idx_transactions_company_category ON transactions (company_id, category_id)
    WHERE deleted_at IS NULL;

-- 테이블 생성 확인
SELECT tablename,
       (SELECT COUNT(*) FROM companies)  as companies_count,
       (SELECT COUNT(*) FROM categories) as categories_count
FROM pg_tables
WHERE schemaname = 'public'
  AND tablename IN ('companies', 'categories', 'processing_jobs', 'transactions');

-- 초기값 추가
INSERT INTO companies (company_id, company_name)
VALUES ('com_1', 'A 커머스'),
       ('com_2', 'B 커머스');
