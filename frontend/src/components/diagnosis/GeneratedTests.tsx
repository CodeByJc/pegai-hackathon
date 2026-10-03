import type { GeneratedTest } from '../../types/diagnosis';

interface GeneratedTestsProps {
  tests: GeneratedTest[];
}

export function GeneratedTests({ tests }: GeneratedTestsProps) {
  if (tests.length === 0) {
    return null;
  }

  return (
    <div className="result-card">
      <div className="result-card__header">
        <span className="result-card__section-label">Generated Tests</span>
        <span style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-tertiary)' }}>
          {tests.length} {tests.length === 1 ? 'file' : 'files'}
        </span>
      </div>
      <div className="result-card__body">
        {tests.map((test, i) => (
          <div key={i} className="code-block" style={{ marginBottom: i < tests.length - 1 ? 'var(--space-3)' : 0 }}>
            <div className="code-block__filename">{test.filename}</div>
            <pre className="code-block__content">{test.content}</pre>
          </div>
        ))}
      </div>
    </div>
  );
}
