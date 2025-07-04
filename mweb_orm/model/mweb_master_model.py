from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass


class MWebMasterModel(DeclarativeBase, MappedAsDataclass):
    __abstract__ = True
