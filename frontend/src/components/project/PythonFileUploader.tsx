import { useRef, useState } from 'react';
import type { PythonFile } from '../../types/project';
import { FileList } from './FileList';
import type { UploadError } from '../../hooks/useProjectFiles';

interface PythonFileUploaderProps {
  files: PythonFile[];
  uploadError: UploadError | null;
  onAddFiles: (fileList: FileList) => Promise<void>;
  onRemoveFile: (id: string) => void;
  onClearFiles: () => void;
  onClearError: () => void;
}

export function PythonFileUploader({
  files,
  uploadError,
  onAddFiles,
  onRemoveFile,
  onClearFiles,
  onClearError,
}: PythonFileUploaderProps) {
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const addMoreInputRef = useRef<HTMLInputElement>(null);

  const hasFiles = files.length > 0;

  function handleDragOver(e: React.DragEvent) {
    e.preventDefault();
    setIsDragOver(true);
  }

  function handleDragLeave(e: React.DragEvent) {
    // Only clear if leaving the drop zone entirely
    if (!e.currentTarget.contains(e.relatedTarget as Node)) {
      setIsDragOver(false);
    }
  }

  function handleDrop(e: React.DragEvent) {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files.length > 0) {
      onAddFiles(e.dataTransfer.files);
    }
  }

  function handleInputChange(e: React.ChangeEvent<HTMLInputElement>) {
    if (e.target.files && e.target.files.length > 0) {
      onAddFiles(e.target.files);
      // Reset so the same file can be re-added after removal
      e.target.value = '';
    }
  }

  if (!hasFiles) {
    return (
      <div>
        <div
          className={`file-uploader${isDragOver ? ' file-uploader--drag-over' : ''}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          role="region"
          aria-label="Python file upload area"
        >
          <label
            className="file-uploader__dropzone"
            htmlFor="python-file-input"
            aria-describedby={uploadError ? 'upload-error' : undefined}
          >
            <input
              id="python-file-input"
              ref={fileInputRef}
              type="file"
              className="file-uploader__dropzone-input"
              accept=".py"
              multiple
              onChange={handleInputChange}
              aria-label="Select Python files"
            />
            <svg
              className="file-uploader__icon"
              viewBox="0 0 36 36"
              fill="none"
              aria-hidden="true"
            >
              <rect x="6" y="4" width="24" height="28" rx="2" stroke="currentColor" strokeWidth="1.5" />
              <path d="M12 12h12M12 17h12M12 22h8" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
              <path d="M20 4v7h7" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round" />
            </svg>
            <div>
              <p className="file-uploader__title">Upload Python files</p>
            </div>
            <p className="file-uploader__subtitle">
              Add the files involved in the error.
              <br />
              Drag and drop or click to browse. Only <code>.py</code> files are accepted.
            </p>
          </label>
        </div>

        {uploadError && (
          <div
            id="upload-error"
            className="field-message field-message--error"
            role="alert"
            style={{ marginTop: 'var(--space-3)' }}
          >
            <svg className="field-message__icon" viewBox="0 0 16 16" fill="none" aria-hidden="true">
              <circle cx="8" cy="8" r="7" stroke="currentColor" strokeWidth="1.5" />
              <path d="M8 5v3.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
              <circle cx="8" cy="11" r="0.75" fill="currentColor" />
            </svg>
            <span>{uploadError.message}</span>
            <button
              className="field-message__dismiss"
              onClick={onClearError}
              type="button"
              aria-label="Dismiss error"
            >
              <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                <path d="M1 1l10 10M11 1L1 11" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
              </svg>
            </button>
          </div>
        )}
      </div>
    );
  }

  return (
    <div
      className={`file-uploader file-uploader--compact${isDragOver ? ' file-uploader--drag-over' : ''}`}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      role="region"
      aria-label="Python project files"
    >
      <div className="file-uploader__header">
        <span className="file-uploader__header-title">
          Python project · {files.length} {files.length === 1 ? 'file' : 'files'}
        </span>
        <div className="file-uploader__header-actions">
          <button
            className="btn btn--ghost btn--sm"
            onClick={onClearFiles}
            type="button"
            aria-label="Remove all files"
          >
            Clear all
          </button>
        </div>
      </div>

      <FileList
        files={files}
        onRemoveFile={onRemoveFile}
      />

      {/* Add more files */}
      <label
        className="file-list__add-row"
        htmlFor="python-file-add-more"
        aria-label="Add more Python files"
      >
        <input
          id="python-file-add-more"
          ref={addMoreInputRef}
          type="file"
          className="file-list__add-row-input"
          accept=".py"
          multiple
          onChange={handleInputChange}
          aria-label="Add more Python files"
        />
        <svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true" style={{ color: 'var(--color-accent)', flexShrink: 0 }}>
          <path d="M7 1v12M1 7h12" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
        </svg>
        <span className="file-list__add-label">Add Python files</span>
      </label>

      {uploadError && (
        <div
          className="field-message field-message--error"
          role="alert"
          style={{ margin: 'var(--space-3) var(--space-3) var(--space-3)' }}
        >
          <svg className="field-message__icon" viewBox="0 0 16 16" fill="none" aria-hidden="true">
            <circle cx="8" cy="8" r="7" stroke="currentColor" strokeWidth="1.5" />
            <path d="M8 5v3.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
            <circle cx="8" cy="11" r="0.75" fill="currentColor" />
          </svg>
          <span>{uploadError.message}</span>
          <button
            className="field-message__dismiss"
            onClick={onClearError}
            type="button"
            aria-label="Dismiss error"
          >
            <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
              <path d="M1 1l10 10M11 1L1 11" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
            </svg>
          </button>
        </div>
      )}
    </div>
  );
}
