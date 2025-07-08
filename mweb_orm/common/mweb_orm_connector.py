from abc import ABC, abstractmethod
from mweb_orm.orm.mweb_orm_data import DBConnectionData


class MWebTenantResolver(ABC):

    @abstractmethod
    def get_db_connection_data(self, db_key: str, default_connection: DBConnectionData) -> DBConnectionData:
        pass

    @abstractmethod
    def get_tenant_key(self, default=None) -> str | None:
        pass
