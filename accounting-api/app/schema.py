from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, ConfigDict


class CompanyRecord(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    company_id: str = Field(None, description="회사 ID")
    company_name: str = Field(description="회사명")
    category_id: Optional[str] = Field(None, description="계정과목 ID")
    category_name: Optional[str] = Field("미분류", description="계정과목명")
    transaction_date: datetime = Field(..., description="거래일시")
    created_at: datetime = Field(..., description="생성일시")


class CompanyRecordsRes(BaseModel):
    records: List[CompanyRecord] = Field(default_factory=list)
