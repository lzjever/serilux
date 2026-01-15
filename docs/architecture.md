# Serilux Architecture

本文档描述 Serilux 的核心架构、设计决策和实现细节。

## 目录

- [概述](#概述)
- [核心组件](#核心组件)
- [序列化流程](#序列化流程)
- [反序列化流程](#反序列化流程)
- [类型注册机制](#类型注册机制)
- [Callable 序列化](#callable-序列化)
- [安全考虑](#安全考虑)
- [设计决策](#设计决策)

## 概述

Serilux 是一个零依赖的 Python 对象序列化框架，核心特性包括：

- **自动类型注册**: 使用装饰器自动注册类
- **嵌套对象支持**: 自动处理任意深度的嵌套结构
- **Callable 序列化**: 支持函数、方法和 lambda 表达式
- **两阶段反序列化**: 解决循环引用和前向引用问题

## 核心组件

### 1. Serializable 类

基类，提供序列化/反序列化功能。

```python
class Serializable:
    def __init__(self):
        self.fields_to_serialize = []

    def add_serializable_fields(self, fields: List[str]) -> None
    def serialize(self, max_depth: int = 100, _current_depth: int = 0) -> Dict[str, Any]
    def deserialize(self, data: Dict[str, Any], strict: bool = False, registry: Optional[Any] = None) -> None
```

**设计原则**:
- 必须支持无参数构造（`__init__` 不需要参数）
- 显式声明要序列化的字段
- 自动处理嵌套的 Serializable 对象

### 2. SerializableRegistry

全局类注册表，用于类型查找和实例化。

```python
class SerializableRegistry:
    registry: Dict[str, type] = {}

    @classmethod
    def register_class(cls, class_name: str, class_ref: type)
    @classmethod
    def get_class(cls, class_name: str) -> Optional[type]
```

**特性**:
- 类名冲突检测（防止不同类同名导致的错误）
- 全局单例模式
- 装饰器自动注册

### 3. ObjectRegistry

运行时对象注册表，用于解决循环引用。

```python
class ObjectRegistry:
    def register(self, obj: Any, object_id: Optional[str] = None)
    def find_by_id(self, object_id: str) -> Optional[Any]
    def find_by_class_and_id(self, class_name: str, object_id: str) -> Optional[Any]
```

**用途**:
- 在反序列化期间跟踪对象实例
- 支持方法反序列化（通过 `_id` 查找对象）
- 支持自定义查找函数

## 序列化流程

### 基本序列化

```
user_obj.serialize()
  ↓
创建 dict {"_type": "ClassName", ...}
  ↓
遍历 fields_to_serialize
  ↓
对每个字段值调用 _serialize_value()
  ↓
  - Serializable: 递归调用 serialize()
  - list/dict: 递归处理元素
  - callable: 调用 serialize_callable()
  - 其他: 直接存储
  ↓
返回完整 dict
```

### 嵌套对象序列化

自动处理任意深度的嵌套结构：

```python
{
  "_type": "Person",
  "name": "Alice",
  "address": {              # 嵌套对象
    "_type": "Address",
    "street": "123 Main St",
    "city": "NYC"
  },
  "friends": [               # 嵌套列表
    {
      "_type": "Person",
      "name": "Bob",
      ...
    }
  ]
}
```

### 深度保护

为防止栈溢出攻击，`serialize()` 方法包含深度限制：

```python
def serialize(self, max_depth: int = 100, _current_depth: int = 0):
    if _current_depth >= max_depth:
        raise ValueError("Serialization depth limit exceeded")
    ...
```

**保护对象**:
- 恶意构造的深度嵌套结构
- 意外的循环引用
- DoS 攻击

## 反序列化流程

### 两阶段反序列化

这是 Serilux 的核心设计，解决了循环引用和前向引用问题。

#### Phase 1: 预创建和注册

```
deserialize(data)
  ↓
扫描所有字段（包括嵌套容器）
  ↓
find_and_register_serializables()
  ↓
找到所有 Serializable 对象（识别 "_type" 字段）
  ↓
为每个对象创建空实例: obj = ClassName()
  ↓
注册到 ObjectRegistry: registry.register(obj, object_id)
  ↓
返回预创建的对象结构
```

**目的**:
- 在反序列化之前创建所有对象实例
- 建立对象 ID 到实例的映射
- 确保后续引用可以找到目标对象

#### Phase 2: 反序列化所有字段

```
遍历所有字段
  ↓
对每个值调用 deserialize_item()
  ↓
  - 检查 ObjectRegistry 中是否存在（Phase 1 预创建）
  - 如果存在：使用现有实例
  - 如果不存在：创建新实例并注册
  ↓
递归调用 deserialize()
  ↓
恢复所有字段值
```

**关键**:
- Phase 1 创建的实例在 Phase 2 中被找到并使用
- 避免重复创建对象
- 支持对象间的相互引用

### 示例：相互引用

```python
# 反序列化前
data = {
  "_type": "Person",
  "name": "Alice",
  "friend": {
    "_type": "Person",
    "_id": "bob",
    "name": "Bob",
    "friend": {"_type": "Person", "_id": "alice"}  # 循环引用
  }
}

# Phase 1: 创建两个空实例，注册到 registry
# Phase 2: 填充字段时，friend 字段从 registry 中查找已创建的实例
```

## 类型注册机制

### @register_serializable 装饰器

```python
@register_serializable
class MyClass(Serializable):
    def __init__(self):
        super().__init__()
        self.add_serializable_fields(["field1"])
```

**装饰器功能**:
1. 验证 `__init__` 无必需参数
2. 调用 `SerializableRegistry.register_class()`
3. 检测类名冲突

### 类名冲突检测

```python
# 第一次注册
@register_serializable
class Processor(Serializable):
    pass

# 第二次注册同名类（不同类）
@register_serializable
class Processor(Serializable):  # ❌ ValueError!
    pass
```

**错误消息**:
```
ValueError: Class name conflict: 'Processor' is already registered as
<class '__main__.Processor'>. Cannot register <class '__main__.Processor'>.
```

## Callable 序列化

### 支持的 Callable 类型

1. **函数** (Function)
   ```python
   {
     "_type": "callable",
     "callable_type": "function",
     "module": "mymodule",
     "name": "my_function"
   }
   ```

2. **方法** (Method)
   ```python
   {
     "_type": "callable",
     "callable_type": "method",
     "class_name": "MyClass",
     "method_name": "my_method",
     "object_id": "obj123"
   }
   ```

3. **内置函数** (Builtin)
   ```python
   {
     "_type": "callable",
     "callable_type": "builtin",
     "name": "len"
   }
   ```

4. **Lambda 表达式** (Lambda Expression)
   ```python
   {
     "_type": "lambda_expression",
     "expression": "data.get('priority') == 'high'"
   }
   ```

### 安全的 Lambda 反序列化

Lambda 反序列化包含多层安全保护：

#### 1. AST 验证

```python
tree = ast.parse(expr, mode="eval")

# 只允许安全的 AST 节点
allowed_nodes = (
    ast.Expression, ast.Compare, ast.BoolOp, ast.BinOp, ...
)

# 只允许安全的操作符
operator_types = (
    ast.Eq, ast.NotEq, ast.Lt, ast.Gt, ast.Add, ast.Sub, ...
)

for node in ast.walk(tree):
    if not isinstance(node, allowed_nodes + operator_types):
        raise ValueError("Unsafe operation detected")
```

#### 2. 函数白名单

```python
safe_functions = {
    "len", "sum", "min", "max", "abs", "any", "all",
    "isinstance", "hasattr", "getattr", ...
}

# 检查函数调用
if isinstance(node.func, ast.Name):
    if node.func.id not in safe_functions:
        raise ValueError("Unsafe function call")
```

#### 3. 受限的 Globals

```python
safe_globals = {
    "__builtins__": {
        name: __builtins__.get(name)
        for name in safe_functions
        if name in __builtins__
    }
}
```

**拒绝的危险操作**:
- `exec()`, `eval()`, `compile()`
- `__import__()`, `open()`
- 文件操作、网络操作
- 任意代码执行

## 安全考虑

### 1. 深度限制

**威胁**: 恶意构造的深度嵌套对象导致栈溢出
**防御**: `max_depth=100` 参数

```python
obj.serialize(max_depth=100)
```

### 2. Lambda 注入

**威胁**: 恶意 lambda 表达式执行任意代码
**防御**: AST 验证 + 函数白名单

```python
deserialize_lambda_expression({
    "_type": "lambda_expression",
    "expression": "exec('rm -rf /')"  # ❌ 被 AST 验证拒绝
})
```

### 3. 类型混淆

**威胁**: 类名冲突导致错误的反序列化
**防御**: 类名冲突检测

```python
@register_serializable
class User(Serializable):
    pass

# 在另一个模块中
@register_serializable
class User(Serializable):  # ❌ ValueError!
    pass
```

### 4. Strict 模式

**威胁**: 未知字段覆盖内部属性
**防御**: `strict=True` 参数

```python
obj.deserialize(data, strict=True)  # 拒绝未知字段
```

## 设计决策

### 为什么需要两阶段反序列化？

**问题**: 对象之间可能存在相互引用：

```python
alice.friend = bob
bob.friend = alice  # 循环引用
```

**解决方案**:
1. Phase 1: 创建所有对象实例（不填充字段）
2. Phase 2: 填充字段时从 ObjectRegistry 查找已创建的实例

### 为什么使用 `_type` 字段？

**问题**: 反序列化时需要知道创建哪个类

**解决方案**: 在序列化数据中包含类名

```python
{
  "_type": "Person",  # 类名
  "name": "Alice",
  ...
}
```

### 为什么使用 `_id` 字段？

**问题**: 方法需要绑定到特定对象实例

**解决方案**: 序列化对象 ID，反序列化时通过 ID 查找对象

```python
{
  "_type": "callable",
  "callable_type": "method",
  "method_name": "process",
  "object_id": "obj123"  # 用于查找对象
}
```

### 为什么 Callable 需要特殊处理？

**问题**: Python 函数/方法无法直接序列化为 JSON

**解决方案**:
- 函数: 存储模块名和函数名
- 方法: 存储类名、方法名和对象 ID
- Lambda: 存储源代码表达式（带 AST 验证）

## 性能考虑

### 递归深度

- 默认限制: 100 层
- 可配置: `serialize(max_depth=200)`
- 超过限制抛出 `ValueError`

### 大对象序列化

对于包含大量数据的对象：
- 考虑使用流式序列化（未来功能）
- 考虑数据压缩（未来功能）

### 反序列化缓存

`ObjectRegistry` 在反序列化期间缓存所有对象：
- 内存开销: O(对象数量)
- 查找时间: O(1)

## 扩展性

### 自定义序列化

继承 `Serializable` 并覆盖 `serialize()`/`deserialize()`:

```python
class MySerializable(Serializable):
    def serialize(self):
        data = super().serialize()
        data["custom_field"] = self.custom_serialize()
        return data

    def deserialize(self, data, **kwargs):
        super().deserialize(data, **kwargs)
        self.custom_deserialize(data["custom_field"])
```

### 自定义 Callable 处理

扩展 `serialize_callable()`/`deserialize_callable()`:

```python
def my_serialize_callable(callable_obj):
    # 自定义序列化逻辑
    pass

# 在 Serializable._serialize_value 中使用
if callable(value):
    serialized = my_serialize_callable(value)
```

## 最佳实践

### 1. 始终使用装饰器

```python
@register_serializable  # ✅ 好的做法
class MyClass(Serializable):
    pass
```

### 2. 显式声明字段

```python
def __init__(self):
    super().__init__()
    self.name = ""
    self.age = 0
    self.add_serializable_fields(["name", "age"])  # ✅ 显式
```

### 3. 使用 Strict 模式

```python
obj.deserialize(data, strict=True)  # ✅ 生产环境推荐
```

### 4. 限制嵌套深度

```python
# 对于可能深度嵌套的结构
data = obj.serialize(max_depth=50)  # ✅ 更保守的限制
```

### 5. 验证 Lambda 表达式

```python
# 只接受可信的 lambda 源
expr = extract_from_trusted_source()
deserialize_lambda_expression({"_type": "lambda_expression", "expression": expr})
```

## 未来改进

### 计划中的功能

1. **流式序列化**: 支持大对象的增量序列化
2. **压缩**: 自动压缩序列化输出
3. **版本兼容性**: 支持跨版本反序列化
4. **性能优化**: 减少 Phase 1 的扫描开销
5. **类型注解**: 完整的类型提示支持

### 贡献

欢迎贡献！请参阅 [CONTRIBUTING.md](../CONTRIBUTING.md)。
