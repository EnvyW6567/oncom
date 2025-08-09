from abc import abstractmethod

from app.entity.processing_job import ProcessingJob


class ProcessingJobRepository:

    @abstractmethod
    def find_and_update_status(self, id: str):
        pass

    @abstractmethod
    def update_progress(self, processing_job: ProcessingJob):
        pass

    @abstractmethod
    def complete_job(self, processing_job: ProcessingJob):
        pass

    @abstractmethod
    def fail_job(self, processing_job: ProcessingJob, e: Exception):
        pass
