import type { Hypothesis } from '../../types/diagnosis';
import { ConfidenceBadge } from '../common/Badge';

interface HypothesisListProps {
  hypotheses: Hypothesis[];
}

export function HypothesisList({ hypotheses }: HypothesisListProps) {
  return (
    <div className="result-card">
      <div className="result-card__header">
        <span className="result-card__section-label">Ranked Hypotheses</span>
        <span style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-tertiary)' }}>
          {hypotheses.length} candidates
        </span>
      </div>
      <div className="result-card__body">
        <ul className="hypothesis-list" aria-label="Ranked hypotheses">
          {hypotheses.map((h) => (
            <li key={h.rank} className="hypothesis-item">
              <div className="hypothesis-item__header">
                <span className="hypothesis-item__rank">{h.rank}</span>
                <span className="hypothesis-item__title">{h.title}</span>
                <ConfidenceBadge confidence={h.confidence} />
              </div>
              <p className="hypothesis-item__explanation">{h.explanation}</p>
              {h.evidence.length > 0 && (
                <ul className="hypothesis-item__evidence" aria-label={`Evidence for hypothesis ${h.rank}`}>
                  {h.evidence.map((e, i) => (
                    <li key={i} className="hypothesis-item__evidence-item">
                      {e}
                    </li>
                  ))}
                </ul>
              )}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
