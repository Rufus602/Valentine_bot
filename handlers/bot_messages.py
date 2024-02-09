from aiogram import Router, F
from aiogram.types import Message
from motor.core import AgnosticDatabase as MDB

router = Router()


@router.edited_message()
async def editing_messages(message: Message, db: MDB) -> None:
    user = await db.users.find_one({"_id": message.from_user.id})
    if user["status"] == 2:
        if message.text:
            await message.bot.edit_message_text(message.text, user["interlocutor"], message.message_id + 1)
        elif message.caption:
            await message.bot.edit_message_caption(
                message.caption,
                user["interlocutor"],
                message.message_id + 1,
                caption_entities=message.caption_entities,
                parse_mode=None
            )
    if user["status"] == 3:
        await message.reply(f"Пользователь не принимает " + message.content_type + ".\n"
                                                                                   "Отправьте что-то другое ")
        # letter = await db.users.find_one({"waiting": message.message_id})
        # if letter:
        #     receiver_id = letter["waiting"][message.message_id][0]
        #     sender_id = letter["waiting"][message.message_id][1]
        #     result = {message.message_id+1: [receiver_id, sender_id]}
        #     await db.users.update({"waiting": message.message_id},
        #                               {"$push": {"waiting": result}})
        #     await db.users.update({"waiting": message.message_id},
        #                                {"$pull": {"waiting": message.message_id}})
        #     await db.users.update({"conv": message.message_id},{"$push": {"conv": result}})
        #     await db.users.update({"conv": message.message_id}, {"$pull": {"conv": message.message_id}})
        #     if message.text:
        #
        #         await message.bot.edit_message_text(message.text, receiver_id, message.message_id + 1)
        #     elif message.caption:
        #         await message.bot.edit_message_caption(
        #             message.caption,
        #             receiver_id,
        #             message.message_id + 1,
        #             caption_entities=message.caption_entities,
        #             parse_mode=None
        #         )
        # else:
        #     conv = await db.users.find_one({"conv.message": message.message_id})
        #     receiver_id = conv["conv"][message.message_id][0]
        #     sender_id = conv["conv"][message.message_id][1]
        #     result = {message.message_id + 1: [receiver_id, sender_id]}
        #     await db.users.updateMany({"conv": message.message_id}, {"$push": {"conv": result}})
        #     await db.users.updateMany({"conv": message.message_id}, {"$pull": {"conv": message.message_id}})
        #     receiver_id = conv[0]
        #     if message.text:
        #         await message.bot.edit_message_text(message.text, receiver_id, message.message_id + 1)
        #     elif message.caption:
        #         await message.bot.edit_message_caption(
        #             message.caption,
        #             receiver_id,
        #             message.message_id + 1,
        #             caption_entities=message.caption_entities,
        #             parse_mode=None
        #         )
        #     await db.users.find_one({"waiting.message": message.message_id}, )


@router.message(F.content_type.in_(
        [
            "text", "audio", "voice",
            "sticker", "document", "photo",
            "video", "animation"
        ]
    )
)
async def echo(message: Message, db: MDB) -> None:

    user = await db.users.find_one({"_id": message.from_user.id})

    if user["status"] == 2:
        receiver_type = await db.allowance.find_one({"user_id": user["interlocutor"]}, {"_id": 0, "user_id": 0})
        allowed_types = list(receiver_type.keys())
        allowed_list = list(filter(lambda x: receiver_type[x] == True, allowed_types))
        if message.content_type in allowed_list:
            reply = None
            if message.reply_to_message:
                if message.reply_to_message.from_user.id == message.from_user.id:
                    reply = message.reply_to_message.message_id + 1
                else:
                    reply = message.reply_to_message.message_id - 1
            if message.content_type == "text":
                await message.bot.send_message(
                    user["interlocutor"],
                    message.text,
                    entities=message.entities,
                    reply_to_message_id=reply,
                    parse_mode=None
                )
            elif message.content_type == "photo":
                await message.bot.send_photo(
                    user["interlocutor"],
                    message.photo[-1].file_id,
                    caption=message.caption,
                    caption_entities=message.caption_entities,
                    parse_mode=None,
                    has_spoiler=True
                )
            elif message.content_type == "audio":
                await message.bot.send_audio(
                    user["interlocutor"],
                    message.audio.file_id,
                    caption=message.caption,
                    caption_entities=message.caption_entities,
                    parse_mode=None
                )
            elif message.content_type == "voice":
                await message.bot.send_voice(
                    user["interlocutor"],
                    message.voice.file_id,
                    caption=message.caption,
                    caption_entities=message.caption_entities,
                    parse_mode=None
                )
            elif message.content_type == "document":
                await message.bot.send_document(
                    user["interlocutor"],
                    message.document.file_id,
                    caption=message.caption,
                    caption_entities=message.caption_entities,
                    parse_mode=None
                )
            elif message.content_type == "sticker":
                await message.bot.send_sticker(
                    user["interlocutor"],
                    message.sticker.file_id
                )
            elif message.content_type == "video":
                await message.bot.send_video(
                    user["interlocutor"],
                    message.video.file_id,
                    caption=message.caption,
                    caption_entities=message.caption_entities,
                    parse_mode=None,
                    has_spoiler=True
                )
            else:
                await message.answer("Ваш собеседник не принимает такой тип сообщений")
    else:
        await message.answer("Если вы хотите ответить на открытку\n"
                             "Вы сначало должны войти в 📩 Открытки")
