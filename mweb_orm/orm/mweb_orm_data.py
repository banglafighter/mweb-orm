from dataclasses import dataclass


@dataclass(kw_only=True)
class DBConnectionData:
    uri: str
    poolPrePing: bool = True
    printLog: bool = False
    poolSize: int = 5
    maxOverflow: int = 10
    poolTimeout: int = 30  # Seconds
    poolRecycle: int = 1800  # 30 minutes
    expireOnCommit: bool = False
    future: bool = True
