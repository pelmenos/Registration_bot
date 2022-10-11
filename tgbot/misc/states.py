from aiogram.dispatcher.filters.state import StatesGroup, State


class Register(StatesGroup):
    service = State()
    fullname = State()
    phone_number = State()


class Application(StatesGroup):
    selected_service = State()
    fullname = State()
    time = State()
    address = State()
