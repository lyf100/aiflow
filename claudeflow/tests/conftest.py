"""
Pytest配置文件和共享fixtures
"""
import pytest
import tempfile
import shutil
from pathlib import Path


@pytest.fixture
def temp_project_dir():
    """创建临时项目目录用于测试"""
    temp_dir = tempfile.mkdtemp(prefix="claudeflow_test_")
    yield Path(temp_dir)
    # 清理
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def sample_python_file(temp_project_dir):
    """创建示例Python文件"""
    sample_file = temp_project_dir / "sample.py"
    sample_file.write_text("""
def hello():
    '''Say hello'''
    return "Hello, World!"

class Calculator:
    def add(self, a, b):
        return a + b

    def multiply(self, a, b):
        return a * b
""", encoding='utf-8')
    return sample_file


@pytest.fixture
def sample_project_structure(temp_project_dir):
    """创建示例项目结构"""
    # 创建目录结构
    (temp_project_dir / "src").mkdir()
    (temp_project_dir / "tests").mkdir()
    (temp_project_dir / "docs").mkdir()

    # 创建Python文件
    (temp_project_dir / "src" / "__init__.py").write_text("", encoding='utf-8')
    (temp_project_dir / "src" / "main.py").write_text("""
def main():
    print("Main function")

if __name__ == "__main__":
    main()
""", encoding='utf-8')

    # 创建配置文件
    (temp_project_dir / "requirements.txt").write_text("""
pyyaml>=6.0
colorama>=0.4.6
""", encoding='utf-8')

    (temp_project_dir / ".claudeflow.yml").write_text("""
project:
  name: "test-project"
  language: "py"

analysis:
  depth: 3
""", encoding='utf-8')

    return temp_project_dir


@pytest.fixture
def mock_git_repo(temp_project_dir, monkeypatch):
    """模拟Git仓库"""
    import subprocess

    def mock_run(*args, **kwargs):
        """模拟subprocess.run"""
        class MockResult:
            returncode = 0
            stdout = "mock git output"
            stderr = ""
        return MockResult()

    monkeypatch.setattr(subprocess, 'run', mock_run)
    return temp_project_dir