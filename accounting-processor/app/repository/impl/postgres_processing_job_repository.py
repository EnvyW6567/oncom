from datetime import datetime

from app.database.postgres_db import get_cursor
from app.entity.processing_job import ProcessingJob
from app.repository.processing_job_repository import ProcessingJobRepository


class PostgresProcessingJobRepository(ProcessingJobRepository):

    def find_and_update_status(self, id: str):
        with get_cursor() as cursor:
            cursor.execute("""
                    UPDATE processing_jobs 
                    SET status = 'processing', started_at = %s
                    WHERE job_id = %s
                    RETURNING csv_file_path, rules_data
                """, (datetime.now(), id))

            job_info = cursor.fetchone()

            if not job_info:
                raise Exception(f"Job not found: {id}")

            return job_info

    def update_progress(self, processing_job: ProcessingJob):
        with get_cursor() as cursor:
            cursor.execute("""
                            UPDATE processing_jobs 
                            SET processed_rows = %s, total_rows = %s
                            WHERE job_id = %s
                            """,
                           (processing_job.processed_rows,
                            processing_job.total_rows,
                            processing_job.job_id))

    def complete_job(self, processing_job: ProcessingJob):
        with get_cursor() as cursor:
            cursor.execute("""
                    UPDATE processing_jobs 
                    SET status = 'completed', 
                        completed_at = %s,
                        processed_rows = %s,
                        total_rows = %s
                    WHERE job_id = %s
                """, (datetime.now(),
                      processing_job.processed_rows,
                      processing_job.total_rows,
                      processing_job.job_id))

    def fail_job(self, processing_job: ProcessingJob, e: Exception):
        with get_cursor() as cursor:
            cursor.execute("""
                    UPDATE processing_jobs 
                    SET status = 'failed', 
                        error_message = %s,
                        completed_at = %s
                    WHERE job_id = %s
                """, (str(e), datetime.now(),
                      processing_job.job_id))
