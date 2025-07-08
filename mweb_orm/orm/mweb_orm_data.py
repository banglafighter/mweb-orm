from dataclasses import dataclass


@dataclass(kw_only=True)
class DBConnectionData:
    uri: str
    poolPrePing: bool = False
    printLog: bool = False
    poolSize: int = 5
    maxOverflow: int = 10
    poolTimeout: int = 30  # Seconds
    poolRecycle: int = -1
    expireOnCommit: bool = False
    future: bool = True
