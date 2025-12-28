Advanced Usage
==============

This guide covers advanced features of Serilux.

Nested Objects
--------------

Serilux automatically handles nested Serializable objects:

.. code-block:: python

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

Lists and Dictionaries
----------------------

Serilux handles lists and dictionaries containing Serializable objects:

.. code-block:: python

   @register_serializable
   class Team(Serializable):
       def __init__(self):
           super().__init__()
           self.name = ""
           self.members = []
           self.add_serializable_fields(["name", "members"])

   team = Team()
   team.name = "Engineering"
   team.members = [person1, person2, person3]

   data = team.serialize()

Callable Serialization
-----------------------

Serilux supports serializing and deserializing callable objects (functions, methods, and lambda expressions).
This is useful for storing callbacks, handlers, or conditional logic.

Automatic Callable Handling
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When you have a callable field in a Serializable object, Serilux automatically serializes it:

.. code-block:: python

   @register_serializable
   class Processor(Serializable):
       def __init__(self):
           super().__init__()
           self.name = ""
           self.handler = None  # Will be a function or method
           self.add_serializable_fields(["name", "handler"])

   def process_data(data):
       return data.upper()

   processor = Processor()
   processor.name = "Uppercase Processor"
   processor.handler = process_data  # Function is automatically serialized

   data = processor.serialize()
   # handler is serialized as: {"_type": "callable", "callable_type": "function", ...}

Serializing Functions
~~~~~~~~~~~~~~~~~~~~~

Module-level functions are automatically serialized:

.. code-block:: python

   from serilux import serialize_callable

   def my_function(x):
       return x * 2

   serialized = serialize_callable(my_function)
   # Returns: {"_type": "callable", "callable_type": "function", "module": "...", "name": "my_function"}

Serializing Methods
~~~~~~~~~~~~~~~~~~~

Methods are serialized with their object reference:

.. code-block:: python

   @register_serializable
   class Handler(Serializable):
       def __init__(self):
           super().__init__()
           self._id = "handler1"
           self.process = self.process_data  # Method reference
           self.add_serializable_fields(["process"])

       def process_data(self, data):
           return data.upper()

   handler = Handler()
   data = handler.serialize()
   # process is serialized with object_id reference

Deserializing Callables
~~~~~~~~~~~~~~~~~~~~~~~

When deserializing, you need to provide an ObjectRegistry for methods:

.. code-block:: python

   from serilux import deserialize_callable, ObjectRegistry

   # For methods, create a registry and register the object
   registry = ObjectRegistry()
   registry.register(handler, object_id="handler1")

   # Deserialize the callable
   callable_data = data["process"]
   restored_method = deserialize_callable(callable_data, registry=registry)

Lambda Expressions
~~~~~~~~~~~~~~~~~~

Lambda functions and function bodies can be serialized as expressions:

.. code-block:: python

   from serilux import serialize_callable_with_fallback

   # Lambda function
   condition = lambda x: x.get('priority') == 'high'
   serialized = serialize_callable_with_fallback(condition)
   # Returns: {"_type": "lambda_expression", "expression": "x.get('priority') == 'high'"}

   # Deserialize
   from serilux import deserialize_lambda_expression
   restored = deserialize_lambda_expression(serialized)

ObjectRegistry
--------------

The ObjectRegistry is used to find objects by ID during deserialization, especially for methods:

.. code-block:: python

   from serilux import ObjectRegistry

   registry = ObjectRegistry()

   # Register objects
   registry.register(obj1, object_id="obj1")
   registry.register(obj2, object_id="obj2")

   # Find by ID
   obj = registry.find_by_id("obj1")

   # Find by class and ID
   obj = registry.find_by_class_and_id("MyClass", "obj1")

   # Register multiple objects
   registry.register_many({"obj1": obj1, "obj2": obj2})

Using the Registry
------------------

You can manually register classes:

.. code-block:: python

   from serilux import SerializableRegistry

   SerializableRegistry.register_class("MyClass", MyClass)

   # Retrieve a class
   cls = SerializableRegistry.get_class("MyClass")

Two-Phase Deserialization
--------------------------

Serilux uses a two-phase deserialization process for containers (dicts/lists) containing Serializable objects:

1. **Phase 1**: Pre-create all Serializable instances and register them in the ObjectRegistry
2. **Phase 2**: Deserialize all instances (so callables can reference them)

This ensures that methods can reference their owner objects even when there are circular references.

.. code-block:: python

   # This happens automatically when you call deserialize()
   obj.deserialize(data, registry=registry)
