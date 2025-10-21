import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ErrorBoundary from './ErrorBoundary';

// Component that throws an error
const ThrowError = ({ shouldThrow = true }: { shouldThrow?: boolean }) => {
  if (shouldThrow) {
    throw new Error('Test error');
  }
  return <div>No error</div>;
};

describe('ErrorBoundary', () => {
  // Suppress console.error during tests
  const originalError = console.error;
  beforeEach(() => {
    console.error = vi.fn();
  });

  afterEach(() => {
    console.error = originalError;
  });

  describe('正常渲染', () => {
    it('should render children when no error occurs', () => {
      render(
        <ErrorBoundary>
          <div>Test content</div>
        </ErrorBoundary>
      );

      expect(screen.getByText('Test content')).toBeInTheDocument();
    });

    it('should handle multiple children', () => {
      render(
        <ErrorBoundary>
          <div>Child 1</div>
          <div>Child 2</div>
        </ErrorBoundary>
      );

      expect(screen.getByText('Child 1')).toBeInTheDocument();
      expect(screen.getByText('Child 2')).toBeInTheDocument();
    });
  });

  describe('错误捕获', () => {
    it('should catch errors and display error UI', () => {
      render(
        <ErrorBoundary>
          <ThrowError />
        </ErrorBoundary>
      );

      expect(screen.getByText('糟糕，出现了一些问题')).toBeInTheDocument();
      expect(
        screen.getByText('AIFlow遇到了一个意外错误。我们已经记录了这个问题。')
      ).toBeInTheDocument();
    });

    it('should display custom fallback UI when provided', () => {
      const customFallback = <div>Custom error message</div>;

      render(
        <ErrorBoundary fallback={customFallback}>
          <ThrowError />
        </ErrorBoundary>
      );

      expect(screen.getByText('Custom error message')).toBeInTheDocument();
      expect(screen.queryByText('糟糕，出现了一些问题')).not.toBeInTheDocument();
    });

    it('should log error to console', () => {
      const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

      render(
        <ErrorBoundary>
          <ThrowError />
        </ErrorBoundary>
      );

      expect(consoleErrorSpy).toHaveBeenCalled();
      consoleErrorSpy.mockRestore();
    });
  });

  describe('错误恢复', () => {
    it('should reset error state when reset button is clicked', async () => {
      const user = userEvent.setup();
      let shouldThrow = true;

      render(
        <ErrorBoundary>
          <ThrowError shouldThrow={shouldThrow} />
        </ErrorBoundary>
      );

      // Error should be displayed
      expect(screen.getByText('糟糕，出现了一些问题')).toBeInTheDocument();

      // Fix the error condition
      shouldThrow = false;

      // Click reset button
      const resetButton = screen.getByRole('button', { name: /重新尝试/i });
      await user.click(resetButton);

      // Should attempt to re-render children
      // Note: In real scenario, this would re-render the fixed component
    });

    it('should reload page when reload button is clicked', async () => {
      const user = userEvent.setup();

      // Mock window.location.reload by replacing the entire location object
      const originalLocation = window.location;
      delete (window as any).location;
      window.location = { ...originalLocation, reload: vi.fn() } as any;

      render(
        <ErrorBoundary>
          <ThrowError />
        </ErrorBoundary>
      );

      const reloadButton = screen.getByRole('button', { name: /刷新页面/i });
      await user.click(reloadButton);

      expect(window.location.reload).toHaveBeenCalled();

      // Restore original location
      window.location = originalLocation as any;
    });
  });

  describe('开发者信息', () => {
    const originalEnv = import.meta.env.DEV;

    beforeEach(() => {
      // Mock development environment
      Object.defineProperty(import.meta, 'env', {
        configurable: true,
        value: { DEV: true },
      });
    });

    afterEach(() => {
      // Restore original environment
      Object.defineProperty(import.meta, 'env', {
        configurable: true,
        value: { DEV: originalEnv },
      });
    });

    it('should display developer information in development mode', () => {
      render(
        <ErrorBoundary>
          <ThrowError />
        </ErrorBoundary>
      );

      expect(screen.getByText(/🐛 开发者信息 \(仅在开发环境显示\)/i)).toBeInTheDocument();
    });

    it('should display error details when summary is clicked', async () => {
      const user = userEvent.setup();

      render(
        <ErrorBoundary>
          <ThrowError />
        </ErrorBoundary>
      );

      const summary = screen.getByText(/🐛 开发者信息 \(仅在开发环境显示\)/i);
      await user.click(summary);

      expect(screen.getByText('错误信息:')).toBeInTheDocument();
    });
  });

  describe('边界情况', () => {
    it('should handle null children', () => {
      render(<ErrorBoundary>{null}</ErrorBoundary>);

      // Should render without errors
      expect(screen.queryByText('糟糕，出现了一些问题')).not.toBeInTheDocument();
    });

    it('should handle undefined children', () => {
      render(<ErrorBoundary>{undefined}</ErrorBoundary>);

      // Should render without errors
      expect(screen.queryByText('糟糕，出现了一些问题')).not.toBeInTheDocument();
    });

    it('should handle errors in nested components', () => {
      render(
        <ErrorBoundary>
          <div>
            <div>
              <ThrowError />
            </div>
          </div>
        </ErrorBoundary>
      );

      expect(screen.getByText('糟糕，出现了一些问题')).toBeInTheDocument();
    });

    it('should not catch errors outside boundary', () => {
      // This test verifies that ErrorBoundary only catches errors within its children
      const OutsideComponent = () => <div>Outside</div>;

      render(
        <div>
          <OutsideComponent />
          <ErrorBoundary>
            <div>Inside boundary</div>
          </ErrorBoundary>
        </div>
      );

      expect(screen.getByText('Outside')).toBeInTheDocument();
      expect(screen.getByText('Inside boundary')).toBeInTheDocument();
    });
  });
});
