"""
Test class name conflict detection in @register_serializable decorator.
"""

import pytest

from serilux import (
    Serializable,
    SerializableRegistry,
    register_serializable,
)


def test_same_class_re_registration_allowed():
    """Test that re-registering the same class object is allowed (idempotent)."""

    @register_serializable
    class TestClass(Serializable):
        def __init__(self):
            super().__init__()
            self.name = ""
            self.add_serializable_fields(["name"])

    # Re-register the same class object (not redefining) - should not raise error
    SerializableRegistry.register_class("TestClass", TestClass)

    # Verify it's registered
    assert SerializableRegistry.get_class("TestClass") is TestClass


def test_different_class_same_name_raises_error():
    """Test that registering a different class with the same name raises ValueError."""

    @register_serializable
    class ConflictClass(Serializable):
        def __init__(self):
            super().__init__()
            self.field1 = ""
            self.add_serializable_fields(["field1"])

    # Try to register a different class with the same name
    with pytest.raises(ValueError, match="Class name conflict"):

        @register_serializable
        class ConflictClass(Serializable):
            def __init__(self):
                super().__init__()
                self.field2 = ""  # Different field
                self.add_serializable_fields(["field2"])


def test_different_class_same_name_different_module():
    """Test conflict detection works even when classes are in different modules."""

    # First class
    @register_serializable
    class MultiModuleClass(Serializable):
        def __init__(self):
            super().__init__()
            self.value = 0
            self.add_serializable_fields(["value"])

    # Try to register another class with same name (simulating different module)
    with pytest.raises(ValueError, match="Class name conflict"):
        # Create a new class with same name but different implementation
        class MultiModuleClass(Serializable):
            def __init__(self):
                super().__init__()
                self.data = ""
                self.add_serializable_fields(["data"])

        # Register it
        register_serializable(MultiModuleClass)


def test_register_class_directly_with_conflict():
    """Test that SerializableRegistry.register_class also detects conflicts."""

    class ClassA(Serializable):
        def __init__(self):
            super().__init__()
            self.a = ""
            self.add_serializable_fields(["a"])

    class ClassB(Serializable):
        def __init__(self):
            super().__init__()
            self.b = ""
            self.add_serializable_fields(["b"])

    # Register first class
    SerializableRegistry.register_class("DirectConflict", ClassA)

    # Try to register different class with same name
    with pytest.raises(ValueError, match="Class name conflict"):
        SerializableRegistry.register_class("DirectConflict", ClassB)


def test_register_class_directly_same_class_allowed():
    """Test that registering the same class directly is allowed."""

    class DirectSameClass(Serializable):
        def __init__(self):
            super().__init__()
            self.value = ""
            self.add_serializable_fields(["value"])

    # Register first time
    SerializableRegistry.register_class("DirectSameClass", DirectSameClass)

    # Register same class again - should not raise error
    SerializableRegistry.register_class("DirectSameClass", DirectSameClass)

    # Verify it's still registered
    assert SerializableRegistry.get_class("DirectSameClass") is DirectSameClass


def test_multiple_conflicts():
    """Test that multiple conflicts are detected correctly."""

    @register_serializable
    class FirstClass(Serializable):
        def __init__(self):
            super().__init__()
            self.first = ""
            self.add_serializable_fields(["first"])

    @register_serializable
    class SecondClass(Serializable):
        def __init__(self):
            super().__init__()
            self.second = ""
            self.add_serializable_fields(["second"])

    # Try to register conflicts
    with pytest.raises(ValueError, match="Class name conflict.*FirstClass"):

        class FirstClass(Serializable):
            def __init__(self):
                super().__init__()
                self.conflict = ""
                self.add_serializable_fields(["conflict"])

        register_serializable(FirstClass)

    # Second class should still work
    assert SerializableRegistry.get_class("SecondClass") is not None


def test_error_message_contains_class_info():
    """Test that error message contains useful information about the conflict."""

    @register_serializable
    class ErrorTestClass(Serializable):
        def __init__(self):
            super().__init__()
            self.original = ""
            self.add_serializable_fields(["original"])

    try:

        class ErrorTestClass(Serializable):
            def __init__(self):
                super().__init__()
                self.conflict = ""
                self.add_serializable_fields(["conflict"])

        register_serializable(ErrorTestClass)
        pytest.fail("Should have raised ValueError")
    except ValueError as e:
        error_msg = str(e)
        # Check that error message contains useful information
        assert "ErrorTestClass" in error_msg
        assert "already registered" in error_msg or "Class name conflict" in error_msg
        assert "Cannot register" in error_msg or "class name conflict" in error_msg.lower()


def test_unregister_then_register_different_class():
    """Test that after unregistering, a different class can be registered."""

    @register_serializable
    class UnregisterTest(Serializable):
        def __init__(self):
            super().__init__()
            self.old = ""
            self.add_serializable_fields(["old"])

    # Unregister
    if "UnregisterTest" in SerializableRegistry.registry:
        del SerializableRegistry.registry["UnregisterTest"]

    # Now register a different class with same name
    @register_serializable
    class UnregisterTest(Serializable):  # noqa: F811 - intentional redefinition for testing
        def __init__(self):
            super().__init__()
            self.new = ""
            self.add_serializable_fields(["new"])

    # Should work now
    assert SerializableRegistry.get_class("UnregisterTest") is not None
    # Verify it's the new class
    obj = SerializableRegistry.get_class("UnregisterTest")()
    assert hasattr(obj, "new")
    assert not hasattr(obj, "old")
