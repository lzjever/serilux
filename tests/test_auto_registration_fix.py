"""
Test to verify the fix for automatic registration of nested objects in Phase 2.

This test verifies that single object fields (not in containers) are now
automatically registered in Phase 2, allowing their methods to be deserialized.
"""

from serilux import (
    ObjectRegistry,
    Serializable,
    register_serializable,
)


@register_serializable
class Processor(Serializable):
    """Processor with a method field."""

    def __init__(self):
        super().__init__()
        self._id = None
        self.name = ""
        self.process = self.process_data
        self.add_serializable_fields(["_id", "name", "process"])

    def process_data(self, data):
        """Process data."""
        return data.upper()


@register_serializable
class Handler(Serializable):
    """Handler with nested Processor object."""

    def __init__(self):
        super().__init__()
        self._id = None
        self.name = ""
        self.processor = None  # Single object field (not in container)
        self.add_serializable_fields(["_id", "name", "processor"])


def test_single_object_field_auto_registration():
    """
    Test that single object fields are automatically registered in Phase 2.

    This was the limitation: single object fields were not registered,
    so their methods couldn't find their owner objects.
    """
    # Create objects
    handler = Handler()
    handler._id = "handler1"
    handler.name = "My Handler"

    processor = Processor()
    processor._id = "processor1"
    processor.name = "My Processor"
    handler.processor = processor

    # Serialize
    data = handler.serialize()
    assert "processor" in data
    assert data["processor"]["_id"] == "processor1"
    assert "process" in data["processor"]  # Method field

    # Deserialize
    new_handler = Handler()
    registry = ObjectRegistry()
    registry.register(new_handler, object_id="handler1")
    new_handler.deserialize(data, registry=registry)

    # Verify processor was deserialized
    assert new_handler.processor is not None
    assert new_handler.processor.name == "My Processor"

    # Verify processor was registered in registry (this is the fix!)
    found_processor = registry.find_by_id("processor1")
    assert found_processor is not None
    assert found_processor is new_handler.processor

    # Verify processor's method works (this tests the fix!)
    # Before the fix, this would fail because processor wasn't registered
    assert new_handler.processor.process is not None
    assert callable(new_handler.processor.process)
    result = new_handler.processor.process("test")
    assert result == "TEST"


def test_deeply_nested_objects():
    """Test deeply nested objects with methods."""

    @register_serializable
    class Level3(Serializable):
        def __init__(self):
            super().__init__()
            self._id = None
            self.handler = self.process
            self.add_serializable_fields(["_id", "handler"])

        def process(self, x):
            return x * 2

    @register_serializable
    class Level2(Serializable):
        def __init__(self):
            super().__init__()
            self._id = None
            self.level3 = None
            self.add_serializable_fields(["_id", "level3"])

    @register_serializable
    class Level1(Serializable):
        def __init__(self):
            super().__init__()
            self._id = None
            self.level2 = None
            self.add_serializable_fields(["_id", "level2"])

    # Create nested structure
    level1 = Level1()
    level1._id = "l1"

    level2 = Level2()
    level2._id = "l2"

    level3 = Level3()
    level3._id = "l3"

    level2.level3 = level3
    level1.level2 = level2

    # Serialize
    data = level1.serialize()

    # Deserialize
    new_level1 = Level1()
    registry = ObjectRegistry()
    registry.register(new_level1, object_id="l1")
    new_level1.deserialize(data, registry=registry)

    # Verify all levels were registered
    assert registry.find_by_id("l2") is not None
    assert registry.find_by_id("l3") is not None

    # Verify method works at deepest level
    assert new_level1.level2.level3.handler(5) == 10
