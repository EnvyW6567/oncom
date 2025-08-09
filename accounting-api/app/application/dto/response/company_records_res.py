from typing import List

from pydantic import BaseModel, Field

from app.domain.entity.company_record import CompanyRecord


class CompanyRecordsRes(BaseModel):
    records: List[CompanyRecord] = Field(default_factory=list)

