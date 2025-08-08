from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, JSON, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Company(Base):
    __tablename__ = "companies"

    company_id = Column(String(50), primary_key=True)
    company_name = Column(String(200), nullable=False)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    deleted_at = Column(DateTime, nullable=True)


class Category(Base):
    __tablename__ = "categories"

    category_id = Column(String(50), primary_key=True)
    company_id = Column(String(50), ForeignKey("companies.company_id"))
    category_name = Column(String(200), nullable=False)
    keywords = Column(JSON, default=[])
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    deleted_at = Column(DateTime, nullable=True)


class ProcessingJob(Base):
    __tablename__ = "processing_jobs"

    job_id = Column(UUID, primary_key=True)
    status = Column(String(20), default="pending")
    csv_file_path = Column(String(500))
    rules_data = Column(JSON)
    total_rows = Column(Integer, default=0)
    processed_rows = Column(Integer, default=0)
    error_message = Column(Text)
    created_at = Column(DateTime)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    deleted_at = Column(DateTime, nullable=True)


class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id = Column(BigInteger, primary_key=True, autoincrement=True)
    job_id = Column(UUID, ForeignKey("processing_jobs.job_id"))
    company_id = Column(String(50), ForeignKey("companies.company_id"))
    category_id = Column(String(50), ForeignKey("categories.category_id"))
    transaction_date = Column(DateTime, nullable=False)
    description = Column(Text, nullable=False)
    amount_in = Column(Integer, default=0)
    amount_out = Column(Integer, default=0)
    balance_after = Column(Integer, nullable=False)
    transaction_location = Column(String(200))
    created_at = Column(DateTime)
    deleted_at = Column(DateTime, nullable=True)
