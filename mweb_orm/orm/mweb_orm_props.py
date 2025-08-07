from typing import Optional, Any, Literal, Union
from sqlalchemy import (
    Integer, String, Boolean, DateTime, Date, Float, Text, BigInteger, Time, SmallInteger,
    ForeignKey, func
)
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import MappedColumn, relationship
from sqlalchemy.orm.interfaces import _AttributeOptions
from sqlalchemy.sql.base import _NoArg
from sqlalchemy.sql.functions import _FunctionGenerator
from mweb_orm.orm.mweb_orm_fields import JSONType
from sqlalchemy.orm.relationships import _RelationshipJoinConditionArgument

LazyLoadType = Literal[
    "select",
    "joined",
    "selectin",
    "subquery",
    "raise",
    "raise_on_sql",
    "noload",
    "immediate",
    "write_only",
    "dynamic",
]

class MWebORMProps:

    def Column(self,
               name: str,
               data_type,
               primary_key: bool = False,
               foreign_key: ForeignKey = None,
               autoincrement: bool = False,
               nullable: bool = True,
               unique: bool = None,
               index: bool = None,
               default: Optional[Any] = _NoArg.NO_ARG,
               init: Union[_NoArg, bool] = _NoArg.NO_ARG,
               onupdate=None,
               **kw: Any,
               ) -> MappedColumn:

        argument_list = []
        if foreign_key is not None:
            argument_list.append(foreign_key)
        argument = tuple(argument_list)

        # Don't know the usages that's why not adding as params
        default_factory = _NoArg.NO_ARG
        repr = _NoArg.NO_ARG
        compare = _NoArg.NO_ARG
        kw_only = True
        hash = _NoArg.NO_ARG

        if (nullable == True or autoincrement == True) and init == _NoArg.NO_ARG:
            init = False

        return MappedColumn(
            *argument,
            name=name, type_=data_type, primary_key=primary_key, index=index,
            unique=unique, default=default, autoincrement=autoincrement, nullable=nullable,
            onupdate=onupdate,
            attribute_options=_AttributeOptions(
                init, repr, default, default_factory, compare, kw_only, hash
            ),
            **kw,
        )

    def Integer(self):
        return Integer()

    def String(self, length: Optional[int] = None, collation: Optional[str] = None):
        return String(length=length, collation=collation)

    def Boolean(self, create_constraint: bool = False, name: Optional[str] = None):
        return Boolean(create_constraint=create_constraint, name=name)

    def DateTime(self):
        return DateTime()

    def Date(self):
        return Date()

    def Time(self):
        return Time()

    def Float(self):
        return Float()

    def Text(self):
        return Text().with_variant(LONGTEXT, "mysql")

    def BigInteger(self):
        return BigInteger().with_variant(self.Integer(), "sqlite")

    def SmallInteger(self):
        return SmallInteger()

    def JSON(self):
        return JSONType()

    def ForeignKey(self, column, onupdate: str = None, ondelete: str = None, name=None):
        return ForeignKey(column, onupdate=onupdate, ondelete=ondelete, name=name)

    def Relationship(self, argument, viewonly: bool = False, lazy: LazyLoadType = "joined", order_by: str | bool = False, uselist: bool = True, primaryjoin: Optional[_RelationshipJoinConditionArgument] = None, remote_side: str = None, backref: str = None, secondaryjoin: Optional[_RelationshipJoinConditionArgument] = None, back_populates: str = None):
        return relationship(
            argument=argument,
            viewonly=viewonly,
            lazy=lazy,
            order_by=order_by,
            uselist=uselist,
            primaryjoin=primaryjoin,
            remote_side=remote_side,
            backref=backref,
            back_populates=back_populates,
            secondaryjoin=secondaryjoin
        )

    @property
    def func(self) -> _FunctionGenerator:
        return func
