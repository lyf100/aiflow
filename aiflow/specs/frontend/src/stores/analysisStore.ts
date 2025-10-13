/**
 * Analysis Store - 分析数据状态管理
 *
 * 管理从 AIFlow 后端生成的分析结果数据。
 * 这是整个前端应用的核心数据源。
 */

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import type { AnalysisResult } from '../types/protocol';

interface AnalysisState {
  // 分析数据
  analysisData: AnalysisResult | null;
  isLoading: boolean;
  error: string | null;

  // 当前选中的元素
  selectedNodeId: string | null;
  selectedButtonId: string | null;
  selectedTraceId: string | null;

  // 高亮状态
  highlightedNodeIds: Set<string>;
  highlightedEdgeIds: Set<string>;

  // 操作方法
  setAnalysisData: (data: AnalysisResult) => void;
  clearAnalysisData: () => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;

  // 选择操作
  selectNode: (nodeId: string | null) => void;
  selectButton: (buttonId: string | null) => void;
  selectTrace: (traceId: string | null) => void;

  // 高亮操作
  highlightNodes: (nodeIds: string[]) => void;
  highlightEdges: (edgeIds: string[]) => void;
  clearHighlights: () => void;

  // 查询方法
  getNodeById: (nodeId: string) => any | undefined;
  getButtonById: (buttonId: string) => any | undefined;
  getTraceById: (traceId: string) => any | undefined;
  getChildNodes: (parentId: string) => any[];
}

export const useAnalysisStore = create<AnalysisState>()(
  devtools(
    persist(
      (set, get) => ({
        // 初始状态
        analysisData: null,
        isLoading: false,
        error: null,
        selectedNodeId: null,
        selectedButtonId: null,
        selectedTraceId: null,
        highlightedNodeIds: new Set(),
        highlightedEdgeIds: new Set(),

        // 数据操作
        setAnalysisData: (data: AnalysisResult) => {
          set({
            analysisData: data,
            error: null,
            isLoading: false,
          });
        },

        clearAnalysisData: () => {
          set({
            analysisData: null,
            selectedNodeId: null,
            selectedButtonId: null,
            selectedTraceId: null,
            highlightedNodeIds: new Set(),
            highlightedEdgeIds: new Set(),
            error: null,
          });
        },

        setLoading: (loading: boolean) => {
          set({ isLoading: loading });
        },

        setError: (error: string | null) => {
          set({ error, isLoading: false });
        },

        // 选择操作
        selectNode: (nodeId: string | null) => {
          set({ selectedNodeId: nodeId });
        },

        selectButton: (buttonId: string | null) => {
          set({ selectedButtonId: buttonId });

          // 自动选择关联的节点
          if (buttonId) {
            const button = get().getButtonById(buttonId);
            if (button?.node_id) {
              set({ selectedNodeId: button.node_id });
            }
          }
        },

        selectTrace: (traceId: string | null) => {
          set({ selectedTraceId: traceId });
        },

        // 高亮操作
        highlightNodes: (nodeIds: string[]) => {
          set({ highlightedNodeIds: new Set(nodeIds) });
        },

        highlightEdges: (edgeIds: string[]) => {
          set({ highlightedEdgeIds: new Set(edgeIds) });
        },

        clearHighlights: () => {
          set({
            highlightedNodeIds: new Set(),
            highlightedEdgeIds: new Set(),
          });
        },

        // 查询方法
        getNodeById: (nodeId: string) => {
          const data = get().analysisData;
          if (!data?.code_structure?.nodes) return undefined;
          return data.code_structure.nodes.find((node) => node.id === nodeId);
        },

        getButtonById: (buttonId: string) => {
          const data = get().analysisData;
          if (!data?.behavior_metadata?.launch_buttons) return undefined;
          return data.behavior_metadata.launch_buttons.find(
            (button) => button.id === buttonId
          );
        },

        getTraceById: (traceId: string) => {
          const data = get().analysisData;
          if (!data?.execution_trace?.traceable_units) return undefined;
          return data.execution_trace.traceable_units.find(
            (trace) => trace.id === traceId
          );
        },

        getChildNodes: (parentId: string) => {
          const data = get().analysisData;
          if (!data?.code_structure?.nodes) return [];
          return data.code_structure.nodes.filter(
            (node) => node.parent === parentId
          );
        },
      }),
      {
        name: 'aiflow-analysis-storage',
        partialize: (state) => ({
          // 只持久化分析数据，不持久化 UI 状态
          analysisData: state.analysisData,
        }),
      }
    ),
    { name: 'AnalysisStore' }
  )
);
