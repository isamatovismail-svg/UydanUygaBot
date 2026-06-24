from aiogram.utils.keyboard import ReplyKeyboardBuilder
from app.utils.texts import get_text

def get_phone_kb(lang: str):
    kb = ReplyKeyboardBuilder()
    kb.button(text=get_text(lang, "btn_send_phone"), request_contact=True)
    return kb.as_markup(resize_keyboard=True, one_time_keyboard=True)

def get_region_kb(lang: str):
    kb = ReplyKeyboardBuilder()
    kb.button(text=get_text(lang, "btn_uzb"))
    return kb.as_markup(resize_keyboard=True)

def get_city_region_kb(lang: str):
    kb = ReplyKeyboardBuilder()
    kb.button(text=get_text(lang, "btn_tashkent_city"))
    kb.button(text=get_text(lang, "btn_tashkent_region"))
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)

def get_districts_kb(lang: str):
    districts = get_text(lang, "districts")
    kb = ReplyKeyboardBuilder()
    for d in districts:
        kb.button(text=d)
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)

def get_location_a_kb(lang: str):
    kb = ReplyKeyboardBuilder()
    kb.button(text=get_text(lang, "btn_location_a"), request_location=True)
    return kb.as_markup(resize_keyboard=True)

def get_location_b_kb(lang: str):
    kb = ReplyKeyboardBuilder()
    kb.button(text=get_text(lang, "btn_location_b"), request_location=True)
    return kb.as_markup(resize_keyboard=True)

def get_truck_type_kb(lang: str):
    kb = ReplyKeyboardBuilder()
    kb.button(text=get_text(lang, "truck_gazelle"))
    kb.button(text=get_text(lang, "truck_labo"))
    kb.button(text=get_text(lang, "truck_isuzu"))
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)

def get_movers_kb(lang: str):
    kb = ReplyKeyboardBuilder()
    kb.button(text=get_text(lang, "movers_yes"))
    kb.button(text=get_text(lang, "movers_no"))
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)

def get_photo_kb(lang: str):
    kb = ReplyKeyboardBuilder()
    kb.button(text=get_text(lang, "btn_no_photo"))
    return kb.as_markup(resize_keyboard=True)
