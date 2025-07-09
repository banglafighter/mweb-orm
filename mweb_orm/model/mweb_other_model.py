from datetime import datetime
from mw_common import MwUtil
from mweb_orm.model.mweb_base_model import MWebBaseModel
from mweb_orm.orm.mweb_orm import mweb_orm


class MWebIDModel(MWebBaseModel):
    __abstract__ = True
    id: int = mweb_orm.Column("id", mweb_orm.BigInteger().with_variant(mweb_orm.Integer(), "sqlite"), primary_key=True, autoincrement=True, nullable=False)


class MWebDatedModel(MWebIDModel):
    __abstract__ = True
    created: datetime = mweb_orm.Column("created", mweb_orm.DateTime(), default=mweb_orm.func.now(), nullable=False)
    updated: datetime = mweb_orm.Column("updated", mweb_orm.DateTime(), default=mweb_orm.func.now(), onupdate=mweb_orm.func.now(), nullable=False)


class MWebModel(MWebDatedModel):
    __abstract__ = True
    isDeleted: bool = mweb_orm.Column("is_deleted", mweb_orm.Boolean(), default=False, nullable=False)
    uuid: str = mweb_orm.Column("uuid", mweb_orm.String(40), unique=True, nullable=False, index=True, init=False)

    def before_save(self):
        if not self.uuid:
            self.uuid = MwUtil.uuid()

