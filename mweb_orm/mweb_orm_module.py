from mweb import MWebBase, MWebConfig
from mweb.engine.mweb_hook import MWebHook
from mweb.engine.mweb_util import MWebUtil
from mweb_orm.common.mweb_orm_cli import register_mweb_orm_cli
from mweb_orm.common.mweb_orm_config import MWebORMConfig
from mweb_orm.common.mweb_orm_hook import MWebORMHook


class MWebORMModule:

    def register(self, mweb_app: MWebBase, config: MWebConfig, hook: MWebHook):
        MWebUtil.copy_config_property(source=config, destination=MWebORMConfig)
        MWebUtil.copy_config_property(source=hook, destination=MWebORMHook)

        register_mweb_orm_cli(mweb_app=mweb_app, config=config)

