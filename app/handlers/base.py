from aiogram import Router, types
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

from app.keyboards.inline import get_language_kb
from app.states.order_state import OrderState
from app.utils.texts import get_text

router = Router()

@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    
    # Send welcome text in both languages
    welcome_text = get_text("uz", "welcome") + "\n\n" + get_text("ru", "welcome")
    
    await message.answer(
        welcome_text,
        reply_markup=get_language_kb()
    )
    await state.set_state(OrderState.language)

@router.message(Command("cancel"))
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    data = await state.get_data()
    lang = data.get("chosen_lang", "uz")
    
    if current_state is None:
        await message.answer(get_text(lang, "cancel_empty"))
        return
        
    await state.clear()
    await message.answer(
        get_text(lang, "cancel_success"),
        reply_markup=types.ReplyKeyboardRemove()
    )
