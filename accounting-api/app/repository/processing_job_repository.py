from abc import ABCMeta, abstractmethod
from typing import List

from ..model import ProcessingJob
from ..schema import CompanyRecord


class ProcessingJobRepository(metaclass=ABCMeta):
    @abstractmethod
    async def save(self, processing_job: ProcessingJob):
        pass

    @abstractmethod
    async def find_company_records(self, company_id: int) -> List[CompanyRecord]:
        pass
