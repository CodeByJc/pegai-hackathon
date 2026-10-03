import type { DiagnosisResult } from '../types/diagnosis';
import { ErrorSummary } from '../components/diagnosis/ErrorSummary';
import { RootCause } from '../components/diagnosis/RootCause';
import { HypothesisList } from '../components/diagnosis/HypothesisList';
import { ProposedFixCard } from '../components/diagnosis/ProposedFix';
import { GeneratedTests } from '../components/diagnosis/GeneratedTests';
import { VerificationResultCard } from '../components/diagnosis/VerificationResult';
import { Button } from '../components/common/Button';
import { formatDuration } from '../utils/format';

interface ResultPageProps {
  result: DiagnosisResult;
  onNewAnalysis: () => void;
}

export function ResultPage({ result, onNewAnalysis }: ResultPageProps) {
  return (
    <>
      <div className="page-intro">
        <h1 className="page-intro__title">Diagnosis ready</h1>
        <p className="page-intro__description">
          Analysis completed in {formatDuration(result.durationMs)}.
        </p>
      </div>

      <div className="new-analysis-bar">
        <p className="new-analysis-bar__text">
          Want to debug a different error? Start a new analysis.
        </p>
        <Button variant="ghost" size="sm" onClick={onNewAnalysis}>
          New analysis
        </Button>
      </div>

      <div className="result-section">
        <ErrorSummary result={result} />
        <RootCause result={result} />
        <HypothesisList hypotheses={result.hypotheses} />
        <ProposedFixCard fix={result.fix} />
        <GeneratedTests tests={result.tests} />
        <VerificationResultCard verification={result.verification} />
      </div>
    </>
  );
}
