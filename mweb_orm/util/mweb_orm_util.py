from mw_common import DataUtil


class MWebORMUtil:
    @staticmethod
    def enum_to_string(data: dict, name):
        value = DataUtil.dict_value(data, name)
        if value is not None:
            data[name] = str(value)
        return data
