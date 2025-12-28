Basic Usage
===========

This guide covers the basic usage of Serilux.

Creating Serializable Classes
------------------------------

To create a serializable class, inherit from ``Serializable`` and use the
``@register_serializable`` decorator:

.. code-block:: python

   from serilux import Serializable, register_serializable

   @register_serializable
   class MyClass(Serializable):
       def __init__(self):
           super().__init__()
           self.field1 = ""
           self.field2 = 0
           self.add_serializable_fields(["field1", "field2"])

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

