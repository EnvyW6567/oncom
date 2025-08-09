import json
import os
import re
import uuid
from datetime import datetime

import aiofiles
from fastapi import UploadFile, Depends

from ..database.redis_db import get_redis
from ..model import ProcessingJob
from ..repository.company_record_repository import CompanyRecordRepository
from ..repository.impl.postgres_company_record_repository import PostgresCompanyRecordRepository
from ..repository.impl.postgres_processing_job_repository import PostgresProcessingJobRepository
from ..repository.processing_job_repository import ProcessingJobRepository
from ..schema import CompanyRecordsRes


class AccountingService:
    UPLOAD_PATH = '/app/shared/uploads'
    CHUNK_SIZE = 1024 * 1024
    TASK_TYPE = 'process_transactions'
    REDIS_QUEUE_NAME = 'accounting_tasks'

    def __init__(
            self,
            processing_job_repository: ProcessingJobRepository = Depends(PostgresProcessingJobRepository),
            company_record_repository: CompanyRecordRepository = Depends(PostgresCompanyRecordRepository),
            redis=Depends(get_redis)
    ):
        self.__company_record_repository = company_record_repository
        self.__processing_job_repository = processing_job_repository
        self.__redis_client = redis

    async def process(self, transactions_file: UploadFile, rules_file: UploadFile) -> ProcessingJob:
        transactions_path = await self.__process_transactions_file(transactions_file)
        rules_data = await self.__process_rules_file(rules_file)

        job = ProcessingJob(
            job_id=uuid.uuid4(),
            status="pending",
            csv_file_path=transactions_path,
            rules_data=rules_data,
            created_at=datetime.now()
        )
        await self.__save_and_publish_job(job)

        return job

    async def get_company_records(self, company_id: str) -> CompanyRecordsRes:
        company_records = await self.__company_record_repository.find_company_records(company_id)

        return CompanyRecordsRes(records=company_records)

    async def __process_transactions_file(self, file: UploadFile) -> str:
        file_id = str(uuid.uuid4())
        filename = re.match(r'^(.+)\.[^.]+$', file.filename).group(1) or file.filename  # without extension
        new_filename = f"{filename}-{file_id}.csv"
        file_path = os.path.join(self.UPLOAD_PATH, new_filename)

        await file.seek(0)
        await self.__save_file_stream(file, file_path)

        return file_path

    async def __process_rules_file(self, file: UploadFile) -> dict:
        await file.seek(0)
        content = await file.read()

        return json.loads(content.decode())

    async def __save_file_stream(self, file: UploadFile, file_path: str):
        async with aiofiles.open(file_path, 'wb') as f:
            while chunk := await file.read(1024 * 1024):
                await f.write(chunk)

    async def __save_and_publish_job(self, job: ProcessingJob):
        await self.__processing_job_repository.save(job)
        await self.__publish_job(job)

    async def __publish_job(self, job: ProcessingJob):
        task = {
            "job_id": str(job.job_id),
            "task": self.TASK_TYPE
        }
        await self.__redis_client.lpush(self.REDIS_QUEUE_NAME, json.dumps(task))
