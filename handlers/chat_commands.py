from aiogram import Router, F
from aiogram.filters import Command, or_f

from aiogram.types import Message
from motor.core import AgnosticDatabase as MDB
from keyboards import reply_builder, main_kb

router = Router()


@router.message(or_f(Command("search"), F.text == "☕ Искать собеседника"))
async def search_interlocutor(message: Message, db: MDB) -> None:
    print("in messaging")
    user = await db.users.find_one({"_id": message.from_user.id})
    pattern = {
        "text": (
            "*☕ У вас уже есть активный чат*\n"
            "Либо вы читаете открытки 📨\n"
            "_Используйте команду /leave или /cancel_"
        ),
        "reply_markup": reply_builder("❌ Прекратить")
    }

    if user["status"] == 0:
        interlocutor = await db.users.find_one({"status": 1})
        await db.users.update_one({"_id": user["_id"]}, {"$set": {"status": 1}})

        if not interlocutor:
            pattern["text"] = (
                "*👀 Ищу тебе собеседника\.\.\.*\n"
                "/cancel _\- Отменить поиск собеседника_"
            )
            pattern["reply_markup"] = reply_builder("❌ Прекратить")
        else:
            pattern["text"] = (
                "*🎁 Я нашел тебе собеседника, приятного общения\!*\n"
                "/next _\- Следующий собеседник_\n"
                "/leave _\- Прекратить диалог_"
            )
            pattern["reply_markup"] = reply_builder("❌ Прекратить")

            await db.users.update_one(
                {"_id": user["_id"]}, {"$set": {"status": 2, "interlocutor": interlocutor["_id"]}}
            )
            await db.users.update_one(
                {"_id": interlocutor["_id"]}, {"$set": {"status": 2, "interlocutor": user["_id"]}}
            )
            await message.bot.send_message(interlocutor["_id"], **pattern)
    elif user["status"] == 1:
        pattern["text"] = (
            "*👀 УЖЕ ИЩУ тебе собеседника\.\.\.*\n"
            "/cancel _\- Отменить поиск собеседника_"
        )
        pattern["reply_markup"] = reply_builder("❌ Прекратить")

    await message.reply(**pattern)


@router.message(Command("next"))
async def next_interlocutor(message: Message, db: MDB) -> None:
    print("in next")
    user = await db.users.find_one({"_id": message.from_user.id})
    if user["status"] == 2:
        await message.bot.send_message(
            user["interlocutor"], "*💬 Собеседник покинул чат\!*", reply_markup=main_kb
        )
        await db.users.update_many(
            {"_id": {"$in": [user["_id"], user["interlocutor"]]}},
            {"$set": {"status": 0, "interlocutor": ""}}
        )

    await search_interlocutor(message, db)