import type { DiagnosisResult } from '../../types/diagnosis';
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
    {
      rank: 2,
      title: "Incorrect settings object imported",
      explanation:
        "A different `settings` dict from a sibling module shadows the one populated by `load_config()`, " +
        "so the loaded keys never appear in the object being read.",
      confidence: 'medium',
      evidence: [
        "Two `settings` dicts defined: config.py and app/settings.py",
        "Import path in main.py points to the empty fallback dict",
      ],
    },
    {
      rank: 3,
      title: "Configuration file absent or malformed",
      explanation:
        "The configuration file does not exist in the deployment environment or contains a syntax error " +
        "that causes the parser to return an empty dict without raising an exception.",
      confidence: 'low',
      evidence: [
        "No config file found in the uploaded project files",
        "config.py silently returns `{}` on any parse error",
      ],
    },
  ],
  fix: {
    summary:
      "Await `load_config()` before accessing the settings dictionary, or ensure the configuration is loaded synchronously during application startup.",
    diffs: [
      {
        filename: 'main.py',
        before: `async def startup():
    schedule_config_load()
    process(settings['config'])`,
        after: `async def startup():
    await load_config()
    process(settings['config'])`,
      },
    ],
  },
  tests: [
    {
      filename: 'tests/test_startup.py',
      content: `import pytest
from unittest.mock import AsyncMock, patch
from main import startup

@pytest.mark.asyncio
async def test_startup_loads_config_before_access():
    """startup() must await load_config before reading settings."""
    with patch("main.load_config", new_callable=AsyncMock) as mock_load:
        mock_load.return_value = {"config": {"debug": False}}
        await startup()
        mock_load.assert_awaited_once()

@pytest.mark.asyncio
async def test_startup_raises_without_config():
    """startup() raises KeyError if config is not loaded."""
    with patch("main.load_config", new_callable=AsyncMock) as mock_load:
        mock_load.return_value = {}
        with pytest.raises(KeyError, match="config"):
            await startup()
`,
    },
  ],
  verification: {
    status: 'verified',
    testsRun: 3,
    passed: 3,
    failed: 0,
    output:
      '============================= test session starts ==============================\n' +
      'collected 3 items\n\n' +
      'tests/test_startup.py::test_startup_loads_config_before_access PASSED\n' +
      'tests/test_startup.py::test_startup_raises_without_config PASSED\n' +
      'tests/test_startup.py::test_config_key_present_after_load PASSED\n\n' +
      '============================== 3 passed in 0.42s ==============================',
  },
  durationMs: 8340,
};

function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export class MockDiagnosisService implements DiagnosisService {
  async diagnose(_project: DebugProject): Promise<DiagnosisResult> {
    // Simulate realistic backend latency
    await delay(3800);
    return { ...MOCK_RESULT, id: `mock-${Date.now()}` };
  }
}

// Production implementation — wires to the real backend.
export class ApiDiagnosisService implements DiagnosisService {
  private baseUrl: string;

  constructor(baseUrl = '/api') {
    this.baseUrl = baseUrl;
  }

  async diagnose(project: DebugProject): Promise<DiagnosisResult> {
    const formData = new FormData();
    formData.append('traceback', project.traceback);
    for (const file of project.files) {
      if (file.content !== undefined) {
        const blob = new Blob([file.content], { type: 'text/x-python' });
        formData.append('files', blob, file.name);
      }
    }

    const response = await fetch(`${this.baseUrl}/diagnose`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const text = await response.text().catch(() => 'Unknown error');
      throw new Error(`Diagnosis failed (${response.status}): ${text}`);
    }

    return response.json() as Promise<DiagnosisResult>;
  }
}

// Toggle to MockDiagnosisService for local development without a backend.
export const diagnosisService: DiagnosisService = new MockDiagnosisService();
