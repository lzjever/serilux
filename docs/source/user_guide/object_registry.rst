ObjectRegistry: Design and Implementation
===========================================

The ``ObjectRegistry`` is a fundamental component of Serilux's callable serialization system.
Understanding its design, principles, and implementation is crucial for effectively using
callable serialization features, especially when working with method serialization.

**Table of Contents**:

- :ref:`object-registry-design-philosophy`
- :ref:`object-registry-architecture`
- :ref:`object-registry-implementation`
- :ref:`object-registry-integration`
- :ref:`object-registry-usage`
- :ref:`object-registry-why-essential`
- :ref:`object-registry-examples`
- :ref:`object-registry-best-practices`

.. _object-registry-design-philosophy:

Design Philosophy
-----------------

Why ObjectRegistry?
~~~~~~~~~~~~~~~~~~~

When serializing a method (bound method), we need to store:

1. **Method name**: The name of the method (e.g., ``"process_data"``)
2. **Object reference**: A way to identify the object that owns the method
3. **Class name**: The class the method belongs to (for type safety)

However, during deserialization, we face a critical challenge:

**Problem**: Methods are bound to specific object instances. When we deserialize, we need to
find the correct object instance to bind the method to. But objects are deserialized in a
specific order, and methods might reference objects that haven't been deserialized yet.

**Solution**: ObjectRegistry provides a centralized registry that:
- Tracks all objects by their unique IDs during deserialization
- Allows methods to look up their owner objects by ID
- Supports multiple lookup strategies for flexibility
- Works seamlessly with two-phase deserialization

Key Design Principles
~~~~~~~~~~~~~~~~~~~~~

1. **Generic and Extensible**: Not tied to specific object types (like "routines" or "handlers").
   Works with any Serializable object.

2. **Multiple Lookup Strategies**: Supports ID-based, class-based, and custom lookup functions.

3. **Automatic Registration**: Objects are automatically registered during deserialization's
   Phase 1, before methods need to reference them.

4. **Type Safety**: Can filter by class name to ensure type correctness.

5. **Backward Compatible**: Supports legacy context-based lookup for migration.

.. _object-registry-architecture:

Architecture Overview
---------------------

The ObjectRegistry maintains three internal data structures:

.. code-block:: python

   class ObjectRegistry:
       def __init__(self):
           # Map object IDs to objects (primary lookup)
           self._objects_by_id: Dict[str, Any] = {}
           
           # Map class names to lists of objects (secondary lookup)
           self._objects_by_class: Dict[str, list] = {}
           
           # Map class names to custom lookup functions (extensibility)
           self._custom_lookups: Dict[str, Callable] = {}

**Data Structure Relationships**:

::

   _objects_by_id: {
       "obj1" -> ObjectInstance1,
       "obj2" -> ObjectInstance2,
       ...
   }
   
   _objects_by_class: {
       "Handler" -> [ObjectInstance1, ObjectInstance3, ...],
       "Processor" -> [ObjectInstance2, ...],
       ...
   }
   
   _custom_lookups: {
       "MyClass" -> custom_lookup_function,
       ...
   }

.. _object-registry-implementation:

Implementation Details
----------------------

Registration Process
~~~~~~~~~~~~~~~~~~~~

When an object is registered, it's added to both ID and class-based indexes:

.. code-block:: python

   def register(self, obj: Any, object_id: Optional[str] = None) -> None:
       # 1. Get or use provided object_id
       if object_id is None:
           object_id = getattr(obj, "_id", None)
       
       # 2. Register by ID (primary index)
       if object_id:
           self._objects_by_id[object_id] = obj
       
       # 3. Register by class name (secondary index)
       class_name = obj.__class__.__name__
       if class_name not in self._objects_by_class:
           self._objects_by_class[class_name] = []
       if obj not in self._objects_by_class[class_name]:
           self._objects_by_class[class_name].append(obj)

**Why Both Indexes?**

- **ID Index**: Fast O(1) lookup when you know the exact ID
- **Class Index**: Enables class-based filtering and custom lookup strategies
- **Redundancy**: Provides flexibility and fallback options

Lookup Strategies
~~~~~~~~~~~~~~~~~

The registry supports three lookup strategies, tried in order:

1. **Direct ID Lookup** (Fastest)
   - O(1) time complexity
   - Used when you know the exact object ID

2. **Class-Based Lookup** (Fallback)
   - Iterates through objects of a specific class
   - Used when ID lookup fails or for type safety

3. **Custom Lookup** (Extensibility)
   - Allows custom lookup logic
   - Used for special cases or external object stores

.. code-block:: python

   def find_by_class_and_id(self, class_name: str, object_id: str) -> Optional[Any]:
       # Strategy 1: Direct ID lookup (fastest)
       obj = self._objects_by_id.get(object_id)
       if obj and obj.__class__.__name__ == class_name:
           return obj
       
       # Strategy 2: Class-based lookup (fallback)
       if class_name in self._objects_by_class:
           for obj in self._objects_by_class[class_name]:
               if hasattr(obj, "_id") and obj._id == object_id:
                   return obj
       
       # Strategy 3: Custom lookup (extensibility)
       if class_name in self._custom_lookups:
           return self._custom_lookups[class_name](class_name, object_id)
       
       return None

.. _object-registry-integration:

Integration with Two-Phase Deserialization
-------------------------------------------

ObjectRegistry is tightly integrated with Serilux's two-phase deserialization process:

Phase 1: Pre-Creation and Registration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

During Phase 1, all Serializable objects in containers (dicts/lists) are pre-created
and immediately registered in the ObjectRegistry:

.. code-block:: python

   # Phase 1: Pre-create and register
   for key, value in data.items():
       if isinstance(value, dict):
           for k, v in value.items():
               if isinstance(v, dict) and "_type" in v:
                   # Create instance
                   attr_class = SerializableRegistry.get_class(v["_type"])
                   obj = attr_class()
                   
                   # Register in registry (CRITICAL: before deserialization)
                   object_id = v.get("_id") or k
                   registry.register(obj, object_id=object_id)
                   
                   pre_created[key][k] = obj

**Why Register Before Deserialization?**

Methods serialized in the data might reference objects by ID. If we register objects
during Phase 1, methods can find their owner objects during Phase 2, even if the
owner object hasn't finished deserializing yet.

Phase 2: Deserialization with Method Resolution
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

During Phase 2, when deserializing callable fields, methods use the registry to find
their owner objects:

.. code-block:: python

   # Phase 2: Deserialize (methods can now find owners)
   if value.get("_type") == "callable":
       if callable_type == "method":
           method_name = callable_data.get("method_name")
           object_id = callable_data.get("object_id")
           class_name = callable_data.get("class_name")
           
           # Find owner object from registry
           obj = registry.find_by_class_and_id(class_name, object_id)
           
           # Get the method from the owner object
           if obj and hasattr(obj, method_name):
               return getattr(obj, method_name)

**Timeline Example**:

::

   Time    Action
   ----    ------
   T1      Phase 1: Create Handler() instance
   T2      Phase 1: Register Handler in registry with ID "handler1"
   T3      Phase 2: Deserialize method field
   T4      Phase 2: Method lookup: find_by_class_and_id("Handler", "handler1")
   T5      Phase 2: Method found! Return handler.process_data
   T6      Phase 2: Continue deserializing Handler's other fields

This ensures methods can always find their owner objects, regardless of deserialization order.

.. _object-registry-usage:

Usage Patterns
--------------

Basic Usage
~~~~~~~~~~~

Register objects and look them up:

.. code-block:: python

   from serilux import ObjectRegistry

   registry = ObjectRegistry()

   # Register objects
   handler1 = Handler()
   handler1._id = "handler1"
   registry.register(handler1)

   handler2 = Handler()
   handler2._id = "handler2"
   registry.register(handler2, object_id="handler2")

   # Lookup by ID
   found = registry.find_by_id("handler1")
   assert found is handler1

   # Lookup by class and ID
   found = registry.find_by_class_and_id("Handler", "handler1")
   assert found is handler1

Batch Registration
~~~~~~~~~~~~~~~~~~

Register multiple objects at once:

.. code-block:: python

   handlers = {
       "handler1": handler1,
       "handler2": handler2,
       "handler3": handler3,
   }
   registry.register_many(handlers)

Custom Lookup Functions
~~~~~~~~~~~~~~~~~~~~~~~

For special cases, register custom lookup functions:

.. code-block:: python

   def find_in_database(class_name: str, object_id: str):
       # Custom logic to find object (e.g., from database, cache, etc.)
       return database.get_object(class_name, object_id)

   registry.register_custom_lookup("DatabaseObject", find_in_database)

   # Now find_by_class_and_id will use custom lookup for DatabaseObject
   obj = registry.find_by_class_and_id("DatabaseObject", "obj123")

Integration with Deserialization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The registry is automatically used during deserialization:

.. code-block:: python

   from serilux import Serializable, register_serializable, ObjectRegistry

   @register_serializable
   class Handler(Serializable):
       def __init__(self):
           super().__init__()
           self._id = None
           self.process = self.process_data
           self.add_serializable_fields(["_id", "process"])

       def process_data(self, data):
           return data.upper()

   # Serialize
   handler = Handler()
   handler._id = "handler1"
   data = handler.serialize()

   # Deserialize with registry
   new_handler = Handler()
   registry = ObjectRegistry()
   registry.register(new_handler, object_id="handler1")
   new_handler.deserialize(data, registry=registry)

   # Method is restored and works!
   assert new_handler.process("test") == "TEST"

Automatic Registry Creation
~~~~~~~~~~~~~~~~~~~~~~~~~~~

If no registry is provided, Serilux creates one automatically:

.. code-block:: python

   # Registry created automatically
   obj.deserialize(data)

   # Or provide your own
   registry = ObjectRegistry()
   obj.deserialize(data, registry=registry)

.. _object-registry-why-essential:

Why ObjectRegistry is Essential for Callable Serialization
------------------------------------------------------------

The Challenge of Method Serialization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Methods in Python are bound to specific object instances:

.. code-block:: python

   handler = Handler()
   method = handler.process_data  # Bound method
   # method.__self__ is handler
   # method.__func__ is Handler.process_data

When we serialize a method, we store:
- The method name: ``"process_data"``
- The object's ID: ``"handler1"``
- The class name: ``"Handler"``

But during deserialization:
- We need to find the Handler instance with ID "handler1"
- Then get its ``process_data`` method
- The Handler might not be fully deserialized yet

The Solution: ObjectRegistry
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

ObjectRegistry solves this by:

1. **Pre-registering objects** during Phase 1 of deserialization
2. **Providing fast lookup** by ID during Phase 2
3. **Supporting type-safe lookup** by class name and ID
4. **Enabling extensibility** through custom lookup functions

Without ObjectRegistry, method deserialization would be impossible because:
- We can't serialize the actual object reference (it's not JSON-serializable)
- We can't rely on deserialization order (methods might reference objects created later)
- We need a way to resolve object IDs to actual instances

.. _object-registry-examples:

Real-World Example
------------------

Let's trace through a complete example:

**Step 1: Serialization**

.. code-block:: python

   @register_serializable
   class Processor(Serializable):
       def __init__(self):
           super().__init__()
           self._id = "processor1"
           self.handler = self.process  # Method reference
           self.add_serializable_fields(["_id", "handler"])

       def process(self, data):
           return data.upper()

   processor = Processor()
   data = processor.serialize()
   # data["handler"] = {
   #     "_type": "callable",
   #     "callable_type": "method",
   #     "class_name": "Processor",
   #     "method_name": "process",
   #     "object_id": "processor1"
   # }

**Step 2: Deserialization Phase 1**

.. code-block:: python

   new_processor = Processor()
   registry = ObjectRegistry()
   
   # Phase 1: Pre-create and register
   # (In real code, this happens inside deserialize())
   registry.register(new_processor, object_id="processor1")
   # Now registry._objects_by_id["processor1"] = new_processor

**Step 3: Deserialization Phase 2**

.. code-block:: python

   # Phase 2: Deserialize handler field
   handler_data = data["handler"]
   # handler_data = {
   #     "_type": "callable",
   #     "callable_type": "method",
   #     "class_name": "Processor",
   #     "method_name": "process",
   #     "object_id": "processor1"
   # }
   
   # Lookup owner object
   obj = registry.find_by_class_and_id("Processor", "processor1")
   # Returns: new_processor
   
   # Get method from owner
   method = getattr(obj, "process")
   # Returns: bound method new_processor.process
   
   # Set handler field
   new_processor.handler = method

**Step 4: Verification**

.. code-block:: python

   # Method works!
   assert new_processor.handler("test") == "TEST"

.. _object-registry-best-practices:

Best Practices
--------------

1. **Always Register Before Deserialization**
   - Register objects in the registry before calling ``deserialize()``
   - Or let Serilux handle it automatically during Phase 1

2. **Use Consistent Object IDs**
   - Use the same ID format throughout your application
   - Consider using UUIDs for globally unique IDs

3. **Provide Registry for Methods**
   - Always provide a registry when deserializing objects with methods
   - The registry must contain all objects that methods might reference

4. **Handle Missing Objects Gracefully**
   - Check if lookup returns None
   - Provide meaningful error messages

5. **Use Custom Lookups for Special Cases**
   - For objects stored in databases or external systems
   - For objects with complex lookup requirements

Common Pitfalls
---------------

1. **Forgetting to Register Objects**
   - Methods won't be able to find their owner objects
   - Solution: Always register objects before deserialization

2. **Using Wrong Object IDs**
   - ID mismatch between serialization and deserialization
   - Solution: Use consistent ID generation/assignment

3. **Registry Not Shared Across Objects**
   - Each object creates its own registry
   - Solution: Create one registry and pass it to all deserialize() calls

4. **Registering After Deserialization**
   - Methods can't find owners during deserialization
   - Solution: Register during Phase 1, before Phase 2

Performance Considerations
--------------------------

- **ID Lookup**: O(1) - Very fast, use when possible
- **Class Lookup**: O(n) where n is number of objects of that class
- **Custom Lookup**: Depends on implementation
- **Memory**: Minimal overhead - just stores references, not copies

The registry is designed for deserialization-time lookups, not for high-frequency runtime
queries. For production use, consider caching or optimizing custom lookup functions.

Advanced Topics
----------------

Circular References
~~~~~~~~~~~~~~~~~~~

ObjectRegistry enables handling circular references in object graphs:

.. code-block:: python

   @register_serializable
   class Node(Serializable):
       def __init__(self):
           super().__init__()
           self._id = None
           self.next = None
           self.handler = self.process
           self.add_serializable_fields(["_id", "next", "handler"])

       def process(self, data):
           return data.upper()

   # Create circular reference
   node1 = Node()
   node1._id = "node1"
   node2 = Node()
   node2._id = "node2"
   node1.next = node2
   node2.next = node1  # Circular!

   # Serialize
   data = node1.serialize()

   # Deserialize - registry handles circular references
   new_node1 = Node()
   registry = ObjectRegistry()
   registry.register(new_node1, object_id="node1")
   new_node1.deserialize(data, registry=registry)

   # Both nodes and their methods work correctly
   assert new_node1.handler("test") == "TEST"
   assert new_node1.next.next is new_node1  # Circular reference restored

Distributed Deserialization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When deserializing across process boundaries, ObjectRegistry allows you to
reconstruct object relationships:

.. code-block:: python

   # Process A: Serialize
   handler = Handler()
   handler._id = "handler1"
   data = handler.serialize()

   # Send data over network (JSON, message queue, etc.)
   # ...

   # Process B: Deserialize
   new_handler = Handler()
   registry = ObjectRegistry()
   registry.register(new_handler, object_id="handler1")
   new_handler.deserialize(data, registry=registry)

   # Method works in new process!
   assert new_handler.process("test") == "TEST"

Custom Lookup for External Systems
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For objects stored in external systems (databases, caches, etc.):

.. code-block:: python

   class DatabaseLookup:
       def __init__(self, db_connection):
           self.db = db_connection

       def lookup(self, class_name: str, object_id: str):
           # Query database for object
           return self.db.get_object(class_name, object_id)

   db_lookup = DatabaseLookup(my_db)
   registry = ObjectRegistry()
   registry.register_custom_lookup("DatabaseObject", db_lookup.lookup)

   # Now methods can reference objects in database
   obj = registry.find_by_class_and_id("DatabaseObject", "obj123")

Performance Optimization
~~~~~~~~~~~~~~~~~~~~~~~~~

For large object graphs, consider:

1. **Lazy Registration**: Only register objects that methods might reference
2. **Custom Lookup Caching**: Cache results in custom lookup functions
3. **Registry Pooling**: Reuse registries across deserialization operations

.. code-block:: python

   class CachedLookup:
       def __init__(self):
           self._cache = {}

       def lookup(self, class_name: str, object_id: str):
           cache_key = (class_name, object_id)
           if cache_key in self._cache:
               return self._cache[cache_key]

           # Expensive lookup operation
           obj = expensive_lookup(class_name, object_id)
           self._cache[cache_key] = obj
           return obj

   registry = ObjectRegistry()
   cached = CachedLookup()
   registry.register_custom_lookup("ExpensiveObject", cached.lookup)

Troubleshooting
---------------

Common Issues and Solutions
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Issue**: Method deserialization returns None

**Solution**: Ensure the owner object is registered in the registry before deserialization:

.. code-block:: python

   # ❌ Wrong: Register after deserialization
   obj.deserialize(data)
   registry.register(obj, object_id="obj1")  # Too late!

   # ✅ Correct: Register before deserialization
   registry.register(obj, object_id="obj1")
   obj.deserialize(data, registry=registry)

**Issue**: Wrong object found by ID

**Solution**: Check for ID conflicts and use class-based lookup:

.. code-block:: python

   # Use class-based lookup for type safety
   obj = registry.find_by_class_and_id("Handler", "obj1")
   # This ensures obj is actually a Handler instance

**Issue**: Custom lookup not being called

**Solution**: Ensure custom lookup is registered before deserialization:

.. code-block:: python

   # Register custom lookup first
   registry.register_custom_lookup("MyClass", my_lookup)
   
   # Then deserialize
   obj.deserialize(data, registry=registry)

Summary
-------

ObjectRegistry is the foundation of callable serialization in Serilux. Key takeaways:

1. **Purpose**: Enables method deserialization by mapping object IDs to instances
2. **Design**: Generic, extensible, supports multiple lookup strategies
3. **Integration**: Tightly integrated with two-phase deserialization
4. **Usage**: Register objects before deserialization, lookup during deserialization
5. **Essential**: Without ObjectRegistry, method serialization would be impossible

For more information, see:
- :doc:`callable_serialization` - How to use callable serialization
- :doc:`advanced_usage` - Advanced serialization patterns
- :doc:`../api_reference/serializable` - Complete API reference

