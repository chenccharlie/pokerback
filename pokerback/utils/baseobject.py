import json
from collections import OrderedDict
from enum import Enum
from typing import List, Dict, Union

from pokerback.utils.redis import get_redis


def _get_value_class_from_optional(cls):
    classes = cls.__args__
    assert len(classes) == 2
    for clas in classes:
        if clas is not type(None):
            return clas
    raise Exception("No actual type in Optional")


def _get_value_class_from_list(cls):
    classes = cls.__args__
    assert len(classes) == 1
    return classes[0]


def _get_value_class_from_dict(cls):
    classes = cls.__args__
    assert len(classes) == 2
    return classes[1]


def _get_class(cls):
    if hasattr(cls, "__origin__"):
        return cls.__origin__
    else:
        return cls


def _get_value_class(cls):
    if hasattr(cls, "__origin__"):
        if cls.__origin__ is Union:
            return _get_value_class_from_optional(cls)
        elif cls.__origin__ is Dict:
            return _get_value_class_from_dict(cls)
        elif cls.__origin__ is List:
            return _get_value_class_from_list(cls)
        else:
            raise Exception(f"Unsupported class {cls}")
    else:
        return cls


def _object_from_json_value(cls, json_value):
    if json_value is None:
        return None

    real_cls = _get_class(cls)
    if real_cls is Dict:
        assert isinstance(json_value, dict)
        value_cls = _get_value_class(cls)
        res = {}
        for key in json_value.keys():
            res[key] = _object_from_json_value(value_cls, json_value[key])
        return res
    elif real_cls is List:
        assert isinstance(json_value, list)
        value_cls = _get_value_class(cls)
        res = []
        for val in json_value:
            res.append(_object_from_json_value(value_cls, val))
        return res
    elif real_cls is Union:
        value_cls = _get_value_class(cls)
        return _object_from_json_value(value_cls, json_value)
    elif issubclass(real_cls, BaseObject):
        assert isinstance(json_value, dict)
        return baseobject_from_json_dict(real_cls, json_value)
    elif issubclass(real_cls, Enum):
        return real_cls(json_value)
    return json_value


def baseobject_from_json_dict(cls, diict):
    for key in diict.keys():
        field_class = cls.__annotations__[key]
        diict[key] = _object_from_json_value(field_class, diict[key])
    return cls(**diict)


def baseobject_as_json_dict(obj):
    if isinstance(obj, BaseObject):  # detect baseobject
        return OrderedDict(
            {
                key: baseobject_as_json_dict(value)
                for key, value in obj._asdict().items()
            }
        )
    elif isinstance(obj, str):  # iterables - strings
        return obj
    elif hasattr(obj, "keys"):  # iterables - mapping
        return OrderedDict(
            zip(obj.keys(), (baseobject_as_json_dict(item) for item in obj.values()))
        )
    elif hasattr(obj, "__iter__"):  # iterables - sequence
        return type(obj)((baseobject_as_json_dict(item) for item in obj))
    elif isinstance(obj, Enum):
        return obj.value
    else:  # non-iterable cannot contain baseobjects
        return obj


def validate_baseobject_types(cls, obj):
    real_cls = _get_class(cls)
    if real_cls is Dict:
        value_cls = _get_value_class(cls)
        for key in obj.keys():
            validate_baseobject_types(value_cls, obj.get(key, None))
    elif real_cls is List:
        value_cls = _get_value_class(cls)
        for val in obj:
            validate_baseobject_types(value_cls, val)
    elif real_cls is Union:
        if not obj:
            return
        value_cls = _get_value_class(cls)
        validate_baseobject_types(value_cls, obj)
    elif issubclass(real_cls, Enum):
        assert str(obj) in [e.value for e in real_cls]
    else:
        assert isinstance(obj, cls)
        if issubclass(real_cls, BaseObject):
            for key, value_cls in real_cls.__annotations__.items():
                validate_baseobject_types(value_cls, getattr(obj, key, None))


class BaseObject(object):
    def __init__(self, *args, **kwargs):
        for key in kwargs:
            setattr(self, key, kwargs[key])
        self.validate()

    def _asdict(self):
        return {
            key: getattr(self, key) for key in self.__class__.__annotations__.keys()
        }

    def __repr__(self) -> str:
        return str(self._asdict())

    def __eq__(self, other) -> bool:
        if not isinstance(other, BaseObject):
            # don't attempt to compare against unrelated types
            return NotImplemented
        return self.__repr__() == other.__repr__()

    def validate(self):
        validate_baseobject_types(self.__class__, self)

    def to_json_str(self):
        return json.dumps(baseobject_as_json_dict(self))

    @classmethod
    def from_json_str(cls, json_str):
        json_dict = json.loads(json_str)
        return baseobject_from_json_dict(cls, json_dict)


class BaseRedisObject(BaseObject):
    object_key_prefix = "fake_prefix_"

    def get_object_key(self):
        raise NotImplemented

    def save(self):
        self.validate()
        get_redis().set(
            self.object_key_prefix + self.get_object_key(), self.to_json_str()
        )

    def refresh(self):
        self.__dict__ = self.__class__.load(self.get_object_key()).__dict__

    @classmethod
    def load(cls, object_key):
        json_str = get_redis().get(cls.object_key_prefix + object_key)
        return cls.from_json_str(json_str)
