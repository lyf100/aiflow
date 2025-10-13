/**
 * Visualization Store - 可视化控制状态管理
 *
 * 管理可视化界面的控制状态，包括视图模式、动画播放、布局配置等。
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

// 视图模式
export type ViewMode = 'structure' | 'sequence' | 'flowchart' | 'step-by-step';

// 动画状态
export type AnimationState = 'idle' | 'playing' | 'paused';

// 布局类型
export type LayoutType = 'dagre' | 'cose' | 'breadthfirst' | 'circle' | 'grid';

interface VisualizationState {
  // 视图控制
  currentView: ViewMode;
  setCurrentView: (view: ViewMode) => void;

  // 动画控制
  animationState: AnimationState;
  currentStep: number;
  totalSteps: number;
  animationSpeed: number; // 1x, 2x, 0.5x
  playAnimation: () => void;
  pauseAnimation: () => void;
  resetAnimation: () => void;
  setAnimationStep: (step: number) => void;
  setAnimationSpeed: (speed: number) => void;

  // 布局控制
  layoutType: LayoutType;
  setLayoutType: (layout: LayoutType) => void;

  // 缩放和平移
  zoom: number;
  pan: { x: number; y: number };
  setZoom: (zoom: number) => void;
  setPan: (pan: { x: number; y: number }) => void;
  resetViewport: () => void;

  // 过滤器
  showSystemNodes: boolean;
  showModuleNodes: boolean;
  showClassNodes: boolean;
  showFunctionNodes: boolean;
  toggleNodeType: (type: 'system' | 'module' | 'class' | 'function') => void;

  // 搜索
  searchQuery: string;
  searchResults: string[];
  setSearchQuery: (query: string) => void;
  setSearchResults: (results: string[]) => void;

  // 侧边栏
  showSidebar: boolean;
  sidebarTab: 'nodes' | 'buttons' | 'traces' | 'details';
  toggleSidebar: () => void;
  setSidebarTab: (tab: 'nodes' | 'buttons' | 'traces' | 'details') => void;

  // 主题
  theme: 'light' | 'dark';
  toggleTheme: () => void;
}

export const useVisualizationStore = create<VisualizationState>()(
  devtools(
    (set, get) => ({
      // 初始状态 - 视图
      currentView: 'structure',
      setCurrentView: (view: ViewMode) => {
        set({ currentView: view });
      },

      // 初始状态 - 动画
      animationState: 'idle',
      currentStep: 0,
      totalSteps: 0,
      animationSpeed: 1,

      playAnimation: () => {
        set({ animationState: 'playing' });
      },

      pauseAnimation: () => {
        set({ animationState: 'paused' });
      },

      resetAnimation: () => {
        set({
          animationState: 'idle',
          currentStep: 0,
        });
      },

      setAnimationStep: (step: number) => {
        const { totalSteps } = get();
        const clampedStep = Math.max(0, Math.min(step, totalSteps));
        set({ currentStep: clampedStep });
      },

      setAnimationSpeed: (speed: number) => {
        set({ animationSpeed: speed });
      },

      // 初始状态 - 布局
      layoutType: 'dagre',
      setLayoutType: (layout: LayoutType) => {
        set({ layoutType: layout });
      },

      // 初始状态 - 视口
      zoom: 1,
      pan: { x: 0, y: 0 },

      setZoom: (zoom: number) => {
        const clampedZoom = Math.max(0.1, Math.min(zoom, 5));
        set({ zoom: clampedZoom });
      },

      setPan: (pan: { x: number; y: number }) => {
        set({ pan });
      },

      resetViewport: () => {
        set({
          zoom: 1,
          pan: { x: 0, y: 0 },
        });
      },

      // 初始状态 - 过滤器
      showSystemNodes: true,
      showModuleNodes: true,
      showClassNodes: true,
      showFunctionNodes: true,

      toggleNodeType: (type: 'system' | 'module' | 'class' | 'function') => {
        const stateKey = `show${type.charAt(0).toUpperCase() + type.slice(1)}Nodes` as keyof VisualizationState;
        set({ [stateKey]: !get()[stateKey] });
      },

      // 初始状态 - 搜索
      searchQuery: '',
      searchResults: [],

      setSearchQuery: (query: string) => {
        set({ searchQuery: query });
      },

      setSearchResults: (results: string[]) => {
        set({ searchResults: results });
      },

      // 初始状态 - 侧边栏
      showSidebar: true,
      sidebarTab: 'nodes',

      toggleSidebar: () => {
        set({ showSidebar: !get().showSidebar });
      },

      setSidebarTab: (tab: 'nodes' | 'buttons' | 'traces' | 'details') => {
        set({ sidebarTab: tab });
      },

      // 初始状态 - 主题
      theme: 'light',

      toggleTheme: () => {
        const newTheme = get().theme === 'light' ? 'dark' : 'light';
        set({ theme: newTheme });
        // 应用到 DOM
        document.documentElement.setAttribute('data-theme', newTheme);
      },
    }),
    { name: 'VisualizationStore' }
  )
);
