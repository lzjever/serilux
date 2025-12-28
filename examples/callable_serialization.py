"""
Callable serialization example for Serilux.

This example demonstrates:
- Serializing and deserializing functions
- Serializing and deserializing methods
- Serializing lambda expressions
- Using ObjectRegistry for method deserialization
"""

from serilux import (
    Serializable,
    register_serializable,
    serialize_callable,
    serialize_callable_with_fallback,
    deserialize_callable,
    deserialize_lambda_expression,
    ObjectRegistry,
)


# Example 1: Serializing module-level functions
def process_data(data):
    """A simple processing function."""
    return data.upper()


def filter_high_priority(item):
    """Filter function for high priority items."""
    return item.get("priority") == "high"


# Example 2: Serializable class with callable fields
@register_serializable
class DataProcessor(Serializable):
    """A processor with a callable handler."""

    def __init__(self):
        super().__init__()
        self.name = ""
        self.handler = None  # Will store a function
        self.add_serializable_fields(["name", "handler"])


@register_serializable
class ConditionalRouter(Serializable):
    """A router with a condition function."""

    def __init__(self):
        super().__init__()
        self._id = None
        self.name = ""
        self.condition = None  # Will store a lambda or function
        self.add_serializable_fields(["name", "condition"])

    def route(self, data):
        """Route data based on condition."""
        if self.condition and self.condition(data):
            return "route_a"
        return "route_b"


def main():
    """Run the callable serialization example."""
    print("=== Serilux Callable Serialization Example ===\n")

    # Example 1: Serialize and deserialize a module function
    print("1. Serializing module-level function...")
    serialized_func = serialize_callable(process_data)
    print(f"   Serialized: {serialized_func}\n")

    # Deserialize the function
    deserialized_func = deserialize_callable(serialized_func)
    print(f"   Deserialized function works: {deserialized_func('hello') == 'HELLO'}\n")

    # Example 2: Serialize a function in a Serializable object
    print("2. Serializing function in Serializable object...")
    processor = DataProcessor()
    processor.name = "Uppercase Processor"
    processor.handler = process_data

    data = processor.serialize()
    print(f"   Processor data: {data}\n")

    # Deserialize
    new_processor = DataProcessor()
    new_processor.deserialize(data)
    print(f"   Handler works: {new_processor.handler('test') == 'TEST'}\n")

    # Example 3: Serialize lambda expression
    print("3. Serializing lambda expression...")
    condition = lambda x: x.get("priority") == "high"
    serialized_lambda = serialize_callable_with_fallback(condition)
    print(f"   Serialized lambda: {serialized_lambda}\n")

    # Deserialize lambda
    deserialized_lambda = deserialize_lambda_expression(serialized_lambda)
    test_data = {"priority": "high"}
    print(f"   Lambda works: {deserialized_lambda(test_data) == True}\n")

    # Example 4: Serialize lambda expression in Serializable object
    # Note: To ensure lambda is serialized as lambda_expression (not as function),
    # we use serialize_callable_with_fallback and store the serialized data directly.
    # This is useful when you want to preserve the lambda expression for deserialization.
    print("4. Serializing lambda expression in Serializable object...")
    router = ConditionalRouter()
    router._id = "router1"
    router.name = "Priority Router"

    # Create lambda and serialize it as expression using fallback
    condition_lambda = lambda x: x.get("priority") == "high"
    condition_serialized = serialize_callable_with_fallback(condition_lambda)
    # Store the serialized data directly (this ensures lambda_expression format)
    router.condition = condition_serialized

    router_data = router.serialize()
    print(f"   Router data: {router_data}\n")

    # Check if condition was serialized as lambda_expression
    condition_data = router_data.get("condition", {})
    if condition_data.get("_type") == "lambda_expression":
        print("   ✓ Condition serialized as lambda_expression\n")
    else:
        print(f"   Note: Condition serialized as {condition_data.get('_type', 'unknown')}\n")

    # Deserialize with registry
    new_router = ConditionalRouter()
    registry = ObjectRegistry()
    registry.register(new_router, object_id="router1")
    new_router.deserialize(router_data, registry=registry)

    # The condition should be deserialized as a callable
    if callable(new_router.condition):
        test_item = {"priority": "high"}
        result = new_router.route(test_item)
        print(f"   Router works: {result == 'route_a'}\n")
    else:
        print("   ⚠ Condition not deserialized as callable\n")

    # Example 5: Serialize method with ObjectRegistry
    print("5. Serializing method with ObjectRegistry...")

    @register_serializable
    class Handler(Serializable):
        def __init__(self):
            super().__init__()
            self._id = "handler1"
            self.name = ""
            self.process = self.process_data
            self.add_serializable_fields(["name", "process"])

        def process_data(self, data):
            return data.upper()

    handler = Handler()
    handler.name = "Uppercase Handler"
    handler_data = handler.serialize()
    print(f"   Handler data: {handler_data}\n")

    # Deserialize with registry
    new_handler = Handler()
    registry2 = ObjectRegistry()
    registry2.register(new_handler, object_id="handler1")
    new_handler.deserialize(handler_data, registry=registry2)

    print(f"   Method works: {new_handler.process('test') == 'TEST'}\n")

    print("✓ All callable serialization examples successful!")


if __name__ == "__main__":
    main()
