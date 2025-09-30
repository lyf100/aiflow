"""
测试缓存模块 (cache.py)
"""
import pytest
import time
from pathlib import Path
from datetime import timedelta

from core.cache import (
    FileCache,
    get_cached_rglob,
    get_cached_hash,
    get_cached_line_count,
    clear_cache,
    get_cache_stats
)


class TestFileCache:
    """测试FileCache类"""

    def test_cache_initialization(self):
        """测试缓存初始化"""
        cache = FileCache(cache_ttl=300)
        assert cache._ttl == timedelta(seconds=300)
        assert len(cache._cache) == 0
        assert len(cache._timestamps) == 0

    def test_set_and_get_cached_files(self, temp_project_dir):
        """测试文件列表缓存的设置和获取"""
        cache = FileCache()
        pattern = "*.py"
        files = [temp_project_dir / "test1.py", temp_project_dir / "test2.py"]

        # 设置缓存
        cache.set_cached_files(pattern, temp_project_dir, files)

        # 获取缓存
        cached_files = cache.get_cached_files(pattern, temp_project_dir)
        assert cached_files == files

    def test_cache_expiration(self, temp_project_dir):
        """测试缓存过期"""
        cache = FileCache(cache_ttl=1)  # 1秒过期
        pattern = "*.py"
        files = [temp_project_dir / "test.py"]

        cache.set_cached_files(pattern, temp_project_dir, files)

        # 立即获取，应该命中
        assert cache.get_cached_files(pattern, temp_project_dir) == files

        # 等待过期
        time.sleep(1.1)

        # 应该返回None (过期)
        assert cache.get_cached_files(pattern, temp_project_dir) is None

    def test_file_hash_cache(self, sample_python_file):
        """测试文件哈希缓存"""
        cache = FileCache()
        test_hash = "abc123"

        # 设置哈希缓存
        cache.set_file_hash(sample_python_file, test_hash)

        # 获取哈希缓存
        cached_hash = cache.get_file_hash(sample_python_file)
        assert cached_hash == test_hash

    def test_file_hash_invalidation(self, sample_python_file):
        """测试文件修改后哈希缓存失效"""
        cache = FileCache()
        test_hash = "abc123"

        cache.set_file_hash(sample_python_file, test_hash)
        assert cache.get_file_hash(sample_python_file) == test_hash

        # 修改文件
        time.sleep(0.1)  # 确保mtime变化
        sample_python_file.write_text("# Modified", encoding='utf-8')

        # 缓存应该失效
        assert cache.get_file_hash(sample_python_file) is None

    def test_file_lines_cache(self, sample_python_file):
        """测试文件行数缓存"""
        cache = FileCache()

        # 设置行数缓存
        cache.set_file_lines(sample_python_file, 10)

        # 获取行数缓存
        cached_lines = cache.get_file_lines(sample_python_file)
        assert cached_lines == 10

    def test_clear_cache(self):
        """测试清空缓存"""
        cache = FileCache()
        cache._cache["test"] = ["data"]
        cache._timestamps["test"] = None
        cache._file_metadata["file"] = {}

        cache.clear()

        assert len(cache._cache) == 0
        assert len(cache._timestamps) == 0
        assert len(cache._file_metadata) == 0

    def test_clear_expired_cache(self, temp_project_dir):
        """测试清除过期缓存"""
        cache = FileCache(cache_ttl=1)

        # 添加缓存
        cache.set_cached_files("*.py", temp_project_dir, [])

        # 等待过期
        time.sleep(1.1)

        # 清除过期缓存
        cache.clear_expired()

        # 应该被清除
        assert len(cache._cache) == 0

    def test_cache_stats(self, temp_project_dir):
        """测试缓存统计信息"""
        cache = FileCache()
        cache.set_cached_files("*.py", temp_project_dir, [])

        stats = cache.get_stats()

        assert stats['file_lists'] == 1
        assert stats['total_entries'] >= 1
        assert 'ttl_seconds' in stats


class TestGlobalCacheFunctions:
    """测试全局缓存函数"""

    def test_get_cached_rglob(self, sample_project_structure):
        """测试缓存版rglob"""
        # 清空缓存
        clear_cache()

        # 第一次调用，应该执行rglob
        files1 = get_cached_rglob(sample_project_structure, "*.py")
        assert len(files1) > 0

        # 第二次调用，应该从缓存获取
        files2 = get_cached_rglob(sample_project_structure, "*.py")
        assert files1 == files2

    def test_get_cached_hash(self, sample_python_file):
        """测试缓存版哈希计算"""
        # 清空缓存
        clear_cache()

        # 第一次调用，应该计算哈希
        hash1 = get_cached_hash(sample_python_file)
        assert hash1 != "unknown"
        assert len(hash1) == 32  # MD5长度

        # 第二次调用，应该从缓存获取
        hash2 = get_cached_hash(sample_python_file)
        assert hash1 == hash2

    def test_get_cached_line_count(self, sample_python_file):
        """测试缓存版行数统计"""
        # 清空缓存
        clear_cache()

        # 第一次调用，应该统计行数
        lines1 = get_cached_line_count(sample_python_file)
        assert lines1 > 0

        # 第二次调用，应该从缓存获取
        lines2 = get_cached_line_count(sample_python_file)
        assert lines1 == lines2

    def test_cache_stats_global(self):
        """测试全局缓存统计"""
        clear_cache()
        stats = get_cache_stats()

        assert 'file_lists' in stats
        assert 'file_metadata' in stats
        assert 'total_entries' in stats