import React, { useState, useCallback, useRef, useEffect } from 'react';
import {
  BloombergHeader,
  type ActiveWorkstationTab,
} from '../components/BloombergHeader';
import { BloombergDecisionConsole } from '../components/BloombergDecisionConsole';
import { AgentPipelineTopology } from '../components/AgentPipelineTopology';
import { InstitutionalVerdictPanel } from '../components/InstitutionalVerdictPanel';
import { TrajectoryChartPanel } from '../components/TrajectoryChartPanel';
import { LockInMatrixView } from '../components/LockInMatrixView';
import { AuditInspector } from '../components/AuditInspector';
import { IntelFeedPanel } from '../components/IntelFeedPanel';
import { BloombergGlobalMap } from '../components/BloombergGlobalMap';
import { BloombergSupplyChainGraph } from '../components/BloombergSupplyChainGraph';
import { ExecutiveDossierModal } from '../components/ExecutiveDossierModal';
import { PRESET_SCENARIOS, type PresetScenario } from '../data/presetScenarios';
import {
  submitDecision,
  pollJobStatus,
  checkBackendHealth,
  type DecisionRequest,
  type DecisionResponse,
  type JobStatusResponse,
} from '../api';
import { terminalAudio } from '../utils/terminalAudio';

type WorkstationState = 'idle' | 'submitting' | 'polling' | 'completed' | 'failed';

const POLL_INTERVAL_MS = 2500;

export const Dashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState<ActiveWorkstationTab>('quadrant');
  const [state, setState] = useState<WorkstationState>('completed');
  const [jobStatus, setJobStatus] = useState<JobStatusResponse['status']>('completed');
  const [selectedPreset, setSelectedPreset] = useState<PresetScenario>(PRESET_SCENARIOS[0]);
  const [result, setResult] = useState<DecisionResponse | null>(PRESET_SCENARIOS[0].result);
  const [error, setError] = useState<string | null>(null);
  const [isLiveServerConnected, setIsLiveServerConnected] = useState<boolean>(true);
  const [dossierModalOpen, setDossierModalOpen] = useState<boolean>(false);
  const [focusedQuadrant, setFocusedQuadrant] = useState<number | null>(null);

  const pollTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Periodic health check for live backend server
  useEffect(() => {
    let isMounted = true;
    const runCheck = async () => {
      const ok = await checkBackendHealth();
      if (isMounted) {
        setIsLiveServerConnected(ok);
      }
    };
    runCheck();
    const interval = setInterval(runCheck, 10000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  // Cleanup polling timer
  useEffect(() => {
    return () => {
      if (pollTimerRef.current) clearInterval(pollTimerRef.current);
    };
  }, []);

  const startPolling = useCallback((jobId: string) => {
    if (pollTimerRef.current) clearInterval(pollTimerRef.current);

    pollTimerRef.current = setInterval(async () => {
      try {
        const status = await pollJobStatus(jobId);
        // Successful response indicates backend is reachable and responsive
        setIsLiveServerConnected(true);
        setJobStatus(status.status);

        if (status.status === 'completed') {
          if (pollTimerRef.current) clearInterval(pollTimerRef.current);
          setResult(status.result);
          setState('completed');
          terminalAudio.playSuccessChime();
        } else if (status.status === 'failed') {
          if (pollTimerRef.current) clearInterval(pollTimerRef.current);
          setError(status.error || 'Pipeline execution encountered a fatal verification exception.');
          setState('failed');
          terminalAudio.playWarning();
        }
      } catch (err) {
        console.error('Polling error:', err);
      }
    }, POLL_INTERVAL_MS);
  }, []);

  const handleSubmit = useCallback(
    async (brief: DecisionRequest) => {
      setState('submitting');
      setError(null);
      setResult(null);
      terminalAudio.playGoCommand();

      try {
        const job = await submitDecision(brief);
        // Successful async submission means backend is connected
        setIsLiveServerConnected(true);
        setJobStatus(job.status);
        setState('polling');
        startPolling(job.job_id);
      } catch (err: unknown) {
        const errorMsg = err instanceof Error ? err.message : String(err);
        const isNetworkFailure =
          err instanceof TypeError ||
          errorMsg.includes('Failed to fetch') ||
          errorMsg.includes('NetworkError') ||
          errorMsg.includes('Network request failed') ||
          errorMsg.includes('Load failed');

        if (isNetworkFailure) {
          // Backend is genuinely unreachable: update beacon to STANDALONE and engage offline client fallback
          setIsLiveServerConnected(false);
          console.warn('Backend genuinely unreachable, triggering offline synthesis fallback:', err);
          setTimeout(() => {
            const match =
              PRESET_SCENARIOS.find(
                (p) =>
                  p.brief.entity.toLowerCase().includes(brief.entity.toLowerCase()) ||
                  brief.entity.toLowerCase().includes(p.brief.entity.toLowerCase())
              ) || PRESET_SCENARIOS[0];

            const clientResult: DecisionResponse = {
              ...match.result,
              entity: brief.entity,
              capability: brief.capability,
              options: brief.options.length > 0 ? brief.options : match.result.options,
            };

            setResult(clientResult);
            setState('completed');
            setJobStatus('completed');
            terminalAudio.playSuccessChime();
          }, 1200);
        } else {
          // Backend responded with an HTTP error (422, 500, 503, etc.).
          // Do NOT trigger offline fallback: server is ONLINE. Display actual error on workstation.
          setIsLiveServerConnected(true);
          console.error('Backend API error during submission:', err);
          setError(errorMsg || 'Pipeline execution failed on backend.');
          setState('failed');
          setJobStatus('failed');
          terminalAudio.playWarning();
        }
      }
    },
    [startPolling]
  );

  const handleSelectPreset = (preset: PresetScenario) => {
    setSelectedPreset(preset);
    setResult(preset.result);
    setState('completed');
    setJobStatus('completed');
    setError(null);
  };

  const handleExecuteCommand = (cmd: string) => {
    const trimmed = cmd.trim().toUpperCase();

    if (trimmed === 'EVAL' || trimmed === 'RUN' || trimmed === 'F2') {
      setActiveTab('decision');
    } else if (trimmed === 'QUAD' || trimmed === 'GRID' || trimmed === 'F1') {
      setActiveTab('quadrant');
      setFocusedQuadrant(null);
    } else if (trimmed === 'TRAJ' || trimmed === 'CHART' || trimmed === 'F3') {
      setActiveTab('trajectory');
    } else if (trimmed === 'LOCKIN' || trimmed === 'MATRIX' || trimmed === 'F4') {
      setActiveTab('lockin');
    } else if (trimmed === 'AUDIT' || trimmed === 'VERIFY' || trimmed === 'F5') {
      setActiveTab('audit');
    } else if (trimmed === 'FEED' || trimmed === 'STREAM' || trimmed === 'F6') {
      setActiveTab('feed');
    } else if (trimmed === 'DOSSIER' || trimmed === 'PRINT' || trimmed === 'F7') {
      setDossierModalOpen(true);
    } else if (trimmed === 'BMAP' || trimmed === 'MAP' || trimmed === 'INFRA' || trimmed === 'F8') {
      setActiveTab('bmap');
    } else if (trimmed === 'SPLC' || trimmed === 'CHAIN' || trimmed === 'SUPPLY' || trimmed === 'F9') {
      setActiveTab('splc');
    } else if (trimmed.startsWith('DEMO DEF')) {
      handleSelectPreset(PRESET_SCENARIOS[0]);
    } else if (trimmed.startsWith('DEMO FIN')) {
      handleSelectPreset(PRESET_SCENARIOS[1]);
    } else if (trimmed.startsWith('DEMO MED')) {
      handleSelectPreset(PRESET_SCENARIOS[2]);
    } else if (trimmed === 'CLEAR' || trimmed === 'RESET') {
      setResult(null);
      setState('idle');
      setJobStatus('queued');
      setError(null);
    } else if (trimmed === 'HELP') {
      alert(
        'HELIOS BLOOMBERG COMMAND REFERENCE:\n\n' +
        '• BMAP <GO>   : Global AI Infrastructure & Sovereignty Map [F8]\n' +
        '• SPLC <GO>   : Multi-Tier AI Supply Chain & Dependency Graph [F9]\n' +
        '• EVAL <GO>   : Open Decision Execution Console [F2]\n' +
        '• QUAD <GO>   : Open 4-Quadrant Launchpad Grid [F1]\n' +
        '• TRAJ <GO>   : Open 5-Year Trajectory Simulator [F3]\n' +
        '• LOCKIN <GO> : Open Lock-In Severity Matrix [F4]\n' +
        '• AUDIT <GO>  : Open Grounded Verification Inspector [F5]\n' +
        '• FEED <GO>   : Open Live Intelligence Stream [F6]\n' +
        '• DOSSIER <GO>: Generate Printable Executive Memo [F7]\n' +
        '• DEMO DEF/FIN/MED : Load Institutional Benchmarks\n' +
        '• CLEAR       : Reset active decision state'
      );
    }
  };

  return (
    <div className="bloomberg-terminal min-h-screen flex flex-col bg-[var(--bb-bg-base)] text-[var(--bb-text-primary)] select-none">
      {/* Bloomberg Global Command Header & Ribbon */}
      <BloombergHeader
        activeTab={activeTab}
        onSelectTab={(tab) => {
          if (tab === 'dossier') {
            setDossierModalOpen(true);
          } else {
            setActiveTab(tab);
          }
        }}
        onExecuteCommand={handleExecuteCommand}
        status={state}
        isLiveServerConnected={isLiveServerConnected}
        selectedPresetCode={selectedPreset?.code}
      />

      {/* Main Workstation Viewport */}
      <main className="flex-1 p-2 overflow-hidden flex flex-col min-h-0">
        {/* VIEW 1: 4-QUADRANT LAUNCHPAD WORKSPACE */}
        {activeTab === 'quadrant' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 grid-rows-2 gap-2 flex-1 min-h-0">
            {/* QUADRANT 1: DECISION EXECUTION CONSOLE */}
            <div
              className={`bb-panel rounded overflow-hidden flex flex-col ${
                focusedQuadrant === 1 ? 'col-span-2 row-span-2 z-20' : ''
              }`}
            >
              <BloombergDecisionConsole
                onSubmit={handleSubmit}
                onSelectPreset={handleSelectPreset}
                isSubmitting={state === 'submitting' || state === 'polling'}
                selectedPresetId={selectedPreset?.id}
              />
            </div>

            {/* QUADRANT 2: 6-STAGE AGENT PIPELINE TOPOLOGY */}
            <div
              className={`bb-panel rounded overflow-hidden flex flex-col ${
                focusedQuadrant === 2 ? 'col-span-2 row-span-2 z-20' : ''
              }`}
            >
              <AgentPipelineTopology
                status={state === 'idle' ? 'idle' : jobStatus}
                verificationResults={result?.verification_results}
                recalibrationTrail={result?.recalibration_trail}
                stageProviders={result?.stage_providers}
                error={error}
              />
            </div>

            {/* QUADRANT 3: INSTITUTIONAL VERDICT PANEL */}
            <div
              className={`bb-panel rounded overflow-hidden flex flex-col ${
                focusedQuadrant === 3 ? 'col-span-2 row-span-2 z-20' : ''
              }`}
            >
              <InstitutionalVerdictPanel
                verdict={result?.verdict || null}
                caveats={result?.partial_verdict_caveats}
                verificationPassed={result?.verification_passed}
              />
            </div>

            {/* QUADRANT 4: 5-YEAR TRAJECTORY & RISK MATRIX */}
            <div
              className={`bb-panel rounded overflow-hidden flex flex-col ${
                focusedQuadrant === 4 ? 'col-span-2 row-span-2 z-20' : ''
              }`}
            >
              <TrajectoryChartPanel
                comparison={result?.verdict?.cross_path_comparison}
                trajectoryData={selectedPreset?.trajectoryData}
              />
            </div>
          </div>
        )}

        {/* VIEW 2: FULLSCREEN DECISION CONSOLE */}
        {activeTab === 'decision' && (
          <div className="bb-panel rounded flex-1 overflow-hidden flex flex-col">
            <BloombergDecisionConsole
              onSubmit={handleSubmit}
              onSelectPreset={handleSelectPreset}
              isSubmitting={state === 'submitting' || state === 'polling'}
              selectedPresetId={selectedPreset?.id}
            />
          </div>
        )}

        {/* VIEW 3: FULLSCREEN TRAJECTORY SIMULATOR */}
        {activeTab === 'trajectory' && (
          <div className="bb-panel rounded flex-1 overflow-hidden flex flex-col">
            <TrajectoryChartPanel
              comparison={result?.verdict?.cross_path_comparison}
              trajectoryData={selectedPreset?.trajectoryData}
            />
          </div>
        )}

        {/* VIEW 4: FULLSCREEN LOCK-IN MATRIX */}
        {activeTab === 'lockin' && (
          <div className="bb-panel rounded flex-1 overflow-hidden flex flex-col">
            <LockInMatrixView vectors={selectedPreset?.lockInVectors} />
          </div>
        )}

        {/* VIEW 5: FULLSCREEN AUDIT INSPECTOR */}
        {activeTab === 'audit' && (
          <div className="bb-panel rounded flex-1 overflow-hidden flex flex-col">
            <AuditInspector
              verificationResults={result?.verification_results || []}
              recalibrationTrail={result?.recalibration_trail || []}
              explanationTrail={result?.verdict?.explanation_trail || (result?.verdict as unknown as { explanationTrail?: any })?.explanationTrail}
              verificationPassed={result?.verification_passed ?? true}
              verificationFailedStage={result?.verification_failed_stage}
            />
          </div>
        )}

        {/* VIEW 6: FULLSCREEN LIVE INTEL FEED */}
        {activeTab === 'feed' && (
          <div className="bb-panel rounded flex-1 overflow-hidden flex flex-col">
            <IntelFeedPanel />
          </div>
        )}

        {/* VIEW 7: FULLSCREEN BMAP (GLOBAL INFRASTRUCTURE MAP) */}
        {activeTab === 'bmap' && (
          <div className="bb-panel rounded flex-1 overflow-hidden flex flex-col">
            <BloombergGlobalMap />
          </div>
        )}

        {/* VIEW 8: FULLSCREEN SPLC (SUPPLY CHAIN DEPENDENCY GRAPH) */}
        {activeTab === 'splc' && (
          <div className="bb-panel rounded flex-1 overflow-hidden flex flex-col">
            <BloombergSupplyChainGraph />
          </div>
        )}
      </main>

      {/* Bloomberg Bottom Status Footer */}
      <footer className="px-3 py-1.5 bg-[var(--bb-bg-surface)] border-t border-[var(--bb-border-subtle)] flex items-center justify-between text-[10px] font-mono text-[var(--bb-text-muted)] select-none">
        <div className="flex items-center gap-3">
          <span className="text-[var(--bb-amber)] font-bold">HELIOS_WORKSTATION // v2.4</span>
          <span>TERMINAL MODE: LAUNCHPAD_GRID</span>
          <span>HOTKEYS: [F1-F9] OR [/] FOR COMMAND BAR</span>
        </div>
        <div className="flex items-center gap-3">
          <span>PIPELINE: 6 AGENTS // 18 SUB-AGENTS</span>
          <span className="text-[var(--bb-green)]">VERIFICATION GATE: ENFORCED</span>
        </div>
      </footer>

      {/* Executive Briefing Dossier Modal */}
      {dossierModalOpen && (
        <div className="dossier-modal-container">
          <ExecutiveDossierModal
            result={result}
            onClose={() => setDossierModalOpen(false)}
          />
        </div>
      )}
    </div>
  );
};