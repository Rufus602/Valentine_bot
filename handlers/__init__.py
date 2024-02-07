from aiogram import Router


def setup_message_routers() -> Router:
    from . import start, chat_commands, profile, bot_messages, letter, input, cancel

    router = Router()
    router.include_router(start.router)
    router.include_router(chat_commands.router)
    router.include_router(cancel.router)
    router.include_router(letter.router)
    router.include_router(input.router)

    router.include_router(profile.router)

    router.include_router(bot_messages.router)

    return router