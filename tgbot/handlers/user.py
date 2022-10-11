from aiogram import Dispatcher, Bot
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery

from tgbot.keyboards.inline import choice, buy_callback, all_services
from tgbot.misc.other_func import distribution
from tgbot.models.users import User, Performers

from tgbot.misc.states import Register, Application


async def user_start(message: Message, user: User):
    await message.reply("Что вы хотите?", reply_markup=choice)


async def register_performer(call: CallbackQuery):
    await call.answer(cache_time=60)
    await call.message.answer('Какую услугу предоставляете?')
    await Register.service.set()


async def part_1(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['service'] = message.text
        await message.answer('Введите ваше ФИО.')
        await Register.next()


async def part_2(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['fullname'] = message.text
        await message.answer('Введите ваш номер телефона.')
        await Register.next()


async def part_3(message: Message, state: FSMContext):
    session_maker = Bot.get_current().get('db')
    async with state.proxy() as data:
        data['phone_number'] = message.text
        await Performers.add_performer(
            session_maker=session_maker,
            performer_id=message.from_user.id,
            service=data['service'],
            full_name=data['fullname'],
            phone_number=data['phone_number']
        )
        await message.answer(f'Вы зарегестрированы!\n{data["fullname"]}')
        await state.finish()


async def client(call: CallbackQuery):
    await call.answer()
    kb = await all_services()
    await call.message.edit_text('Вот то, что мы можем предоставить:')
    await call.message.edit_reply_markup(kb)
    await Application.selected_service.set()


async def service_is_selected(call: CallbackQuery, state: FSMContext):
    await call.answer()
    async with state.proxy() as data:
        data['select_service'] = call.data.split(':')[1]
    await call.message.answer('Далее нужно заполнить заявку.')
    await call.message.answer('Скажите ваше ФИО.')
    await Application.next()


async def start_application(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['fullname'] = message.text
        await message.answer(f'Когда будет вам удобно встретиться?')
        await Application.next()


async def application_2(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['time'] = message.text
        await message.answer(f'А также скажите ваш адрес.')
        await Application.next()


async def application_3(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['address'] = message.text
        await message.answer(f'Ваша заявка создана.\nС вами свяжится один из наших специалистов.')
        await distribution(data, message.from_user.id)
        await state.finish()


def register_user(dp: Dispatcher):
    dp.register_message_handler(user_start, commands=["start"])

    dp.register_callback_query_handler(register_performer, buy_callback.filter(user='performer'))
    dp.register_message_handler(part_1, state=Register.service)
    dp.register_message_handler(part_2, state=Register.fullname)
    dp.register_message_handler(part_3, state=Register.phone_number)

    dp.register_callback_query_handler(client, buy_callback.filter(user='client'))
    dp.register_callback_query_handler(service_is_selected, state=Application.selected_service)
    dp.register_message_handler(start_application, state=Application.fullname)
    dp.register_message_handler(application_2, state=Application.time)
    dp.register_message_handler(application_3, state=Application.address)
