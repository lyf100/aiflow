#!/usr/bin/env python3
"""
MCP 服务器快速测试脚本

测试 Code2Claude MCP 服务器的基本功能
"""

import json
import sys
from pathlib import Path

def test_server_import():
    """测试服务器模块导入"""
    print("🔍 测试1: 导入 MCP 服务器模块...")
    try:
        # 尝试导入 mcp 模块
        import mcp
        print("✅ MCP SDK 已安装")

        # 尝试导入服务器
        sys.path.insert(0, str(Path(__file__).parent))
        from mcp_server import mcp as server
        print(f"✅ MCP 服务器已加载")
        print(f"   服务器名称: {server.name}")

        # 获取工具列表
        tools = server._tool_manager.list_tools()
        print(f"   已注册工具: {len(tools)} 个")
        for tool in tools:
            print(f"     - {tool['name']}: {tool.get('description', 'No description')[:50]}...")

        return True
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        print("   请运行: pip install mcp[cli]>=1.4.0")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def test_core_modules():
    """测试核心模块导入"""
    print("\n🔍 测试2: 核心模块导入...")
    try:
        from core.analyzer import CodeAnalyzer
        from core.mapper import ProjectMapper
        from core.grapher import DependencyGrapher
        from core.tracker import ChangeTracker
        from core.exporter import DataExporter
        from core.cache import get_cached_rglob

        print("✅ 所有核心模块导入成功")
        print("   - CodeAnalyzer")
        print("   - ProjectMapper")
        print("   - DependencyGrapher")
        print("   - ChangeTracker")
        print("   - DataExporter")
        print("   - FileCache")
        return True
    except ImportError as e:
        print(f"❌ 核心模块导入失败: {e}")
        return False


def test_config_file():
    """测试配置文件"""
    print("\n🔍 测试3: MCP 配置文件...")
    config_path = Path(__file__).parent / "mcp_config.json"

    if not config_path.exists():
        print(f"❌ 配置文件不存在: {config_path}")
        return False

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        if "mcpServers" not in config:
            print("❌ 配置文件格式错误: 缺少 mcpServers")
            return False

        if "code2claude" not in config["mcpServers"]:
            print("❌ 配置文件格式错误: 缺少 code2claude 配置")
            return False

        server_config = config["mcpServers"]["code2claude"]
        print("✅ 配置文件格式正确")
        print(f"   命令: {server_config.get('command')}")
        print(f"   参数: {server_config.get('args')}")
        return True
    except json.JSONDecodeError as e:
        print(f"❌ 配置文件 JSON 格式错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 配置文件测试失败: {e}")
        return False


def test_documentation():
    """测试文档完整性"""
    print("\n🔍 测试4: 文档完整性...")
    docs = {
        "README.md": "项目说明文档",
        "MCP_SETUP.md": "MCP 配置指南",
        "requirements.txt": "依赖文件"
    }

    missing_docs = []
    for doc, desc in docs.items():
        doc_path = Path(__file__).parent / doc
        if doc_path.exists():
            size = doc_path.stat().st_size
            print(f"✅ {desc}: {doc} ({size} bytes)")
        else:
            print(f"❌ {desc}缺失: {doc}")
            missing_docs.append(doc)

    return len(missing_docs) == 0


def main():
    """运行所有测试"""
    print("="*60)
    print("Code2Claude MCP 服务器测试")
    print("="*60)

    results = []

    # 运行测试
    results.append(("服务器模块导入", test_server_import()))
    results.append(("核心模块导入", test_core_modules()))
    results.append(("配置文件", test_config_file()))
    results.append(("文档完整性", test_documentation()))

    # 汇总结果
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {name}")

    print("\n" + "="*60)
    print(f"总计: {passed}/{total} 测试通过")
    print("="*60)

    if passed == total:
        print("\n🎉 所有测试通过！MCP 服务器已准备就绪。")
        print("\n下一步:")
        print("1. 按照 MCP_SETUP.md 配置 Claude Desktop")
        print("2. 重启 Claude Desktop")
        print("3. 在 Claude Code 中测试工具调用")
        return 0
    else:
        print("\n⚠️ 部分测试失败，请检查配置。")
        return 1


if __name__ == "__main__":
    sys.exit(main())