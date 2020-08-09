import json
import pytest
from enum import Enum
from typing import List, Dict, Optional, NamedTuple

from pokerback.utils.namedtuple import BaseObjectMixin


class Choice(Enum):
    CHOICE_A = 1
    CHOICE_B = 2


class A(NamedTuple, BaseObjectMixin):
    num: int
    text: str
    choice: Choice = Choice.CHOICE_B


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
            "a": {"num": 1, "text": "text_a", "choice": 2},
            "lists": [
                {
                    "first": {"num": 1, "text": "text_a", "choice": 2},
                    "second": {"num": 1, "text": "text_a", "choice": 2},
                },
                {"third": {"num": 1, "text": "text_a", "choice": 2}},
            ],
            "dicts": {
                "first": [{"num": 1, "text": "text_a", "choice": 2}, None],
                "second": [{"num": 1, "text": "text_a", "choice": 2}],
            },
            "optionals_none": None,
            "optionals_present": {"num": 1, "text": "text_a", "choice": 2},
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
