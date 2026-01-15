# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Serilux is a lightweight, zero-dependency serialization framework for Python objects. It enables automatic serialization/deserialization of complex object hierarchies with type registration and validation.

## Common Development Commands

### Setup

```bash
# Recommended: Install package with all dev dependencies (for active development)
make dev-install

# Alternative: Install dependencies only (for CI/CD or code review)
make setup-venv
# Later, if needed: make install
```

The project uses `uv` for dependency management. All Makefile commands automatically use `uv` if available, otherwise fall back to `pip`.

### Testing

```bash
# Run all tests
make test

# Run with coverage report
make test-cov

# Run specific test file
pytest tests/test_serializable.py

# Run specific test
pytest tests/test_serializable.py::test_serialize_basic
```

### Code Quality

```bash
# Run linting (ruff)
make lint

# Format code
make format

# Run all checks (lint + format check + tests)
make check
```

### Building

```bash
# Build source and wheel distributions
make build

# Check package before uploading
make check-package
```

## Architecture

### Core Components

The framework is built around a few key components in `serilux/serializable.py`:

1. **Serializable** - Base class for serializable objects. Subclasses register fields via `add_serializable_fields()`.
2. **SerializableRegistry** - Global registry mapping class names to class references for deserialization.
3. **@register_serializable** - Decorator that registers classes and validates they have parameterless `__init__`.
4. **ObjectRegistry** - Runtime registry for tracking object instances during deserialization (critical for method resolution).

### Serialization Flow

When `serialize()` is called on a Serializable object:
1. Creates dict with `_type` key (class name)
2. Iterates through registered fields in `fields_to_serialize`
3. For each value:
   - Serializable objects: recursively call `serialize()`
   - Lists/dicts: recursively process items
   - Callables: serialize via `serialize_callable()` (functions, methods, builtins)
   - Primitives: store as-is

### Deserialization Flow (Two-Phase)

When `deserialize(data)` is called:

**Phase 1: Pre-create and Register**
- Recursively scan containers (dict/list) for Serializable objects
- Create empty instances via `class()` (requires parameterless `__init__`)
- Register instances in `ObjectRegistry` using `_id` field if present

**Phase 2: Deserialize**
- Process all fields, using `deserialize_item()` for each value
- For Serializable objects: check `ObjectRegistry` first (return pre-created instance), then call `deserialize()`
- For callables: use `deserialize_callable()` with registry to resolve methods

The two-phase approach ensures that:
1. Forward references are resolved (objects can reference objects not yet deserialized)
2. Methods can find their owner objects via `ObjectRegistry`

### Callable Serialization

Callables are serialized with different strategies:

1. **Functions**: Stored as `{"module": "...", "name": "..."}` - imported at deserialization
2. **Methods**: Stored as `{"class_name": "...", "method_name": "...", "object_id": "..."}` - resolved via ObjectRegistry
3. **Builtins**: Stored as `{"name": "..."}` - looked up in `__builtins__`
4. **Lambda expressions**: Stored as `{"expression": "..."}` - evaluated with safe globals (fallback via `serialize_callable_with_fallback()`)

Method validation: When serializing methods, the `owner` parameter ensures only methods belonging to the serialized object can be serialized (cross-process safety).

### Type Registration and Conflicts

The `@register_serializable` decorator:
1. Validates `__init__` has no required parameters (except `self`)
2. Registers class in `SerializableRegistry` by class name
3. Detects class name conflicts - raises `ValueError` if different class with same name is registered

This prevents silent deserialization bugs where the wrong class would be instantiated.

### Validation Utilities

- **check_serializable_constructability()** - Validates a single object can be instantiated without arguments
- **validate_serializable_tree()** - Recursively validates entire object tree, catching issues before serialization

## CI/CD

The project uses GitHub Actions (`.github/workflows/ci.yml`):
- Runs tests on Python 3.14 using `uv`
- Uploads coverage to Codecov
- Runs linting (ruff check) and formatting checks (black - replaced with ruff format locally)
- Builds package and docs

Note: CI uses `black --check` for formatting, but local development uses `ruff format`. Both are compatible.

## Project Structure

```
serilux/
├── serilux/
│   ├── __init__.py          # Public API exports
│   └── serializable.py      # Core implementation (~1064 lines)
├── tests/                   # Comprehensive test suite
├── examples/                # Usage examples
├── docs/                    # Sphinx documentation
└── pyproject.toml           # Project config (ruff, pytest, mypy)
```

## Key Design Constraints

1. **Zero dependencies** - Pure Python, no external runtime dependencies
2. **Parameterless __init__** - All Serializable classes must support instantiation with no arguments
3. **Explicit field registration** - Fields must be added via `add_serializable_fields()`, not introspected
4. **Type safety** - Classes are registered by name, conflicts are detected at registration time
5. **Method ownership validation** - Only methods of the serialized object can be serialized (prevents cross-process bugs)
