# Serilux Project Charter

## 1. Vision & Core Philosophy
**Serilux** aims to make the persistence of complex Python object trees as simple as handling JSON, while uniquely preserving code logic (methods) and object identity.

*   **Zero-Dependency**: No external runtime dependencies, ensuring maximum compatibility and zero version conflicts.
*   **High Fidelity**: Captures the "living" state of objects, including class references, method bindings, and safe lambda closures.
*   **Explicit Integrity**: Favor explicit field registration over implicit introspection to ensure security and predictability.
*   **Security First**: Employs AST static analysis for executable code serialization, providing a safe alternative to `pickle`.

## 2. Architectural Essence
### 2.1 Two-Phase Reconstruction
The cornerstone of Serilux's reliability is its two-phase deserialization:
1.  **Phase 1 (Skeleton Creation)**: Recursively instantiates all objects and populates the `ObjectRegistry`.
2.  **Phase 2 (Data Population)**: Fills fields and resolves method bindings.
*Result*: Perfect preservation of shared references and cross-object method ownership.

### 2.2 Secured Execution
Serilux bridges the gap between static data and dynamic logic through:
*   **Source Reconstruction**: Rebuilding functions from source via `inspect`.
*   **AST Sandboxing**: A strict whitelist-based AST validator that prevents arbitrary code execution during lambda/function evaluation.

## 3. Strategic Positioning
Serilux is not a competitor to data-validation libraries like Pydantic; it is the **modern, secure, and human-readable evolution of Pickle**.

| Feature | Serilux | Pickle | Pydantic |
| :--- | :--- | :--- | :--- |
| **Logic Retention** | Yes (Methods/Lambdas) | Yes | No |
| **Readability** | High (JSON/Dict) | Binary | High |
| **Security** | High (AST Validation) | Low (Unsafe) | High |
| **Identity** | Preserved | Preserved | Lost (Deep Copy) |

## 4. Guiding Mandates
1.  **Transparency**: Serialized output must remain human-readable and editable (standard Python dicts).
2.  **Safety**: Never `eval()` or `exec()` without prior AST validation against a strict safe-list.
3.  **Stability**: Maintain strict backward compatibility for serialized data formats across minor versions.
4.  **Simplicity**: The barrier to making a class serializable should never exceed one decorator and one method call.
