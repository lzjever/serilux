# Serilux Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.1] - 2025-12-29

### Added

- **GitHub Actions workflow**: Automated build and release workflow with automatic release notes generation
- **Release scripts**: Scripts for generating release notes from CHANGELOG.md or git commits

### Improved

- **Documentation**: Updated documentation and README
- **Code quality**: Added linting configuration (flake8) for better code quality
- **Nested object support**: Enhanced support for deeply nested objects in serialization

### Documentation

- **Release automation**: Added scripts and documentation for automated releases
- **GitHub integration**: Integrated GitHub Actions for automated package building and publishing

## [0.2.0] - 2025-12-28

### Added

- **Callable Serialization**: Full support for serializing and deserializing callable objects (functions, methods, builtins)
- **Lambda Expression Support**: Serialize lambda functions and function bodies as expressions
- **ObjectRegistry**: Generic registry for looking up objects by ID and class name during deserialization
- **Two-Phase Deserialization**: Enhanced deserialization with pre-creation phase for handling circular references
- **Automatic Callable Handling**: Serializable objects automatically serialize callable fields
- **Expression Extraction**: Extract lambda expressions and function bodies from source code
- **Registry-Based Method Deserialization**: Methods can be deserialized using ObjectRegistry
- **Deeply Nested Container Support**: Full support for arbitrarily deep nesting of containers (dict -> list -> dict -> Serializable, etc.)
- **Automatic Registration for Single Object Fields**: Single object fields (not in containers) are now automatically registered in Phase 2
- **Class Name Conflict Detection**: ``@register_serializable`` now detects and prevents class name conflicts, raising ``ValueError`` when different classes with the same name are registered

### Enhanced

- **Serializable.deserialize**: Now supports `registry` parameter for callable deserialization
- **Serializable.serialize**: Recursively handles nested containers at any depth, automatically serializing Serializable objects
- **Serializable._serialize_value**: Now recursively processes nested dicts and lists
- **Phase 1 Deserialization**: Recursively finds and registers all Serializable objects in nested structures
- **Phase 2 Deserialization**: Automatically registers single object fields immediately after creation
- **deserialize_item**: Checks registry first before creating new objects, ensuring pre-registered objects are reused
- **SerializableRegistry.register_class**: Now detects class name conflicts and raises ``ValueError`` when attempting to register a different class with the same name
- **Error Messages**: Improved error messages for missing classes, deserialization failures, and class name conflicts

### Changed

- **Version**: Bumped to 0.2.0 to reflect major feature additions
- **Module Structure**: Complete serialization framework migrated from Routilux

### Documentation

- Updated API reference for callable serialization
- Added examples for callable and lambda expression serialization

### Testing

- Added comprehensive tests for callable serialization
- Tests for lambda expression serialization
- Tests for ObjectRegistry functionality

## [0.1.0] - 2025-07-01

### Added

- **Initial Release**: First release of Serilux serialization framework
- **Serializable Base Class**: Core `Serializable` class for object serialization
- **Automatic Type Registration**: `@register_serializable` decorator for automatic class registration
- **SerializableRegistry**: Class registry for managing serializable types
- **Nested Object Support**: Automatic serialization/deserialization of nested Serializable objects
- **List and Dictionary Support**: Automatic handling of lists and dictionaries containing Serializable objects
- **Strict Mode**: Optional strict mode for deserialization validation
- **Validation Functions**: `check_serializable_constructability` and `validate_serializable_tree` for pre-serialization validation
- **Field Management**: `add_serializable_fields` and `remove_serializable_fields` methods
- **Comprehensive Documentation**: Full Sphinx documentation with examples
- **Test Suite**: Comprehensive test coverage
- **Examples**: Practical usage examples

### Documentation

- Initial documentation structure
- API reference documentation
- User guide with examples
- Quick start guide

### Testing

- Unit tests for core functionality
- Integration tests for nested objects
- Validation tests
- Registry tests

---

**Note**: This is the initial release extracted from the Routilux project's serializable module.

