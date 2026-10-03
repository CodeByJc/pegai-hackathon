interface TracebackEditorProps {
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
}

const PLACEHOLDER = `Traceback (most recent call last):
  File "main.py", line 42, in startup
    process(settings['config'])
KeyError: 'config'`;

export function TracebackEditor({ value, onChange, disabled }: TracebackEditorProps) {
  return (
    <div className="traceback-editor">
      <div className="traceback-editor__label">
        <label
          htmlFor="traceback-input"
          className="traceback-editor__label-text"
        >
          Python traceback
        </label>
      </div>
      <p className="traceback-editor__support">
        Paste the complete traceback from your terminal or IDE.
      </p>
      <textarea
        id="traceback-input"
        className="traceback-editor__textarea"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={PLACEHOLDER}
        disabled={disabled}
        spellCheck={false}
        autoComplete="off"
        autoCorrect="off"
        autoCapitalize="off"
        aria-label="Python traceback input"
        aria-describedby="traceback-hint"
      />
      <p id="traceback-hint" className="sr-only">
        Enter the full Python traceback including the error type and message.
      </p>
    </div>
  );
}
