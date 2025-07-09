from typing import TypeVar, Type
from sqlalchemy import inspect
from mweb_orm.model.mweb_master_model import MWebMasterModel
from mweb_orm.orm import mweb_orm

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
        async with await mweb_orm.get_session() as session:
            async with session.begin():
                self.before_save()
                session.add(self)
                await session.flush()
                self.after_save()
                if commit:
                    await session.commit()
                self._set_save_status(self)
        return self

    def _set_save_status(self, model):
        self.__was_saved = inspect(model).persistent

    def is_saved(self) -> bool:
        return self.__was_saved

    @classmethod
    async def save_all(cls: Type[T], models: list[T], commit: bool = True):
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
