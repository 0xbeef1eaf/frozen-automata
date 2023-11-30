class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        else:
            instance = cls._instances[cls]
        return instance


class Factory(type):
    _base_classes = {}

    def __call__(cls, child_type: str, *args, **kwargs):
        if cls not in cls._base_classes:
            cls._base_classes[cls] = {}
        if child_type not in cls._base_classes[cls]:
            instance = super().__call__(*args, **kwargs)
            cls._base_classes[cls][child_type] = instance
        else:
            instance = cls._base_classes[cls][child_type]
        return instance
