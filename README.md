# Serilux 📦

[![PyPI version](https://badge.fury.io/py/serilux.svg)](https://badge.fury.io/py/serilux)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](LICENSE)
[![Documentation](https://readthedocs.org/projects/serilux/badge/?version=latest)](https://serilux.readthedocs.io)

**Serilux** is a powerful, flexible serialization framework for Python objects. With its intuitive API and automatic type registration, you can easily serialize and deserialize complex object hierarchies with minimal code.

## ✨ Why Serilux?

- 🎯 **Simple API**: Just inherit from `Serializable` and you're ready to go
- 🔄 **Automatic Type Registration**: Classes are automatically registered for deserialization
- 🛡️ **Type Safety**: Built-in validation ensures objects can be properly deserialized
- 🌳 **Nested Objects**: Automatically handles nested Serializable objects, lists, and dictionaries
- 🔧 **Callable Serialization**: Full support for serializing functions, methods, and lambda expressions
- 🔒 **Security**: Strict mode prevents deserialization of unknown fields
- ⚡ **Zero Dependencies**: Pure Python with no external dependencies
- 🎓 **Easy to Use**: Minimal boilerplate, maximum flexibility

## 🎯 Perfect For

- **Object Persistence**: Save and restore complex object states
- **Configuration Management**: Serialize configuration objects to JSON/YAML
- **Data Transfer**: Convert objects to dictionaries for API communication
- **State Management**: Save application state for recovery
- **Workflow Orchestration**: Serialize workflow definitions and states
- **Testing**: Create test fixtures from serialized objects

## 📦 Installation

### Quick Install (Recommended)

```bash
pip install serilux
```

That's it! You're ready to go.

### Development Install

For development with all dependencies:

```bash
pip install -e ".[dev]"
# Or using Makefile
make dev-install
```

## 🚀 Quick Start

### Create Your First Serializable Class in 3 Steps

**Step 1: Define a Serializable Class**

```python
from serilux import Serializable, register_serializable

@register_serializable
class Person(Serializable):
    def __init__(self):
        super().__init__()
        self.name = ""
        self.age = 0
        # Register fields to serialize
        self.add_serializable_fields(["name", "age"])
```

**Step 2: Create and Use Objects**

```python
# Create an object
person = Person()
person.name = "Alice"
person.age = 30

# Serialize to dictionary
data = person.serialize()
print(data)
# {'_type': 'Person', 'name': 'Alice', 'age': 30}
```

**Step 3: Deserialize**

```python
# Deserialize from dictionary
new_person = Person()
new_person.deserialize(data)
print(new_person.name)  # "Alice"
print(new_person.age)   # 30
```

**🎉 Done!** You've created your first serializable class.

## 💡 Key Features

### 🔄 Automatic Type Registration

Classes decorated with `@register_serializable` are automatically registered:

```python
@register_serializable
class MyClass(Serializable):
    def __init__(self):
        super().__init__()
        self.add_serializable_fields(["field1", "field2"])
```

**Class Name Conflict Detection**: Serilux automatically detects and prevents class name conflicts.
If you try to register a different class with the same name, a `ValueError` is raised to prevent
incorrect deserialization:

```python
@register_serializable
class Processor(Serializable):
    def __init__(self):
        super().__init__()
        self.name = ""
        self.add_serializable_fields(["name"])

# This will raise ValueError: Class name conflict
@register_serializable
class Processor(Serializable):  # Different class, same name
    def __init__(self):
        super().__init__()
        self.value = 0
        self.add_serializable_fields(["value"])
```

### 🌳 Nested Objects

Automatically handles nested Serializable objects:

```python
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

# Create nested objects
person = Person()
person.name = "Alice"
person.address = Address()
person.address.street = "123 Main St"
person.address.city = "New York"

# Serialize - nested objects are automatically handled
data = person.serialize()
```

### 📋 Lists and Dictionaries

Handles lists and dictionaries containing Serializable objects:

```python
@register_serializable
class Team(Serializable):
    def __init__(self):
        super().__init__()
        self.name = ""
        self.members = []  # List of Person objects
        self.add_serializable_fields(["name", "members"])

team = Team()
team.name = "Engineering"
team.members = [person1, person2, person3]

# Serialize - list items are automatically serialized
data = team.serialize()
```

### 🔧 Callable Serialization

Serilux supports serializing and deserializing callable objects (functions, methods, lambda expressions):

```python
from serilux import serialize_callable, deserialize_callable, serialize_callable_with_fallback

# Serialize a function
def process_data(data):
    return data.upper()

serialized = serialize_callable(process_data)
restored = deserialize_callable(serialized)
result = restored("hello")  # Returns "HELLO"

# Serialize lambda expression
condition = lambda x: x.get("priority") == "high"
serialized_lambda = serialize_callable_with_fallback(condition)
# Returns: {"_type": "lambda_expression", "expression": "x.get('priority') == 'high'"}
```

Callable fields in Serializable objects are automatically serialized:

```python
@register_serializable
class Processor(Serializable):
    def __init__(self):
        super().__init__()
        self.handler = None  # Will store a function
        self.add_serializable_fields(["handler"])

processor = Processor()
processor.handler = process_data  # Function is automatically serialized
data = processor.serialize()
```

### 🔒 Strict Mode

Enable strict mode to prevent deserialization of unknown fields:

```python
# Strict mode raises error for unknown fields
try:
    person.deserialize(data, strict=True)
except ValueError as e:
    print(f"Error: {e}")
```

### ✅ Validation

Validate that objects can be properly deserialized:

```python
from serilux import validate_serializable_tree

# Validate before serialization
validate_serializable_tree(person)
```

## 📚 Documentation

**📖 Full documentation available at: [serilux.readthedocs.io](https://serilux.readthedocs.io)**

### Documentation Highlights

- **📘 [User Guide](https://serilux.readthedocs.io/en/latest/user_guide/index.html)**: Comprehensive guide covering all features
- **🔧 [API Reference](https://serilux.readthedocs.io/en/latest/api_reference/index.html)**: Complete API documentation
- **💻 [Examples](https://serilux.readthedocs.io/en/latest/examples/index.html)**: Real-world code examples

### Build Documentation Locally

```bash
pip install -e ".[docs]"
cd docs && make html
```

## 🎓 Examples

Check out the `examples/` directory for practical examples:

- **`basic_usage.py`** - Your first serializable class
- **`advanced_usage.py`** - Nested objects, lists, and dictionaries
- **`callable_serialization.py`** - Serializing functions, methods, and lambda expressions

Run examples:

```bash
python examples/basic_usage.py
```

## 🏗️ Project Structure

```
serilux/
├── serilux/              # Main package
│   ├── __init__.py       # Package initialization
│   └── serializable.py   # Core serialization classes
├── tests/                # Comprehensive test suite
├── examples/             # Usage examples
└── docs/                 # Sphinx documentation
```

## 🧪 Testing

Serilux comes with comprehensive tests:

```bash
# Run all tests
make test-all

# Run with coverage
make test-cov

# Run specific test suite
pytest tests/
```

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Star the project** ⭐ - Show your support
2. **Report bugs** 🐛 - Help us improve
3. **Suggest features** 💡 - Share your ideas
4. **Submit PRs** 🔧 - Contribute code

## 📄 License

Serilux is licensed under the **Apache License 2.0**. See [LICENSE](LICENSE) for details.

## 🔗 Links

- **📦 PyPI**: [pypi.org/project/serilux](https://pypi.org/project/serilux)
- **📚 Documentation**: [serilux.readthedocs.io](https://serilux.readthedocs.io)
- **🐙 GitHub**: [github.com/lzjever/serilux](https://github.com/lzjever/serilux)
- **📧 Issues**: [github.com/lzjever/serilux/issues](https://github.com/lzjever/serilux/issues)

## ⭐ Show Your Support

If Serilux helps you build amazing applications, consider giving it a star on GitHub!

---

**Built with ❤️ by the Serilux Team**

*Making object serialization simple, powerful, and fun.*

