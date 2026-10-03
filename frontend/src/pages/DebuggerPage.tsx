import { useState } from 'react';
import { PythonFileUploader } from '../components/project/PythonFileUploader';
import { TracebackEditor } from '../components/traceback/TracebackEditor';
import { DiagnosisProgress } from '../components/diagnosis/DiagnosisProgress';
import { Button } from '../components/common/Button';
import { useProjectFiles } from '../hooks/useProjectFiles';
import { useDiagnosis } from '../hooks/useDiagnosis';
import { ResultPage } from './ResultPage';


export function DebuggerPage() {
  const [traceback, setTraceback] = useState('');
  const { files, uploadError, addFiles, removeFile, clearFiles, clearError } =
    useProjectFiles();
  const { diagnosisState, runDiagnosis, resetDiagnosis } = useDiagnosis();

  const isAnalyzing = diagnosisState.status === 'analyzing';
  const hasFiles = files.length > 0;
  const hasTraceback = traceback.trim().length > 0;
  const canDiagnose = hasFiles && hasTraceback && !isAnalyzing;

  function getButtonHint(): string | null {
    if (isAnalyzing) return null;
    if (!hasFiles && !hasTraceback) return 'Upload Python files and paste a traceback to continue';
    if (!hasFiles) return 'Upload at least one Python file to continue';
    if (!hasTraceback) return 'Paste a traceback to continue';
    return null;
  }

  async function handleDiagnose() {
    if (!canDiagnose) return;
    await runDiagnosis(files, traceback);
  }

  function handleNewAnalysis() {
    resetDiagnosis();
  }

  // Show result page after successful diagnosis
  if (diagnosisState.status === 'success') {
    return (
      <ResultPage
        result={diagnosisState.result}
        onNewAnalysis={handleNewAnalysis}
      />
    );
  }

  const hint = getButtonHint();

  return (
    <>
      <div className="page-intro">
        <h1 className="page-intro__title">Python Debugging Assistant</h1>
        <p className="page-intro__description">
          Upload your Python files, paste the traceback, and get a structured diagnosis.
        </p>
      </div>

      {/* File upload section */}
      <div className="section">
        <PythonFileUploader
          files={files}
          uploadError={uploadError}
          onAddFiles={addFiles}
          onRemoveFile={removeFile}
          onClearFiles={clearFiles}
          onClearError={clearError}
        />
      </div>

      {/* Traceback section */}
      <div className="section">
        <TracebackEditor
          value={traceback}
          onChange={setTraceback}
          disabled={isAnalyzing}
        />
      </div>

      {/* Analyzing progress */}
      {isAnalyzing && <DiagnosisProgress />}

      {/* Backend error */}
      {diagnosisState.status === 'error' && (
        <div className="app-error" role="alert">
          <p className="app-error__title">Couldn't analyze the project</p>
          <p className="app-error__message">{diagnosisState.message}</p>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleDiagnose}
            disabled={!canDiagnose}
          >
            Try again
          </Button>
        </div>
      )}

      {/* Action bar */}
      <div className="action-bar">
        {hint && (
          <p className="action-bar__hint" aria-live="polite">
            {hint}
          </p>
        )}
        <Button
          id="diagnose-btn"
          variant="primary"
          size="lg"
          onClick={handleDiagnose}
          disabled={!canDiagnose}
          aria-label={
            isAnalyzing
              ? 'Analysis in progress'
              : canDiagnose
              ? 'Diagnose Error'
              : hint ?? 'Diagnose Error'
          }
        >
          {isAnalyzing ? (
            <>
              <span className="spinner-ring" aria-hidden="true" style={{ width: 14, height: 14 }} />
              Analyzing…
            </>
          ) : (
            'Diagnose Error'
          )}
        </Button>
      </div>
    </>
  );
}
