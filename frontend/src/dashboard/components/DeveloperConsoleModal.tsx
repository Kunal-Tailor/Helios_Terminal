import React, { useState } from 'react';
import {
  Code,
  Copy,
  Check,
  X,
  Play,
} from 'lucide-react';
import type { DecisionRequest, DecisionResponse } from '../api';
import { terminalAudio } from '../utils/terminalAudio';

interface DeveloperConsoleModalProps {
  isOpen: boolean;
  onClose: () => void;
  activeBrief: DecisionRequest;
  currentResult: DecisionResponse | null;
  onSubmitJson: (brief: DecisionRequest) => void;
}

type CodeTab = 'curl' | 'python' | 'typescript' | 'json_req' | 'json_res';

export const DeveloperConsoleModal: React.FC<DeveloperConsoleModalProps> = ({
  isOpen,
  onClose,
  activeBrief,
  currentResult,
  onSubmitJson,
}) => {
  const [activeTab, setActiveTab] = useState<CodeTab>('curl');
  const [jsonInput, setJsonInput] = useState(() => JSON.stringify(activeBrief, null, 2));
  const [jsonError, setJsonError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  if (!isOpen) return null;

  const handleCopy = (text: string) => {
    terminalAudio.playBlip();
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const curlSnippet = `curl -X POST http://127.0.0.1:8000/decisions/async \\
  -H "Content-Type: application/json" \\
  -d '${JSON.stringify(activeBrief, null, 2)}'`;

  const pythonSnippet = `import httpx
import asyncio
import json

API_BASE = "http://127.0.0.1:8000"

payload = ${JSON.stringify(activeBrief, null, 4)}

async def execute_helios_decision():
    async with httpx.AsyncClient(timeout=120.0) as client:
        print("[HELIOS] Submitting decision brief...")
        res = await client.post(f"{API_BASE}/decisions/async", json=payload)
        res.raise_for_status()
        job_id = res.json()["job_id"]
        print(f"[HELIOS] Job created: {job_id}. Polling pipeline...")

        while True:
            await asyncio.sleep(2.5)
            status_res = await client.get(f"{API_BASE}/decisions/jobs/{job_id}")
            job_data = status_res.json()
            status = job_data["status"]
            print(f" -> Pipeline status: {status}")

            if status == "completed":
                print("\\n[VERDICT SYNTHESIZED]")
                print(json.dumps(job_data["result"]["verdict"], indent=2))
                break
            elif status == "failed":
                print(f"Pipeline failed: {job_data.get('error')}")
                break

if __name__ == "__main__":
    asyncio.run(execute_helios_decision())`;

  const tsSnippet = `import { submitDecision, pollJobStatus, type DecisionRequest } from './api';

const brief: DecisionRequest = ${JSON.stringify(activeBrief, null, 2)};

async function runPipeline() {
  console.log('Submitting brief to Helios 6-Agent pipeline...');
  const { job_id } = await submitDecision(brief);
  
  const timer = setInterval(async () => {
    const job = await pollJobStatus(job_id);
    console.log('Stage status:', job.status);
    
    if (job.status === 'completed') {
      clearInterval(timer);
      console.log('Recommended Path:', job.result?.verdict?.recommended_path);
      console.log('Verification Status:', job.result?.verification_passed);
    }
  }, 2500);
}

runPipeline();`;

  const handleExecuteCustomJson = () => {
    try {
      setJsonError(null);
      const parsed = JSON.parse(jsonInput);
      if (!parsed.entity || !parsed.capability) {
        throw new Error('Payload must contain "entity" and "capability" string fields.');
      }
      terminalAudio.playGoCommand();
      onSubmitJson(parsed);
      onClose();
    } catch (err) {
      setJsonError(err instanceof Error ? err.message : 'Invalid JSON format');
      terminalAudio.playWarning();
    }
  };

  const getActiveCode = () => {
    if (activeTab === 'curl') return curlSnippet;
    if (activeTab === 'python') return pythonSnippet;
    if (activeTab === 'typescript') return tsSnippet;
    if (activeTab === 'json_req') return JSON.stringify(activeBrief, null, 2);
    if (activeTab === 'json_res') return currentResult ? JSON.stringify(currentResult, null, 2) : '// No completed decision result available yet';
    return '';
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/85 flex items-center justify-center p-4 backdrop-blur-sm select-none font-mono">
      <div className="bg-[var(--bb-bg-surface)] border border-[var(--bb-border-bright)] rounded max-w-4xl w-full max-h-[90vh] flex flex-col shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="bb-panel-header">
          <div className="flex items-center gap-2">
            <Code className="w-3.5 h-3.5 text-[var(--bb-cyan)]" />
            <span>DEVELOPER & CODER WORKBENCH // API CODE GENERATOR</span>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => handleCopy(getActiveCode())}
              className="bb-button bb-button-ghost px-2.5 py-1 text-[10px]"
              title="Copy Code Snippet"
            >
              {copied ? <Check className="w-3 h-3 text-[var(--bb-green)]" /> : <Copy className="w-3 h-3" />}
              <span>{copied ? 'COPIED' : 'COPY CODE'}</span>
            </button>

            <button
              type="button"
              onClick={onClose}
              className="text-[var(--bb-text-muted)] hover:text-[var(--bb-text-bright)] p-1 transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex items-center justify-between px-3 py-1.5 bg-[var(--bb-bg-raised)] border-b border-[var(--bb-border-subtle)] text-[10px]">
          <div className="flex items-center gap-1">
            <button
              type="button"
              onClick={() => {
                terminalAudio.playBlip();
                setActiveTab('curl');
              }}
              className={`px-2.5 py-1 rounded font-bold uppercase transition-all ${
                activeTab === 'curl'
                  ? 'bg-[var(--bb-amber-dim)] text-[var(--bb-amber)] border border-[var(--bb-amber)]'
                  : 'text-[var(--bb-text-muted)] hover:text-[var(--bb-text-primary)]'
              }`}
            >
              cURL CLI
            </button>

            <button
              type="button"
              onClick={() => {
                terminalAudio.playBlip();
                setActiveTab('python');
              }}
              className={`px-2.5 py-1 rounded font-bold uppercase transition-all ${
                activeTab === 'python'
                  ? 'bg-[var(--bb-cyan-dim)] text-[var(--bb-cyan)] border border-[var(--bb-cyan)]'
                  : 'text-[var(--bb-text-muted)] hover:text-[var(--bb-text-primary)]'
              }`}
            >
              Python (Async HTTPX)
            </button>

            <button
              type="button"
              onClick={() => {
                terminalAudio.playBlip();
                setActiveTab('typescript');
              }}
              className={`px-2.5 py-1 rounded font-bold uppercase transition-all ${
                activeTab === 'typescript'
                  ? 'bg-[var(--bb-purple-dim)] text-[var(--bb-purple)] border border-[var(--bb-purple)]'
                  : 'text-[var(--bb-text-muted)] hover:text-[var(--bb-text-primary)]'
              }`}
            >
              TypeScript / Fetch
            </button>

            <button
              type="button"
              onClick={() => {
                terminalAudio.playBlip();
                setActiveTab('json_req');
              }}
              className={`px-2.5 py-1 rounded font-bold uppercase transition-all ${
                activeTab === 'json_req'
                  ? 'bg-[var(--bb-green-dim)] text-[var(--bb-green)] border border-[var(--bb-green)]'
                  : 'text-[var(--bb-text-muted)] hover:text-[var(--bb-text-primary)]'
              }`}
            >
              JSON Payload Editor
            </button>

            <button
              type="button"
              onClick={() => {
                terminalAudio.playBlip();
                setActiveTab('json_res');
              }}
              className={`px-2.5 py-1 rounded font-bold uppercase transition-all ${
                activeTab === 'json_res'
                  ? 'bg-[var(--bb-bg-surface)] text-[var(--bb-text-bright)] border border-[var(--bb-border-bright)]'
                  : 'text-[var(--bb-text-muted)] hover:text-[var(--bb-text-primary)]'
              }`}
            >
              Response AST ({currentResult ? 'LIVE' : 'EMPTY'})
            </button>
          </div>

          <div className="flex items-center gap-2 text-[9px] text-[var(--bb-text-dim)]">
            <span>ENDPOINT: POST /decisions/async</span>
            <span>AUTH: NONE (LOCAL DEV)</span>
          </div>
        </div>

        {/* Code Content Viewport */}
        <div className="p-4 overflow-y-auto bb-scroll flex-1 bg-[var(--bb-bg-base)] text-xs">
          {activeTab === 'json_req' ? (
            <div className="space-y-3 h-full flex flex-col">
              <div className="flex items-center justify-between text-[11px] text-[var(--bb-text-secondary)]">
                <span>Directly edit the raw DecisionRequest schema below:</span>
                <span className="text-[10px] text-[var(--bb-amber)]">Pydantic v2 Compliant</span>
              </div>

              <textarea
                value={jsonInput}
                onChange={(e) => setJsonInput(e.target.value)}
                className="w-full flex-1 min-h-[260px] bg-[var(--bb-bg-input)] border border-[var(--bb-border-mid)] focus:border-[var(--bb-cyan)] text-[var(--bb-text-bright)] p-3 rounded font-mono text-xs outline-none bb-tabular"
              />

              {jsonError && (
                <div className="p-2 bg-[var(--bb-red-dim)] border border-[var(--bb-red)] rounded text-xs text-[var(--bb-red-bright)]">
                  Syntax Error: {jsonError}
                </div>
              )}

              <div className="flex items-center justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setJsonInput(JSON.stringify(activeBrief, null, 2))}
                  className="bb-button bb-button-ghost px-3 py-1.5 text-xs"
                >
                  RESET TO ACTIVE BRIEF
                </button>
                <button
                  type="button"
                  onClick={handleExecuteCustomJson}
                  className="bb-button bb-button-go px-4 py-1.5 text-xs font-bold"
                >
                  <Play className="w-3.5 h-3.5" /> EXECUTE CUSTOM JSON &lt;GO&gt;
                </button>
              </div>
            </div>
          ) : (
            <pre className="p-3 bg-[var(--bb-bg-input)] border border-[var(--bb-border-subtle)] rounded text-[var(--bb-text-bright)] overflow-x-auto leading-relaxed text-xs">
              <code>{getActiveCode()}</code>
            </pre>
          )}
        </div>

        {/* Developer Footer */}
        <div className="px-3 py-2 bg-[var(--bb-bg-surface)] border-t border-[var(--bb-border-subtle)] flex items-center justify-between text-[10px] text-[var(--bb-text-dim)]">
          <div className="flex items-center gap-3">
            <span className="text-[var(--bb-cyan)] font-bold">PIPELINE PROTOCOL: REST/JSON</span>
            <span>PYDANTIC SCHEMAS: DecisionRequest / DecisionResponse</span>
          </div>
          <span>HOTKEY: [ESC] TO DISMISS</span>
        </div>
      </div>
    </div>
  );
};
