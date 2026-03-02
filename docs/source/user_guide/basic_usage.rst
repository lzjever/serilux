Basic Usage
===========

This guide covers the basic usage of Serilux.

Creating Serializable Classes
------------------------------

To create a serializable class, inherit from ``Serializable`` and use the
``@register_serializable`` decorator.

**Zero-Boilerplate Approach (Recommended)**:

Starting with Serilux 0.5.0, fields with type hints are automatically discovered.
You don't need to manually call ``add_serializable_fields()`` for these fields.

.. code-block:: python

   from serilux import Serializable, register_serializable

   @register_serializable
   class MyClass(Serializable):
       field1: str = ""
       field2: int = 0
       # ✨ field1 and field2 are automatically discovered!

**Manual Approach**:

For fields without type hints or when more control is needed, use ``add_serializable_fields()``:

.. code-block:: python

   @register_serializable
   class MyClass(Serializable):
       def __init__(self):
           super().__init__()
           self.field1 = ""
           self.field2 = 0
           self.add_serializable_fields(["field1", "field2"])

**Dataclass Support**:

Serilux natively supports Python ``dataclasses``:

.. code-block:: python

   import dataclasses
   from serilux import Serializable, register_serializable

   @register_serializable
   @dataclasses.dataclass
   class Point(Serializable):
       x: int = 0
       y: int = 0

**Constructor Parameter Mapping**:

Serilux 0.5.0+ can reconstruct objects using ``__init__`` arguments from the serialized data.
This allows you to use classes with required constructor parameters:

.. code-block:: python

   @register_serializable
   class User(Serializable):
       def __init__(self, uid: int, login: str):
           super().__init__()
           self.uid = uid
           self.login = login
           self.add_serializable_fields(["uid", "login"])

   # Deserialization will map 'uid' and 'login' from data to __init__
   new_user = Serializable.deserialize_item(data)

Class Name Conflict Detection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``@register_serializable`` decorator automatically detects and prevents class name conflicts.
If you try to register a different class with the same name as an already registered class,
a ``ValueError`` will be raised:

.. code-block:: python

   @register_serializable
   class MyClass(Serializable):
       def __init__(self):
           super().__init__()
           self.field1 = ""
           self.add_serializable_fields(["field1"])

   # This will raise ValueError: Class name conflict
   @register_serializable
   class MyClass(Serializable):  # Different class, same name
       def __init__(self):
           super().__init__()
           self.field2 = ""  # Different field
           self.add_serializable_fields(["field2"])

**Why This Matters**:

- Prevents accidental class name collisions that could lead to incorrect deserialization
- Ensures that deserialization always uses the correct class definition
- Helps catch bugs early during development

**Re-registering the Same Class**:

Re-registering the same class object is allowed (idempotent operation):

.. code-block:: python

   @register_serializable
   class MyClass(Serializable):
       def __init__(self):
           super().__init__()
           self.field1 = ""
           self.add_serializable_fields(["field1"])

   # Re-registering the same class is allowed
   from serilux.serializable import SerializableRegistry
   SerializableRegistry.register_class("MyClass", MyClass)  # OK

Registering Fields
------------------

Use ``add_serializable_fields()`` to specify which fields should be serialized:

.. code-block:: python

   obj.add_serializable_fields(["field1", "field2", "field3"])

You can also remove fields:

.. code-block:: python

   obj.remove_serializable_fields(["field2"])

Serialization
-------------

Serialize an object to a dictionary:

.. code-block:: python

   data = obj.serialize()
   # Returns: {'_type': 'MyClass', 'field1': 'value1', 'field2': 42}

Deserialization
---------------

Deserialize from a dictionary:

.. code-block:: python

   new_obj = MyClass()
   new_obj.deserialize(data)

Strict Mode
-----------

Enable strict mode to raise errors for unknown fields:

.. code-block:: python

   obj.deserialize(data, strict=True)

