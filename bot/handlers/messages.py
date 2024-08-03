from types import NoneType
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.enums import ParseMode
from database.messages import services
from handlers.admin import AdminProtect
import keyboards.admin as admin_kb
import keyboards.messages as kb


router = Router()


class AddMessage(StatesGroup):
    message = State()


router.message.filter(AdminProtect())
router.callback_query.filter(AdminProtect())


@router.callback_query(F.data == "back_start")
async def cmd_main_menu(callback: CallbackQuery):
    await callback.answer("")
    await callback.message.edit_text(
        "Список доступных действий:",
        reply_markup=admin_kb.start_kb,
    )


@router.callback_query(F.data == "msg_management")
async def cmd_msg_management(callback: CallbackQuery):
    await callback.answer("")
    await callback.message.edit_text(
        "Выберите категорию рассылок", reply_markup=kb.message_managment_kb
    )


@router.callback_query(F.data.endswith("_messages_panel"))
async def cmd_choose_msg_cat(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer("")
    service_type = callback.data.split("_")[0]
    await callback.message.edit_text(
        "Выберите действие", reply_markup=kb.messages_kb(service_type=service_type)
    )


@router.callback_query(F.data.endswith("_messages_add"))
async def cmd_add_msg_s1(callback: CallbackQuery, state: FSMContext):
    await callback.answer("")
    await state.set_state(AddMessage.message)
    service_type = callback.data.split("_")[0]
    await state.update_data(service_type=service_type)
    if callback.data.startswith("psy"):
        await callback.message.edit_text(
            "Отправьте текст сообщения\n\nВнимание! Текст сообщения не должен превышать 70 символов!",
            reply_markup=kb.go_back_kb(f"{service_type}_messages_panel"),
        )
    elif callback.data.startswith("clinic"):
        await callback.message.edit_text(
            "Отправьте текст сообщения",
            reply_markup=kb.go_back_kb(f"{service_type}_messages_panel"),
        ),


@router.message(AddMessage.message)
async def cmd_add_msg_s2(message: Message, state: FSMContext):
    user_data = await state.get_data()
    service_type = user_data["service_type"]
    content = message.text
    user = await services.get_user_by_tg_id(tg_id=message.from_user.id)
    msg = await services.create_message(
        service_type=service_type, content=content, user_id=user.id
    )
    await message.answer(
        f"🟢 Сообщение успешно создано!\n\n<b>Текст сообщения:</b> «{msg.content}»",
        parse_mode=ParseMode.HTML,
        reply_markup=kb.go_back_kb(f"{service_type}_messages_panel"),
    )
    await state.clear()


@router.callback_query(F.data.endswith("_messages_get_last"))
async def cmd_get_last_message(callback: CallbackQuery):
    await callback.answer("")
    service_type = callback.data.split("_")[0]
    msg = await services.get_last_message(service_type=service_type)
    date = msg.date_created.strftime("%d.%m.%Y, %H:%M")
    if isinstance(msg, NoneType):
        await callback.message.edit_text("Сообщения не найдены")
    else:
        await callback.message.edit_text(
            f"<b>Текст сообщения:</b> «{msg.content}»\n\n<b>Создано:</b> {date}\n\n",
            parse_mode=ParseMode.HTML,
            reply_markup=kb.delete_message_kb(
                service_type=service_type, msg_id=msg.id, del_type="from_one"
            ),
        )


@router.callback_query(F.data.endswith("_messages_get_all"))
async def cmd_get_all_messages(callback: CallbackQuery):
    await callback.answer("")
    service_type = callback.data.split("_")[0]
    await callback.message.edit_text(
        "Список всех сообщений",
        reply_markup=await kb.get_all_messages(
            router=router, service_type=service_type
        ),
    )


@router.callback_query(F.data.split("_")[1] == "getmsg")
async def cmd_get_msg(callback: CallbackQuery):
    await callback.answer("")
    service_type = callback.data.split("_")[0]
    msg_id = int(callback.data.split("_")[-1])
    msg = await services.get_message_by_id(service_type=service_type, msg_id=msg_id)
    date = msg.date_created.strftime("%d.%m.%Y, %H:%M")
    await callback.message.edit_text(
        f"<b>Текст сообщения:</b> «{msg.content}»\n\n<b>Создано:</b> {date}\n\n",
        parse_mode=ParseMode.HTML,
        reply_markup=kb.delete_message_kb(
            service_type=service_type, msg_id=msg_id, del_type="from_all"
        ),
    )


@router.callback_query(F.data.split("_")[1] == "delmsg")
async def cmd_delete_msg(callback: CallbackQuery):
    await callback.answer("")
    service_type = callback.data.split("_")[0]
    msg_id = int(callback.data.split("_")[-1])
    await services.delete_message_by_id(service_type=service_type, msg_id=msg_id)
    await callback.message.edit_text(
        f"Сообщение {msg_id} удалено!",
        reply_markup=kb.go_back_kb(f"{service_type}_messages_get_all"),
    )


# TEST CMDS

# class SingleMessage(StatesGroup):
#     message = State()


# @router.message(Command("add_msgs"))
# async def add_messages(message: Message):
#     user = await services.get_user_by_tg_id(tg_id=message.from_user.id)
#     n = 10
#     for i in range(0, n):
#         await services.create_message(
#             service_type="clinic", content=f"Test message {i}", user_id=user.id
#         )
#     await message.answer(f"Добавлено {n} сообщений")


# @router.message(Command("send_one"))
# async def send_one_s1(message: Message, state: FSMContext):
#     await state.set_state(SingleMessage.message)
#     await message.answer("Введите текст сообщения, которое хотите отправить")


# @router.message(SingleMessage.message)
# async def send_one_s2(message: Message, state: FSMContext):
#     await state.update_data(message=message.text)
#     await state.set_state(SingleMessage.phone_number)
#     await message.answer("Введите номер телефона")


# @router.message(SingleMessage.phone_number)
# async def send_one_s2(message: Message, state: FSMContext):
#     message = await state.get_data(message)
#     phone = await message.text
#     await message.answer("Сообщение отправлено")
