"""
Test ObjectRegistry with nested objects to verify automatic registration works.
"""

from serilux import (
    ObjectRegistry,
    Serializable,
    register_serializable,
)


@register_serializable
class Address(Serializable):
    """Address with a method field."""

    def __init__(self):
        super().__init__()
        self._id = None
        self.street = ""
        self.handler = self.process_address  # Method field
        self.add_serializable_fields(["_id", "street", "handler"])

    def process_address(self, data):
        """Process address data."""
        return f"Address: {data}"


@register_serializable
class PersonWithAddress(Serializable):
    """Person with nested Address object."""

    def __init__(self):
        super().__init__()
        self._id = None
        self.name = ""
        self.address = None  # Single object field (not in container)
        self.add_serializable_fields(["_id", "name", "address"])


def test_nested_object_with_method_auto_registration():
    """Test that nested objects with methods are automatically registered."""
    # Create objects
    person = PersonWithAddress()
    person._id = "person1"
    person.name = "Alice"

    address = Address()
    address._id = "addr1"
    address.street = "123 Main St"
    person.address = address

    # Serialize
    data = person.serialize()

    # Deserialize
    new_person = PersonWithAddress()
    registry = ObjectRegistry()
    registry.register(new_person, object_id="person1")
    new_person.deserialize(data, registry=registry)

    # Verify address was deserialized
    assert new_person.address is not None
    assert new_person.address.street == "123 Main St"

    # Verify address's method works (this tests auto-registration)
    # The address should have been registered in Phase 2, so its method can find it
    assert new_person.address.handler is not None
    assert callable(new_person.address.handler)
    result = new_person.address.handler("test")
    assert result == "Address: test"


def test_nested_object_in_container():
    """Test that objects in containers are registered in Phase 1."""
    from serilux import register_serializable

    @register_serializable
    class TeamWithMembers(Serializable):
        def __init__(self):
            super().__init__()
            self.members = {}  # Container
            self.add_serializable_fields(["members"])

    team = TeamWithMembers()
    person1 = PersonWithAddress()
    person1._id = "person1"
    person1.name = "Alice"

    address1 = Address()
    address1._id = "addr1"
    address1.street = "123 Main St"
    person1.address = address1

    team.members["person1"] = person1

    # Serialize
    data = team.serialize()

    # Deserialize
    new_team = TeamWithMembers()
    registry = ObjectRegistry()
    new_team.deserialize(data, registry=registry)

    # Verify person1 was registered (Phase 1)
    found_person = registry.find_by_id("person1")
    assert found_person is not None
    assert found_person.name == "Alice"

    # Verify address1 was registered (Phase 2, when person1 was deserialized)
    found_address = registry.find_by_id("addr1")
    assert found_address is not None
    assert found_address.street == "123 Main St"

    # Verify address's method works
    assert new_team.members["person1"].address.handler("test") == "Address: test"
