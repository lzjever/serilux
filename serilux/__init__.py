"""
Serilux - A powerful serialization framework for Python objects

Provides flexible serialization and deserialization capabilities with
automatic type registration and validation.
"""

from serilux.serializable import (
    Serializable,
    SerializableRegistry,
    register_serializable,
    check_serializable_constructability,
    validate_serializable_tree,
    ObjectRegistry,
    serialize_callable,
    serialize_callable_with_fallback,
    deserialize_callable,
    deserialize_lambda_expression,
    extract_callable_expression,
)

__all__ = [
    "Serializable",
    "SerializableRegistry",
    "register_serializable",
    "check_serializable_constructability",
    "validate_serializable_tree",
    "ObjectRegistry",
    "serialize_callable",
    "serialize_callable_with_fallback",
    "deserialize_callable",
    "deserialize_lambda_expression",
    "extract_callable_expression",
]

__version__ = "0.2.1"
