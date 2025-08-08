from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/accounting")


@router.post("/process")
async def process_transactions():
    pass


@router.get("/records")
async def get_company_records():
    pass
