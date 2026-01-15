# Contributing to Serilux

感谢您对 Serilux 的贡献！我们欢迎各种形式的贡献，包括但不限于错误报告、功能请求、文档改进和代码提交。

## 开发环境设置

### 快速开始

```bash
# 克隆仓库
git clone https://github.com/lzjever/serilux.git
cd serilux

# 推荐使用 uv 进行依赖管理
pip install uv
uv sync --group docs --all-extras

# 或使用 pip
pip install -e ".[dev]"
```

### 开发依赖

项目使用以下工具进行开发：

- **uv** - 快速的 Python 包管理器（推荐）
- **pytest** - 测试框架
- **ruff** - Linting 和代码格式化
- **mypy** - 静态类型检查
- **sphinx** - 文档生成

## 开发流程

### 分支策略

```
main          (生产分支，只接受合并)
  ├── develop (开发分支，日常开发)
  └── feature/* (功能分支，从 develop 分出)
```

**规则**:
- `main` 分支受保护，需要 PR + 1 review
- `develop` 分支定期合并到 `main`（发版时）
- `feature/*` 分支完成后合并到 `develop` 并删除

### 提交规范

遵循 [Conventional Commits](https://www.conventionalcommits.org/)：

```
<type>(<scope>): <subject>

<body>

<footer>
```

**类型 (type)**:
- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档变更
- `style`: 代码格式（不影响功能）
- `refactor`: 重构
- `perf`: 性能优化
- `test`: 测试相关
- `chore`: 构建/工具相关
- `security`: 安全相关

**示例**:
```bash
feat(callable): add support for partial functions

Closes #123
```

### 标准开发流程

```bash
make dev-install  # 安装包和所有依赖
make test         # 运行测试
make lint         # 代码质量检查
make format       # 格式化代码
make check        # 运行所有检查
```

### CI/CD 或代码审查

```bash
make setup-venv   # 只安装依赖（不安装包）
make lint         # 可运行 linting
make format-check # 检查格式
```

**注意**: 某些测试需要安装包。

## 代码质量标准

### 质量门禁

所有提交必须通过以下检查：

1. **Linting**: `ruff check`
2. **格式化**: `ruff format`
3. **测试**: `pytest tests/ --cov=serilux --cov-fail-under=80`
4. **类型检查**: `mypy serilux/` (公共 API)

### Python 版本

- 项目支持 Python 3.8-3.14
- 新代码应与 Python 3.8+ 兼容
- 使用类型注解提升代码质量

### 代码风格

- 遵循 PEP 8
- 使用 ruff 进行格式化（line-length = 100）
- 在 `serilux/` 模块中使用类型注解
- 为公共 API 添加文档字符串

### 测试要求

- 测试覆盖率不低于 80%
- 为新功能添加单元测试
- 为边界情况添加测试
- 使用有意义的测试名称

### 安全要求

- 避免使用 `eval()` 或 `exec()`（除非有严格的 AST 验证）
- 验证用户输入
- 使用最小权限原则
- 更新依赖时检查安全漏洞

## 运行测试

### 运行所有测试
```bash
make test
# 或
pytest tests/
```

### 运行测试并生成覆盖率报告
```bash
make test-cov
# 或
pytest tests/ --cov=serilux --cov-report=html
```

### 运行特定测试文件
```bash
pytest tests/test_serializable.py
```

### 运行特定测试
```bash
pytest tests/test_serializable.py::TestSerializable::test_basic_serialization
```

## 提交 Pull Request

### PR 检查清单

提交 PR 前请确保：

- [ ] 代码通过所有测试 (`pytest tests/`)
- [ ] 测试覆盖率 ≥ 80% (`pytest --cov=serilux`)
- [ ] 代码通过 linting (`ruff check`)
- [ ] 代码格式化正确 (`ruff format --check`)
- [ ] 公共 API 有类型注解
- [ ] 新功能有文档和测试
- [ ] 提交信息遵循规范

### PR 模板

```markdown
## 描述
简要描述此 PR 的目的和内容。

## 类型
- [ ] Bug 修复
- [ ] 新功能
- [ ] 破坏性变更
- [ ] 文档更新

## 测试
描述如何测试此变更：

## 检查清单
- [ ] 测试通过
- [ ] 覆盖率 ≥ 80%
- [ ] 文档已更新
- [ ] 无 breaking changes（或已在描述中说明）
```

## 项目结构

```
serilux/
├── serilux/              # 源码包
│   ├── __init__.py       # 公共 API 导出
│   └── serializable.py   # 核心实现
├── tests/                # 测试套件
├── examples/             # 使用示例
├── docs/                 # Sphinx 文档
└── pyproject.toml        # 项目配置
```

## 报告问题

### Bug 报告

在提交 bug 前，请：

1. 搜索现有 issues 避免重复
2. 使用最新的 Serilux 版本
3. 提供最小可复现示例
4. 包含环境信息（Python 版本、操作系统等）

**Bug 报告模板**:

```markdown
**描述**
清晰简洁地描述 bug。

**复现步骤**
1. 步骤 1
2. 步骤 3
...

**期望行为**
描述您期望发生什么。

**实际行为**
描述实际发生了什么。

**环境**
- Python 版本:
- 操作系统:
- Serilux 版本:

**附加信息**
其他相关信息（日志、截图等）
```

### 功能请求

在提交功能请求前：

1. 搜索现有 proposals
2. 描述使用场景
3. 说明为什么当前功能无法满足需求
4. 如果可能，提供实现思路

## 文档

### 构建文档

```bash
make docs
# 或
cd docs && make html
```

生成的文档在 `docs/_build/html/` 目录。

### 文档结构

- `README.md` - 项目概述和快速开始
- `CONTRIBUTING.md` - 本文件
- `docs/` - 详细的 API 文档和指南

## 发布流程

发布由维护者负责：

1. 更新版本号
2. 更新 CHANGELOG.md
3. 创建 git tag
4. 构建并发布到 PyPI
5. 更新 GitHub releases

## 社区

- 遵循行为准则
- 尊重所有贡献者
- 建设性讨论
- 乐于助人

## 获取帮助

- 查看 [文档](https://serilux.readthedocs.io)
- 搜索 [GitHub Issues](https://github.com/lzjever/serilux/issues)
- 提问时提供足够的信息和上下文

## 许可

贡献的代码将采用 [Apache License 2.0](LICENSE) 许可。
