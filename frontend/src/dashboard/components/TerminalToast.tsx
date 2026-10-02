import React, { createContext, useContext, useState, useCallback } from 'react';
import { CheckCircle2, AlertTriangle, Info, XCircle, X } from 'lucide-react';
import { terminalAudio } from '../utils/terminalAudio';

export type ToastType = 'success' | 'warning' | 'error' | 'info';

export interface ToastItem {
  id: string;
  type: ToastType;
  title: string;
  message?: string;
  timestamp: string;
}

interface ToastContextValue {
  showToast: (type: ToastType, title: string, message?: string) => void;
  removeToast: (id: string) => void;
}

const ToastContext = createContext<ToastContextValue | null>(null);

export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
};

export const ToastProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [toasts, setToasts] = useState<ToastItem[]>([]);

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const showToast = useCallback(
    (type: ToastType, title: string, message?: string) => {
      const id = `toast-${Date.now()}-${Math.random().toString(36).substr(2, 5)}`;
      const timestamp = new Date().toLocaleTimeString('en-US', { hour12: false });
      const newToast: ToastItem = { id, type, title, message, timestamp };

      setToasts((prev) => [...prev.slice(-4), newToast]); // keep max 5

      if (type === 'success') terminalAudio.playSuccessChime();
      else if (type === 'error' || type === 'warning') terminalAudio.playWarning();
      else terminalAudio.playBlip();

      setTimeout(() => {
        removeToast(id);
      }, 4500);
    },
    [removeToast]
  );

  return (
    <ToastContext.Provider value={{ showToast, removeToast }}>
      {children}
      {/* Toast Render Viewport */}
      <div className="fixed bottom-10 right-4 z-50 flex flex-col gap-2 max-w-sm w-full pointer-events-none font-mono select-none">
        {toasts.map((toast) => {
          const isSuccess = toast.type === 'success';
          const isWarning = toast.type === 'warning';
          const isError = toast.type === 'error';

          return (
            <div
              key={toast.id}
              className={`pointer-events-auto p-3 rounded border shadow-2xl transition-all transform translate-y-0 opacity-100 flex items-start justify-between gap-2.5 backdrop-blur-md ${
                isSuccess
                  ? 'bg-[#0D1612]/95 border-[var(--bb-green)] text-[var(--bb-text-bright)]'
                  : isWarning
                  ? 'bg-[#1C150A]/95 border-[var(--bb-amber)] text-[var(--bb-text-bright)]'
                  : isError
                  ? 'bg-[#1C0D12]/95 border-[var(--bb-red)] text-[var(--bb-text-bright)]'
                  : 'bg-[#0F131A]/95 border-[var(--bb-cyan)] text-[var(--bb-text-bright)]'
              }`}
            >
              <div className="flex items-start gap-2 min-w-0">
                {isSuccess && <CheckCircle2 className="w-4 h-4 text-[var(--bb-green)] mt-0.5 flex-shrink-0" />}
                {isWarning && <AlertTriangle className="w-4 h-4 text-[var(--bb-amber)] mt-0.5 flex-shrink-0" />}
                {isError && <XCircle className="w-4 h-4 text-[var(--bb-red)] mt-0.5 flex-shrink-0" />}
                {!isSuccess && !isWarning && !isError && (
                  <Info className="w-4 h-4 text-[var(--bb-cyan)] mt-0.5 flex-shrink-0" />
                )}

                <div className="min-w-0">
                  <div className="flex items-center gap-1.5">
                    <span className="font-bold text-[11px] tracking-wide uppercase truncate">
                      {toast.title}
                    </span>
                    <span className="text-[9px] text-[var(--bb-text-dim)]">[{toast.timestamp}]</span>
                  </div>
                  {toast.message && (
                    <p className="text-[10px] text-[var(--bb-text-secondary)] mt-0.5 leading-tight">
                      {toast.message}
                    </p>
                  )}
                </div>
              </div>

              <button
                type="button"
                onClick={() => removeToast(toast.id)}
                className="text-[var(--bb-text-muted)] hover:text-[var(--bb-text-bright)] p-0.5 transition-colors flex-shrink-0"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </div>
          );
        })}
      </div>
    </ToastContext.Provider>
  );
};
