from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, or_f
from motor.core import AgnosticDatabase as MDB
from keyboards import inline_builder
from utils import ProfileSettings

router = Router()

#There user can work with own profile to change format
@router.message(or_f(Command("profile"), F.text == "🍪 Профиль"))
async def profile(message: Message, db: MDB):
    await db.users.update_one({"_id": message.from_user.id}, {"$set": {"status": 0}})
    result = await db.users.find_one({"_id": message.from_user.id}, {"_id": 0, "letter": 1})
    letter = result["letter"]
    await message.reply(
        f"Привет, *{message.from_user.first_name}*\!",
        reply_markup=inline_builder(
            f"🟢 Получение открыток" if letter else "🔴 Получение открыток",
            ProfileSettings(value="receive_message_toggle").pack(),
            sizes=1
        )
    )
