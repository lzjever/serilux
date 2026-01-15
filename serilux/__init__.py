"""
Serilux - A powerful serialization framework for Python objects

Provides flexible serialization and deserialization capabilities with
automatic type registration and validation.
"""

from serilux.exceptions import (
    CallableError,
    CircularReferenceError,
    ClassNotFoundError,
    DepthLimitError,
    DeserializationError,
    InvalidFieldError,
    SeriluxError,
    SerializationError,
    UnknownFieldError,
    ValidationError,
)
from serilux.serializable import (
    ObjectRegistry,
    Serializable,
    SerializableRegistry,
    check_serializable_constructability,
    deserialize_callable,
    deserialize_lambda_expression,
    extract_callable_expression,
    register_serializable,
    serialize_callable,
    serialize_callable_with_fallback,
    validate_serializable_tree,
)

__all__ = [
    # Core classes
    "Serializable",
    "SerializableRegistry",
    "ObjectRegistry",
    # Decorators and validation
    "register_serializable",
    "check_serializable_constructability",
    "validate_serializable_tree",
    # Callable serialization
    "serialize_callable",
    "serialize_callable_with_fallback",
    "deserialize_callable",
    "deserialize_lambda_expression",
    "extract_callable_expression",
    # Exceptions
    "SeriluxError",
    "SerializationError",
    "DeserializationError",
    "ClassNotFoundError",
    "ValidationError",
    "CircularReferenceError",
    "DepthLimitError",
    "CallableError",
    "InvalidFieldError",
    "UnknownFieldError",
]

__version__ = "0.3.1"
