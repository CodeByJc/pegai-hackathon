interface ErrorMessageProps {
  message: string;
  onDismiss?: () => void;
  variant?: 'error' | 'warning' | 'success';
  id?: string;
}

export function FieldMessage({
  message,
  onDismiss,
  variant = 'error',
  id,
}: ErrorMessageProps) {
  return (
    <div
      id={id}
      className={`field-message field-message--${variant}`}
      role="alert"
      aria-live="polite"
    >
      {variant === 'error' && (
        <svg className="field-message__icon" viewBox="0 0 16 16" fill="none" aria-hidden="true">
          <circle cx="8" cy="8" r="7" stroke="currentColor" strokeWidth="1.5" />
          <path d="M8 5v3.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
          <circle cx="8" cy="11" r="0.75" fill="currentColor" />
        </svg>
      )}
      {variant === 'warning' && (
        <svg className="field-message__icon" viewBox="0 0 16 16" fill="none" aria-hidden="true">
          <path d="M8 2L14.5 13.5H1.5L8 2Z" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round" />
          <path d="M8 7v2.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
          <circle cx="8" cy="11.5" r="0.75" fill="currentColor" />
        </svg>
      )}
      {variant === 'success' && (
        <svg className="field-message__icon" viewBox="0 0 16 16" fill="none" aria-hidden="true">
          <circle cx="8" cy="8" r="7" stroke="currentColor" strokeWidth="1.5" />
          <path d="M5 8l2 2 4-4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      )}
      <span>{message}</span>
      {onDismiss && (
        <button
          className="field-message__dismiss"
          onClick={onDismiss}
          aria-label="Dismiss message"
          type="button"
        >
          <svg width="12" height="12" viewBox="0 0 12 12" fill="none" aria-hidden="true">
            <path d="M1 1l10 10M11 1L1 11" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
          </svg>
        </button>
      )}
    </div>
  );
}
