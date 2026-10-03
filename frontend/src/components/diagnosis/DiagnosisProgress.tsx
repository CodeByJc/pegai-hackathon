import { useEffect, useState } from 'react';

type StepStatus = 'done' | 'active' | 'pending';

interface Step {
  id: string;
  label: string;
}

const STEPS: Step[] = [
  { id: 'read', label: 'Reading uploaded files' },
  { id: 'parse', label: 'Parsing traceback' },
  { id: 'investigate', label: 'Investigating possible causes' },
  { id: 'diagnose', label: 'Preparing diagnosis' },
];

// How long (ms) to spend on each step in the simulated progress
const STEP_DURATIONS = [600, 900, 1800, 600];

export function DiagnosisProgress() {
  const [activeStep, setActiveStep] = useState(0);

  useEffect(() => {
    let current = 0;

    function advance() {
      current += 1;
      if (current < STEPS.length) {
        setActiveStep(current);
        setTimeout(advance, STEP_DURATIONS[current]);
      }
    }

    const timeout = setTimeout(advance, STEP_DURATIONS[0]);
    return () => clearTimeout(timeout);
  }, []);

  function stepStatus(index: number): StepStatus {
    if (index < activeStep) return 'done';
    if (index === activeStep) return 'active';
    return 'pending';
  }

  return (
    <div className="diagnosis-progress" role="status" aria-live="polite" aria-label="Analysis in progress">
      <h2 className="diagnosis-progress__heading">Analyzing Python project</h2>
      <ul className="diagnosis-progress__steps">
        {STEPS.map((step, i) => {
          const status = stepStatus(i);
          return (
            <li key={step.id} className={`progress-step progress-step--${status}`}>
              <span className="progress-step__indicator" aria-hidden="true">
                {status === 'done' && (
                  <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                    <circle cx="8" cy="8" r="7" fill="var(--color-success)" opacity="0.15" />
                    <path d="M5 8l2 2 4-4" stroke="var(--color-success)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                )}
                {status === 'active' && <span className="spinner-ring" />}
                {status === 'pending' && (
                  <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                    <circle cx="8" cy="8" r="3" fill="var(--color-text-tertiary)" opacity="0.4" />
                  </svg>
                )}
              </span>
              <span className="progress-step__label">{step.label}</span>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
