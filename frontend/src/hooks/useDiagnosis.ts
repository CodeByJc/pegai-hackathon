import { useState, useCallback } from 'react';
import type { PythonFile } from '../types/project';
import type { DiagnosisState } from '../types/diagnosis';
import { diagnosisService } from '../services/api/diagnosisService';

export interface UseDiagnosisReturn {
  diagnosisState: DiagnosisState;
  runDiagnosis: (files: PythonFile[], traceback: string) => Promise<void>;
  resetDiagnosis: () => void;
}

export function useDiagnosis(): UseDiagnosisReturn {
  const [diagnosisState, setDiagnosisState] = useState<DiagnosisState>({
    status: 'idle',
  });

  const runDiagnosis = useCallback(
    async (files: PythonFile[], traceback: string) => {
      if (diagnosisState.status === 'analyzing') return;

      setDiagnosisState({ status: 'analyzing' });

      try {
        const result = await diagnosisService.diagnose({
          id: `project-${Date.now()}`,
          files,
          traceback,
        });
        setDiagnosisState({ status: 'success', result });
      } catch (err) {
        const message =
          err instanceof Error
            ? err.message
            : "We couldn't analyze the project. Please try again.";
        setDiagnosisState({ status: 'error', message });
      }
    },
    [diagnosisState.status]
  );

  const resetDiagnosis = useCallback(() => {
    setDiagnosisState({ status: 'idle' });
  }, []);

  return { diagnosisState, runDiagnosis, resetDiagnosis };
}
