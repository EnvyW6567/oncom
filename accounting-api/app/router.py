from fastapi import APIRouter, UploadFile, Depends, File

from .service.accounting_service import AccountingService

router = APIRouter(prefix="/api/v1/accounting")


@router.post("/process")
async def process_transactions(
        transactions_file: UploadFile = File,
        rules_file: UploadFile = File,
        accounting_service: AccountingService = Depends(AccountingService)
):
    job = await accounting_service.process(transactions_file, rules_file)

    return job


@router.get("/records")
async def get_company_records():
    pass
