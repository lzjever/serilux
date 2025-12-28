Serializable Module
===================

Core Classes
------------

.. autoclass:: serilux.serializable.Serializable
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: serilux.serializable.SerializableRegistry
   :members:
   :undoc-members:

.. autoclass:: serilux.serializable.ObjectRegistry
   :members:
   :undoc-members:
   :special-members: __init__

For detailed information about ObjectRegistry design, principles, and usage patterns,
see the :doc:`../user_guide/object_registry` guide.

Decorators
----------

.. autofunction:: serilux.serializable.register_serializable

Validation Functions
--------------------

.. autofunction:: serilux.serializable.check_serializable_constructability

.. autofunction:: serilux.serializable.validate_serializable_tree

Callable Serialization Functions
--------------------------------

.. autofunction:: serilux.serializable.serialize_callable

.. autofunction:: serilux.serializable.serialize_callable_with_fallback

.. autofunction:: serilux.serializable.deserialize_callable

.. autofunction:: serilux.serializable.deserialize_lambda_expression

.. autofunction:: serilux.serializable.extract_callable_expression
