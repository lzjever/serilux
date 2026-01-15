"""Custom exceptions for Serilux serialization framework.

This module defines a hierarchy of exceptions for different error scenarios
that can occur during serialization and deserialization.
"""


class SeriluxError(Exception):
    """Base exception for all Serilux errors."""

    pass


class SerializationError(SeriluxError):
    """Exception raised when serialization fails."""

    def __init__(self, message: str, obj_type: str = None, field: str = None):
        """Initialize a SerializationError.

        Args:
            message: Error message
            obj_type: Type of object being serialized (optional)
            field: Field that caused the error (optional)
        """
        self.obj_type = obj_type
        self.field = field
        parts = [message]
        if obj_type:
            parts.append(f"Object type: {obj_type}")
        if field:
            parts.append(f"Field: {field}")
        super().__init__(": ".join(parts))


class DeserializationError(SeriluxError):
    """Exception raised when deserialization fails."""

    def __init__(self, message: str, obj_type: str = None, field: str = None):
        """Initialize a DeserializationError.

        Args:
            message: Error message
            obj_type: Type of object being deserialized (optional)
            field: Field that caused the error (optional)
        """
        self.obj_type = obj_type
        self.field = field
        parts = [message]
        if obj_type:
            parts.append(f"Object type: {obj_type}")
        if field:
            parts.append(f"Field: {field}")
        super().__init__(": ".join(parts))


class ClassNotFoundError(DeserializationError):
    """Exception raised when a class is not found in the registry."""

    def __init__(self, class_name: str):
        """Initialize a ClassNotFoundError.

        Args:
            class_name: Name of the class that was not found
        """
        self.class_name = class_name
        super().__init__(
            f"Class '{class_name}' not found in registry. "
            f"This usually means the class was not registered with @register_serializable."
        )


class ValidationError(SeriluxError):
    """Exception raised when validation fails."""

    def __init__(self, message: str, obj=None):
        """Initialize a ValidationError.

        Args:
            message: Error message
            obj: Object that failed validation (optional)
        """
        self.obj = obj
        if obj is not None:
            message = f"{message} (object type: {type(obj).__name__})"
        super().__init__(message)


class CircularReferenceError(SerializationError):
    """Exception raised when a circular reference is detected."""

    def __init__(self, message: str = "Circular reference detected"):
        """Initialize a CircularReferenceError.

        Args:
            message: Error message
        """
        super().__init__(message)


class DepthLimitError(SerializationError):
    """Exception raised when serialization depth limit is exceeded."""

    def __init__(self, max_depth: int, current_depth: int = None):
        """Initialize a DepthLimitError.

        Args:
            max_depth: Maximum allowed depth
            current_depth: Current depth when error occurred (optional)
        """
        self.max_depth = max_depth
        self.current_depth = current_depth
        message = f"Serialization depth limit ({max_depth}) exceeded"
        if current_depth is not None:
            message += f" (current depth: {current_depth})"
        message += ". This may indicate a circular reference or excessively nested structure."
        super().__init__(message)


class CallableError(SeriluxError):
    """Exception raised when callable serialization/deserialization fails."""

    def __init__(self, message: str, callable_type: str = None):
        """Initialize a CallableError.

        Args:
            message: Error message
            callable_type: Type of callable (function/method/builtin/lambda)
        """
        self.callable_type = callable_type
        if callable_type:
            message = f"{message} (callable type: {callable_type})"
        super().__init__(message)


class InvalidFieldError(SerializationError):
    """Exception raised when an invalid field is encountered."""

    def __init__(self, field_name: str, reason: str = None):
        """Initialize an InvalidFieldError.

        Args:
            field_name: Name of the invalid field
            reason: Reason why the field is invalid (optional)
        """
        self.field_name = field_name
        message = f"Invalid field '{field_name}'"
        if reason:
            message += f": {reason}"
        super().__init__(message, field=field_name)


class UnknownFieldError(DeserializationError):
    """Exception raised when an unknown field is encountered during deserialization."""

    def __init__(self, field_name: str, obj_type: str):
        """Initialize an UnknownFieldError.

        Args:
            field_name: Name of the unknown field
            obj_type: Type of object being deserialized
        """
        self.field_name = field_name
        message = f"Unknown field '{field_name}' in {obj_type}"
        super().__init__(message, obj_type=obj_type, field=field_name)
