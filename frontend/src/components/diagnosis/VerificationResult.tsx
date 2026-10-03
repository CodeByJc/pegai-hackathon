import type { VerificationResult } from '../../types/diagnosis';

interface VerificationResultProps {
  verification: VerificationResult;
}

const STATUS_CONFIG = {
  verified: {
    label: 'Fix verified',
    iconClass: 'verification-status__icon--verified',
    labelClass: 'verification-status__label--verified',
    icon: '✓',
  },
  failed: {
    label: 'Verification failed',
    iconClass: 'verification-status__icon--failed',
    labelClass: 'verification-status__label--failed',
    icon: '✗',
  },
  not_verified: {
    label: 'Not verified',
    iconClass: 'verification-status__icon--not_verified',
    labelClass: 'verification-status__label--not_verified',
    icon: '–',
  },
  not_run: {
    label: 'Tests not run',
    iconClass: 'verification-status__icon--not_run',
    labelClass: 'verification-status__label--not_run',
    icon: '○',
  },
};

export function VerificationResultCard({ verification }: VerificationResultProps) {
  const config = STATUS_CONFIG[verification.status];

  return (
    <div className="result-card">
      <div className="result-card__header">
        <span className="result-card__section-label">Verification</span>
      </div>
      <div className="result-card__body">
        <div className="verification-result">
          <div className="verification-status">
            <span
              className={`verification-status__icon ${config.iconClass}`}
              aria-hidden="true"
            >
              {config.icon}
            </span>
            <span className={`verification-status__label ${config.labelClass}`}>
              {config.label}
            </span>
          </div>

          {verification.testsRun > 0 && (
            <div className="verification-stats">
              <div className="verification-stat">
                <span className="verification-stat__value">{verification.testsRun}</span>
                <span className="verification-stat__label">Tests run</span>
              </div>
              <div className="verification-stat">
                <span
                  className="verification-stat__value"
                  style={{ color: verification.passed > 0 ? 'var(--color-success)' : undefined }}
                >
                  {verification.passed}
                </span>
                <span className="verification-stat__label">Passed</span>
              </div>
              <div className="verification-stat">
                <span
                  className="verification-stat__value"
                  style={{ color: verification.failed > 0 ? 'var(--color-error)' : undefined }}
                >
                  {verification.failed}
                </span>
                <span className="verification-stat__label">Failed</span>
              </div>
            </div>
          )}

          {verification.output && (
            <pre className="verification-output" aria-label="Test output">
              {verification.output}
            </pre>
          )}
        </div>
      </div>
    </div>
  );
}
