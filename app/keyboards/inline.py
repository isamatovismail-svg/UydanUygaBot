from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_language_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="🇺🇿 O'zbek tili", callback_data="lang_uz")
    kb.button(text="🇷🇺 Русский", callback_data="lang_ru")
    kb.adjust(1)
    return kb.as_markup()
