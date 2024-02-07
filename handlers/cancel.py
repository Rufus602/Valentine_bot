from aiogram import Router, F, types
from aiogram.filters import Command, or_f
from motor.core import AgnosticDatabase as MDB
from keyboards import  main_kb
from aiogram.fsm.context import FSMContext

router = Router()

@router.message(or_f(Command(commands=["cancel","leave", "stop"]), F.text == "❌ Прекратить"))
async def cmd_cancel(message: types.Message, db: MDB, state: FSMContext) -> None:
    print("in cancel")
    user = await db.users.find_one({"_id": message.from_user.id})
    if user["status"] == 2:
        await message.reply("*💬 Ты покинул чат!*")
        await message.bot.send_message(
            user["interlocutor"], "*💬 Собеседник покинул чат!*"
        )

        await db.users.update_many(
            {"_id": {"$in": [user["_id"], user["interlocutor"]]}},
            {"$set": {"status": 0, "interlocutor": ""}}
        )
    elif user["status"] == 1:
        await message.reply("Понял, отмена")
        await db.users.update_one({"_id": message.from_user.id}, {"$set": {"status": 0}})
    elif user["status"] == 3:
        await state.clear()

        await message.reply("Понял, отмена")
        await db.users.update_one({"_id": message.from_user.id}, {"$set": {"status": 0}})
    else:
        await message.reply("Слушаю вас")

    searchers = await db.users.count_documents({"status": 1})
    result = await db.waitings.aggregate([
        {"$match": {"receiver_id": message.from_user.id}},
        {"$group": {"_id": None, "count": {"$sum": 1}}}
    ]).to_list(1)

    count = result[0]["count"] if result else 0
    await message.answer(
        "*☕ Привет, вы можете отправить открытку \(никто не узнает от кого\), либо начать анонимный чат\!*\n"
        f"_👀 Ты можешь пообщаться ещё с :_ `{searchers}` людьми\n"
        f"_📩 Также вас ожидают :_ `{count}` открыток",
        reply_markup=main_kb
    )