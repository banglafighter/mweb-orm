from typing import TypeVar, Type
from sqlalchemy import inspect
from mw_common import MwException
from .mweb_master_model import MWebMasterModel
from ..orm import mweb_orm
from ..query import MWebQueryProcessor, MWebPropsQueryProcessor

T = TypeVar("T", bound="MWebBaseModel")

class MWebBaseModel(MWebMasterModel):
    __abstract__ = True
    __was_saved = False

    def before_save(self):
        """
            This method is called before saving the data.
        """
        return self

    def after_save(self):
        """
            This method is called after saving the data.
        """
        return self

    async def save(self, commit: bool = True):
        self.__was_saved = False
        try:
            async with await mweb_orm.get_session() as session:
                async with session.begin():
                    self.before_save()
                    session.add(self)
                    await session.flush()
                    await session.refresh(self)
                    self.after_save()
                    if commit:
                        await session.commit()
                    self._set_save_status(self)
        except Exception as e:
            raise MwException(e)
        return self

    def _set_save_status(self, model):
        self.__was_saved = inspect(model).persistent

    def is_saved(self) -> bool:
        return self.__was_saved

    @classmethod
    async def save_all(cls: Type[T], models: list[T], commit: bool = True):
        try:
            async with await mweb_orm.get_session() as session:
                async with session.begin():
                    for model in models:
                        model.before_save()
                        session.add(model)
                    await session.flush()

                    for model in models:
                        model.after_save()
                        model._set_save_status(model)

                    if commit:
                        await session.commit()
        except Exception as e:
            raise MwException(e)

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

    async def delete(self):
        async with await mweb_orm.get_session() as session:
            try:
                self.before_delete()
                session.delete(self)
                await session.flush()
                self.after_delete()
                await session.commit()
            except Exception as e:
                await session.rollback()
                raise MwException(e)

    query: MWebQueryProcessor = MWebPropsQueryProcessor()

    @classmethod
    def select(cls, *fields) -> MWebQueryProcessor:
        return MWebQueryProcessor(cls, fields=fields if fields else None)

