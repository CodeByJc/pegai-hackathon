export interface PythonFile {
  id: string;
  name: string;
  size: number;
  content?: string;
}

export interface DebugProject {
  id: string;
  files: PythonFile[];
  traceback: string;
}
