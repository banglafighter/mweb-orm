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
        Called before saving the model.
        """
        return self

    async def after_save(self):
        """
        Called after saving the model.
        """
        return self

    async def save(self):
        self.__was_saved = False

        try:
            async with await mweb_orm.get_session() as session:
                async with session.begin():
                    await self.before_save()

                    session.add(self)

                    await session.flush()
                    await session.refresh(self)

                    await self.after_save()

                self._set_save_status(self)

        except Exception as e:
            raise MwException(e) from e

        return self

    def _set_save_status(self, model):
        self.__was_saved = inspect(model).persistent

    def is_saved(self) -> bool:
        return self.__was_saved

    @classmethod
    async def save_all(cls: Type[T], models: list[T]):
        if not models:
            return

        try:
            async with await mweb_orm.get_session() as session:
                async with session.begin():
                    for model in models:
                        await model.before_save()
                        session.add(model)

                    await session.flush()

                    for model in models:
                        await model.after_save()
                        model._set_save_status(model)

        except Exception as e:
            raise MwException(e) from e

    def before_delete(self):
        """
        Called before deleting the model.
        """
        return self

    def after_delete(self):
        """
        Called after deleting the model.
        """
        return self

    async def delete(self):
        try:
            async with await mweb_orm.get_session() as session:
                async with session.begin():
                    self.before_delete()

                    await session.delete(self)
                    await session.flush()

                    self.after_delete()

        except Exception as e:
            raise MwException(e) from e

    query: MWebQueryProcessor = MWebPropsQueryProcessor()

    @classmethod
    def select(cls, *fields) -> MWebQueryProcessor:
        return MWebQueryProcessor(cls, fields=fields if fields else None)