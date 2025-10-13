import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { AnalysisResult } from '../types/protocol';

interface AnalysisState {
  data: AnalysisResult | null;
  loading: boolean;
  error: string | null;

  setData: (data: AnalysisResult) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  clear: () => void;
}

export const useAnalysisStore = create<AnalysisState>()(
  persist(
    (set) => ({
      data: null,
      loading: false,
      error: null,

      setData: (data) => set({ data, loading: false, error: null }),
      setLoading: (loading) => set({ loading }),
      setError: (error) => set({ error, loading: false }),
      clear: () => set({ data: null, loading: false, error: null }),
    }),
    {
      name: 'aiflow-analysis-storage',
    }
  )
);
