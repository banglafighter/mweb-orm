import re
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass, DeclarativeMeta, DeclarativeBaseNoMeta, decl_api,  declared_attr


def camel_to_snake_case(name: str) -> str:
    name = re.sub(r"((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))", r"_\1", name)
    return name.lower().lstrip("_")

def should_set_tablename(cls: type) -> bool:
    if (
        cls.__dict__.get("__abstract__", False)
        or (
            not issubclass(cls, (DeclarativeBase, DeclarativeBaseNoMeta))
            and not any(isinstance(b, DeclarativeMeta) for b in cls.__mro__[1:])
        )
        or any(
            (b is DeclarativeBase or b is DeclarativeBaseNoMeta)
            for b in cls.__bases__
        )
    ):
        return False

    for base in cls.__mro__:
        if "__tablename__" not in base.__dict__:
            continue

        if isinstance(base.__dict__["__tablename__"], declared_attr):
            return False

        return not (
            base is cls
            or base.__dict__.get("__abstract__", False)
            or not (
                # SQLAlchemy 1.x
                isinstance(base, DeclarativeMeta)
                # 2.x: DeclarativeBas uses this as metaclass
                or isinstance(base, decl_api.DeclarativeAttributeIntercept)
                # 2.x: DeclarativeBaseNoMeta doesn't use a metaclass
                or issubclass(base, DeclarativeBaseNoMeta)
            )
        )

    return True


class MWebBaseModel(DeclarativeBase, MappedAsDataclass):
    __abstract__ = True

    def __init_subclass__(cls, **kwargs):
        if should_set_tablename(cls):
            cls.__tablename__ = camel_to_snake_case(cls.__name__)

        super().__init_subclass__(**kwargs)
