from aiogram import Router, F, types
from aiogram.filters import Command, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from motor.core import AgnosticDatabase as MDB
from keyboards import reply_builder

router = Router()



class RegistrationStates(StatesGroup):
    START = State()
    PEOPLE = State()
    REGISTRATION = State()
    ACTION = State()
    LETTER = State()


@router.message(or_f(Command(commands=["/send"]), F.text == "📩 Открытки"))
@router.message(RegistrationStates.START)
async def letter(message: types.Message, db: MDB, state: FSMContext):
    user = await db.users.find_one({"_id": message.from_user.id})
    if user["status"] == 0 or user["status"]==3:
        await db.users.update_one({"_id": message.from_user.id}, {"$set": {"status": 3}})
        await state.set_state(RegistrationStates.PEOPLE)
        await message.answer(
            "Пока вас не было, вам пришли эти открытки\!\n"
            "Вы можете заблокировать ответив на открытку командой /block или разблокировать с /unblock\.\n"
            "Либо ответьте отправителю",
            reply_markup = reply_builder(["❌ Прекратить", "✍️ Написать", "↪️ Перезагрузить"])
        )
        letter_cursor = db.waitings.find({'receiver_id': message.from_user.id})
        documents = await letter_cursor.to_list(length=None)
        if not documents:
            await message.answer("Тут пусто")
        else:
            await message.answer("📩 Открытки \(они от разных людей\):\n")
            for document in documents:

                if document['reply']:
                    some = await message.bot.copy_message(chat_id=document["receiver_id"],
                                                            from_chat_id=document["sender_id"],
                                                            message_id= document["_id"],
                                                            reply_to_message_id=document["reply"])
                else:
                    some = await message.bot.copy_message(chat_id=document["receiver_id"],
                                                          from_chat_id=document["sender_id"],
                                                          message_id=document["_id"])
                await db.waitings.delete_one({"_id": document["_id"]})
                mess = {"_id": document["_id"],
                        "rec_message_id": some.message_id,
                        "receiver_id": document["receiver_id"],
                        "sender_id": document["sender_id"]}
                await db.conv.insert_one(mess)
    else:
        pattern = {
            "text": (
                "<b>☕ У вас уже есть активный чат</b>\n"
                "Либо вы в поиске собесенлника 🗣\n"
                "<i>Используй команду /leave или /cancel</i>"
            ),
            "reply_markup": reply_builder("❌ Прекратить")
        }
        await message.reply(**pattern)

@router.message(RegistrationStates.PEOPLE, F.text == "↪️ Перезагрузить")
async def register_user(message: types.Message, db: MDB, state: FSMContext):
    await message.answer(
        "Пока вас не было, вам пришли эти открытки\!\n"
        "Вы можете заблокировать ответив на открытку командой /block или разблокировать с /unblock\.\n"
        "Либо ответьте отправителю")
    letter_cursor = db.waitings.find({'receiver_id': message.from_user.id})
    documents = await letter_cursor.to_list(length=None)
    if not documents:
        await message.answer("Тут пусто")
    else:
        await message.answer("📩 Открытки \(они от разных людей\):\n")
        for document in documents:
            if document['reply']:
                some = await message.bot.copy_message(chat_id=document["receiver_id"],
                                                      from_chat_id=document["sender_id"],
                                                      message_id=document["_id"],
                                                      reply_to_message_id=document["reply"])
            else:
                some = await message.bot.copy_message(chat_id=document["receiver_id"],
                                                      from_chat_id=document["sender_id"],
                                                      message_id=document["_id"])
            await db.waitings.delete_one({"_id": document["_id"]})
            mess = {"_id": document["_id"],
                    "rec_message_id": some.message_id,
                    "receiver_id": document["receiver_id"],
                    "sender_id": document["sender_id"]}
            await db.conv.insert_one(mess)


@router.message(RegistrationStates.PEOPLE, F.text == "✍️ Написать")
async def register_user(message: types.Message, db: MDB, state: FSMContext):
    await state.set_state(RegistrationStates.REGISTRATION)
    # Set the user's state to USERNAME
    await message.answer("Пожалуйста, введите имя пользователя \(standard\_username\):",
                             reply_markup=reply_builder("❌ Прекратить"))


@router.message(RegistrationStates.PEOPLE)
async def register_user(message: types.Message, db: MDB, state: FSMContext):
    if message.reply_to_message:
        user = await db.users.find_one({"_id": message.from_user.id})
        if message.text == "/block": #здесь происходит блок пользователя по сообщению
            conversation = await db.conv.find_one({"rec_message_id": message.reply_to_message.message_id})
            user = await db.blocked.find_one({"user_id": message.from_user.id})
            if conversation["sender_id"] not in user["block"]:
                await db.blocked.update_one({"user_id": message.from_user.id}, {'$push': {"block": conversation["sender_id"]}})
            await message.reply("Теперь, этот пользователь теперь не сможет отправить вам открытки")
        elif message.text == "/unblock": #здесь происходит разблокировка пользователя по сообщению
            conversation = await db.conv.find_one({"rec_message_id": message.reply_to_message.message_id})
            user = await db.blocked.find_one({"user_id": message.from_user.id})
            if conversation["sender_id"] in user["block"]:
                await db.blocked.update_one({"user_id": message.from_user.id}, {'$pull': {"block": conversation["sender_id"]}})
            await message.reply("Теперь этот пользователь открыт к общению")
        else:
            #Происходит отправка ответов от неизвестного пользователя
            query = {"$or": [{"rec_message_id": message.reply_to_message.message_id},
                             {"_id": message.reply_to_message.message_id}]}
            conversation = await db.conv.find_one(query)
            if not conversation:
                await message.reply("Вы можете ответить только на последнее сообщение человека, либо ваше сообщение ещё не прочитали\n")
            else:
                if message.reply_to_message.from_user.id == message.from_user.id:
                #Продолжение цепочки ответов от неизвестного пользователя
                    mess = {"_id": message.message_id, "receiver_id": conversation["receiver_id"],
                            "sender_id": conversation["sender_id"], "reply": conversation["rec_message_id"]}
                    receiver_type = await db.allowance.find_one({"user_id": conversation["receiver_id"]},
                                                                {"_id": 0, "user_id": 0})
                    allowed_types = list(receiver_type.keys())
                    allowed_list = list(filter(lambda x: receiver_type[x] == True, allowed_types))
                else:
                    # Продолжение цепочки ответом на сообщение неизвестного пользователя
                    mess = {"_id": message.message_id, "receiver_id": conversation["sender_id"],
                            "sender_id": conversation["receiver_id"], "reply": conversation["_id"]}
                    receiver_type = await db.allowance.find_one({"user_id": conversation["sender_id"]}, {"_id": 0, "user_id": 0})
                    allowed_types = list(receiver_type.keys())
                    allowed_list = list(filter(lambda x: receiver_type[x] == True, allowed_types))
                #Происходит проверка не заблокирован ли пользователь
                block = await db.blocked.find_one({"user_id": mess["receiver_id"], "block": mess["sender_id"]}, {"_id": 0, "block": 1})
                if block:
                    await message.reply(
                        "Этот пользователь вас заблокировал 😕\n"
                        "Напишите другое имя пользователя"
                    )
                elif message.content_type in allowed_list:
                    await message.answer("Отправленно, теперь ждём")
                    await db.conv.delete_one({"_id": conversation["_id"]})
                    await db.waitings.insert_one(mess)
                else:
                    await message.reply(f"Пользователь не принимает такой вид сообщении\n"
                                        "Отправьте что-то другое",
                                        reply_markup=reply_builder("❌ Прекратить"))
                    await message.answer("Вы можете только ответить на последнее сообщение отправителя\n"
                                         "с уже отвеченными ничего сделать нельзя")
    else:
        await message.answer("Отправьте возможные иконки, либо ответьте на сообщение")





@router.message(RegistrationStates.REGISTRATION)
async def registration(message: types.Message, db: MDB, state: FSMContext):
    receiver_name = message.text
    receiver = await db.users.find_one({"username": receiver_name})
    if receiver:

        if not receiver["letter"]:
            await message.reply(
                "Этот пользователь сейчас не хочет принимать сообщения \n"
                "Напишите позже 🙃"
            )
        else:
            block = await db.blocked.find_one({"user_id": receiver["_id"], "block": message.from_user.id}, {"_id": 0, "block": 1})
            if block:
                await message.reply(
                    "Этот пользователь вас заблокировал 😕\n"
                    "Напишите другое имя пользователя"
                )
            else:
                await state.update_data(user_id=message.from_user.id)
                await state.update_data(receiver_id=receiver["_id"])
                await state.set_state(RegistrationStates.ACTION)
                await message.reply(
                        "*🕊 Вы можете отправить открытку, заблокировать, либо разблокировать пользователя*",
                        reply_markup=reply_builder(["📩 Отправить",
                                                    "💩 В блок",
                                                    "🔓 Разблокировать",
                                                    "❌ Прекратить"]))
    else:
        await message.reply(
            "Этот пользователь ещё не использует нашего бота или вероятно вы написали с \"@\", а нужно просто \"имя\_пользователя\" \n"
            "Напишите ещё раз"
        )


@router.message(RegistrationStates.ACTION)
async def action(message: types.Message, db: MDB, state: FSMContext):
    action = message.text
    if action == "📩 Отправить":
        await message.reply("Хорошо, слушаю вас", reply_markup=reply_builder("❌ Прекратить"))
        await state.set_state(RegistrationStates.LETTER)
    elif action == "💩 В блок":
        data = await state.get_data()
        receiver_id = data.get('receiver_id')
        user = await db.blocked.find_one({"user_id": message.from_user.id})
        if receiver_id not in user["block"]:
            await db.blocked.update_one({"user_id": message.from_user.id}, {'$push': {"block": receiver_id}})
        await message.reply("Теперь, этот пользователь теперь не сможет отправить вам открытку", reply_markup=reply_builder("Продолжить ➡️"))
        await state.clear()
        await state.set_state(RegistrationStates.START)
    elif action == "🔓 Разблокировать":
        data = await state.get_data()
        receiver_id = data.get('receiver_id')
        user = await db.blocked.find_one({"user_id": message.from_user.id})
        if receiver_id in user["block"]:
            await db.blocked.update_one({"user_id": message.from_user.id}, {'$pull': {"block": receiver_id } })
        await message.reply("Теперь этот пользователь открыт к общению", reply_markup=reply_builder("Продолжить ➡️"))
        await state.clear()
        await state.set_state(RegistrationStates.START)
    else:
        await message.reply("Что-то не так, выберите возможные действия")



# Handler for handling message
@router.message(RegistrationStates.LETTER)
async def final(message: types.Message, db: MDB, state: FSMContext):
    data = await state.get_data()
    receiver_id = data.get('receiver_id')
    receiver_type = await db.allowance.find_one({"user_id": receiver_id}, {"_id": 0, "user_id": 0})
    allowed_types = list(receiver_type.keys())
    allowed_list = list(filter(lambda x: receiver_type[x] == True, allowed_types))
    if message.content_type in allowed_list:
        sender_id = message.from_user.id
        mess = {"_id": message.message_id,"receiver_id": receiver_id,"sender_id": sender_id, "reply": 0}
        await db.waitings.insert_one(mess)
        await message.reply(f"Открытка отправлена", reply_markup=reply_builder("Продолжить ➡️"))
        # Finish the registration process by resetting the state
        await state.clear()
        await state.set_state(RegistrationStates.START)
    else:
        await message.reply(f"Пользователь не принимает " + message.content_type + "\.\n"
                            "Отправьте что-то другое ",
                            reply_markup=reply_builder("❌ Прекратить"))