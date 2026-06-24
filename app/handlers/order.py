import logging
from aiogram import Router, F, types, Bot
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from app.states.order_state import OrderState
from app.utils.texts import get_text
from app.utils.validators import is_valid_phone
from app.utils.storage import save_order
from app.config import ADMIN_ID
from app.keyboards import reply as kb

router = Router()

# Helper to add cancel hint
def format_text(lang: str, key: str) -> str:
    return get_text(lang, key) + get_text(lang, "cancel_hint")

# ====== 2. Til tanlash ======
@router.callback_query(F.data.startswith("lang_"))
async def process_language(callback: types.CallbackQuery, state: FSMContext):
    lang = callback.data.split("_")[1]
    await state.update_data(chosen_lang=lang)
    
    await callback.message.edit_text(format_text(lang, "ask_fullname"))
    await state.set_state(OrderState.fullname)
    await callback.answer()

# ====== 3. Ism ======
@router.message(OrderState.fullname)
async def process_fullname(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("chosen_lang", "uz")
    
    if not message.text or len(message.text.strip()) < 3:
        await message.answer(get_text(lang, "invalid_fullname"))
        return

    await state.update_data(fullname=message.text.strip())
    
    await message.answer(
        format_text(lang, "ask_phone"),
        reply_markup=kb.get_phone_kb(lang)
    )
    await state.set_state(OrderState.phone)

# ====== 4. Telefon ======
@router.message(OrderState.phone, F.contact)
async def process_phone_contact(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.contact.phone_number)
    await ask_region(message, state)

@router.message(OrderState.phone, F.text)
async def process_phone_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("chosen_lang", "uz")
    
    if not is_valid_phone(message.text):
        await message.answer(get_text(lang, "invalid_phone"))
        return
        
    await state.update_data(phone=message.text.strip())
    await ask_region(message, state)

async def ask_region(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("chosen_lang", "uz")
    
    await message.answer(
        format_text(lang, "ask_region"),
        reply_markup=kb.get_region_kb(lang)
    )
    await state.set_state(OrderState.region)

# ====== 5. Viloyat ======
@router.message(OrderState.region)
async def process_region(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("chosen_lang", "uz")
    await state.update_data(region=message.text)
    
    await message.answer(
        format_text(lang, "ask_district"),
        reply_markup=kb.get_city_region_kb(lang)
    )
    await state.set_state(OrderState.district)

# ====== 6. Tuman ======
@router.message(OrderState.district)
async def process_district(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("chosen_lang", "uz")
    await state.update_data(district=message.text)
    
    await message.answer(
        format_text(lang, "ask_district_detailed"),
        reply_markup=kb.get_districts_kb(lang)
    )
    await state.set_state(OrderState.district_detailed)

# ====== 7. Tuman tanlangach, A nuqta lokatsiyasini so'rash ======
@router.message(OrderState.district_detailed)
async def process_district_detailed(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("chosen_lang", "uz")
    await state.update_data(district_detailed=message.text)

    # A nuqta uchun maxsus tugma quruvchi
    builder_a = ReplyKeyboardBuilder()
    builder_a.button(text="📍 A nuqtani yuborish (Hozirgi joylashuv)", request_location=True)

    await message.answer(
        "🚚 <b>A Nuqta:</b> Yuk qayerdan olinadi?\n\nAgar hozir o'sha joyda bo'lsangiz, pastdagi tugmani bosing. Yoki 📎 (skrepka) orqali xaritadan tanlab yuboring:\n\n🚫 Bekor qilish uchun /cancel buyrug'ini yuboring.",
        parse_mode="HTML",
        reply_markup=builder_a.as_markup(resize_keyboard=True)
    )
    await state.set_state(OrderState.location_a)


# ====== 8. A nuqta lokatsiyasini qabul qilish va B nuqtani so'rash ======
@router.message(OrderState.location_a, F.location)
async def process_location_a(message: types.Message, state: FSMContext):
    if message.location:
        loc_a = message.location
        await state.update_data(loc_a={"lat": loc_a.latitude, "lon": loc_a.longitude})

    await message.answer(
        "🏁 <b>B Nuqta:</b> Yuk qayerga olib boriladi?\n\nIltimos, pastdagi 📎 (skrepka) tugmasi orqali xaritadan manzilni tanlab yuboring:\n\n🚫 Bekor qilish uchun /cancel buyrug'ini yuboring.",
        parse_mode="HTML",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(OrderState.location_b)


@router.message(OrderState.location_a)
async def process_location_a_wrong(message: types.Message, state: FSMContext):
    await message.answer("⚠️ Iltimos, lokatsiya yuboring (pastdagi tugma yoki 📎 orqali).")


# ====== 9. B nuqta lokatsiyasini qabul qilish va Mashina so'rash ======
@router.message(OrderState.location_b, F.location)
async def process_location_b(message: types.Message, state: FSMContext):
    if message.location:
        loc_b = message.location
        await state.update_data(loc_b={"lat": loc_b.latitude, "lon": loc_b.longitude})

    # Mashinalar uchun tugmalar quruvchi
    builder_truck = ReplyKeyboardBuilder()
    builder_truck.button(text="🚛 Gazelle (Mebel va katta yuklar)")
    builder_truck.button(text="🚙 Labo / Damas (Kichik yuklar)")
    builder_truck.button(text="🚚 Isuzu (Juda katta ko'chishlar)")
    builder_truck.adjust(1)

    await message.answer(
        "📦 Qanday turdagi yuk mashinasi kerak?\n\n🚫 Bekor qilish uchun /cancel buyrug'ini yuboring.",
        reply_markup=builder_truck.as_markup(resize_keyboard=True)
    )
    await state.set_state(OrderState.truck_type)


@router.message(OrderState.location_b)
async def process_location_b_wrong(message: types.Message, state: FSMContext):
    await message.answer("⚠️ Iltimos, 📎 (skrepka) tugmasi orqali xaritadan lokatsiya tanlab yuboring.")

# ====== 10. Yuk tashuvchilar ======
@router.message(OrderState.truck_type)
async def process_truck_type(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("chosen_lang", "uz")
    await state.update_data(truck_type=message.text)
    
    await message.answer(
        format_text(lang, "ask_movers"),
        reply_markup=kb.get_movers_kb(lang)
    )
    await state.set_state(OrderState.movers_needed)

# ====== 11. Rasm ======
@router.message(OrderState.movers_needed)
async def process_movers(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("chosen_lang", "uz")
    await state.update_data(movers=message.text)
    
    await message.answer(
        format_text(lang, "ask_photo"),
        reply_markup=kb.get_photo_kb(lang)
    )
    await state.set_state(OrderState.waiting_photo)

# ====== 12. Finalize Order ======
@router.message(OrderState.waiting_photo, F.photo)
async def receive_photo(message: types.Message, state: FSMContext, bot: Bot):
    photo_id = message.photo[-1].file_id
    await finalize_order(message, state, bot, photo_id=photo_id)

@router.message(OrderState.waiting_photo, F.text)
async def receive_no_photo(message: types.Message, state: FSMContext, bot: Bot):
    await finalize_order(message, state, bot, photo_id=None)

async def finalize_order(message: types.Message, state: FSMContext, bot: Bot, photo_id: str | None):
    data = await state.get_data()
    lang = data.get("chosen_lang", "uz")
    
    await message.answer(
        get_text(lang, "success"),
        reply_markup=types.ReplyKeyboardRemove()
    )
    
    admin_text = (
        "🔔 <b>YANGI BUYURTMA KELDI!</b>\n\n"
        f"👤 <b>Mijoz:</b> {data.get('fullname')}\n"
        f"📞 <b>Telefon:</b> {data.get('phone')}\n"
        f"🌍 <b>Davlat:</b> {data.get('region')}\n"
        f"🏙 <b>Viloyat/Shahar:</b> {data.get('district')}\n"
        f"🗺 <b>Tuman:</b> {data.get('district_detailed')}\n"
        f"🚛 <b>Mashina turi:</b> {data.get('truck_type')}\n"
        f"💪 <b>Ishchilar kerakmi:</b> {data.get('movers')}\n"
        f"🆔 <b>User ID:</b> {message.from_user.id}\n"
        f"👤 <b>Username:</b> @{message.from_user.username or '—'}\n"
    )

    try:
        if photo_id:
            await bot.send_photo(chat_id=ADMIN_ID, photo=photo_id, caption=admin_text, parse_mode="HTML")
        else:
            await bot.send_message(chat_id=ADMIN_ID, text=admin_text, parse_mode="HTML")

        loc_a = data.get('loc_a')
        loc_b = data.get('loc_b')

        if loc_a:
            await bot.send_venue(
                chat_id=ADMIN_ID, 
                latitude=loc_a['lat'], 
                longitude=loc_a['lon'],
                title="📍 A Nuqta",
                address="Yuk qayerdan olinadi"
            )

        if loc_b:
            await bot.send_venue(
                chat_id=ADMIN_ID, 
                latitude=loc_b['lat'], 
                longitude=loc_b['lon'],
                title="🏁 B Nuqta",
                address="Yuk qayerga olib boriladi"
            )

    except Exception as e:
        logging.error(f"Adminga yuborishda xatolik: {e}")

    try:
        await save_order(data, message.from_user.id)
    except Exception as e:
        logging.error(f"Buyurtmani saqlashda xatolik: {e}")

    await state.clear()

# ====== Fallback ======
@router.message()
async def fallback_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("chosen_lang", "uz")
    await message.answer(get_text(lang, "fallback"))
