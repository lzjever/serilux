Callable Serialization
=======================

Serilux provides comprehensive support for serializing and deserializing callable objects,
including functions, methods, and lambda expressions. This feature is essential for
storing callbacks, handlers, and conditional logic in serializable objects.

Overview
--------

Callable serialization allows you to:

- Serialize module-level functions
- Serialize instance methods with object references
- Serialize lambda expressions as code expressions
- Deserialize callables using ObjectRegistry for method resolution

Automatic Callable Handling
----------------------------

When a Serializable object contains a callable field, Serilux automatically serializes it
during the ``serialize()`` process:

.. code-block:: python

   from serilux import Serializable, register_serializable

   def process_data(data):
       return data.upper()

   @register_serializable
   class Processor(Serializable):
       def __init__(self):
           super().__init__()
           self.name = ""
           self.handler = None
           self.add_serializable_fields(["name", "handler"])

   processor = Processor()
   processor.name = "Uppercase"
   processor.handler = process_data  # Function is automatically serialized

   data = processor.serialize()
   # handler field contains serialized function data

Serializing Functions
---------------------

Module-level functions are serialized with their module and name:

.. code-block:: python

   from serilux import serialize_callable

   def my_function(x):
       return x * 2

   serialized = serialize_callable(my_function)
   # Returns:
   # {
   #     "_type": "callable",
   #     "callable_type": "function",
   #     "module": "__main__",
   #     "name": "my_function"
   # }

Serializing Methods
-------------------

Instance methods are serialized with their object reference:

.. code-block:: python

   @register_serializable
   class Handler(Serializable):
       def __init__(self):
           super().__init__()
           self._id = "handler1"
           self.process = self.process_data
           self.add_serializable_fields(["process"])

       def process_data(self, data):
           return data.upper()

   handler = Handler()
   data = handler.serialize()
   # process field contains:
   # {
   #     "_type": "callable",
   #     "callable_type": "method",
   #     "class_name": "Handler",
   #     "method_name": "process_data",
   #     "object_id": "handler1"
   # }

Deserializing Callables
------------------------

Deserializing callables requires different approaches depending on the type:

Functions
~~~~~~~~~

Functions can be deserialized directly:

.. code-block:: python

   from serilux import deserialize_callable

   callable_data = data["handler"]
   restored_function = deserialize_callable(callable_data)
   result = restored_function("test")  # Works!

Methods
~~~~~~~

Methods require an ObjectRegistry to find the owner object:

.. code-block:: python

   from serilux import deserialize_callable, ObjectRegistry

   # Create registry and register the object
   registry = ObjectRegistry()
   handler = Handler()
   handler._id = "handler1"
   registry.register(handler, object_id="handler1")

   # Deserialize the method
   callable_data = data["process"]
   restored_method = deserialize_callable(callable_data, registry=registry)
   result = restored_method("test")  # Works!

Lambda Expressions
------------------

Lambda functions and function bodies can be serialized as expressions:

.. code-block:: python

   from serilux import serialize_callable_with_fallback, deserialize_lambda_expression

   # Lambda function
   condition = lambda x: x.get('priority') == 'high'
   serialized = serialize_callable_with_fallback(condition)
   # Returns:
   # {
   #     "_type": "lambda_expression",
   #     "expression": "x.get('priority') == 'high'"
   # }

   # Deserialize
   restored = deserialize_lambda_expression(serialized)
   result = restored({"priority": "high"})  # Returns True

Fallback to Expression
----------------------

The ``serialize_callable_with_fallback()`` function tries standard serialization first,
then falls back to expression extraction if needed:

.. code-block:: python

   from serilux import serialize_callable_with_fallback

   # Try standard serialization first
   # If that fails or function is not accessible, extract as expression
   serialized = serialize_callable_with_fallback(my_callable, fallback_to_expression=True)

ObjectRegistry
--------------

The ObjectRegistry is essential for deserializing methods. It maintains a mapping
of object IDs to objects, allowing methods to find their owner objects.

**For a comprehensive understanding of ObjectRegistry, including its design philosophy,
implementation details, and integration with two-phase deserialization, see the
:doc:`object_registry` guide.**

Quick Reference
~~~~~~~~~~~~~~~

.. code-block:: python

   from serilux import ObjectRegistry

   registry = ObjectRegistry()

   # Register objects
   registry.register(obj, object_id="obj1")
   registry.register_many({"obj1": obj1, "obj2": obj2})

   # Find objects
   obj = registry.find_by_id("obj1")
   obj = registry.find_by_class_and_id("Handler", "handler1")

Automatic Registry Creation
----------------------------

When deserializing a Serializable object, if no registry is provided, Serilux
automatically creates one:

.. code-block:: python

   # Registry is created automatically
   obj.deserialize(data)

   # Or provide your own registry
   registry = ObjectRegistry()
   obj.deserialize(data, registry=registry)

Two-Phase Deserialization
--------------------------

Serilux uses a two-phase deserialization process for containers (dicts/lists)
containing Serializable objects:

1. **Phase 1**: Pre-create all Serializable instances and register them in the ObjectRegistry
2. **Phase 2**: Deserialize all instances (so callables can reference them)

This ensures that methods can reference their owner objects even when there are
circular references or complex object graphs.

Best Practices
--------------

1. **Use module-level functions** when possible - they're easier to serialize and deserialize
2. **Provide ObjectRegistry** when deserializing objects with methods
3. **Use lambda expressions** for simple conditions that can be extracted from source
4. **Validate callables** before serialization to catch issues early
5. **Handle serialization failures** gracefully - some callables cannot be serialized

Limitations
-----------

- Dynamically created callables (e.g., in interactive shells) cannot be serialized
- Callables defined at runtime without source code cannot be serialized
- Complex lambda expressions may not extract correctly
- Methods must have their owner objects registered in ObjectRegistry for deserialization

