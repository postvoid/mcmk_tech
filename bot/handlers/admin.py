from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Filter, CommandStart
from database.messages import services
import keyboards.admin as kb


router = Router()


async def get_admin_list():
    admins = []
    for manager in await services.get_users_by_role("Admin"):
        admins.append(manager.tg_id)
    return admins


class AdminProtect(Filter):
    async def __call__(self, message: Message):
        return message.from_user.id in await get_admin_list()


router.message.filter(AdminProtect())
router.callback_query.filter(AdminProtect())


@router.message(CommandStart())
async def cmd_admin_start(message: Message):
    await message.answer(
        f"Добро пожаловать, {message.from_user.full_name}! Вот список доступных действий:",
        reply_markup=kb.start_kb,
    )
