import type { DiagnosisResult } from '../../types/diagnosis';

interface ErrorSummaryProps {
  result: DiagnosisResult;
}

export function ErrorSummary({ result }: ErrorSummaryProps) {
  return (
    <div className="result-card">
      <div className="result-card__header">
        <span className="result-card__section-label">Error</span>
      </div>
      <div className="result-card__body">
        <p className="error-summary__type">{result.errorType}</p>
        <p className="error-summary__message">{result.errorMessage}</p>
      </div>
    </div>
  );
}
