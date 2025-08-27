from math import ceil
from sqlalchemy.inspection import inspect as sa_inspect
from sqlalchemy.orm import joinedload, selectinload, subqueryload, noload, immediateload, raiseload, QueryableAttribute
from sqlalchemy import select as sa_select, func, update as sa_update, delete as sa_delete
from mw_common.mw_exception import MwException
from mweb_orm.common import Pagination
from mweb_orm.orm import mweb_orm


class MWebQueryProcessor:

    def __init__(self, model, fields=None):
        self.model = model
        self._fields = fields
        self._filters = []
        self._order_by = []
        self._group_by = []
        self._having_conditions = []
        self._joins = []
        self._limit = None
        self._offset = None
        self._distinct = False

    def select(self, *fields):
        if not self._fields:
            self._fields = list(fields)
        else:
            self._fields.extend(fields)
        return self

    def distinct(self):
        self._distinct = True
        return self

    def where(self, *conditions):
        self._filters.extend(conditions)
        return self

    def order_by(self, *ordering):
        self._order_by.extend(ordering)
        return self

    def group_by(self, *grouping):
        self._group_by.extend(grouping)
        return self

    def having(self, *conditions):
        self._having_conditions.extend(conditions)
        return self

    def join(self, target, onclause=None, isouter=False):
        self._joins.append((target, onclause, isouter))
        return self

    def limit(self, value):
        self._limit = value
        return self

    def offset(self, value):
        self._offset = value
        return self

    def scalar_subquery(self):
        """
        Returns the query as a scalar subquery.
        Useful for IN / NOT IN / EXISTS clauses.
        """
        if not self._fields or len(self._fields) != 1:
            raise MwException("scalar_subquery() requires exactly one selected field.")

        query = self._assemble_and_get_query()
        return query.scalar_subquery()

    def _get_loading_options(self):
        mapper = sa_inspect(self.model)
        options = []

        for rel in mapper.relationships:
            attr = getattr(self.model, rel.key)
            lazy = rel.lazy

            if lazy == "joined":
                options.append(joinedload(attr))
            elif lazy == "selectin":
                options.append(selectinload(attr))
            elif lazy == "subquery":
                options.append(subqueryload(attr))
            elif lazy == "noload":
                options.append(noload(attr))
            elif lazy == "immediate":
                options.append(immediateload(attr))
            elif lazy == "raise":
                options.append(raiseload(attr))
            # "select" is default lazy and doesn't need explicit load

        return options

    def _assemble_and_get_query(self, query=None, paginate: bool = True):
        if query is None:
            query = sa_select(*(self._fields if self._fields else [self.model]))

        if self._distinct:
            query = query.distinct()

        if self._filters:
            query = query.where(*self._filters)

        if self._joins:
            for target, onclause, isouter in self._joins:
                query = query.join(target, onclause=onclause, isouter=isouter)

        if self._group_by:
            query = query.group_by(*self._group_by)

        if self._having_conditions:
            query = query.having(*self._having_conditions)

        if self._order_by:
            query = query.order_by(*self._order_by)

        if self._limit is not None and paginate:
            query = query.limit(self._limit)

        if self._offset is not None and paginate:
            query = query.offset(self._offset)

        return query

    async def _execute(self, query):
        try:
            async with await mweb_orm.get_session() as session:
                return await session.execute(query)
        except Exception as e:
            raise MwException(e)

    async def _begin_execute(self, query):
        try:
            async with await mweb_orm.get_session() as session:
                async with session.begin():
                    return await session.execute(query)
        except Exception as e:
            raise MwException(e)

    def _add_loading_options(self, query):
        if self._fields:
            return query

        loading_options = self._get_loading_options()
        if loading_options:
            query = query.options(*loading_options)

        return query


    async def read_all(self):
        query = self._assemble_and_get_query()
        query = self._add_loading_options(query)
        result = await self._execute(query=query)
        if self._fields:
            return result.all()
        else:
            return result.unique().scalars().all()

    async def first(self):
        query = self._assemble_and_get_query()
        query = self._add_loading_options(query)
        query = query.limit(1)
        result = await self._execute(query=query)
        if self._fields:
            return result.first()
        else:
            return result.unique().scalars().first()

    async def count(self):
        query = sa_select(func.count()).select_from(self.model)
        query = self._assemble_and_get_query(query=query)
        query = query.order_by(None)
        result = await self._execute(query=query)
        return result.scalar_one()

    async def paginate(self, page: int = 1, item_per_page: int = 20, count: bool = True) -> Pagination:
        page = max(page or 1, 1)

        if item_per_page == -1:
            self._limit = None
            self._offset = None
        else:
            item_per_page = max(item_per_page, 1)
            self._limit = item_per_page
            self._offset = (page - 1) * item_per_page

        query = self._assemble_and_get_query()
        query = self._add_loading_options(query)
        result = await self._execute(query=query)

        items = (
            result.unique().scalars().all()
            if not self._fields
            else result.all()
        )

        total = 0
        total_pages = 1

        if count:
            count_query = sa_select(func.count()).select_from(self.model)
            count_query = self._assemble_and_get_query(query=count_query, paginate=False)
            count_query = count_query.order_by(None)
            count_result = await self._execute(query=count_query)
            total = count_result.scalar_one_or_none()
            total_pages = (
                1 if item_per_page == -1 else ceil(total / item_per_page) if total else 1
            )

        return Pagination(
            page=page,
            itemPerPage=item_per_page,
            total=total,
            totalPage=total_pages,
            items=items,
        )

    async def update(self, values: dict):
        if not values:
            raise MwException("No update values provided.")

        if not self._filters:
            raise MwException("Update without filter is not allowed.")

        query = sa_update(self.model).where(*self._filters).values(**values)
        await self._begin_execute(query)

    async def delete(self):
        if not self._filters:
            raise MwException("Delete without filter is not allowed.")

        query = sa_delete(self.model).where(*self._filters)
        await self._begin_execute(query)

    async def soft_delete(self):
        if not self._filters:
            raise MwException("Soft delete without filter is not allowed.")

        if not hasattr(self.model, "isDeleted"):
            raise MwException("Model does not support soft delete.")

        query = sa_update(self.model).where(*self._filters).values(isDeleted=True)
        await self._begin_execute(query)


class MWebPropsQueryProcessor:
    def __get__(self, instance, owner):
        return MWebQueryProcessor(owner)
