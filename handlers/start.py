from contextlib import suppress

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from motor.core import AgnosticDatabase as MDB
from pymongo.errors import DuplicateKeyError

from keyboards import main_kb

router = Router()

#Тут происходит работат над созданием сервера. Новым стало возможности настроики input и концепция открыток
@router.message(CommandStart())
async def start(message: Message, db: MDB) -> None:
    await db.users.update_one({"_id": message.from_user.id}, {"$set": {"status": 0}})
    with suppress(DuplicateKeyError):

        await db.users.insert_one({
            "_id": message.from_user.id,
            "username": message.from_user.username,
            "letter": True,
            "status": 0,
        })

        
        await db.allowance.insert_one({
            "user_id": message.from_user.id,
            "text": True,
            "photo": True,
            "audio": True,
            "voice": True,
            "document": True,
            "sticker": True,
            "video": True,
            "animation": True
        })

        await db.blocked.insert_one({
            "user_id": message.from_user.id,
            "block": [],
        })

    searchers = await db.users.count_documents({"status": 1})
    result = await db.waitings.aggregate([
        {"$match": {"receiver_id": message.from_user.id}},
        {"$group": {"_id": None, "count": {"$sum": 1}}}
    ]).to_list(1)

    count = result[0]["count"] if result else 0
    await message.reply(
        "*☕ Привет, вы можете отправить открытку \(никто не узнает от кого\), либо начать анонимный чат\!*\n"
        f"_👀 Ты можешь пообщаться ещё с :_ `{searchers}` людьми\n"
        f"_📩 Также вас ожидают :_ `{count}` открыток",
        reply_markup=main_kb
    )