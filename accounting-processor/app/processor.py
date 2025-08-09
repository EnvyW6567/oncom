import logging
import traceback
from datetime import datetime

import pandas as pd

from app.entity.processing_job import ProcessingJob
from app.entity.transaction import Transaction
from app.repository.processing_job_repository import ProcessingJobRepository
from app.repository.transaction_repository import TransactionRepository

logger = logging.getLogger(__name__)


class TransactionProcessor:
    def __init__(self, processing_job_repository: ProcessingJobRepository,
                 transaction_repository: TransactionRepository):
        self.__processing_job_repository = processing_job_repository
        self.__transaction_repository = transaction_repository

    def process_job(self, job_id: str):
        try:
            job_info = self.__processing_job_repository.find_and_update_status(job_id)
            processing_job = ProcessingJob.from_job_info(job_id, job_info)

            df = pd.read_csv(processing_job.csv_file_path, encoding='utf-8')
            processing_job.set_total_rows(len(df))

            for _, row in df.iterrows():
                transaction = self.parse_transaction(job_id, row, processing_job.rules_data)
                self.__transaction_repository.save(transaction)

                processing_job.processed()

                if processing_job.processed_rows % 1000 == 0:
                    self.__processing_job_repository.update_progress(processing_job)

            processing_job.complete()
            self.__processing_job_repository.complete_job(processing_job)

            return {
                "job_id": job_id,
                "status": "completed",
                "processed_rows": processing_job.processed_rows,
                "total_rows": processing_job.total_rows
            }

        except Exception as e:
            logger.error(f"Error processing job {job_id}: {str(e)}, trace: {traceback.format_exc()}")
            self.__processing_job_repository.fail_job(job_id, e)

            raise

    def parse_transaction(self, job_id: str, row: pd.Series, rules: dict) -> Transaction:
        row_data = row.to_dict()
        logger.info('ROW_DATA: {}'.format(row_data))
        transaction = Transaction.from_csv_row(job_id, row_data)
        transaction.classify(rules)

        return transaction

    def __str_to_date(self, date_str: str) -> datetime:
        try:
            date = pd.to_datetime(date_str)
        except Exception as e:
            logger.error(e)
            date = datetime.now()

        return date
