from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, or_f

from motor.core import AgnosticDatabase as MDB
from keyboards import inline_builder
from utils import MaterialSettings

router = Router()

#There user can work with own profile to change format
@router.message(or_f(Command("setting"), F.text == "⚙️ Настройки"))
async def setting(message: Message, db: MDB):
    await db.users.update_one({"_id": message.from_user.id}, {"$set": {"status": 0}})
    allow = await db.allowance.find_one({"user_id": message.from_user.id}, {"_id": 0, "user_id": 0})
    await message.reply(
        f"Привет, *{message.from_user.first_name}*\!",
        reply_markup=inline_builder(
            [
                f"🟢 Разрешить фото" if allow["photo"] else f"🔴 Разрешить фото",
                f"🟢 Разрешить аудио" if allow["audio"] else "🔴 Разрешить аудио",
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