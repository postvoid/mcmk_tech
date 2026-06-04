from fastapi import APIRouter
from typing import Any
from fastapi import Body, Depends
from database.core import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from api.helpers import handle_message
import requests


router = APIRouter(prefix="/messages")


@router.post("/clinic")
async def send_clinic_message(
    data: Any = Body(None), db: AsyncSession = Depends(get_db)
):
    return await handle_message(service_type="clinic", data=data, db=db, phone_number=None)


@router.post("/psy")
async def send_psy_message(phone_number: str, db: AsyncSession = Depends(get_db)):
    return await handle_message(service_type="psy", phone_number=phone_number, db=db)


@router.get("/https_test")
def https_test():
    res = requests.get("https://github.com/")
    return res.status_code