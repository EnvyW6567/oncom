from typing import List

from fastapi import Depends
from sqlalchemy import select, and_, null, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dto.response.company_records_res import CompanyRecord
from app.application.repository.company_record_repository import CompanyRecordRepository
from app.infrastructure.database.postgres_db import get_postgres
from app.infrastructure.model.model import Transaction, Company, Category


class PostgresCompanyRecordRepository(CompanyRecordRepository):

    def __init__(self, session: AsyncSession = Depends(get_postgres)):
        self.__session = session

    async def find_company_records(self, company_id: str) -> List[CompanyRecord]:
        query = select(
            Transaction.transaction_id,
            Transaction.transaction_date,
            Transaction.category_id,
            Transaction.transaction_date,
            Transaction.created_at,
            Transaction.company_id,
            Company.company_name,
            Category.category_name
        ).join(
            Category, Transaction.category_id == Category.category_id
        ).join(
            Company, Transaction.company_id == Company.company_id
        ).where(
            and_(
                Transaction.company_id == company_id,
                Transaction.deleted_at == null()
            )
        ).order_by(desc(Transaction.transaction_date))

        result = await self.__session.execute(query)

        return list(map(CompanyRecord.model_validate, result.mappings()))
