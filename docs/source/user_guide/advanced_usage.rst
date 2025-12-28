Advanced Usage
==============

This guide covers advanced features of Serilux.

Class Name Conflict Detection
------------------------------

Serilux automatically detects and prevents class name conflicts when using ``@register_serializable``.
This ensures that deserialization always uses the correct class definition and helps catch bugs early.

**How It Works**:

When you register a class with ``@register_serializable``, Serilux checks if a class with the same name
is already registered. If a different class (not the same object) with the same name exists, a
``ValueError`` is raised with detailed information about the conflict.

**Example**:

.. code-block:: python

   from serilux import Serializable, register_serializable

   @register_serializable
   class Processor(Serializable):
       def __init__(self):
           super().__init__()
           self.name = ""
           self.add_serializable_fields(["name"])

   # This will raise ValueError
   @register_serializable
   class Processor(Serializable):  # Different class, same name
       def __init__(self):
           super().__init__()
           self.value = 0  # Different implementation
           self.add_serializable_fields(["value"])

**Error Message**:

The error message provides clear information about the conflict:

::

   ValueError: Class name conflict: 'Processor' is already registered as 
   <class 'mymodule.Processor'>. Cannot register <class 'mymodule.Processor'>. 
   Please use a different class name or unregister the existing class first.

**Best Practices**:

1. **Use Unique Class Names**: Always use unique, descriptive class names across your project
2. **Avoid Generic Names**: Avoid generic names like ``TestClass``, ``MyClass``, etc. in production code
3. **Use Module-Specific Prefixes**: If you have classes that might conflict, use module-specific prefixes
4. **Re-registration is Safe**: Re-registering the same class object is allowed and safe (idempotent)

**Re-registering the Same Class**:

If you need to re-register the same class (e.g., in tests or during module reload), this is allowed:

.. code-block:: python

   @register_serializable
   class MyClass(Serializable):
       def __init__(self):
           super().__init__()
           self.field = ""
           self.add_serializable_fields(["field"])

   # Re-registering the same class is allowed
   from serilux.serializable import SerializableRegistry
   SerializableRegistry.register_class("MyClass", MyClass)  # OK, no error

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

Deeply Nested Container Structures
-----------------------------------

Serilux supports arbitrarily deep nesting of containers (dicts and lists) containing Serializable objects.
The serialization and deserialization process recursively handles nested structures at any depth.

**Example: Dict -> List -> Dict -> Serializable**

.. code-block:: python

   @register_serializable
   class Person(Serializable):
       def __init__(self):
           super().__init__()
           self._id = None
           self.name = ""
           self.age = 0
           self.add_serializable_fields(["_id", "name", "age"])

   @register_serializable
   class Team(Serializable):
       def __init__(self):
           super().__init__()
           self._id = None
           self.name = ""
           # Structure: departments[dept_name][role] = [Person, Person, ...]
           self.departments = {}
           self.add_serializable_fields(["_id", "name", "departments"])

   team = Team()
   team._id = "team1"
   team.name = "Engineering"

   person1 = Person()
   person1._id = "p1"
   person1.name = "Alice"
   person1.age = 30

   # Nested structure: dict -> dict -> list -> Serializable
   team.departments = {
       "backend": {
           "senior": [person1],
           "junior": [person2]
       },
       "frontend": {
           "senior": [person1]
       }
   }

   # Serialize - automatically handles nested structure
   data = team.serialize()

   # Deserialize - all nested objects are automatically registered
   new_team = Team()
   registry = ObjectRegistry()
   registry.register(new_team, object_id="team1")
   new_team.deserialize(data, registry=registry)

   # All nested Person objects are accessible
   assert new_team.departments["backend"]["senior"][0].name == "Alice"

**Example: List -> Dict -> List -> Serializable**

.. code-block:: python

   @register_serializable
   class Project(Serializable):
       def __init__(self):
           super().__init__()
           self._id = None
           self.name = ""
           # Structure: projects = [{project_name: {phase: [Person, ...]}}]
           self.projects = []
           self.add_serializable_fields(["_id", "name", "projects"])

   project_manager = Project()
   project_manager.projects = [
       {
           "project_a": {
               "phase1": [person1],
               "phase2": [person2]
           }
       },
       {
           "project_b": {
               "phase1": [person1, person2]
           }
       }
   ]

   # Serialize and deserialize work seamlessly
   data = project_manager.serialize()
   new_manager = Project()
   registry = ObjectRegistry()
   registry.register(new_manager, object_id="manager1")
   new_manager.deserialize(data, registry=registry)

**Key Features**:

- **Recursive Serialization**: Automatically serializes Serializable objects at any nesting depth
- **Automatic Registration**: All nested Serializable objects are automatically registered in Phase 1
- **Method Support**: Methods in nested objects work correctly after deserialization
- **No Depth Limit**: Supports arbitrary nesting levels (4+ levels tested)

**How It Works**:

1. **Serialization**: The ``_serialize_value()`` method recursively processes nested dicts and lists,
   automatically serializing any Serializable objects it encounters.

2. **Deserialization Phase 1**: A recursive function ``find_and_register_serializables()`` traverses
   the nested structure, finds all Serializable objects, creates instances, and registers them
   in the ObjectRegistry before deserialization begins.

3. **Deserialization Phase 2**: The ``deserialize_item()`` method checks the registry first before
   creating new objects, ensuring that pre-registered objects are reused and methods can find
   their owner objects.

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
