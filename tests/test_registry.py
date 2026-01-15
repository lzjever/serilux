"""
Tests for the SerializableRegistry class.
"""

import pytest

from serilux import Serializable, SerializableRegistry, register_serializable


class TestSerializableRegistry:
    """Test SerializableRegistry functionality."""

    def test_register_class(self, clear_registry):
        """Test registering a class."""

        class MyClass(Serializable):
            pass

        SerializableRegistry.register_class("MyClass", MyClass)
        assert SerializableRegistry.get_class("MyClass") == MyClass

    def test_get_class(self, clear_registry):
        """Test retrieving a registered class."""

        class MyClass(Serializable):
            pass

        SerializableRegistry.register_class("MyClass", MyClass)
        cls = SerializableRegistry.get_class("MyClass")
        assert cls == MyClass

    def test_get_nonexistent_class(self, clear_registry):
        """Test retrieving a non-existent class."""
        cls = SerializableRegistry.get_class("NonExistent")
        assert cls is None

    def test_register_serializable_decorator(self, clear_registry):
        """Test @register_serializable decorator."""

        @register_serializable
        class MyClass(Serializable):
            def __init__(self):
                super().__init__()
                self.add_serializable_fields([])

        assert SerializableRegistry.get_class("MyClass") == MyClass

    def test_register_serializable_validation(self, clear_registry):
        """Test that @register_serializable validates __init__ signature."""
        with pytest.raises(TypeError):

            @register_serializable
            class InvalidClass(Serializable):
                def __init__(self, required_param):
                    super().__init__()
                    self.add_serializable_fields([])

    def test_register_serializable_with_defaults(self, clear_registry):
        """Test that @register_serializable allows default parameters."""

        @register_serializable
        class ValidClass(Serializable):
            def __init__(self, optional_param="default"):
                super().__init__()
                self.add_serializable_fields([])

        assert SerializableRegistry.get_class("ValidClass") == ValidClass
