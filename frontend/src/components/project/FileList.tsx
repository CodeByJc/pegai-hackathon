import type { PythonFile } from '../../types/project';
import { FileListItem } from './FileListItem';

interface FileListProps {
  files: PythonFile[];
  onRemoveFile: (id: string) => void;
}

export function FileList({ files, onRemoveFile }: FileListProps) {
  return (
    <ul className="file-list" aria-label="Uploaded Python files">
      {files.map((file) => (
        <FileListItem
          key={file.id}
          file={file}
          onRemove={() => onRemoveFile(file.id)}
        />
      ))}
    </ul>
  );
}
