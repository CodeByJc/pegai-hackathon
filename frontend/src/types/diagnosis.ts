export type ConfidenceLevel = 'high' | 'medium' | 'low';

export type VerificationStatus = 'verified' | 'failed' | 'not_verified' | 'not_run' | 'execution_error' | 'unverified';

export interface Hypothesis {
  rank: number;
  title: string;
  explanation: string;
  confidence: ConfidenceLevel;
  evidence: string[];
}

export interface FileDiff {
  filename: string;
  before: string;
  after: string;
}

export interface ProposedFix {
  summary: string;
  diffs: FileDiff[];
}

export interface GeneratedTest {
  filename: string;
  content: string;
}

export interface VerificationResult {
  status: VerificationStatus;
  testsRun: number;
  passed: number;
  failed: number;
  output?: string;
}

export interface DiagnosisResult {
  id: string;
  errorType: string;
  errorMessage: string;
  rootCause: string;
  hypotheses: Hypothesis[];
  fix: ProposedFix;
  tests: GeneratedTest[];
  verification: VerificationResult;
  durationMs: number;
}

export type DiagnosisState =
  | { status: 'idle' }
  | { status: 'analyzing' }
  | { status: 'success'; result: DiagnosisResult }
  | { status: 'error'; message: string };
