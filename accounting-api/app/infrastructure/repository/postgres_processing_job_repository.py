from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.repository.processing_job_repository import ProcessingJobRepository
from app.infrastructure.database.postgres_db import get_postgres
from app.infrastructure.model.model import ProcessingJob


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
