from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database.messages import services
from database.messages.models import PsyReport
from database.messages.services import get_users_by_role
from aiogram.enums import ParseMode
from functools import partial


async def handle_daily_reports(reports) -> dict:
    quantity = 0
    daily_price = 0
    success = []
    unsuccess = []
    for report in await reports:
        quantity += 1
        if isinstance(report, PsyReport):
            daily_price += report.price
        if report.success:
            success.append(report)
        else:
            unsuccess.append(report)
    return {
        "quantity": quantity,
        "success": len(success),
        "unsuccess": len(unsuccess),
        "price": round(daily_price, 2),
    }


def create_daily_report_message(daily: dict, service_type: str) -> str:
    today = datetime.now().strftime("%d.%m.%Y")
    psy = service_type == "psy"
    return f"""
<b>📑 {"Веб-МСМК" if psy else "Клиника"} | Отчет за {today}</b>
Отправлено <b>{daily["quantity"]}</b> сообщений
<b>Успешных:</b> {daily["success"]}, неуспешных: {daily["unsuccess"]}
{f"<b>Потрачено:</b> {daily["price"]} р." if psy else ""}
"""


async def send_reports_to_admins(bot, report_data: dict, service_type: str):
    if report_data["quantity"] >= 1:
        message = create_daily_report_message(report_data, service_type)
        for admin in await get_users_by_role("Admin"):
            await bot.send_message(
                admin.tg_id,
                message,
                parse_mode=ParseMode.HTML,
            )


async def gather_psy_reports(bot):
    psy_reports = await services.get_daily_reports(service_type="psy")
    psy_daily = await handle_daily_reports(reports=psy_reports)
    await send_reports_to_admins(bot, psy_daily, "psy")


async def gather_clinic_reports(bot):
    clinic_reports = await services.get_daily_reports(service_type="clinic")
    clinic_daily = await handle_daily_reports(reports=clinic_reports)
    await send_reports_to_admins(bot, clinic_daily, "clinic")


async def schedule_jobs(bot):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(partial(gather_psy_reports, bot), "cron", hour=20, minute=00)
    scheduler.add_job(partial(gather_clinic_reports, bot), "cron", hour=23, minute=59)
    scheduler.start()
