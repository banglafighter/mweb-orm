from mweb import MWebBase, MWebConfig, Response, MWebHook, MWebUtil
from .common.mweb_orm_cli import register_mweb_orm_cli
from .common.mweb_orm_config import MWebORMConfig
from .common.mweb_orm_hook import MWebORMHook



class MWebORMModule:

    def register(self, mweb_app: MWebBase, config: MWebConfig, hook: MWebHook):
        MWebUtil.copy_config_property(source=config, destination=MWebORMConfig)
        MWebUtil.copy_config_property(source=hook, destination=MWebORMHook)

        register_mweb_orm_cli(mweb_app=mweb_app, config=config)

        mweb_app.after_request_funcs.setdefault(None, []).append(self.close_orm_session)

    async def close_orm_session(self, response: Response):
        from mweb_orm.orm import mweb_orm
        await mweb_orm.close_session()
        return response
