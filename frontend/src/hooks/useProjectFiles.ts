import { useState, useCallback } from 'react';
import { uuid } from '../utils/uuid';
import type { PythonFile } from '../types/project';
import { projectService } from '../services/api/projectService';

export interface UploadError {
  type: 'unsupported' | 'duplicate' | 'read_error';
  message: string;
}

export interface UseProjectFilesReturn {
  files: PythonFile[];
  uploadError: UploadError | null;
  addFiles: (fileList: FileList) => Promise<void>;
  removeFile: (id: string) => void;
  clearFiles: () => void;
  clearError: () => void;
}

export function useProjectFiles(): UseProjectFilesReturn {
  const [files, setFiles] = useState<PythonFile[]>([]);
  const [uploadError, setUploadError] = useState<UploadError | null>(null);

  const addFiles = useCallback(async (fileList: FileList) => {
    setUploadError(null);
    const incoming = Array.from(fileList);

    // Validate extensions first
    const unsupported = incoming.filter(
      (f) => !projectService.validateFile(f).valid
    );
    if (unsupported.length > 0) {
      setUploadError({
        type: 'unsupported',
        reason: `Only Python (.py) files can be uploaded.`,
        message: `Only Python (.py) files can be uploaded.`,
      } as UploadError);
      return;
    }

    let newFiles: PythonFile[];
    try {
      newFiles = await projectService.readFiles(fileList);
    } catch {
      setUploadError({
        type: 'read_error',
        message: 'Failed to read the selected files. Please try again.',
      });
      return;
    }

    setFiles((prev) => {
      const existingNames = new Set(prev.map((f) => f.name));
      const duplicates = newFiles.filter((f) => existingNames.has(f.name));

      if (duplicates.length > 0) {
        const names = duplicates.map((f) => f.name).join(', ');
        setUploadError({
          type: 'duplicate',
          message:
            duplicates.length === 1
              ? `${duplicates[0].name} is already uploaded.`
              : `${names} are already uploaded.`,
        });
        // Still add non-duplicates
        const fresh = newFiles.filter((f) => !existingNames.has(f.name));
        return fresh.length > 0
          ? [...prev, ...fresh.map((f) => ({ ...f, id: f.id || uuid() }))]
          : prev;
      }

      return [...prev, ...newFiles.map((f) => ({ ...f, id: f.id || uuid() }))];
    });
  }, []);

  const removeFile = useCallback((id: string) => {
    setFiles((prev) => prev.filter((f) => f.id !== id));
    setUploadError(null);
  }, []);

  const clearFiles = useCallback(() => {
    setFiles([]);
    setUploadError(null);
  }, []);

  const clearError = useCallback(() => {
    setUploadError(null);
  }, []);

  return { files, uploadError, addFiles, removeFile, clearFiles, clearError };
}
