# 测试指南

## 🧪 测试框架

ClaudeFlow 使用 **pytest** 作为测试框架，配置了完善的单元测试和代码覆盖率检查。

---

## 📦 安装测试依赖

### 方式1: 安装开发依赖
```bash
pip install -r requirements-dev.txt
```

### 方式2: 单独安装pytest
```bash
pip install pytest pytest-cov pytest-mock
```

---

## 🚀 运行测试

### 运行所有测试
```bash
pytest
```

### 运行指定模块测试
```bash
# 测试缓存模块
pytest tests/test_cache.py

# 测试分析器模块
pytest tests/test_analyzer.py

# 测试映射器模块
pytest tests/test_mapper.py
```

### 运行单个测试
```bash
pytest tests/test_cache.py::TestFileCache::test_cache_initialization
```

### 详细输出模式
```bash
pytest -v
```

### 显示打印输出
```bash
pytest -s
```

---

## 📊 代码覆盖率

### 生成覆盖率报告
```bash
# 终端显示
pytest --cov=core --cov=commands --cov-report=term-missing

# 生成HTML报告
pytest --cov=core --cov=commands --cov-report=html
```

### 查看HTML报告
```bash
# Windows
start htmlcov/index.html

# macOS
open htmlcov/index.html

# Linux
xdg-open htmlcov/index.html
```

### 覆盖率目标
- **核心模块 (core/)**: 目标 **80%+**
- **命令模块 (commands/)**: 目标 **75%+**
- **总体覆盖率**: 目标 **75%+**

---

## 🏷️ 测试标记

### 按标记运行测试
```bash
# 只运行单元测试
pytest -m unit

# 跳过慢速测试
pytest -m "not slow"

# 只运行集成测试
pytest -m integration
```

### 可用标记
- `unit`: 单元测试
- `integration`: 集成测试
- `slow`: 慢速测试

---

## 📁 测试结构

```
tests/
├── __init__.py              # 测试包初始化
├── conftest.py              # Pytest配置和共享fixtures
├── test_cache.py            # 缓存模块测试
├── test_analyzer.py         # 分析器模块测试
├── test_mapper.py           # 映射器模块测试
├── test_tracker.py          # 追踪器模块测试 (待添加)
├── test_cli.py              # CLI测试 (待添加)
└── integration/             # 集成测试 (待添加)
```

---

## 🔧 共享Fixtures

### `temp_project_dir`
创建临时项目目录用于测试
```python
def test_example(temp_project_dir):
    # temp_project_dir 是一个临时目录Path对象
    test_file = temp_project_dir / "test.py"
    test_file.write_text("print('test')")
```

### `sample_python_file`
创建示例Python文件
```python
def test_example(sample_python_file):
    # sample_python_file 是一个包含示例代码的文件
    assert sample_python_file.exists()
```

### `sample_project_structure`
创建完整的示例项目结构
```python
def test_example(sample_project_structure):
    # 包含src/, tests/, docs/目录和配置文件
    assert (sample_project_structure / "src").exists()
```

### `mock_git_repo`
模拟Git仓库
```python
def test_example(mock_git_repo):
    # Git命令被模拟，不会执行真实操作
    pass
```

---

## ✍️ 编写测试

### 测试类命名规范
```python
class TestModuleName:
    """测试ModuleName类"""

    def test_feature_name(self):
        """测试特定功能"""
        # 测试代码
        pass
```

### 测试方法命名规范
- `test_<功能>`: 测试正常功能
- `test_<功能>_edge_cases`: 测试边界情况
- `test_<功能>_error_handling`: 测试错误处理

### 示例测试
```python
def test_cache_set_and_get(temp_project_dir):
    """测试缓存的设置和获取"""
    cache = FileCache()
    pattern = "*.py"
    files = [temp_project_dir / "test.py"]

    # 设置缓存
    cache.set_cached_files(pattern, temp_project_dir, files)

    # 获取缓存
    cached_files = cache.get_cached_files(pattern, temp_project_dir)

    # 断言
    assert cached_files == files
```

---

## 🐛 调试测试

### 进入调试模式
```bash
pytest --pdb
```

### 在失败时进入调试器
```bash
pytest --pdb -x
```

### 显示局部变量
```bash
pytest -l
```

### 详细的traceback
```bash
pytest --tb=long
```

---

## ⚡ 快速测试

### 只运行失败的测试
```bash
pytest --lf
```

### 先运行失败的测试
```bash
pytest --ff
```

### 并行运行测试
```bash
# 安装pytest-xdist
pip install pytest-xdist

# 并行运行
pytest -n auto
```

---

## 📈 持续集成

### GitHub Actions配置示例
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: '3.8'
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    - name: Run tests
      run: pytest --cov=core --cov=commands --cov-report=xml
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

---

## 💡 测试最佳实践

### 1. 测试隔离
- 每个测试独立运行
- 使用fixtures创建测试数据
- 测试完成后清理临时文件

### 2. 测试覆盖
- 测试正常路径
- 测试边界情况
- 测试错误处理
- 测试异常情况

### 3. 测试可读性
- 清晰的测试名称
- 充分的注释
- AAA模式: Arrange, Act, Assert

### 4. 测试性能
- 使用缓存避免重复计算
- 模拟外部依赖
- 标记慢速测试

---

## 🎯 测试覆盖率当前状态

### 已测试模块
- ✅ `core/cache.py`: 完整测试覆盖
- ✅ `core/analyzer.py`: 主要功能测试
- ✅ `core/mapper.py`: 核心功能测试

### 待测试模块
- ⏳ `core/tracker.py`: 需要添加测试
- ⏳ `core/grapher.py`: 需要添加测试
- ⏳ `core/exporter.py`: 需要添加测试
- ⏳ `commands/*`: 命令处理器测试
- ⏳ `cli.py`: CLI集成测试

---

## 🔗 相关资源

- [Pytest官方文档](https://docs.pytest.org/)
- [Pytest-cov文档](https://pytest-cov.readthedocs.io/)
- [Python测试最佳实践](https://docs.python-guide.org/writing/tests/)

---

## 📞 需要帮助?

如果在测试过程中遇到问题:
1. 查看测试输出的详细错误信息
2. 使用 `pytest -v -s` 查看详细输出
3. 检查 `conftest.py` 中的fixtures配置
4. 参考现有测试用例的写法