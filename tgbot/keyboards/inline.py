from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from tgbot.models.users import Performers

buy_callback = CallbackData('choice', 'user')
selected_service = CallbackData('service', 'name')
agree = CallbackData('agree', 'yn', 'id')

choice = InlineKeyboardMarkup(row_width=1,
                              inline_keyboard=[
                                  [
                                      InlineKeyboardButton(
                                          text='Выбрать услугу',
                                          callback_data=buy_callback.new(user='client')
                                      )
                                  ],
                                  [
                                      InlineKeyboardButton(
                                          text='Регистрация для проффесионалов',
                                          callback_data=buy_callback.new(user='performer')
                                      ),
                                  ],
                              ],
                              )


async def add_dynamic_btn(ID):
    kb = InlineKeyboardMarkup(row_width=2)
    kb.insert(InlineKeyboardButton(text='Соласиться', callback_data=agree.new(yn='yes', id=ID)))
    kb.insert(InlineKeyboardButton(text='Отказаться', callback_data=agree.new(yn='no', id=ID)))
    return kb


async def all_services():
    session_maker = Bot.get_current().get('db')
    services = await Performers.get_services(session_maker)
    kb = InlineKeyboardMarkup(row_width=1)
    for i in services:
        kb.insert(InlineKeyboardButton(text=i[0], callback_data=selected_service.new(name=i[0])))
    return kb
