from mweb_orm.common.mweb_orm_connector import MWebTenantResolver


class MWebORMHook:
    TENANT_RESOLVER: MWebTenantResolver = None

    @classmethod
    def get_tenant_resolver(cls) -> MWebTenantResolver | None:
        if cls.TENANT_RESOLVER is not None and isinstance(cls.TENANT_RESOLVER, MWebTenantResolver):
            return cls.TENANT_RESOLVER
        return None
