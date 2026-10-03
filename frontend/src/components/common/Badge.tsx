import type { ConfidenceLevel } from '../../types/diagnosis';

interface BadgeProps {
  children: React.ReactNode;
  variant?: ConfidenceLevel | 'neutral';
}

const LABEL_MAP: Record<ConfidenceLevel, string> = {
  high: 'High confidence',
  medium: 'Medium confidence',
  low: 'Low confidence',
};

export function ConfidenceBadge({ confidence }: { confidence: ConfidenceLevel }) {
  return (
    <span className={`badge badge--${confidence}`}>
      {LABEL_MAP[confidence]}
    </span>
  );
}

export function Badge({ children, variant = 'neutral' }: BadgeProps) {
  return <span className={`badge badge--${variant}`}>{children}</span>;
}
