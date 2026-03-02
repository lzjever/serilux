# Serilux Roadmap

## Phase 1: Efficiency & Modernization (0.5.x)
**Goal**: Reduce boilerplate and improve the developer experience (DX).

- [ ] **Type-Hint Auto-Discovery**: Optional automatic field registration by parsing Python 3.8+ type annotations.
- [ ] **Dataclass Native Support**: A specialized decorator (e.g., `@serializable_dataclass`) to eliminate the need for `add_serializable_fields`.
- [ ] **Constructor Parameter Mapping**: Support for `__init__` parameters during deserialization (mapping dict keys to constructor arguments).
- [ ] **Enhanced AST Sandbox**: Expand the default whitelist for math and logic functions while maintaining strict security.

## Phase 2: Performance & Scalability (0.6.x)
**Goal**: Optimize for large object trees and high-frequency serialization.

- [ ] **Msgpack/CBOR Integration**: Direct binary serialization support to reduce output size and speed up I/O.
- [ ] **Lazy Deserialization**: Support for proxy objects that only deserialize branches of the tree upon access.
- [ ] **Benchmarking Suite**: Establish automated performance regression tests against standard libraries (Pickle, JSON).

## Phase 3: Ecosystem & Extensibility (0.7.x)
**Goal**: Integration with third-party scientific and data libraries.

- [ ] **Plugin System**: Allow users to register custom serializers for non-Serializable types (e.g., `NumPy` arrays, `Pandas` DataFrames).
- [ ] **Schema Migration Tools**: Mechanism to handle field renaming or type changes in serialized data (Versioned Data).
- [ ] **Integration Packages**: Native support for common frameworks (e.g., FastAPI, Celery).

## Phase 4: Full Topology Support (0.8.x)
**Goal**: Complete support for any Python object graph.

- [ ] **True Circular Reference Support**: Native serialization of cyclical graphs (beyond `max_depth` limits).
- [ ] **Async Support**: Native async serialization/deserialization for performance in non-blocking environments.
