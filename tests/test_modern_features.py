import dataclasses
from typing import List

import pytest

from serilux import Serializable, register_serializable
from serilux.serializable import SerializableRegistry


@pytest.fixture(autouse=True)
def clear_registry():
    SerializableRegistry.clear_registry()
    yield


def test_type_hint_auto_discovery():
    """Verify that fields with type hints are automatically registered."""

    @register_serializable
    class UserHint(Serializable):
        name: str = ""
        age: int = 0
        tags: List[str] = []

        def __init__(self):
            super().__init__()

    user = UserHint()
    user.name = "Alice"
    user.age = 30
    user.tags = ["python", "serilux"]

    data = user.serialize()
    assert "_type" in data
    assert data["name"] == "Alice"
    assert data["age"] == 30
    assert data["tags"] == ["python", "serilux"]

    # Round trip
    new_user = UserHint()
    new_user.deserialize(data)
    assert new_user.name == "Alice"
    assert new_user.age == 30
    assert new_user.tags == ["python", "serilux"]


def test_dataclass_support():
    """Verify full support for standard dataclasses."""

    @register_serializable
    @dataclasses.dataclass
    class PointData(Serializable):
        x: int = 0
        y: int = 0

    p = PointData(x=10, y=20)
    data = p.serialize()
    assert data["x"] == 10
    assert data["y"] == 20

    # Deserialization without explicit __init__ call
    new_p = Serializable.deserialize_item(data)
    assert isinstance(new_p, PointData)
    assert new_p.x == 10
    assert new_p.y == 20


def test_constructor_mapping_required():
    """Verify instantiation with required constructor arguments from data."""

    @register_serializable
    class UserRequired(Serializable):
        def __init__(self, uid: int, login: str):
            super().__init__()
            self.uid = uid
            self.login = login
            self.add_serializable_fields(["uid", "login"])

    u = UserRequired(uid=1, login="admin")
    data = u.serialize()

    # Deserialization maps 'uid' and 'login' from data to __init__
    new_u = Serializable.deserialize_item(data)
    assert isinstance(new_u, UserRequired)
    assert new_u.uid == 1
    assert new_u.login == "admin"


def test_mixed_hints_and_manual():
    """Verify that manual fields and hinted fields coexist correctly."""

    @register_serializable
    class MixedObject(Serializable):
        hinted_field: str = "hint"

        def __init__(self):
            super().__init__()
            self.manual_field = "manual"
            self.add_serializable_fields(["manual_field"])

    obj = MixedObject()
    assert "hinted_field" in obj.fields_to_serialize
    assert "manual_field" in obj.fields_to_serialize

    data = obj.serialize()
    assert data["hinted_field"] == "hint"
    assert data["manual_field"] == "manual"
