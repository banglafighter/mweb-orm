from mweb_orm.model.mweb_master_model import MWebMasterModel


class MWebBaseModel(MWebMasterModel):
    __abstract__ = True


class MWebIDModel(MWebBaseModel):
    __abstract__ = True
    id = None


class MWebDatedModel(MWebIDModel):
    __abstract__ = True
    created = None
    updated = None


class MWebModel(MWebDatedModel):
    __abstract__ = True
    isDeleted = None
    uuid = None
