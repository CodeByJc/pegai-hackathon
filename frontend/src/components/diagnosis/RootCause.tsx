import type { DiagnosisResult } from '../../types/diagnosis';

interface RootCauseProps {
  result: DiagnosisResult;
}

export function RootCause({ result }: RootCauseProps) {
  return (
    <div className="result-card">
      <div className="result-card__header">
        <span className="result-card__section-label">Root Cause</span>
      </div>
      <div className="result-card__body">
        <p className="root-cause__text">{result.rootCause}</p>
      </div>
    </div>
  );
}
