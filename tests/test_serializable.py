"""
Tests for the Serializable class and core serialization functionality.
"""

import pytest

from serilux import Serializable, register_serializable, UnknownFieldError


class TestSerializable:
    """Test basic Serializable functionality."""

    def test_basic_serialization(self, clear_registry):
        """Test basic serialization of a simple object."""

        @register_serializable
        class Person(Serializable):
            def __init__(self):
                super().__init__()
                self.name = ""
                self.age = 0
                self.add_serializable_fields(["name", "age"])

        person = Person()
        person.name = "Alice"
        person.age = 30

        data = person.serialize()
        assert data["_type"] == "Person"
        assert data["name"] == "Alice"
        assert data["age"] == 30

    def test_basic_deserialization(self, clear_registry):
        """Test basic deserialization of a simple object."""

        @register_serializable
        class Person(Serializable):
            def __init__(self):
                super().__init__()
                self.name = ""
                self.age = 0
                self.add_serializable_fields(["name", "age"])

        data = {"_type": "Person", "name": "Bob", "age": 25}
        person = Person()
        person.deserialize(data)

        assert person.name == "Bob"
        assert person.age == 25

    def test_nested_objects(self, clear_registry):
        """Test serialization of nested Serializable objects."""

        @register_serializable
        class Address(Serializable):
            def __init__(self):
                super().__init__()
                self.street = ""
                self.city = ""
                self.add_serializable_fields(["street", "city"])

        @register_serializable
        class Person(Serializable):
            def __init__(self):
                super().__init__()
                self.name = ""
                self.address = None
                self.add_serializable_fields(["name", "address"])

        person = Person()
        person.name = "Alice"
        person.address = Address()
        person.address.street = "123 Main St"
        person.address.city = "New York"

        data = person.serialize()
        assert data["name"] == "Alice"
        assert data["address"]["_type"] == "Address"
        assert data["address"]["street"] == "123 Main St"
        assert data["address"]["city"] == "New York"

        # Test deserialization
        new_person = Person()
        new_person.deserialize(data)
        assert new_person.name == "Alice"
        assert new_person.address.street == "123 Main St"
        assert new_person.address.city == "New York"

    def test_lists(self, clear_registry):
        """Test serialization of lists containing Serializable objects."""

        @register_serializable
        class Person(Serializable):
            def __init__(self):
                super().__init__()
                self.name = ""
                self.add_serializable_fields(["name"])

        @register_serializable
        class Team(Serializable):
            def __init__(self):
                super().__init__()
                self.name = ""
                self.members = []
                self.add_serializable_fields(["name", "members"])

        team = Team()
        team.name = "Engineering"
        person1 = Person()
        person1.name = "Alice"
        person2 = Person()
        person2.name = "Bob"
        team.members = [person1, person2]

        data = team.serialize()
        assert data["name"] == "Engineering"
        assert len(data["members"]) == 2
        assert data["members"][0]["name"] == "Alice"
        assert data["members"][1]["name"] == "Bob"

        # Test deserialization
        new_team = Team()
        new_team.deserialize(data)
        assert new_team.name == "Engineering"
        assert len(new_team.members) == 2
        assert new_team.members[0].name == "Alice"
        assert new_team.members[1].name == "Bob"

    def test_dictionaries(self, clear_registry):
        """Test serialization of dictionaries containing Serializable objects."""

        @register_serializable
        class Person(Serializable):
            def __init__(self):
                super().__init__()
                self.name = ""
                self.add_serializable_fields(["name"])

        @register_serializable
        class Company(Serializable):
            def __init__(self):
                super().__init__()
                self.name = ""
                self.employees = {}
                self.add_serializable_fields(["name", "employees"])

        company = Company()
        company.name = "Acme Corp"
        person1 = Person()
        person1.name = "Alice"
        person2 = Person()
        person2.name = "Bob"
        company.employees = {"manager": person1, "developer": person2}

        data = company.serialize()
        assert data["name"] == "Acme Corp"
        assert data["employees"]["manager"]["name"] == "Alice"
        assert data["employees"]["developer"]["name"] == "Bob"

        # Test deserialization
        new_company = Company()
        new_company.deserialize(data)
        assert new_company.name == "Acme Corp"
        assert new_company.employees["manager"].name == "Alice"
        assert new_company.employees["developer"].name == "Bob"

    def test_add_serializable_fields(self, clear_registry):
        """Test adding fields to serialize."""

        @register_serializable
        class Person(Serializable):
            def __init__(self):
                super().__init__()
                self.name = ""
                self.age = 0
                self.add_serializable_fields(["name", "age"])

        person = Person()
        person.email = "test@example.com"
        person.add_serializable_fields(["email"])

        data = person.serialize()
        assert "email" in data

    def test_remove_serializable_fields(self, clear_registry):
        """Test removing fields from serialization."""

        @register_serializable
        class Person(Serializable):
            def __init__(self):
                super().__init__()
                self.name = ""
                self.age = 0
                self.add_serializable_fields(["name", "age"])

        person = Person()
        person.name = "Alice"
        person.age = 30

        person.remove_serializable_fields(["age"])
        data = person.serialize()
        assert "name" in data
        assert "age" not in data

    def test_strict_mode(self, clear_registry):
        """Test strict mode for deserialization."""

        @register_serializable
        class Person(Serializable):
            def __init__(self):
                super().__init__()
                self.name = ""
                self.add_serializable_fields(["name"])

        data = {"_type": "Person", "name": "Alice", "unknown_field": "value"}
        person = Person()

        # Non-strict mode should ignore unknown fields
        person.deserialize(data, strict=False)
        assert person.name == "Alice"

        # Strict mode should raise error
        with pytest.raises(UnknownFieldError):
            person.deserialize(data, strict=True)

    def test_deserialize_item(self, clear_registry):
        """Test static deserialize_item method."""

        @register_serializable
        class Person(Serializable):
            def __init__(self):
                super().__init__()
                self.name = ""
                self.add_serializable_fields(["name"])

        # Test dict with _type
        data = {"_type": "Person", "name": "Alice"}
        result = Serializable.deserialize_item(data)
        assert isinstance(result, Person)
        assert result.name == "Alice"

        # Test dict without _type
        data = {"key": "value"}
        result = Serializable.deserialize_item(data)
        assert result == {"key": "value"}

        # Test list
        data = [1, 2, 3]
        result = Serializable.deserialize_item(data)
        assert result == [1, 2, 3]

        # Test primitive
        result = Serializable.deserialize_item(42)
        assert result == 42
