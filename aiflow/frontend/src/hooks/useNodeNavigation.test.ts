import { describe, it, expect, vi } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useNodeNavigation } from './useNodeNavigation';
import type { CodeNode, CodeEdge } from '../types/protocol';

// Mock console.log to suppress test output
vi.spyOn(console, 'log').mockImplementation(() => {});

// Test data
const mockNodes: CodeNode[] = [
  {
    id: 'system-1',
    name: 'System',
    type: 'system',
    stereotype: 'system',
    file_path: '/test/system.ts',
  },
  {
    id: 'module-1',
    name: 'TestModule',
    type: 'module',
    stereotype: 'module',
    file_path: '/test/module.ts',
  },
  {
    id: 'component-1',
    name: 'TestComponent',
    type: 'class',
    stereotype: 'component',
    file_path: '/test/component.ts',
  },
  {
    id: 'function-1',
    name: 'testFunction',
    type: 'function',
    stereotype: 'function',
    file_path: '/test/function.ts',
    parent_class_id: 'component-1',
  },
  {
    id: 'function-2',
    name: 'helperFunction',
    type: 'function',
    stereotype: 'function',
    file_path: '/test/helper.ts',
    parent_class_id: 'component-1',
  },
];

const mockEdges: CodeEdge[] = [
  {
    id: 'edge-1',
    source: 'system-1',
    target: 'module-1',
    type: 'contains',
  },
  {
    id: 'edge-2',
    source: 'module-1',
    target: 'component-1',
    type: 'contains',
  },
  {
    id: 'edge-3',
    source: 'function-1',
    target: 'function-2',
    type: 'calls',
  },
];

const mockExecutionTraces = [
  {
    id: 'trace-1',
    flowchart: {
      steps: [
        { node_id: 'function-1', timestamp: 1000 },
        { node_id: 'function-2', timestamp: 2000 },
      ],
    },
  },
];

describe('useNodeNavigation', () => {
  const defaultProps = {
    codeStructure: {
      nodes: mockNodes,
      edges: mockEdges,
    },
    executionTraces: mockExecutionTraces,
    onAnimationModalOpen: vi.fn(),
  };

  describe('初始化状态', () => {
    it('should initialize with null selectedNodeId', () => {
      const { result } = renderHook(() => useNodeNavigation(defaultProps));

      expect(result.current.selectedNodeId).toBeNull();
    });

    it('should initialize with empty navigationHistory', () => {
      const { result } = renderHook(() => useNodeNavigation(defaultProps));

      expect(result.current.navigationHistory).toEqual([]);
    });

    it('should initialize with empty filteredNodes', () => {
      const { result } = renderHook(() => useNodeNavigation(defaultProps));

      expect(result.current.filteredNodes).toEqual([]);
    });

    it('should initialize with empty filteredEdges', () => {
      const { result } = renderHook(() => useNodeNavigation(defaultProps));

      expect(result.current.filteredEdges).toEqual([]);
    });
  });

  describe('节点点击处理', () => {
    it('should update selectedNodeId when node is clicked', () => {
      const { result } = renderHook(() => useNodeNavigation(defaultProps));

      act(() => {
        result.current.handleNodeClick('system-1');
      });

      expect(result.current.selectedNodeId).toBe('system-1');
    });

    it('should filter nodes for system stereotype', () => {
      const { result } = renderHook(() => useNodeNavigation(defaultProps));

      act(() => {
        result.current.handleNodeClick('system-1');
      });

      expect(result.current.filteredNodes).toHaveLength(2); // system-1 + module-1
      expect(result.current.filteredNodes.some((n) => n.id === 'system-1')).toBe(true);
      expect(result.current.filteredNodes.some((n) => n.id === 'module-1')).toBe(true);
    });

    it('should filter nodes for module stereotype', () => {
      const { result } = renderHook(() => useNodeNavigation(defaultProps));

      act(() => {
        result.current.handleNodeClick('module-1');
      });

      // module-1 + component-1
      expect(result.current.filteredNodes).toHaveLength(2);
      expect(result.current.filteredNodes.some((n) => n.id === 'module-1')).toBe(true);
      expect(result.current.filteredNodes.some((n) => n.id === 'component-1')).toBe(true);
    });

    it('should filter nodes for component stereotype', () => {
      const { result } = renderHook(() => useNodeNavigation(defaultProps));

      act(() => {
        result.current.handleNodeClick('component-1');
      });

      // component-1 + function-1 + function-2
      expect(result.current.filteredNodes).toHaveLength(3);
      expect(result.current.filteredNodes.some((n) => n.id === 'component-1')).toBe(true);
      expect(result.current.filteredNodes.some((n) => n.id === 'function-1')).toBe(true);
      expect(result.current.filteredNodes.some((n) => n.id === 'function-2')).toBe(true);
    });

    it('should filter nodes for function stereotype', () => {
      const { result } = renderHook(() => useNodeNavigation(defaultProps));

      act(() => {
        result.current.handleNodeClick('function-1');
      });

      // function-1 + function-2 (called method)
      expect(result.current.filteredNodes).toHaveLength(2);
      expect(result.current.filteredNodes.some((n) => n.id === 'function-1')).toBe(true);
      expect(result.current.filteredNodes.some((n) => n.id === 'function-2')).toBe(true);
    });

    it('should filter edges based on filtered nodes', () => {
      const { result } = renderHook(() => useNodeNavigation(defaultProps));

      act(() => {
        result.current.handleNodeClick('function-1');
      });

      expect(result.current.filteredEdges).toHaveLength(1); // edge-3 (function-1 -> function-2)
      expect(result.current.filteredEdges[0]!.id).toBe('edge-3');
    });

    it('should add to navigation history when addToHistory is true', () => {
      const { result } = renderHook(() => useNodeNavigation(defaultProps));

      act(() => {
        result.current.handleNodeClick('system-1');
      });

      act(() => {
        result.current.handleNodeClick('module-1', true);
      });

      expect(result.current.navigationHistory).toEqual(['system-1']);
    });

    it('should not add to navigation history when addToHistory is false', () => {
      const { result } = renderHook(() => useNodeNavigation(defaultProps));

      act(() => {
        result.current.handleNodeClick('system-1');
      });

      act(() => {
        result.current.handleNodeClick('module-1', false);
      });

      expect(result.current.navigationHistory).toEqual([]);
    });
  });

  describe('执行轨迹查找', () => {
    it('should call onAnimationModalOpen when traces are found', () => {
      const onAnimationModalOpen = vi.fn();
      const { result } = renderHook(() =>
        useNodeNavigation({
          ...defaultProps,
          onAnimationModalOpen,
        })
      );

      act(() => {
        result.current.handleNodeClick('function-1');
      });

      expect(onAnimationModalOpen).toHaveBeenCalled();
      expect(onAnimationModalOpen).toHaveBeenCalledWith(
        expect.arrayContaining([
          expect.objectContaining({
            id: 'trace-1',
          }),
        ]),
        'testFunction'
      );
    });

    it('should not call onAnimationModalOpen when no traces found', () => {
      const onAnimationModalOpen = vi.fn();
      const { result } = renderHook(() =>
        useNodeNavigation({
          codeStructure: {
            nodes: mockNodes,
            edges: mockEdges,
          },
          executionTraces: [],
          onAnimationModalOpen,
        })
      );

      act(() => {
        result.current.handleNodeClick('function-1');
      });

      expect(onAnimationModalOpen).not.toHaveBeenCalled();
    });

    it('should filter trace steps by relevant node IDs', () => {
      const onAnimationModalOpen = vi.fn();
      const { result } = renderHook(() =>
        useNodeNavigation({
          ...defaultProps,
          onAnimationModalOpen,
        })
      );

      act(() => {
        result.current.handleNodeClick('function-1');
      });

      const [[traces]] = onAnimationModalOpen.mock.calls;
      // For function stereotype, relevantNodeIds only includes the clicked node itself
      // So we should only get steps that match function-1
      expect(traces[0].flowchart.steps).toHaveLength(1);
      expect(traces[0].flowchart.steps[0].node_id).toBe('function-1');
    });
  });

  describe('导航历史管理', () => {
    it('should navigate back when handleBack is called', () => {
      const { result } = renderHook(() => useNodeNavigation(defaultProps));

      // Navigate to system-1
      act(() => {
        result.current.handleNodeClick('system-1');
      });

      // Navigate to module-1 (adds system-1 to history)
      act(() => {
        result.current.handleNodeClick('module-1', true);
      });

      expect(result.current.selectedNodeId).toBe('module-1');
      expect(result.current.navigationHistory).toEqual(['system-1']);

      // Navigate back
      act(() => {
        result.current.handleBack();
      });

      expect(result.current.selectedNodeId).toBe('system-1');
      expect(result.current.navigationHistory).toEqual([]);
    });

    it('should reset navigation when handleBack is called with empty history', () => {
      const { result } = renderHook(() => useNodeNavigation(defaultProps));

      act(() => {
        result.current.handleNodeClick('system-1');
      });

      expect(result.current.selectedNodeId).toBe('system-1');

      act(() => {
        result.current.handleBack();
      });

      expect(result.current.selectedNodeId).toBeNull();
      expect(result.current.filteredNodes).toEqual([]);
      expect(result.current.filteredEdges).toEqual([]);
    });
  });

  describe('导航重置', () => {
    it('should reset all navigation state', () => {
      const { result } = renderHook(() => useNodeNavigation(defaultProps));

      // Set some state
      act(() => {
        result.current.handleNodeClick('system-1');
      });

      act(() => {
        result.current.handleNodeClick('module-1', true);
      });

      expect(result.current.selectedNodeId).not.toBeNull();
      expect(result.current.navigationHistory).not.toEqual([]);

      // Reset
      act(() => {
        result.current.resetNavigation();
      });

      expect(result.current.selectedNodeId).toBeNull();
      expect(result.current.navigationHistory).toEqual([]);
      expect(result.current.filteredNodes).toEqual([]);
      expect(result.current.filteredEdges).toEqual([]);
    });
  });

  describe('边界情况', () => {
    it('should handle clicking non-existent node', () => {
      const { result } = renderHook(() => useNodeNavigation(defaultProps));

      act(() => {
        result.current.handleNodeClick('non-existent-id');
      });

      expect(result.current.selectedNodeId).toBe('non-existent-id');
      expect(result.current.filteredNodes).toEqual([]);
    });

    it('should handle empty code structure', () => {
      const { result } = renderHook(() =>
        useNodeNavigation({
          codeStructure: {
            nodes: [],
            edges: [],
          },
          executionTraces: [],
        })
      );

      act(() => {
        result.current.handleNodeClick('any-id');
      });

      expect(result.current.filteredNodes).toEqual([]);
      expect(result.current.filteredEdges).toEqual([]);
    });

    it('should handle component with no child functions', () => {
      const noChildNodes: CodeNode[] = [
        {
          id: 'component-empty',
          name: 'EmptyComponent',
          type: 'class',
          stereotype: 'component',
          file_path: '/test/empty.ts',
        },
      ];

      const { result } = renderHook(() =>
        useNodeNavigation({
          codeStructure: {
            nodes: noChildNodes,
            edges: [],
          },
          executionTraces: [],
        })
      );

      act(() => {
        result.current.handleNodeClick('component-empty');
      });

      expect(result.current.filteredNodes).toHaveLength(1);
      expect(result.current.filteredNodes[0]!.id).toBe('component-empty');
    });
  });
});
