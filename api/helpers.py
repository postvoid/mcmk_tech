from urllib.parse import parse_qs
from fastapi.encoders import jsonable_encoder
from dotenv import load_dotenv
import os
from httpx import AsyncClient
from database.messages.models import PsyReport, ClinicReport
from typing import Any
from fastapi import Body, Depends
from database.core import get_db
from api.tlg import async_send_tlg
from sqlalchemy.ext.asyncio import AsyncSession
from database.messages import services


load_dotenv()


class MessageSender:
    def __init__(self, service_type, phone_number, message) -> None:
        self.service_type = service_type
        self.phone_number = phone_number
        self.message = message
        self.wazzup_url = "https://api.wazzup24.com/v3/message"

    @property
    def smsaero_url(self) -> str:
        SMSAERO_EMAIL = os.getenv("SMSAERO_EMAIL")
        SMSAERO_API_KEY = os.getenv("SMSAERO_API_KEY")
        return f"https://{SMSAERO_EMAIL}:{SMSAERO_API_KEY}@gate.smsaero.ru/v2/sms/send?number={self.phone_number}&text={self.message}&sign=SMS Aero"

    @property
    def wazzup_creds(self) -> dict:
        WAZZUP_API_KEY = os.getenv("WAZZUP_API_KEY")
        WAZZUP_CHANNEL_ID = os.getenv("WAZZUP_CHANNEL_ID")
        return {
            "headers": {
                "Authorization": f"Bearer {WAZZUP_API_KEY}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            "data": {
                "channelId": WAZZUP_CHANNEL_ID,
                "chatType": "whatsapp",
                "chatId": self.phone_number,
                "text": self.message,
            },
        }

    async def send_message(self) -> dict:
        async with AsyncClient() as client:
            if self.service_type == "psy":
                res = await client.get(url=self.smsaero_url, timeout=10.0)
                return {"status_code": res.status_code, "data": res.json()}
            elif self.service_type == "clinic":
                res = await client.post(
                    self.wazzup_url, **self.wazzup_creds, timeout=10.0
                )
            return {"status_code": res.status_code, "data": res.text}


async def handle_message(
    service_type: str,
    phone_number: str | None,
    data: Any = Body(None),
    db: AsyncSession = Depends(get_db),
):
    # Обработка начальных данных и отправка реквеста
    message = await services.get_last_message(service_type=service_type)
    if service_type == "clinic":
        rel_phone, deal = await get_rel_phone(data)
        phone_number = rel_phone
        if phone_number == "":
            return None
    sender = MessageSender(
        service_type=service_type,
        phone_number=phone_number,
        message=message.content,
    )
    # Обработка ответа
    response = await sender.send_message()
    if service_type == "psy":
        success = True if response["data"]["success"] else False
        price = response["data"]["data"]["cost"] if success else 0
        deal = None
    elif service_type == "clinic":
        success = True if response["status_code"] == 200 or 201 else False
        price = None
    report = await services.create_msg_report(
        success=success,
        phone_number=phone_number,
        message=message,
        price=price,
        db=db,
        deal=deal,
    )
    details = await create_report_details(report)
    await async_send_tlg(details)
    return report


async def get_rel_phone(data) -> tuple[str]:
    json_data = jsonable_encoder(data)
    parsed_dict = parse_qs(str(json_data))
    deal_id = parsed_dict["document_id[2]"][0].replace("DEAL_", "")
    async with AsyncClient() as client:
        response = await client.get(
            f"https://klinikamsmk.bitrix24.ru/rest/1/565095l7kxskzhlq/crm.deal.get.json?ID={deal_id}"
        )
    rel_phone = "".join(
        filter(str.isdigit, response.json()["result"]["UF_CRM_1677846335"])
    )
    deal = "".join(["https://klinikamsmk.bitrix24.ru/crm/deal/details/",response.json()["result"]["ID"], "/"])
    return rel_phone, deal


async def create_report_details(report: PsyReport | ClinicReport) -> str:
    psy = isinstance(report, PsyReport)
    content = await report.message_content
    message = content[:80] + "..." if len(content) > 100 else content
    time = report.date_created.strftime("%H:%M")
    return f"""<b>{"🟢" if report.success else "🔴"} {"МСМК-Веб" if psy else "[КЛИНИКА]"} | Сообщение {"" if report.success else "не было"} отправлено</b>

<b>Номер</b>: {report.phone_number}
<b>Время:</b> {time}
<b>Сообщение:</b> "{message}"
{f"<b>Сделка:</b> {report.deal}" if not psy else ""}
{f"<b>Стоимость:</b> {report.price} р."  if psy else ""}

{"Скорее всего, номер телефона недействителен. Подробности на https://smsaero.ru/cabinet/sendings/" if psy and report.success == False else ""}
"""
