from abc import ABCMeta, abstractmethod

from app.infrastructure.model.model import ProcessingJob


class ProcessingJobRepository(metaclass=ABCMeta):
    @abstractmethod
    async def save(self, processing_job: ProcessingJob):
        pass
