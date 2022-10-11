from aiogram import Dispatcher, Bot
from aiogram.types import CallbackQuery
from tgbot.keyboards.inline import agree
from tgbot.models.users import Performers, Orders


async def agreement_yes(call: CallbackQuery):
    await call.answer()
    order_id = int(call.data.split(':')[2])
    bot = Bot.get_current()
    sess = bot.get('db')
    if await Orders.get_perf_id(sess, order_id):
        await call.message.answer('Это задание уже выполняет кто-то другой')
    else:
        performer = await Performers.get_performer(sess, call.from_user.id)
        await Orders.update_order(sess, order_id=order_id, performer_id=call.from_user.id)
        await call.message.answer('Хорошо, я запишу вас как исполнителя')
        await bot.send_message(await Orders.get_customer_id(sess, order_id),
                               f'Вашу заявку принял: {performer.full_name}\n'
                               f'Можете с ним связаться, его номер: {performer.phone_number}')


async def agreement_no(call: CallbackQuery):
    await call.answer()
    await call.message.answer('Вы отказались')


def register_all(dp: Dispatcher):
    dp.register_callback_query_handler(agreement_yes, agree.filter(yn='yes'))
    dp.register_callback_query_handler(agreement_no, agree.filter(yn='no'))
