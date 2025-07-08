from mw_common.mw_console_log import Console
from mw_common.mw_exception import MwException
from mweb_orm import MWebBaseModel
from mweb_orm.orm.mweb_orm_actions import MWebORMActions
from mweb_orm.orm.mweb_orm_data import DBConnectionData
from contextvars import ContextVar
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from mweb_orm.orm.mweb_orm_props import MWebORMProps


_orm_session_context: ContextVar[Optional[AsyncSession]] = ContextVar("orm_session_context", default=None)
class MWebORM(MWebORMProps, MWebORMActions):

    def __init__(self):
        self.connection_data: dict[str, DBConnectionData] = {}

    def get_engine(self, db_key: str = None):
        connection_data: DBConnectionData = self.get_engine_connection_data(db_key=db_key)

        if connection_data is None:
            raise MwException("Database connection configuration not found!")

        engine = create_async_engine(
            connection_data.uri,
            echo=connection_data.printLog,
            pool_pre_ping=connection_data.poolPrePing,
            pool_size=connection_data.poolSize,
            max_overflow=connection_data.maxOverflow,
            pool_timeout=connection_data.poolTimeout,
            pool_recycle=connection_data.poolRecycle,
            future=connection_data.future,
        )
        return engine

    def get_session_maker(self, db_key: str = None):
        connection_data: DBConnectionData = self.get_engine_connection_data(db_key=db_key)

        if connection_data is None:
            raise MwException("Database connection configuration not found!")

        engine = self.get_engine(db_key=db_key)
        session_maker = async_sessionmaker(bind=engine, expire_on_commit=connection_data.expireOnCommit)
        return session_maker

    async def get_session(self, db_key: str = None) -> AsyncSession:
        session = _orm_session_context.get()
        if session is None:
            session_maker = self.get_session_maker(db_key=db_key)
            session = session_maker()
            _orm_session_context.set(session)
        return session

    async def close_session(self):
        session = _orm_session_context.get()
        if session:
            await session.close()
        _orm_session_context.set(None)

    async def _create_drop_model_by_data(self, db_key: str, models, action: str = "create"):
        engine = self.get_engine(db_key=db_key)
        if not engine:
            Console.error(f" engine for {db_key} not found, skipping", system_log=True)
            return

        async with engine.begin() as connection:
            if action == "create":
                await connection.run_sync(
                    lambda sync_connection: MWebBaseModel.metadata.create_all(
                        sync_connection,
                        tables=models
                    )
                )
                Console.info(f"Created models for database = {db_key if db_key else "Default"}", system_log=True)
            elif action == "drop":
                await connection.run_sync(
                    lambda sync_connection: MWebBaseModel.metadata.drop_all(
                        sync_connection,
                        tables=models
                    )
                )
                Console.info(f"Dropped models for database = {db_key if db_key else "Default"}", system_log=True)
            else:
                Console.error("Unknown action", system_log=True)

    async def create_drop_all_model(self, action: str = "create"):
        db_key_to_models = self.get_db_key_and_model_dict()
        for db_key, tables in db_key_to_models.items():
            await self._create_drop_model_by_data(db_key=db_key, models=tables, action=action)

    async def create_drop_default_model_by_db_key(self, db_key: str, action: str = "create"):
        db_key_to_models = self.get_db_key_and_model_dict()
        default_models = None
        if None in db_key_to_models:
            default_models = db_key_to_models[None]
        await self._create_drop_model_by_data(db_key=db_key, models=default_models, action=action)


mweb_orm = MWebORM()
