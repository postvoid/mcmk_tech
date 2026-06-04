from aiogram import types

start_kb = types.InlineKeyboardMarkup(
    inline_keyboard=[
        [
            types.InlineKeyboardButton(
                text="Управление рассылками", callback_data="msg_management"
            )
        ]
    ]
)

