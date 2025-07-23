from sqlalchemy.ext.asyncio import AsyncEngine
from mw_common.mw_exception import MwException
from mweb.engine.mweb_registry import MWebRegistry
from mweb_orm.model.mweb_master_model import MWebMasterModel
from mweb_orm.orm.mweb_orm_data import DBConnectionData


class MWebORMActions:
    connection_data: dict[str, DBConnectionData] = {}
    _engines: dict[str, AsyncEngine] = {}

    @property
    def hook(self):
        from mweb.engine.mweb_hook import MWebHook
        return MWebHook

    def get_model_db_key(self, model_class, default=None):
        return getattr(model_class, '__db_key__', default)

    def get_engine_connection_data(self, db_key: str | None) -> DBConnectionData | None:

        if db_key in self.connection_data:
            return self.connection_data[db_key]

        connection = DBConnectionData(uri=MWebRegistry.config.DB_CONNECTION_URI)
        connection.poolSize = MWebRegistry.config.DB_POOL_SIZE
        connection.poolPrePing = MWebRegistry.config.DB_POOL_PRE_PING
        connection.printLog = MWebRegistry.config.DB_PRINT_LOG
        connection.maxOverflow = MWebRegistry.config.DB_MAX_OVERFLOW
        connection.poolTimeout = MWebRegistry.config.DB_POOL_TIMEOUT
        connection.poolRecycle = MWebRegistry.config.DB_POOL_RECYCLE
        connection.expireOnCommit = MWebRegistry.config.DB_EXPIRE_ON_COMMIT
        connection.future = MWebRegistry.config.DB_FUTURE

        connection_data = None
        if db_key is None:
            connection_data = connection
        elif db_key and isinstance(db_key, str) and MWebRegistry.config.DB_MULTI_CONNECTION_URIS and db_key in MWebRegistry.config.DB_MULTI_CONNECTION_URIS:
            connection.uri = MWebRegistry.config.DB_MULTI_CONNECTION_URIS[db_key]
            connection_data = connection

        # Resolve SaaS Database Connection
        tenant_resolver = self.hook.tenant_resolver()
        if tenant_resolver is not None and MWebRegistry.config.ENABLE_SAAS:
            connection_data = tenant_resolver.get_db_connection_data(db_key=db_key, default_connection=connection)

        if connection_data is not None:
            self.connection_data[db_key] = connection_data

        if not connection_data or not connection_data.uri:
            raise MwException("Database connection configuration not found!")

        return connection_data

    def get_db_key_and_model_dict(self) -> dict:
        db_key_to_models = {}
        for cls in MWebMasterModel.registry.mappers:
            model = cls.class_
            db_key = self.get_model_db_key(model_class=model)
            table = model.__table__
            db_key_to_models.setdefault(db_key, []).append(table)
        return db_key_to_models
