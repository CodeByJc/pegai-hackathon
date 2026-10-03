import type { PythonFile } from '../../types/project';

export interface ProjectService {
  readFiles(fileList: FileList): Promise<PythonFile[]>;
  validateFile(file: File): { valid: boolean; reason?: string };
}

export class BrowserProjectService implements ProjectService {
  private readonly ALLOWED_EXTENSION = '.py';

  validateFile(file: File): { valid: boolean; reason?: string } {
    if (!file.name.endsWith(this.ALLOWED_EXTENSION)) {
      return {
        valid: false,
        reason: `Only Python (.py) files can be uploaded. "${file.name}" is not allowed.`,
      };
    }
    return { valid: true };
  }

  async readFiles(fileList: FileList): Promise<PythonFile[]> {
    const files: PythonFile[] = [];

    for (const file of Array.from(fileList)) {
      const validation = this.validateFile(file);
      if (!validation.valid) continue;

      const content = await file.text();
      files.push({
        id: `${file.name}-${file.lastModified}-${file.size}`,
        name: file.name,
        size: file.size,
        content,
      });
    }

    return files;
  }
}

export const projectService: ProjectService = new BrowserProjectService();
