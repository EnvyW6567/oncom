from abc import abstractmethod
from typing import List

from app.application.dto.response.company_records_res import CompanyRecord


class CompanyRecordRepository:

    @abstractmethod
    async def find_company_records(self, company_id: str) -> List[CompanyRecord]:
        pass
