import pathlib
import sys

content = """import type { DiagnosisResult } from '../../types/diagnosis';
import type { DebugProject } from '../../types/project';
import type { DiagnosisService } from './diagnosis';

const MOCK_RESULT: DiagnosisResult = {
  id: 'mock-001',
  errorType: 'KeyError',
  errorMessage: "KeyError: 'config'",
  rootCause:
    "The application attempts to access `settings['config']` before the configuration file has been loaded. " +
    "The `load_config()` function is called asynchronously, but the key is read synchronously before the coroutine completes, " +
    "leaving the dictionary without the expected `'config'` key at the time of access.",
  hypotheses: [
    {
      rank: 1,
      title: "Configuration key missing at access time",
      explanation:
        "The `config` key is accessed before `load_config()` populates the settings dictionary. " +
        "The async initialization is not awaited before the first read.",
      confidence: 'high',
      evidence: [
        "Line 42 in main.py accesses `settings['config']` directly",
        "`load_config()` is scheduled but not awaited on line 38",
        "Traceback shows KeyError on the first call after startup",
      ],
    },
  ],
  fix: {
    summary:
      "Await `load_config()` before accessing the settings dictionary, or ensure the configuration is loaded synchronously during application startup.",
    diffs: [
      {
        filename: 'main.py',
        before: `async def startup():\\n    schedule_config_load()\\n    process(settings['config'])`,
        after: `async def startup():\\n    await load_config()\\n    process(settings['config'])`,
      },
    ],
  },
  tests: [],
  verification: {
    status: 'verified',
    testsRun: 3,
    passed: 3,
    failed: 0,
    output: '',
  },
  durationMs: 8340,
};

function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export class MockDiagnosisService implements DiagnosisService {
  async diagnose(_project: DebugProject): Promise<DiagnosisResult> {
    await delay(3800);
    return { ...MOCK_RESULT, id: `mock-${Date.now()}` };
  }
}

export class ApiDiagnosisService implements DiagnosisService {
  private baseUrl: string;

  constructor(baseUrl = '/api') {
    this.baseUrl = baseUrl;
  }

  async diagnose(project: DebugProject): Promise<DiagnosisResult> {
    // 1. Create project
    const createRes = await fetch(`${this.baseUrl}/projects`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({}),
    });
    if (!createRes.ok) throw new Error(`Failed to create project`);
    const { project_id } = await createRes.json();

    // 2. Upload files
    const formData = new FormData();
    for (const file of project.files) {
      if (file.content !== undefined) {
        const blob = new Blob([file.content], { type: 'text/x-python' });
        formData.append('files', blob, file.name);
      }
    }
    const filesRes = await fetch(`${this.baseUrl}/projects/${project_id}/files`, {
      method: 'POST',
      body: formData,
    });
    if (!filesRes.ok) throw new Error(`Failed to upload files`);

    // 3. Set traceback
    const tracebackRes = await fetch(`${this.baseUrl}/projects/${project_id}/traceback`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ traceback: project.traceback }),
    });
    if (!tracebackRes.ok) throw new Error(`Failed to set traceback`);

    // 4. Diagnose
    const diagnoseRes = await fetch(`${this.baseUrl}/projects/${project_id}/diagnose`, {
      method: 'POST',
    });
    if (!diagnoseRes.ok) throw new Error(`Diagnosis failed`);

    const data = await diagnoseRes.json();
    
    return {
      id: data.project_id || `diag-${Date.now()}`,
      errorType: data.diagnosis?.error_type || 'UnknownError',
      errorMessage: data.diagnosis?.error_message || 'Unknown Error',
      rootCause: data.diagnosis?.root_cause || '',
      hypotheses: data.hypotheses || [],
      fix: {
        summary: data.fix?.description || '',
        diffs: (data.fix?.files_to_modify || []).map((f: any) => ({
          filename: f.path,
          before: '',
          after: f.patch,
        })),
      },
      tests: (data.tests || []).map((t: any) => ({
        filename: t.path,
        content: t.content,
      })),
      verification: data.verification ? {
        status: data.verification.status,
        testsRun: data.verification.tests_run,
        passed: data.verification.passed,
        failed: data.verification.failed,
        output: data.verification.output || '',
      } : undefined,
      durationMs: data.verification?.duration_ms || 0,
    };
  }
}

// Toggle to ApiDiagnosisService for local development with a backend.
export const diagnosisService: DiagnosisService = new ApiDiagnosisService();
"""

path = pathlib.Path('/home/jc/JC_PROJECT/pegai-hackathon/frontend/src/services/api/diagnosisService.ts')
path.write_text(content)
print("Updated frontend diagnosisService.ts")
