from aiogram.filters.callback_data import CallbackData


class ProfileSettings(CallbackData, prefix="profile"):
    action: str = "change"
    value: str | None = None


class MaterialSettings(CallbackData, prefix="setting"):
    action: str = "material"
    value: str | None = None
