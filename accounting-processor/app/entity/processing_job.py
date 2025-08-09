from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from uuid import UUID


class JobStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ProcessingJob:
    job_id: UUID
    status: str
    csv_file_path: str
    rules_data: Dict[str, Any]
    total_rows: int
    processed_rows: int
    error_message: Optional[str]
    created_at: Optional[datetime]
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    @classmethod
    def from_job_info(cls, job_id: str, job_info: Any) -> 'ProcessingJob':
        return cls(
            job_id=job_id,
            status=JobStatus.PENDING.value,
            csv_file_path=job_info['csv_file_path'],
            rules_data=job_info['rules_data'],
            total_rows=0,
            processed_rows=0,
            error_message=None,
            created_at=datetime.now()
        )

    def set_total_rows(self, total_rows: int) -> None:
        if total_rows < 0:
            raise ValueError("Total rows cannot be negative")

        self.total_rows = total_rows

    def processed(self):
        self.processed_rows += 1

    def complete(self):
        self.status = JobStatus.COMPLETED
