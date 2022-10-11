import asyncio

from sqlalchemy import Column, BigInteger, insert, String, ForeignKey, update, Integer
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from tgbot.config import load_config
from tgbot.services.database import create_db_session
from tgbot.services.db_base import Base


class User(Base):
    __tablename__ = "telegram_users"
    telegram_id = Column(BigInteger, primary_key=True)
    full_name = Column(String(length=100))
    username = Column(String(length=100), nullable=True)
    lang_code = Column(String(length=4), default='ru_RU')
    role = Column(String(length=100), default='user')

    @classmethod
    async def get_user(cls, session_maker: sessionmaker, telegram_id: int) -> 'User':
        async with session_maker() as db_session:
            sql = select(cls).where(cls.telegram_id == telegram_id)
            request = await db_session.execute(sql)
            user: cls = request.scalar()
        return user

    @classmethod
    async def add_user(cls,
                       session_maker: sessionmaker,
                       telegram_id: int,
                       full_name: str,
                       username: str = None,
                       lang_code: str = None,
                       role: str = None
                       ) -> 'User':
        async with session_maker() as db_session:
            sql = insert(cls).values(telegram_id=telegram_id,
                                     full_name=full_name,
                                     username=username,
                                     lang_code=lang_code,
                                     role=role).returning('*')
            result = await db_session.execute(sql)
            await db_session.commit()
            return result.first()

    async def update_user(self, session_maker: sessionmaker, updated_fields: dict) -> 'User':
        async with session_maker() as db_session:
            sql = update(User).where(User.telegram_id == self.telegram_id).values(**updated_fields)
            result = await db_session.execute(sql)
            await db_session.commit()
            return result

    @classmethod
    async def get_user_ids(cls, session_maker: sessionmaker):
        async with session_maker() as db_session:
            sql = select(cls.telegram_id).distinct()
            request = await db_session.execute(sql)
        return request.fetchall()

    def __repr__(self):
        return f'User (ID: {self.telegram_id} - {self.first_name} {self.last_name})'


class Performers(Base):
    __tablename__ = "performers"
    performer_id = Column(BigInteger, primary_key=True, unique=True)
    full_name = Column(String(length=100))
    service = Column(String(length=100))
    phone_number = Column(String(length=20))

    @classmethod
    async def add_performer(cls,
                            session_maker: sessionmaker,
                            performer_id: int,
                            full_name: str,
                            service: str,
                            phone_number: str
                            ):
        async with session_maker() as db_session:
            sql = insert(cls).values(performer_id=performer_id,
                                     full_name=full_name,
                                     service=service,
                                     phone_number=phone_number).returning('*')
            result = await db_session.execute(sql)
            await db_session.commit()
            return result.first()

    @classmethod
    async def get_services(cls, session_maker: sessionmaker):
        async with session_maker() as db_session:
            sql = select(cls.service).distinct()
            request = await db_session.execute(sql)
        return request.fetchall()

    @classmethod
    async def get_performer(cls, session_maker: sessionmaker, performer_id: int) -> 'User':
        async with session_maker() as db_session:
            sql = select(cls).where(cls.performer_id == performer_id)
            request = await db_session.execute(sql)
            performer: cls = request.scalar()
        return performer


class Orders(Base):
    __tablename__ = "orders"
    order_id = Column(Integer(), unique=True, primary_key=True)
    performer_id = Column(ForeignKey(Performers.performer_id, ondelete='SET NULL'), nullable=True)
    customer_id = Column(BigInteger)

    @classmethod
    async def add_order(cls,
                        session_maker: sessionmaker,
                        order_id: int,
                        customer_id: int,
                        performer_id: int = None
                        ):
        async with session_maker() as db_session:
            sql = insert(cls).values(order_id=order_id, customer_id=customer_id, performer_id=performer_id).returning('*')
            result = await db_session.execute(sql)
            await db_session.commit()
            return result.first()

    @classmethod
    async def update_order(cls,
                           session_maker: sessionmaker,
                           order_id: int,
                           performer_id: int
                           ):
        async with session_maker() as db_session:
            sql = update(cls).where(cls.order_id == order_id).values(**{'performer_id': performer_id})
            result = await db_session.execute(sql)
            await db_session.commit()

    @classmethod
    async def get_perf_id(cls, session_maker: sessionmaker, order_id: int):
        async with session_maker() as db_session:
            sql = select(cls.performer_id).where(cls.order_id == order_id)
            request = await db_session.execute(sql)
            request = request.scalar()
        return request

    @classmethod
    async def get_customer_id(cls, session_maker: sessionmaker, order_id: int):
        async with session_maker() as db_session:
            sql = select(cls.customer_id).where(cls.order_id == order_id)
            request = await db_session.execute(sql)
            request = request.scalar()
        return request
