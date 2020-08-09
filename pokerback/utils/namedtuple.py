import json
from collections import OrderedDict
from typing import NamedTuple, NamedTupleMeta, List, Dict, Union


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
    elif issubclass(real_cls, NamedTuple):
        assert isinstance(json_value, dict)
        return namedtuple_from_json_dict(real_cls, json_value)
    return json_value


def namedtuple_from_json_dict(cls, diict):
    for key in diict.keys():
        field_class = cls._field_types[key]
        diict[key] = _object_from_json_value(field_class, diict[key])
    return cls(**diict)


def namedtuple_as_json_dict(obj):
    if hasattr(obj, "_asdict"):  # detect namedtuple
        return OrderedDict(
            zip(obj._fields, (namedtuple_as_json_dict(item) for item in obj))
        )
    elif isinstance(obj, str):  # iterables - strings
        return obj
    elif hasattr(obj, "keys"):  # iterables - mapping
        return OrderedDict(
            zip(obj.keys(), (namedtuple_as_json_dict(item) for item in obj.values()))
        )
    elif hasattr(obj, "__iter__"):  # iterables - sequence
        return type(obj)((namedtuple_as_json_dict(item) for item in obj))
    else:  # non-iterable cannot contain namedtuples
        return obj


class MultipleInheritanceNamedTupleMeta(NamedTupleMeta):
    def __new__(mcls, typename, bases, ns):
        if NamedTuple in bases:
            base = super().__new__(mcls, "_base_" + typename, bases, ns)
            bases = (base, *(b for b in bases if not isinstance(b, NamedTuple)))
        return super(NamedTupleMeta, mcls).__new__(mcls, typename, bases, ns)


class NamedTupleJsonMixin(metaclass=MultipleInheritanceNamedTupleMeta):
    def validate(self):
        pass

    def to_json_str(self):
        return json.dumps(namedtuple_as_json_dict(self))

    @classmethod
    def from_json_str(cls, json_str):
        json_dict = json.loads(json_str)
        return namedtuple_from_json_dict(cls, json_dict)


class BaseObjectMixin(NamedTupleJsonMixin):
    pass
