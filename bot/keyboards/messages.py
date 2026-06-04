from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.messages import services
from aiogram_widgets.pagination import KeyboardPaginator
from aiogram import Router


message_managment_kb = types.InlineKeyboardMarkup(
    inline_keyboard=[
        [
            types.InlineKeyboardButton(
                text="Управление рассылками МСМК PSY",
                callback_data="psy_messages_panel",
            )
        ],
        [
            types.InlineKeyboardButton(
                text="Управление рассылками Клиники МСМК",
                callback_data="clinic_messages_panel",
            )
        ],
        [
            types.InlineKeyboardButton(
                text="⬅️ Назад", callback_data="back_start"
            )
        ]
    ]
)


def messages_panel_kb(service_type: str) -> InlineKeyboardBuilder:
    keyboard = InlineKeyboardBuilder()
    cmd_list = ["Управление рассылками МСМК PSY", "Управление рассылками Клиники МСМК"]
    for text in cmd_list:
        keyboard.add(types.InlineKeyboardButton(text=text, callback_data="".join([service_type, "_messages_panel"])))
    return keyboard.adjust(1).as_markup()


def messages_kb(service_type: str) -> InlineKeyboardBuilder:
    keyboard = InlineKeyboardBuilder()
    cmd_dict = {
        "Добавить новое сообщение": "_messages_add",
        "Список всех сообщений": "_messages_get_all",
        "Посмотреть последнее сообщение": "_messages_get_last",
    }
    for text, data in cmd_dict.items():
        keyboard.add(
            types.InlineKeyboardButton(
                text=text, callback_data="".join([service_type, data])
            )
        )
    keyboard.add(
        types.InlineKeyboardButton(text="⬅️ Назад", callback_data="msg_management"))
    return keyboard.adjust(1).as_markup()


async def get_all_messages(router: Router, service_type: str) -> InlineKeyboardBuilder:
    all_messages = await services.get_all_messages(service_type=service_type)
    buttons = []
    i = 0
    for msg in all_messages:
        i += 1
        btn = types.InlineKeyboardButton(
            text=f"{i}. {msg.content[:40]+"..." if len(msg.content) > 40 else msg.content}",
            callback_data=f"{service_type}_getmsg_{msg.id}",
        )
        buttons.append(btn)
    additional_buttons = [[types.InlineKeyboardButton(text="⬅️ Назад", callback_data=f"{service_type}_messages_panel")]]
    paginator = KeyboardPaginator(router=router, data=buttons, additional_buttons=additional_buttons, per_page=10, per_row=1)
    return paginator.as_markup()


def delete_message_kb(service_type: str, msg_id: int, del_type: str):
    keyboard = InlineKeyboardBuilder()
    if del_type == "from_all":
        callback_data = f"{service_type}_messages_get_all"
    elif del_type == "from_one":
        callback_data = f"{service_type}_messages_panel"       
    keyboard.add(types.InlineKeyboardButton(text="❌ Удалить сообщение", callback_data=f"{service_type}_delmsg_{msg_id}"))
    keyboard.add(types.InlineKeyboardButton(text="⬅️ Назад", callback_data=callback_data))
    return keyboard.adjust(1).as_markup()


def go_back_kb(where: str):
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(text="⬅️ Назад", callback_data=where)
            ]
        ]
    )
