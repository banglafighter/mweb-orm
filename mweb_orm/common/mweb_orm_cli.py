import asyncio
from mw_common.mw_console_log import Console
from mweb import MWebBase, MWebConfig
from mweb.engine.mweb_cli import MWebCLI
from mweb_orm.orm.mweb_orm import mweb_orm

mweb_orm_cli = MWebCLI(name="db", help_text="MWeb Database Manipulation Interface")
_orm_mweb_app: MWebBase = None


@mweb_orm_cli.command("init", help="Initialize database models")
def initialize():
    asyncio.run(_initialize_async())

async def _initialize_async():
    async with _orm_mweb_app.app_context():
        await mweb_orm.create_drop_all_model(action="create")
        Console.blue("Successfully Initialized Database & Models", bold=True, system_log=True)


@mweb_orm_cli.command("drop", help="Drop database tables")
def drop():
    asyncio.run(_drop_async())


async def _drop_async():
    async with _orm_mweb_app.app_context():
        await mweb_orm.create_drop_all_model(action="drop")
        Console.blue('Successfully Drop Database Models', bold=True, system_log=True)


def register_mweb_orm_cli(mweb_app: MWebBase, config: MWebConfig):
    global _orm_mweb_app
    _orm_mweb_app = mweb_app
    if mweb_app is not None:
        mweb_app.cli.add_command(mweb_orm_cli)
