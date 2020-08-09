import json
import pytest
from typing import List, Dict, Optional, NamedTuple

from pokerback.utils.namedtuple import BaseObjectMixin


class A(NamedTuple, BaseObjectMixin):
    num: int
    text: str


class B(NamedTuple, BaseObjectMixin):
    a: A
    lists: List[Dict[str, A]]
    dicts: Dict[str, List[Optional[A]]]
    optionals_none: Optional[A] = None
    optionals_present: Optional[A] = None


@pytest.fixture
def a_object():
    return A(num=1, text="text_a")


@pytest.fixture
def b_object(a_object):
    return B(
        a=a_object,
        lists=list(
            [dict({"first": a_object, "second": a_object}), dict({"third": a_object})]
        ),
        dicts=dict({"first": [a_object, None], "second": [a_object]}),
        optionals_present=a_object,
    )


@pytest.fixture
def b_json():
    return json.dumps(
        {
            "a": {"num": 1, "text": "text_a",},
            "lists": [
                {
                    "first": {"num": 1, "text": "text_a"},
                    "second": {"num": 1, "text": "text_a"},
                },
                {"third": {"num": 1, "text": "text_a"}},
            ],
            "dicts": {
                "first": [{"num": 1, "text": "text_a"}, None],
                "second": [{"num": 1, "text": "text_a"}],
            },
            "optionals_none": None,
            "optionals_present": {"num": 1, "text": "text_a"},
        }
    )


@pytest.mark.django_db
def test_serialize(b_object, b_json):
    json_str = b_object.to_json_str()
    assert json_str == b_json


@pytest.mark.django_db
def test_deserialize(b_object, b_json):
    constructed_b = B.from_json_str(b_json)
    assert constructed_b == b_object
