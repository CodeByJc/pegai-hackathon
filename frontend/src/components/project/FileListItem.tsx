import { formatFileSize } from '../../utils/format';
import type { PythonFile } from '../../types/project';

interface FileListItemProps {
  file: PythonFile;
  onRemove: () => void;
}

export function FileListItem({ file, onRemove }: FileListItemProps) {
  return (
    <li className="file-list__item">
      {/* Python snake icon */}
      <svg
        className="file-list__icon"
        viewBox="0 0 16 16"
        fill="none"
        aria-hidden="true"
      >
        <path
          d="M6.5 2C4.57 2 3 3.57 3 5.5V7h5.5A1.5 1.5 0 0 1 10 8.5V10H7v1h3v1.5C10 14.43 11.57 16 13.5 16S17 14.43 17 12.5V11h-5.5A1.5 1.5 0 0 1 10 9.5V8H13V7h-3V5.5C10 3.57 8.43 2 6.5 2z"
          fill="currentColor"
          transform="scale(0.88) translate(0.5, 0.5)"
        />
        <circle cx="5.5" cy="5" r="1" fill="var(--color-bg)" />
        <circle cx="10.5" cy="11" r="1" fill="var(--color-bg)" />
      </svg>

      <span className="file-list__name" title={file.name}>
        {file.name}
      </span>
      <span className="file-list__size">{formatFileSize(file.size)}</span>
      <button
        className="file-list__remove"
        onClick={onRemove}
        type="button"
        aria-label={`Remove ${file.name}`}
        title={`Remove ${file.name}`}
      >
        <svg width="12" height="12" viewBox="0 0 12 12" fill="none" aria-hidden="true">
          <path
            d="M1 1l10 10M11 1L1 11"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
          />
        </svg>
      </button>
    </li>
  );
}
