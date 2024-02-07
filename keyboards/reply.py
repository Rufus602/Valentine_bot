from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

rmk = ReplyKeyboardRemove()

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="☕ Искать собеседника")
        ],
        [
            KeyboardButton(text="📩 Открытки")
        ],
        [
            KeyboardButton(text="🍪 Профиль")
        ],
        [
            KeyboardButton(text="⚙️ Настройки")
        ]
    ],
    resize_keyboard=True
)