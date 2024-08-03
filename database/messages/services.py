from datetime import datetime, timedelta
from database.core import async_session
from database.messages.models import (
    PsyReport,
    ClinicReport,
    PsyMessage,
    ClinicMessage,
    Role,
    User,
)
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession


async def create_msg_report(
    message: PsyMessage | ClinicMessage,
    phone_number: str,
    success: bool,
    price: float | None,
    deal: str | None,
    db: AsyncSession,
):
    kwargs = {
        "message": message,
        "phone_number": phone_number,
        "success": success,
        "message_id": message.id,
    }
    if isinstance(message, PsyMessage):
        msg_report = PsyReport(**kwargs, price=price)
    elif isinstance(message, ClinicMessage):
        msg_report = ClinicReport(**kwargs, deal=deal)
    db.add(msg_report)
    await db.commit()
    await db.refresh(msg_report)
    return msg_report


async def create_message(service_type: str, content: str, user_id: int):
    kwargs = {"content": content, "user_id": user_id}
    async with async_session() as db:
        if service_type == "psy":
            msg = PsyMessage(**kwargs)
        elif service_type == "clinic":
            msg = ClinicMessage(**kwargs)
        db.add(msg)
        await db.commit()
        await db.refresh(msg)
        return msg


async def get_last_message(service_type: str):
    async with async_session() as db:
        if service_type == "psy":
            return await db.scalar(select(PsyMessage).order_by(PsyMessage.id.desc()))
        elif service_type == "clinic":
            return await db.scalar(
                select(ClinicMessage).order_by(ClinicMessage.id.desc())
            )


async def get_all_messages(service_type: str):
    async with async_session() as db:
        if service_type == "psy":
            return await db.scalars(select(PsyMessage).order_by(PsyMessage.id.desc()))
        elif service_type == "clinic":
            return await db.scalars(
                select(ClinicMessage).order_by(ClinicMessage.id.desc())
            )


async def get_message_by_id(service_type: str, msg_id: int):
    async with async_session() as db:
        if service_type == "psy":
            return await db.scalar(select(PsyMessage).where(PsyMessage.id == msg_id))
        elif service_type == "clinic":
            return await db.scalar(
                select(ClinicMessage).where(ClinicMessage.id == msg_id)
            )


async def delete_message_by_id(service_type: str, msg_id: int):
    async with async_session() as db:
        if service_type == "psy":
            message = await db.scalar(select(PsyMessage).where(PsyMessage.id == msg_id))
        elif service_type == "clinic":
            message = await db.scalar(
                select(ClinicMessage).where(ClinicMessage.id == msg_id)
            )
        await db.delete(message)
        await db.commit()


async def get_users_by_role(role: Role):
    async with async_session() as db:
        res = await db.scalars(select(User).where(User.role == role))
        return res


async def get_user_by_tg_id(tg_id: int):
    async with async_session() as db:
        res = await db.scalar(select(User).where(User.tg_id == tg_id))
        return res


async def create_user(tg_id: int):
    async with async_session() as db:
        user = await db.scalar(select(User).where(User.tg_id == tg_id))
        if user:
            return None
        new_user = User(tg_id=tg_id)
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user


async def update_user_role(tg_id: int, role: Role):
    async with async_session() as db:
        await db.execute(update(User).where(User.tg_id == tg_id).values({"role": role}))
        await db.commit()
        return await db.scalar(select(User).where(User.tg_id == tg_id))


# GATHER REPORTS


async def get_daily_reports(service_type: str):
    async with async_session() as db:
        now = datetime.now()
        start_of_day = datetime(now.year, now.month, now.day)
        end_of_day = start_of_day + timedelta(days=1)
        if service_type == "psy":
            return db.scalars(
                select(PsyReport).where(
                    PsyReport.date_created >= start_of_day,
                    PsyReport.date_created < end_of_day,
                )
            )
        if service_type == "clinic":
            return db.scalars(
                select(ClinicReport).where(
                    ClinicReport.date_created >= start_of_day,
                    ClinicReport.date_created < end_of_day,
                )
            )


# DEBUG FUNCS


async def get_report_by_id(service_type: str, id: int):
    async with async_session() as db:
        if service_type == "psy":
            return await db.scalar(select(PsyReport).where(PsyReport.id == id))
        elif service_type == "clinic":
            return await db.scalar(select(ClinicReport).where(ClinicReport.id == id))
