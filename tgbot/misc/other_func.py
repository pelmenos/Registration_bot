from aiogram import Bot

from tgbot.keyboards.inline import add_dynamic_btn
from tgbot.models.users import User, Orders

ID = 0


async def distribution(data, customer_id):
    global ID
    ID += 1
    bot = Bot.get_current()
    session = bot.get('db')
    try:
        await Orders.add_order(session, order_id=ID, customer_id=customer_id)
    except Exception:
        ID += 1
        await Orders.add_order(session, order_id=ID, customer_id=customer_id)
    text = f"Имя: {data['fullname']}\n" \
           f"Заказ на услугу: {data['select_service']}\n" \
           f"Приехать на адрес: {data['address']}\n" \
           f"Желаемое время: {data['time']}"
    ids = await User.get_user_ids(session)
    for i in ids:
        kb = await add_dynamic_btn(ID)
        await bot.send_message(i[0], text, reply_markup=kb)
