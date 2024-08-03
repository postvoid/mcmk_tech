from aiogram import types


login_kb = types.InlineKeyboardMarkup(
    inline_keyboard=[
        [
            types.InlineKeyboardButton(
                text="Войти как администратор",
                callback_data="chrole_admin",
            )
        ]
    ]
)
