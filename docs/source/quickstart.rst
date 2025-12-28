Quick Start
===========

This guide will help you get started with Serilux in just a few minutes.

Creating Your First Serializable Class
---------------------------------------

Let's create a simple ``Person`` class that can be serialized:

.. code-block:: python

   from serilux import Serializable, register_serializable

   @register_serializable
   class Person(Serializable):
       def __init__(self):
           super().__init__()
           self.name = ""
           self.age = 0
           # Register fields to serialize
           self.add_serializable_fields(["name", "age"])

That's it! Your class is now serializable.

Using Serializable Objects
---------------------------

Create and use objects:

.. code-block:: python

   # Create an object
   person = Person()
   person.name = "Alice"
   person.age = 30

   # Serialize to dictionary
   data = person.serialize()
   print(data)
   # {'_type': 'Person', 'name': 'Alice', 'age': 30}

Deserializing
-------------

Deserialize from a dictionary:

.. code-block:: python

   # Deserialize from dictionary
   new_person = Person()
   new_person.deserialize(data)
   print(new_person.name)  # "Alice"
   print(new_person.age)    # 30

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

   # Create nested objects
   person = Person()
   person.name = "Alice"
   person.address = Address()
   person.address.street = "123 Main St"
   person.address.city = "New York"

   # Serialize - nested objects are automatically handled
   data = person.serialize()

Lists and Dictionaries
----------------------

Serilux also handles lists and dictionaries:

.. code-block:: python

   @register_serializable
   class Team(Serializable):
       def __init__(self):
           super().__init__()
           self.name = ""
           self.members = []  # List of Person objects
           self.add_serializable_fields(["name", "members"])

   team = Team()
   team.name = "Engineering"
   team.members = [person1, person2, person3]

   # Serialize - list items are automatically serialized
   data = team.serialize()

Callable Serialization
-----------------------

Serilux can also serialize callable objects (functions, methods, lambda expressions):

.. code-block:: python

   from serilux import serialize_callable, deserialize_callable

   def process_data(data):
       return data.upper()

   # Serialize a function
   serialized = serialize_callable(process_data)

   # Deserialize it
   restored = deserialize_callable(serialized)
   result = restored("hello")  # Returns "HELLO"

For more details on callable serialization, see the :doc:`user_guide/callable_serialization` guide.

Next Steps
----------

- Read the :doc:`user_guide/index` for more advanced features
- Check out the :doc:`examples/index` for real-world examples
- Browse the :doc:`api_reference/index` for complete API documentation

