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
        try:
            session = await mweb_orm.get_session()

            # If the session doesn't have an active transaction, start one cleanly
            if not session.in_transaction():
                await session.begin()

            # 1. Run the hooks safely
            await self.before_save()

            # 2. Add and stage changes
            session.add(self)
            await session.flush()
            await session.refresh(self)

            # 3. Run post-save hooks
            await self.after_save()

            # 4. Commit if requested
            if commit:
                await session.commit()

            self._set_save_status(self)
        except Exception as e:
            # If anything goes wrong, rollback the transaction state cleanly
            session = await mweb_orm.get_session()
            if session.in_transaction():
                await session.rollback()
            raise MwException(e)

        return self

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

    @classmethod
    async def save_all(cls: Type[T], models: list[T], commit: bool = True):
        try:
            session = await mweb_orm.get_session()
            # If no transaction exists yet, start one safely
            if not session.in_transaction():
                await session.begin()

            for model in models:
                await model.before_save()
                session.add(model)
            await session.flush()

            for model in models:
                await model.after_save()
                model._set_save_status(model)

            # Only commit here if we started the transaction and commit=True
            if commit:
                await session.commit()
        except Exception as e:
            session = await mweb_orm.get_session()
            if session.in_transaction():
                await session.rollback()
            raise MwException(e)

    async def delete(self):
        try:
            session = await mweb_orm.get_session()
            if not session.in_transaction():
                await session.begin()

            self.before_delete()
            await session.delete(self)
            await session.flush()
            self.after_delete()

            await session.commit()
        except Exception as e:
            session = await mweb_orm.get_session()
            if session.in_transaction():
                await session.rollback()
            raise MwException(e)

    query: MWebQueryProcessor = MWebPropsQueryProcessor()

    @classmethod
    def select(cls, *fields) -> MWebQueryProcessor:
        return MWebQueryProcessor(cls, fields=fields if fields else None)

