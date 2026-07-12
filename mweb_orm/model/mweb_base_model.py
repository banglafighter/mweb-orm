from typing import TypeVar, Type
from sqlalchemy import inspect
from mw_common import MwException
from .mweb_master_model import MWebMasterModel
from ..orm.mweb_orm import mweb_orm
from ..query import MWebQueryProcessor, MWebPropsQueryProcessor

T = TypeVar("T", bound="MWebBaseModel")

class MWebBaseModel(MWebMasterModel):
    __abstract__ = True
    __was_saved = False

    async def before_save(self):
        """
            This method is called before saving the data.
        """
        return self

    async def after_save(self):
        """
            This method is called after saving the data.
        """
        return self

    # TODO: Implemented using Gemini
    async def save(self, commit: bool = True):
        self.__was_saved = False
        session = await mweb_orm.get_session()
        try:
            # If a transaction is already active, use a sub-transaction (SAVEPOINT)
            # This prevents validation queries from triggering a fatal database Autoflush crash
            if session.in_transaction():
                async with session.begin_nested():
                    await self._execute_save_workflow(session)
            else:
                await session.begin()
                await self._execute_save_workflow(session)
                if commit:
                    await session.commit()

            self._set_save_status(self)
        except Exception as e:
            if session.in_transaction():
                await session.rollback()
            raise MwException(e)
        finally:
            # Crucial step: Explicitly close/return the session to the pool
            # This completely removes the "SAWarning: garbage collector..." pool leak error
            await session.close()

        return self

    async def _execute_save_workflow(self, session):
        await self.before_save()
        session.add(self)
        await session.flush()
        await session.refresh(self)
        await self.after_save()

    @classmethod
    async def save_all(cls: Type[T], models: list[T], commit: bool = True):
        session = await mweb_orm.get_session()
        try:
            if session.in_transaction():
                async with session.begin_nested():
                    await cls._execute_save_all_workflow(session, models)
            else:
                await session.begin()
                await cls._execute_save_all_workflow(session, models)
                if commit:
                    await session.commit()
        except Exception as e:
            if session.in_transaction():
                await session.rollback()
            raise MwException(e)
        finally:
            await session.close()

    @classmethod
    async def _execute_save_all_workflow(cls, session, models: list[T]):
        for model in models:
            await model.before_save()
            session.add(model)
        await session.flush()

        for model in models:
            await model.after_save()
            model._set_save_status(model)

    async def delete(self):
        session = await mweb_orm.get_session()
        try:
            if session.in_transaction():
                async with session.begin_nested():
                    await self._execute_delete_workflow(session)
            else:
                await session.begin()
                await self._execute_delete_workflow(session)
                await session.commit()
        except Exception as e:
            if session.in_transaction():
                await session.rollback()
            raise MwException(e)
        finally:
            await session.close()

    async def _execute_delete_workflow(self, session):
        self.before_delete()
        await session.delete(self)
        await session.flush()
        self.after_delete()

    # TODO: Previously implemented Method, without AI
    # async def save(self, commit: bool = True):
    #     self.__was_saved = False
    #     try:
    #         async with await mweb_orm.get_session() as session:
    #             async with session.begin():
    #                 await self.before_save()
    #                 session.add(self)
    #                 await session.flush()
    #                 await session.refresh(self)
    #                 await self.after_save()
    #                 if commit:
    #                     await session.commit()
    #                 self._set_save_status(self)
    #     except Exception as e:
    #         raise MwException(e)
    #     return self

    def _set_save_status(self, model):
        self.__was_saved = inspect(model).persistent

    def is_saved(self) -> bool:
        return self.__was_saved

    # @classmethod
    # async def save_all(cls: Type[T], models: list[T], commit: bool = True):
    #     try:
    #         async with await mweb_orm.get_session() as session:
    #             async with session.begin():
    #                 for model in models:
    #                     await model.before_save()
    #                     session.add(model)
    #                 await session.flush()
    #
    #                 for model in models:
    #                     await model.after_save()
    #                     model._set_save_status(model)
    #
    #                 if commit:
    #                     await session.commit()
    #     except Exception as e:
    #         raise MwException(e)

    def before_delete(self):
        """
            This method is called before delete the data.
        """
        return self

    def after_delete(self):
        """
            This method is called after delete the data.
        """
        return self

    # async def delete(self):
    #     async with await mweb_orm.get_session() as session:
    #         try:
    #             self.before_delete()
    #             session.delete(self)
    #             await session.flush()
    #             self.after_delete()
    #             await session.commit()
    #         except Exception as e:
    #             await session.rollback()
    #             raise MwException(e)

    query: MWebQueryProcessor = MWebPropsQueryProcessor()

    @classmethod
    def select(cls, *fields) -> MWebQueryProcessor:
        return MWebQueryProcessor(cls, fields=fields if fields else None)

