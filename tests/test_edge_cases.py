"""Edge case tests to improve coverage."""

import pytest
from serilux import (
    Serializable,
    register_serializable,
    serialize_callable_with_fallback,
    deserialize_lambda_expression,
    ObjectRegistry,
    validate_serializable_tree,
)


@register_serializable
class SimpleObject(Serializable):
    def __init__(self):
        super().__init__()
        self.name = ""
        self.value = 0
        self.add_serializable_fields(["name", "value"])


class TestEdgeCases:
    """Test edge cases and error paths."""

    def test_add_non_string_field_raises_error(self):
        """Test that adding non-string fields raises ValueError."""
        obj = SimpleObject()
        with pytest.raises(ValueError, match="All fields must be strings"):
            obj.add_serializable_fields(["valid", 123, None])

    def test_remove_serializable_fields(self):
        """Test removing serializable fields."""
        obj = SimpleObject()
        initial_count = len(obj.fields_to_serialize)
        obj.remove_serializable_fields(["name"])
        assert len(obj.fields_to_serialize) == initial_count - 1
        assert "name" not in obj.fields_to_serialize

    def test_validate_tree_with_invalid_object(self):
        """Test validate_serializable_tree with non-constructable object."""

        class InvalidClass(Serializable):
            def __init__(self, required_param):
                super().__init__()
                self.required_param = required_param

        obj = InvalidClass("test")
        with pytest.raises(TypeError):
            validate_serializable_tree(obj)

    def test_serialize_non_serializable_callable(self):
        """Test serialization of callable that cannot be serialized."""
        obj = SimpleObject()
        # Add handler field to fields_to_serialize
        obj.add_serializable_fields(["handler"])
        # Create a lambda that cannot be serialized (no source)
        obj.handler = lambda x: x + 1
        # This should not crash, but may return None for the callable
        data = obj.serialize()
        # The callable should be serialized or None
        assert "handler" in data
        # Lambda should be serialized as lambda_expression
        if data["handler"] is not None:
            assert data["handler"].get("_type") in ["callable", "lambda_expression"]

    def test_deserialize_with_unknown_type(self):
        """Test deserialization with unknown type raises error."""
        obj = SimpleObject()
        data = {
            "_type": "SimpleObject",
            "name": "test",
            "value": 42,
            "unknown_field": "should_fail_in_strict"
        }
        # Should work in non-strict mode
        obj.deserialize(data, strict=False)

        # Should fail in strict mode
        with pytest.raises(ValueError, match="Unknown fields"):
            obj.deserialize(data, strict=True)

    def test_object_registry_find_by_id_not_found(self):
        """Test ObjectRegistry.find_by_id with non-existent ID."""
        registry = ObjectRegistry()
        result = registry.find_by_id("non_existent_id")
        assert result is None

    def test_object_registry_find_by_class_and_id_not_found(self):
        """Test ObjectRegistry.find_by_class_and_id with non-existent objects."""
        registry = ObjectRegistry()
        result = registry.find_by_class_and_id("TestClass", "non_existent_id")
        assert result is None

    def test_object_registry_clear(self):
        """Test ObjectRegistry.clear method."""
        registry = ObjectRegistry()
        obj = SimpleObject()
        obj._id = "test_id"
        registry.register(obj, object_id="test_id")
        assert len(registry._objects_by_id) > 0

        registry.clear()
        assert len(registry._objects_by_id) == 0
        assert len(registry._objects_by_class) == 0
        assert len(registry._custom_lookups) == 0

    def test_object_registry_register_custom_lookup(self):
        """Test ObjectRegistry.register_custom_lookup."""
        registry = ObjectRegistry()

        def custom_lookup(class_name, object_id):
            return f"custom_{class_name}_{object_id}"

        registry.register_custom_lookup("TestClass", custom_lookup)
        assert "TestClass" in registry._custom_lookups

    def test_deserialize_lambda_with_missing_expression(self):
        """Test deserialize_lambda_expression with missing expression field."""
        with pytest.raises(ValueError, match="missing 'expression' field"):
            deserialize_lambda_expression({"_type": "lambda_expression"})

    def test_deserialize_lambda_with_invalid_type(self):
        """Test deserialize_lambda_expression with wrong type."""
        result = deserialize_lambda_expression({"_type": "wrong_type"})
        assert result is None

    def test_deserialize_lambda_with_syntax_error(self):
        """Test deserialize_lambda_expression with syntax error."""
        with pytest.raises(ValueError, match="syntax error"):
            deserialize_lambda_expression({
                "_type": "lambda_expression",
                "expression": "this is not valid python !@#"
            })

    def test_serialize_callable_with_fallback_none(self):
        """Test serialize_callable_with_fallback with None."""
        result = serialize_callable_with_fallback(None)
        assert result is None


class TestCallableExpressionExtraction:
    """Test callable expression extraction and serialization."""

    def test_serialize_lambda_with_fallback(self):
        """Test serializing lambda with fallback to expression."""
        # Define a lambda at module level for testing
        condition = lambda x: x.get("priority") == "high"
        result = serialize_callable_with_fallback(condition)
        assert result is not None
        assert result.get("_type") in ["callable", "lambda_expression"]

    def test_serialize_lambda_with_fallback_no_fallback(self):
        """Test serialize_callable_with_fallback without fallback."""
        condition = lambda x: x.get("priority") == "high"
        result = serialize_callable_with_fallback(condition, fallback_to_expression=False)
        # Should still work if lambda can be serialized
        assert result is not None


class TestErrorHandling:
    """Test error handling paths."""

    def test_serialize_depth_limit(self):
        """Test that serialization respects depth limit."""
        # Create a deeply nested structure
        obj = SimpleObject()
        obj.add_serializable_fields(["nested"])

        # Create 10 levels of nesting (should work)
        current = obj
        for i in range(10):
            nested = SimpleObject()
            nested.add_serializable_fields(["nested"])  # Add nested field to each object
            nested.name = f"level_{i}"
            current.nested = nested
            current = nested

        # Should serialize fine with default limit
        data = obj.serialize()
        assert data is not None

        # Create a very deep structure (over 100 levels)
        obj2 = SimpleObject()
        obj2.add_serializable_fields(["nested"])
        current = obj2
        for i in range(101):
            nested = SimpleObject()
            nested.add_serializable_fields(["nested"])  # Add nested field to each object
            nested.name = f"level_{i}"
            current.nested = nested
            current = nested

        # Should raise ValueError due to depth limit
        with pytest.raises(ValueError, match="depth limit"):
            obj2.serialize(max_depth=100)

    def test_serialize_custom_depth_limit(self):
        """Test serialization with custom depth limit."""
        obj = SimpleObject()
        obj.add_serializable_fields(["nested"])

        # Create 5 levels of nesting
        current = obj
        for i in range(5):
            nested = SimpleObject()
            nested.add_serializable_fields(["nested"])  # Add nested field to each object
            nested.name = f"level_{i}"
            current.nested = nested
            current = nested

        # Should fail with limit of 3
        with pytest.raises(ValueError, match="depth limit"):
            obj.serialize(max_depth=3)

    def test_deserialize_with_missing_class(self):
        """Test deserialization with missing class raises error."""
        obj = SimpleObject()
        # Need to add a field that references the missing class
        obj.add_serializable_fields(["nested_obj"])
        data = {
            "_type": "SimpleObject",
            "name": "test",
            "value": 42,
            "nested_obj": {
                "_type": "NonExistentClass",
                "value": 123
            }
        }
        # Should raise error when trying to deserialize the nested object
        with pytest.raises(ValueError, match="Failed to deserialize field"):
            obj.deserialize(data)

    def test_deserialize_item_with_missing_class(self):
        """Test deserialize_item with missing class."""
        from serilux.serializable import Serializable
        data = {"_type": "NonExistentClass", "value": 42}
        with pytest.raises(ValueError, match="class not found in registry"):
            Serializable.deserialize_item(data)
