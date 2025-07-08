from typing import Optional, Any, Literal
from sqlalchemy import (
    Integer, String, Boolean, DateTime, Date, Float, Text, BigInteger, Time, SmallInteger,
    ForeignKey, func
)
from sqlalchemy.orm import MappedColumn, relationship
from sqlalchemy.sql.base import _NoArg
from sqlalchemy.sql.functions import _FunctionGenerator

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
    True,
    False,
    None,
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
               onupdate=None,
               **kw: Any,
               ) -> MappedColumn:

        argument_list = []
        if foreign_key is not None:
            argument_list.append(foreign_key)
        argument = tuple(argument_list)

        return MappedColumn(
            *argument,
            name=name, type_=data_type, primary_key=primary_key, index=index,
            unique=unique, default=default, autoincrement=autoincrement, nullable=nullable,
            onupdate=onupdate,
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
        return Text()

    def BigInteger(self):
        return BigInteger()

    def SmallInteger(self):
        return SmallInteger()

    def ForeignKey(self, column, onupdate: str = None, ondelete: str = None, name=None):
        return ForeignKey(column, onupdate=onupdate, ondelete=ondelete, name=name)

    def Relationship(self, argument, viewonly: bool = False, lazy: LazyLoadType = "select", order_by: str | bool = False, uselist: bool = False, primaryjoin: str = None, remote_side: str = None, backref: str = None, back_populates: str = None):
        return relationship(
            argument=argument, viewonly=viewonly, lazy=lazy, order_by=order_by, uselist=uselist,
            primaryjoin=primaryjoin, remote_side=remote_side, backref=backref, back_populates=back_populates,
        )

    @property
    def func(self) -> _FunctionGenerator:
        return func
