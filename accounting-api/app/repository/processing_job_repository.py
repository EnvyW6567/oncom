from abc import ABCMeta, abstractmethod

from app.model import ProcessingJob


class ProcessingJobRepository(metaclass=ABCMeta):
    @abstractmethod
    async def save(self, processing_job: ProcessingJob):
        pass
