from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
)
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.messages import services
# import bot.keyboards_depr as kb
import keyboards.user as kb 
import keyboards.admin as admin_kb
import os
from dotenv import load_dotenv
import bcrypt


load_dotenv()


tg_hashed_password = os.getenv("TG_HASHED_PASSWORD")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


class SetAdmin(StatesGroup):
    password = State()


router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await services.create_user(tg_id=message.from_user.id)
    await message.answer(f"Войдите в систему", reply_markup=kb.login_kb)


@router.callback_query(F.data == "chrole_admin")
async def cmd_set_admin(callback: CallbackQuery, state: FSMContext):
    await callback.answer("")
    await state.set_state(SetAdmin.password)
    await callback.message.edit_text("Введите пароль администратора")


@router.message(SetAdmin.password)
async def cmd_get_admin_pass(message: Message, state: FSMContext):
    is_valid = verify_password(message.text, tg_hashed_password)
    await message.delete()
    if is_valid:
        await services.update_user_role(tg_id=message.from_user.id, role="Admin")
        await message.answer(
            "Ура! Теперь ты админ :)", reply_markup=admin_kb.start_kb
        )
        state.clear()
    else:
        await message.answer(
            "Неверный пароль, отправьте его еще раз или вернитесь в начало коммандой /start",
        )
        await state.set_state(SetAdmin.password)
