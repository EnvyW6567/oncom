from abc import abstractmethod
from typing import List

from app.schema import CompanyRecord


class CompanyRecordRepository:

    @abstractmethod
    async def find_company_records(self, company_id: str) -> List[CompanyRecord]:
        pass
