from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.exceptions import TelegramBadRequest
from motor.core import AgnosticDatabase as MDB
from contextlib import suppress
from keyboards import inline_builder
from utils import ProfileSettings, MaterialSettings

router = Router()


@router.callback_query(ProfileSettings.filter(F.action == "change"))
async def change_profile_settings(query: CallbackQuery, callback_data: ProfileSettings, db: MDB) -> None:
    result = await db.users.find_one({"_id": query.from_user.id}, {"_id": 0, "letter": 1})
    letter = result["letter"]
    if callback_data.value == "receive_message_toggle":
        await db.users.update_one({"_id": query.from_user.id}, {"$set": {"letter": not letter}})
        letter = not letter
    with suppress(TelegramBadRequest):
        await query.message.edit_reply_markup(
            reply_markup=inline_builder(

                 f"🟢 Получение открыток" if letter else "🔴 Получение открыток",
                 ProfileSettings(value="receive_message_toggle").pack(),
                sizes=1
        ))

    await query.answer()

@router.callback_query(MaterialSettings.filter(F.action == "material"))
async def change_input_settings(query: CallbackQuery, callback_data: MaterialSettings, db: MDB) -> None:
    condition = {"user_id": query.from_user.id}
    allow = await db.allowance.find_one(condition, {"_id": 0, "user_id": 0})
    if callback_data.value == "receive_image_toggle":
        await db.allowance.update_one(condition, {"$set": {"photo": not allow["photo"]}})
        allow["photo"] = not allow["photo"]
    elif callback_data.value == "receive_video_toggle":
        await db.allowance.update_one(condition, {"$set": {"video": not allow["video"]}})
        allow["video"] = not allow["video"]
    elif callback_data.value == "receive_animation_toggle":
        await db.allowance.update_one(condition, {"$set": {"animation": not allow["animation"]}})
        allow["animation"] = not allow["animation"]
    elif callback_data.value == "receive_sticker_toggle":
        await db.allowance.update_one(condition, {"$set": {"sticker": not allow["sticker"]}})
        allow["sticker"] = not allow["sticker"]
    elif callback_data.value == "receive_audio_toggle":
        await db.allowance.update_one(condition, {"$set": {"audio": not allow["audio"]}})
        allow["audio"] = not allow["audio"]
    elif callback_data.value == "receive_document_toggle":
        await db.allowance.update_one(condition, {"$set": {"document": not allow["document"]}})
        allow["document"] = not allow["document"]
    elif callback_data.value == "receive_voice_toggle":
        await db.allowance.update_one(condition, {"$set": {"voice": not allow["voice"]}})
        allow["voice"] = not allow["voice"]
    with suppress(TelegramBadRequest):
        await query.message.edit_reply_markup(
        reply_markup=inline_builder(
            [
                f"🟢 Разрешить фото" if allow["photo"] else f"🔴 Разрешить фото",
                f"🟢 Разрешить аудио" if  allow["audio"] else "🔴 Разрешить аудио",
                f"🟢 Разрешить голосовой" if allow["voice"] else "🔴 Разрешить голосовой",
                f"🟢 Разрешить файлы" if allow["document"] else "🔴 Разрешить файлы",
                f"🟢 Разрешить стикеры" if allow["sticker"] else "🔴 Разрешить стикеры",
                f"🟢 Разрешить видео" if allow["video"] else "🔴 Разрешить видео",
                f"🟢 Разрешить GIF" if allow["animation"] else "🔴 Разрешить GIF",
            ],
            [
                MaterialSettings(value="receive_image_toggle").pack(),
                MaterialSettings(value="receive_audio_toggle").pack(),
                MaterialSettings(value="receive_voice_toggle").pack(),
                MaterialSettings(value="receive_document_toggle").pack(),
                MaterialSettings(value="receive_sticker_toggle").pack(),
                MaterialSettings(value="receive_video_toggle").pack(),
                MaterialSettings(value="receive_animation_toggle").pack(),
            ],
            sizes=[1, 1, 1, 1, 1, 1, 1]
        )
    )
    await query.answer()


