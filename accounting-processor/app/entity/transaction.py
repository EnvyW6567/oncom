from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass
class Transaction:
    job_id: UUID
    company_id: Optional[str]
    category_id: Optional[str]
    transaction_date: datetime
    description: str
    amount_in: int
    amount_out: int
    balance_after: int
    transaction_location: Optional[str]
    created_at: datetime

    @classmethod
    def from_csv_row(cls, job_id: UUID, row_data: dict) -> 'Transaction':
        return cls(
            job_id=job_id,
            company_id=None,  # 초기값은 미분류
            category_id=None,
            transaction_date=row_data['거래일시'],
            description=row_data['적요'],
            amount_in=row_data['입금액'] or 0,
            amount_out=row_data['출금액'] or 0,
            balance_after=row_data['거래후잔액'],
            transaction_location=row_data.get('거래점'),
            created_at=datetime.now()
        )

    def classify(self, rules: dict) -> None:
        description_lower = self.description.lower()

        for company in rules.get('companies', []):
            company_id = company['company_id']

            for category in company.get('categories', []):
                keywords = category.get('keywords', [])

                for keyword in keywords:
                    if keyword.lower() in description_lower:
                        self.company_id = company_id
                        self.category_id = category['category_id']
                        return

        self.company_id = None
        self.category_id = None
