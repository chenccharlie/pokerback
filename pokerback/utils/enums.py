from enum import Enum


class ModelEnum(Enum):
    @classmethod
    def choices(cls):
        return tuple((i.value, i.name) for i in cls)

    def __str__(self):
        return self.value
