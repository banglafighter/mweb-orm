from mweb_orm.model.mweb_master_model import MWebMasterModel
from mweb_orm.orm import mweb_orm


class MWebBaseModel(MWebMasterModel):
    __abstract__ = True

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
        async with await mweb_orm.get_session() as session:
            async with session.begin():
                self.before_save()
                session.add(self)
                await session.flush()
                self.after_save()
                if commit:
                    await session.commit()
        return self
