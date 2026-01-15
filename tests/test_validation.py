"""
Tests for validation functions.
"""

import pytest

from serilux import (
    Serializable,
    check_serializable_constructability,
    register_serializable,
    validate_serializable_tree,
)


class TestValidation:
    """Test validation functionality."""

    def test_check_constructability_valid(self, clear_registry):
        """Test checking constructability of a valid object."""

        @register_serializable
        class ValidClass(Serializable):
            def __init__(self):
                super().__init__()
                self.add_serializable_fields([])

        obj = ValidClass()
        # Should not raise
        check_serializable_constructability(obj)

    def test_check_constructability_invalid(self, clear_registry):
        """Test checking constructability of an invalid object."""

        class InvalidClass(Serializable):
            def __init__(self, required_param):
                super().__init__()
                self.add_serializable_fields([])

        obj = InvalidClass("test")
        with pytest.raises(TypeError, match="cannot be deserialized"):
            check_serializable_constructability(obj)

    def test_validate_tree_valid(self, clear_registry):
        """Test validating a valid object tree."""

        @register_serializable
        class Address(Serializable):
            def __init__(self):
                super().__init__()
                self.street = ""
                self.add_serializable_fields(["street"])

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

        # Should not raise
        validate_serializable_tree(person)

    def test_validate_tree_invalid(self, clear_registry):
        """Test validating an invalid object tree."""

        @register_serializable
        class ValidClass(Serializable):
            def __init__(self):
                super().__init__()
                self.add_serializable_fields([])

        class InvalidClass(Serializable):
            def __init__(self, required_param):
                super().__init__()
                self.add_serializable_fields([])

        valid_obj = ValidClass()
        invalid_obj = InvalidClass("test")
        valid_obj.invalid_field = invalid_obj
        valid_obj.add_serializable_fields(["invalid_field"])

        with pytest.raises(TypeError, match="non-constructable"):
            validate_serializable_tree(valid_obj)

    def test_validate_tree_with_list(self, clear_registry):
        """Test validating a tree with lists."""

        @register_serializable
        class Item(Serializable):
            def __init__(self):
                super().__init__()
                self.name = ""
                self.add_serializable_fields(["name"])

        @register_serializable
        class Container(Serializable):
            def __init__(self):
                super().__init__()
                self.items = []
                self.add_serializable_fields(["items"])

        container = Container()
        item1 = Item()
        item1.name = "Item 1"
        item2 = Item()
        item2.name = "Item 2"
        container.items = [item1, item2]

        # Should not raise
        validate_serializable_tree(container)

    def test_validate_tree_with_dict(self, clear_registry):
        """Test validating a tree with dictionaries."""

        @register_serializable
        class Item(Serializable):
            def __init__(self):
                super().__init__()
                self.name = ""
                self.add_serializable_fields(["name"])

        @register_serializable
        class Container(Serializable):
            def __init__(self):
                super().__init__()
                self.items = {}
                self.add_serializable_fields(["items"])

        container = Container()
        item1 = Item()
        item1.name = "Item 1"
        item2 = Item()
        item2.name = "Item 2"
        container.items = {"first": item1, "second": item2}

        # Should not raise
        validate_serializable_tree(container)
