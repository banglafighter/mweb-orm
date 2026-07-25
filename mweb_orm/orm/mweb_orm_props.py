from typing import Optional, Any, Literal
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import relationship, mapped_column, MappedColumn
from sqlalchemy.sql.functions import _FunctionGenerator
from .mweb_orm_fields import JSONType
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

    # TODO: Implement due to various error, will check extensively later on
    def Column(
            self,
            name: str,
            data_type,
            primary_key: bool = False,
            foreign_key: sa.ForeignKey | None = None,
            autoincrement: bool = False,
            nullable: bool = True,
            unique: bool | None = None,
            index: bool | None = None,
            default: Any = None,
            init: bool | None = None,
            onupdate=None,
            **kw: Any,
    ) -> MappedColumn:
        args = []
        if foreign_key is not None:
            args.append(foreign_key)

        if init is None:
            if nullable or autoincrement:
                init = False
            else:
                init = True

        return mapped_column(
            *args,
            name=name,
            type_=data_type,
            primary_key=primary_key,
            autoincrement=autoincrement,
            nullable=nullable,
            unique=unique,
            index=index,
            default=default,
            onupdate=onupdate,

            # ORM / dataclass-safe
            init=init,
            kw_only=True,

            **kw,
        )

    def Integer(self):
        return sa.Integer()

    def String(self, length: Optional[int] = None, collation: Optional[str] = None):
        return sa.String(length=length, collation=collation)

    def Boolean(self, create_constraint: bool = False, name: Optional[str] = None):
        return sa.Boolean(create_constraint=create_constraint, name=name)

    def DateTime(self):
        return sa.DateTime()

    def Date(self):
        return sa.Date()

    def Time(self):
        return sa.Time()

    def Float(self):
        return sa.Float()

    def Text(self):
        return sa.Text().with_variant(LONGTEXT, "mysql")

    def BigInteger(self):
        return sa.BigInteger().with_variant(self.Integer(), "sqlite")

    def SmallInteger(self):
        return sa.SmallInteger()

    def JSON(self):
        return JSONType()

    def UUID(self, as_uuid: bool = True):
        return sa.UUID(as_uuid=as_uuid)

    def ForeignKey(self, column, onupdate: str | None = None, ondelete: str | None = None, name=None):
        return sa.ForeignKey(column, onupdate=onupdate, ondelete=ondelete, name=name)

    def Relationship(
            self,
            argument,
            viewonly: bool = False,
            lazy: LazyLoadType = "joined",
            order_by=None,
            uselist: bool = True,
            primaryjoin: Optional[_RelationshipJoinConditionArgument] = None,
            remote_side: str | None = None,
            backref: str | None = None,
            secondaryjoin: Optional[_RelationshipJoinConditionArgument] = None,
            back_populates: str | None = None,
            cascade=None,
            **kwargs
    ):
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
            secondaryjoin=secondaryjoin,
            cascade=cascade,
            **kwargs
        )

    @property
    def func(self) -> _FunctionGenerator:
        return sa.func
