import type { DebugProject } from '../../types/project';
import type { DiagnosisResult } from '../../types/diagnosis';

export interface DiagnosisService {
  diagnose(project: DebugProject): Promise<DiagnosisResult>;
}
