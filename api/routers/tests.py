from urllib.parse import parse_qs
from fastapi import APIRouter
from typing import Any
from fastapi import Body
from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient
from api.tlg import async_send_tlg


router = APIRouter()


@router.post("/clinic/b24data")
async def no_rel_phone(
    data: Any = Body(None),
):
    json_data = jsonable_encoder(data)
    parsed_dict = parse_qs(str(json_data))
    # принтим исходный реквест
    await async_send_tlg(str(parsed_dict))
    deal_id = parsed_dict["document_id[2]"][0].replace("DEAL_", "")
    async with AsyncClient() as client:
        response = await client.get(
            f"https://klinikamsmk.bitrix24.ru/rest/1/565095l7kxskzhlq/crm.deal.get.json?ID={deal_id}"
        )
    # принтим полный респонс по сделке
    await async_send_tlg(str(response.json()))
    rel_phone = "".join(
        filter(str.isdigit, response.json()["result"]["UF_CRM_1677846335"])
    )
    return rel_phone
