from typing import List

from fastapi import Depends
from sqlalchemy import and_, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..processing_job_repository import ProcessingJobRepository
from ...database.postgres_db import get_postgres
from ...model import ProcessingJob, Transaction, Category
from ...schema import CompanyRecord


class PostgresProcessingJobRepository(ProcessingJobRepository):

    def __init__(self, session: AsyncSession = Depends(get_postgres)):
        self.__session = session

    async def save(self, processing_job: ProcessingJob):
        try:
            self.__session.add(processing_job)
            await self.__session.commit()
        except Exception as e:
            await self.__session.rollback()
            raise e

    async def find_company_records(self, company_id: int) -> List[CompanyRecord]:
        query = select(
            Transaction.transaction_id,
            Transaction.transaction_date,
            Transaction.category_id,
            Transaction.transaction_date,
            Category.category_name
        ).outerjoin(
            Category, Transaction.category_id == Category.category_id
        ).where(
            and_(
                Transaction.company_id == company_id,
                Transaction.deleted_at is None
            )
        ).order_by(desc(Transaction.transaction_date))

        result = await self.__session.execute(query)

        return list(map(CompanyRecord.model_validate, result.mappings()))
