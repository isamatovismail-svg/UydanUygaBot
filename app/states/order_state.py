from aiogram.fsm.state import State, StatesGroup

class OrderState(StatesGroup):
    language = State()
    fullname = State()
    phone = State()
    region = State()
    district = State()
    district_detailed = State()
    location_a = State()
    location_b = State()
    truck_type = State()
    movers_needed = State()
    waiting_photo = State()
