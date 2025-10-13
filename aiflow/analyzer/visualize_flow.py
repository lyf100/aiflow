#!/usr/bin/env python3
"""
流程图可视化工具 - 在独立窗口中显示静态流程图
"""

import json
import sys
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import networkx as nx
from pathlib import Path


def load_analysis_data(json_path: str) -> dict:
    """加载分析数据"""
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def create_flowchart(data: dict, focus_type: str = 'system'):
    """
    创建流程图

    Args:
        data: 分析数据
        focus_type: 聚焦类型 - 'system'(系统概览), 'module'(模块), 'component'(类), 'function'(方法)
    """
    nodes = data['code_structure']['nodes']
    edges = data['code_structure']['edges']

    # 根据 focus_type 筛选节点
    if focus_type == 'system':
        # 系统层：显示系统 + 所有模块
        filtered_nodes = [n for n in nodes if n['stereotype'] in ['system', 'module']]
    elif focus_type == 'module':
        # 模块层：显示所有类
        filtered_nodes = [n for n in nodes if n['stereotype'] == 'component']
    elif focus_type == 'component':
        # 类层：显示所有方法
        filtered_nodes = [n for n in nodes if n['stereotype'] == 'function']
    else:
        filtered_nodes = nodes[:50]  # 默认显示前50个

    if not filtered_nodes:
        print(f"❌ 没有找到类型为 {focus_type} 的节点")
        return

    print(f"📊 准备显示 {len(filtered_nodes)} 个节点")

    # 创建有向图
    G = nx.DiGraph()

    # 节点ID映射
    node_map = {n['id']: n for n in filtered_nodes}

    # 添加节点
    for node in filtered_nodes:
        G.add_node(node['id'],
                   name=node['name'],
                   stereotype=node['stereotype'])

    # 添加边（只添加筛选后节点之间的边）
    node_ids = set(node_map.keys())
    for edge in edges:
        if edge['source'] in node_ids and edge['target'] in node_ids:
            G.add_edge(edge['source'], edge['target'],
                      relation=edge.get('type', 'unknown'))

    # 创建图形窗口
    fig, ax = plt.subplots(figsize=(16, 10))
    fig.canvas.manager.set_window_title(f'AIFlow - {data["metadata"]["project_name"]} - {focus_type.upper()}')

    # 使用层次布局
    try:
        pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
    except:
        pos = nx.random_layout(G, seed=42)

    # 节点颜色映射
    color_map = {
        'system': '#667eea',
        'module': '#764ba2',
        'component': '#f093fb',
        'function': '#4facfe'
    }

    # 节点大小映射
    size_map = {
        'system': 3000,
        'module': 2000,
        'component': 1500,
        'function': 1000
    }

    # 绘制节点
    for node_id, node_data in node_map.items():
        if node_id not in pos:
            continue

        x, y = pos[node_id]
        stereotype = node_data['stereotype']
        name = node_data['name']

        # 限制显示长度
        if len(name) > 20:
            display_name = name[:17] + '...'
        else:
            display_name = name

        # 绘制节点框
        bbox = FancyBboxPatch(
            (x - 0.1, y - 0.05),
            0.2, 0.1,
            boxstyle="round,pad=0.01",
            facecolor=color_map.get(stereotype, '#cccccc'),
            edgecolor='#333',
            linewidth=2,
            alpha=0.9
        )
        ax.add_patch(bbox)

        # 添加文字
        ax.text(x, y, display_name,
               horizontalalignment='center',
               verticalalignment='center',
               fontsize=10,
               fontweight='bold',
               color='white',
               bbox=dict(boxstyle='round,pad=0.3',
                        facecolor='none',
                        edgecolor='none'))

    # 绘制边
    for edge in G.edges():
        if edge[0] in pos and edge[1] in pos:
            x1, y1 = pos[edge[0]]
            x2, y2 = pos[edge[1]]

            arrow = FancyArrowPatch(
                (x1, y1), (x2, y2),
                arrowstyle='->,head_width=0.4,head_length=0.8',
                color='#666',
                linewidth=1.5,
                alpha=0.6,
                connectionstyle="arc3,rad=0.1"
            )
            ax.add_patch(arrow)

    # 设置标题和图例
    ax.set_title(
        f'{data["metadata"]["project_name"]} - {focus_type.upper()} 流程图\n'
        f'节点数: {len(filtered_nodes)} | 关系数: {G.number_of_edges()}',
        fontsize=16,
        fontweight='bold',
        pad=20
    )

    # 创建图例
    legend_elements = [
        mpatches.Patch(color=color_map['system'], label='系统 System'),
        mpatches.Patch(color=color_map['module'], label='模块 Module'),
        mpatches.Patch(color=color_map['component'], label='类 Component'),
        mpatches.Patch(color=color_map['function'], label='方法 Function')
    ]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=10)

    # 去除坐标轴
    ax.axis('off')
    ax.set_xlim(-0.2, 1.2)
    ax.set_ylim(-0.2, 1.2)

    # 调整布局
    plt.tight_layout()

    # 显示窗口
    print(f"✅ 流程图窗口已打开")
    plt.show()


def main():
    if len(sys.argv) < 2:
        print("❌ 使用方法: python visualize_flow.py <analysis.json> [focus_type]")
        print("   focus_type: system(默认) | module | component | function")
        sys.exit(1)

    json_path = sys.argv[1]
    focus_type = sys.argv[2] if len(sys.argv) > 2 else 'system'

    if not Path(json_path).exists():
        print(f"❌ 文件不存在: {json_path}")
        sys.exit(1)

    print(f"📂 加载分析数据: {json_path}")
    data = load_analysis_data(json_path)

    print(f"🎨 生成流程图 (聚焦: {focus_type})")
    create_flowchart(data, focus_type)


if __name__ == '__main__':
    main()
