Introduction
============

What is Serilux?
----------------

Serilux is a powerful, flexible serialization framework for Python objects. It provides
a simple and intuitive API for serializing and deserializing complex object hierarchies
with minimal boilerplate code.

Key Features
------------

- **Simple API**: Just inherit from ``Serializable`` and you're ready to go
- **Automatic Type Registration**: Classes are automatically registered for deserialization
- **Type Safety**: Built-in validation ensures objects can be properly deserialized
- **Nested Objects**: Automatically handles nested Serializable objects, lists, and dictionaries
- **Callable Serialization**: Full support for serializing functions, methods, and lambda expressions
- **Security**: Strict mode prevents deserialization of unknown fields
- **Zero Dependencies**: Pure Python with no external dependencies

Use Cases
---------

Serilux is perfect for:

- **Object Persistence**: Save and restore complex object states
- **Configuration Management**: Serialize configuration objects to JSON/YAML
- **Data Transfer**: Convert objects to dictionaries for API communication
- **State Management**: Save application state for recovery
- **Workflow Orchestration**: Serialize workflow definitions and states
- **Testing**: Create test fixtures from serialized objects

Next Steps
----------

- Read the :doc:`quickstart` guide to get started quickly
- Check out the :doc:`user_guide/index` for detailed usage
- Browse the :doc:`api_reference/index` for complete API documentation

