import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from tgbot.config import load_config
from tgbot.filters.admin import AdminFilter
from tgbot.handlers.admin import register_admin
from tgbot.handlers.echo import register_echo
from tgbot.handlers.user import register_user
from tgbot.handlers.work_with_all import register_all
from tgbot.middlewares.db import DbMiddleware
from tgbot.services.database import create_db_session

logger = logging.getLogger(__name__)


def register_all_middlewares(dp):
    dp.setup_middleware(DbMiddleware())


def register_all_filters(dp):
    dp.filters_factory.bind(AdminFilter)


def register_all_handlers(dp):
    register_admin(dp)
    register_user(dp)
    register_all(dp)
    register_echo(dp)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',

    )
    logger.info("Starting bot")
    config = load_config(".env")

    storage = MemoryStorage()

    bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    dp = Dispatcher(bot, storage=storage)

    bot['config'] = config
    bot['db'] = await create_db_session(config)

    register_all_middlewares(dp)
    register_all_filters(dp)
    register_all_handlers(dp)

    # start
    try:
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")