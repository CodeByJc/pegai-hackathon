import type { ProposedFix, FileDiff } from '../../types/diagnosis';

interface ProposedFixProps {
  fix: ProposedFix;
}

function DiffView({ diff }: { diff: FileDiff }) {
  const beforeLines = diff.before.split('\n');
  const afterLines = diff.after.split('\n');

  return (
    <div className="code-block" style={{ marginBottom: 'var(--space-3)' }}>
      <div className="code-block__filename">{diff.filename}</div>
      <div className="code-block__content">
        {/* Before */}
        {beforeLines.map((line, i) => (
          <span key={`b-${i}`} className="diff-line diff-line--removed">
            {`- ${line}\n`}
          </span>
        ))}
        {/* After */}
        {afterLines.map((line, i) => (
          <span key={`a-${i}`} className="diff-line diff-line--added">
            {`+ ${line}\n`}
          </span>
        ))}
      </div>
    </div>
  );
}

export function ProposedFixCard({ fix }: ProposedFixProps) {
  return (
    <div className="result-card">
      <div className="result-card__header">
        <span className="result-card__section-label">Proposed Fix</span>
      </div>
      <div className="result-card__body">
        <p className="fix-summary">{fix.summary}</p>
        {fix.diffs.map((diff, i) => (
          <DiffView key={i} diff={diff} />
        ))}
      </div>
    </div>
  );
}
