import React, { useState, useCallback, useRef, useEffect } from 'react';
import confetti from 'canvas-confetti';
import { Maximize2, Minimize2, ShieldCheck } from 'lucide-react';
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
import { CommandPaletteModal, type TerminalTheme } from '../components/CommandPaletteModal';
import { ScenarioComparatorModal } from '../components/ScenarioComparatorModal';
import { DeveloperConsoleModal } from '../components/DeveloperConsoleModal';
import { GuidedDecisionWizardModal } from '../components/GuidedDecisionWizardModal';
import { ToastProvider, useToast } from '../components/TerminalToast';
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

const DashboardView: React.FC = () => {
  const { showToast } = useToast();
  const [activeTab, setActiveTab] = useState<ActiveWorkstationTab>('quadrant');
  const [state, setState] = useState<WorkstationState>('completed');
  const [jobStatus, setJobStatus] = useState<JobStatusResponse['status']>('completed');
  const [selectedPreset, setSelectedPreset] = useState<PresetScenario>(PRESET_SCENARIOS[0]);
  const [result, setResult] = useState<DecisionResponse | null>(PRESET_SCENARIOS[0].result);
  const [currentBrief, setCurrentBrief] = useState<DecisionRequest>(PRESET_SCENARIOS[0].brief);
  const [error, setError] = useState<string | null>(null);
  const [isLiveServerConnected, setIsLiveServerConnected] = useState<boolean>(true);
  const [dossierModalOpen, setDossierModalOpen] = useState<boolean>(false);
  const [paletteModalOpen, setPaletteModalOpen] = useState<boolean>(false);
  const [comparatorModalOpen, setComparatorModalOpen] = useState<boolean>(false);
  const [wizardModalOpen, setWizardModalOpen] = useState<boolean>(false);
  const [devConsoleModalOpen, setDevConsoleModalOpen] = useState<boolean>(false);
  const [focusedQuadrant, setFocusedQuadrant] = useState<number | null>(null);

  const [theme, setTheme] = useState<TerminalTheme>(() => {
    return (localStorage.getItem('helios_terminal_theme') as TerminalTheme) || 'amber';
  });

  const pollTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Apply theme to document element
  useEffect(() => {
    document.documentElement.setAttribute('data-terminal-theme', theme);
    localStorage.setItem('helios_terminal_theme', theme);
  }, [theme]);

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

  const triggerCelebration = useCallback(() => {
    try {
      confetti({
        particleCount: 55,
        spread: 60,
        origin: { y: 0.8 },
        colors: ['#FF9E00', '#00FF66', '#00E5FF', '#FFD700'],
      });
    } catch {
      // ignore on environments where canvas isn't supported
    }
  }, []);

  const startPolling = useCallback(
    (jobId: string) => {
      if (pollTimerRef.current) clearInterval(pollTimerRef.current);

      pollTimerRef.current = setInterval(async () => {
        try {
          const status = await pollJobStatus(jobId);
          setIsLiveServerConnected(true);
          setJobStatus(status.status);

          if (status.status === 'completed') {
            if (pollTimerRef.current) clearInterval(pollTimerRef.current);
            setResult(status.result);
            setState('completed');
            terminalAudio.playSuccessChime();
            triggerCelebration();
            showToast('success', 'VERDICT SYNTHESIZED', '6-Agent pipeline verified claim grounding');
          } else if (status.status === 'failed') {
            if (pollTimerRef.current) clearInterval(pollTimerRef.current);
            const errText = status.error || 'Pipeline execution encountered a fatal verification exception.';
            setError(errText);
            setState('failed');
            terminalAudio.playWarning();
            showToast('error', 'PIPELINE FAILED', errText);
          }
        } catch (err) {
          console.error('Polling error:', err);
        }
      }, POLL_INTERVAL_MS);
    },
    [showToast, triggerCelebration]
  );

  const handleSubmit = useCallback(
    async (brief: DecisionRequest) => {
      setCurrentBrief(brief);
      setState('submitting');
      setError(null);
      setResult(null);
      terminalAudio.playGoCommand();
      showToast('info', 'DECISION SUBMITTED', `Evaluating ${brief.entity} (${brief.options.length} paths)`);

      try {
        const job = await submitDecision(brief);
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
          setIsLiveServerConnected(false);
          console.warn('Backend genuinely unreachable, triggering offline synthesis fallback:', err);
          showToast('warning', 'CLIENT SYNTHESIS MODE', 'Backend unreachable. Running client verification engine.');
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
            triggerCelebration();
            showToast('success', 'CLIENT VERDICT READY', `Synthesized recommendation for ${brief.entity}`);
          }, 1200);
        } else {
          setIsLiveServerConnected(true);
          console.error('Backend API error during submission:', err);
          setError(errorMsg || 'Pipeline execution failed on backend.');
          setState('failed');
          setJobStatus('failed');
          terminalAudio.playWarning();
          showToast('error', 'EXECUTION ERROR', errorMsg);
        }
      }
    },
    [startPolling, showToast, triggerCelebration]
  );

  const handleSelectPreset = (preset: PresetScenario) => {
    setSelectedPreset(preset);
    setCurrentBrief(preset.brief);
    setResult(preset.result);
    setState('completed');
    setJobStatus('completed');
    setError(null);
    showToast('info', 'PRESET LOADED', `${preset.code}: ${preset.brief.entity}`);
  };

  const handleExecuteCommand = (cmd: string) => {
    const trimmed = cmd.trim().toUpperCase();

    if (trimmed === 'EVAL' || trimmed === 'RUN' || trimmed === 'F2') {
      setActiveTab('decision');
      showToast('info', 'VIEW: DECISION CONSOLE');
    } else if (trimmed === 'QUAD' || trimmed === 'GRID' || trimmed === 'F1') {
      setActiveTab('quadrant');
      setFocusedQuadrant(null);
      showToast('info', 'VIEW: 4-QUADRANT GRID');
    } else if (trimmed === 'TRAJ' || trimmed === 'CHART' || trimmed === 'F3') {
      setActiveTab('trajectory');
      showToast('info', 'VIEW: TRAJECTORY SIMULATOR');
    } else if (trimmed === 'LOCKIN' || trimmed === 'MATRIX' || trimmed === 'F4') {
      setActiveTab('lockin');
      showToast('info', 'VIEW: LOCK-IN MATRIX');
    } else if (trimmed === 'AUDIT' || trimmed === 'VERIFY' || trimmed === 'F5') {
      setActiveTab('audit');
      showToast('info', 'VIEW: AUDIT INSPECTOR');
    } else if (trimmed === 'FEED' || trimmed === 'STREAM' || trimmed === 'F6') {
      setActiveTab('feed');
      showToast('info', 'VIEW: INTEL STREAM');
    } else if (trimmed === 'DOSSIER' || trimmed === 'PRINT' || trimmed === 'F7') {
      setDossierModalOpen(true);
    } else if (trimmed === 'BMAP' || trimmed === 'MAP' || trimmed === 'INFRA' || trimmed === 'F8') {
      setActiveTab('bmap');
      showToast('info', 'VIEW: BMAP INFRASTRUCTURE');
    } else if (trimmed === 'SPLC' || trimmed === 'CHAIN' || trimmed === 'SUPPLY' || trimmed === 'F9') {
      setActiveTab('splc');
      showToast('info', 'VIEW: SPLC SUPPLY CHAIN');
    } else if (trimmed === 'COMPARE' || trimmed === 'DIFF') {
      setComparatorModalOpen(true);
    } else if (trimmed === 'WIZARD' || trimmed === 'GUIDE') {
      setWizardModalOpen(true);
    } else if (trimmed === 'DEV' || trimmed === 'API' || trimmed === 'CURL' || trimmed === 'CODE') {
      setDevConsoleModalOpen(true);
    } else if (trimmed === 'PALETTE' || trimmed === 'HOTKEYS' || trimmed === 'HELP') {
      setPaletteModalOpen(true);
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
      showToast('warning', 'STATE CLEARED', 'Active decision brief reset to clean slate');
    } else {
      setPaletteModalOpen(true);
    }
  };

  const toggleQuadrantFocus = (quadrantNumber: number) => {
    terminalAudio.playBlip();
    setFocusedQuadrant((prev) => (prev === quadrantNumber ? null : quadrantNumber));
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
        onOpenCommandPalette={() => setPaletteModalOpen(true)}
        onOpenComparator={() => setComparatorModalOpen(true)}
        onOpenWizard={() => setWizardModalOpen(true)}
        onOpenDevConsole={() => setDevConsoleModalOpen(true)}
      />

      {/* Main Workstation Viewport */}
      <main className="flex-1 p-2 overflow-hidden flex flex-col min-h-0">
        {/* VIEW 1: 4-QUADRANT LAUNCHPAD WORKSPACE */}
        {activeTab === 'quadrant' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 grid-rows-2 gap-2 flex-1 min-h-0">
            {/* QUADRANT 1: DECISION EXECUTION CONSOLE */}
            <div
              className={`bb-panel rounded overflow-hidden flex flex-col relative transition-all ${
                focusedQuadrant === 1
                  ? 'col-span-2 row-span-2 z-20 shadow-2xl border-[var(--bb-amber)]'
                  : focusedQuadrant !== null
                  ? 'hidden'
                  : ''
              }`}
            >
              <button
                type="button"
                onClick={() => toggleQuadrantFocus(1)}
                className="absolute right-2 top-2 z-10 p-1 text-[var(--bb-text-muted)] hover:text-[var(--bb-amber)] bg-[var(--bb-bg-surface)] border border-[var(--bb-border-subtle)] rounded transition-colors"
                title={focusedQuadrant === 1 ? 'Restore 4-Quadrant View' : 'Maximize Quadrant 1'}
              >
                {focusedQuadrant === 1 ? <Minimize2 className="w-3.5 h-3.5" /> : <Maximize2 className="w-3.5 h-3.5" />}
              </button>
              <BloombergDecisionConsole
                onSubmit={handleSubmit}
                onSelectPreset={handleSelectPreset}
                isSubmitting={state === 'submitting' || state === 'polling'}
                selectedPresetId={selectedPreset?.id}
                onOpenWizard={() => setWizardModalOpen(true)}
                onOpenDevConsole={() => setDevConsoleModalOpen(true)}
              />
            </div>

            {/* QUADRANT 2: 6-STAGE AGENT PIPELINE TOPOLOGY */}
            <div
              className={`bb-panel rounded overflow-hidden flex flex-col relative transition-all ${
                focusedQuadrant === 2
                  ? 'col-span-2 row-span-2 z-20 shadow-2xl border-[var(--bb-cyan)]'
                  : focusedQuadrant !== null
                  ? 'hidden'
                  : ''
              }`}
            >
              <button
                type="button"
                onClick={() => toggleQuadrantFocus(2)}
                className="absolute right-2 top-2 z-10 p-1 text-[var(--bb-text-muted)] hover:text-[var(--bb-cyan)] bg-[var(--bb-bg-surface)] border border-[var(--bb-border-subtle)] rounded transition-colors"
                title={focusedQuadrant === 2 ? 'Restore 4-Quadrant View' : 'Maximize Quadrant 2'}
              >
                {focusedQuadrant === 2 ? <Minimize2 className="w-3.5 h-3.5" /> : <Maximize2 className="w-3.5 h-3.5" />}
              </button>
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
              className={`bb-panel rounded overflow-hidden flex flex-col relative transition-all ${
                focusedQuadrant === 3
                  ? 'col-span-2 row-span-2 z-20 shadow-2xl border-[var(--bb-green)]'
                  : focusedQuadrant !== null
                  ? 'hidden'
                  : ''
              }`}
            >
              <button
                type="button"
                onClick={() => toggleQuadrantFocus(3)}
                className="absolute right-2 top-2 z-10 p-1 text-[var(--bb-text-muted)] hover:text-[var(--bb-green)] bg-[var(--bb-bg-surface)] border border-[var(--bb-border-subtle)] rounded transition-colors"
                title={focusedQuadrant === 3 ? 'Restore 4-Quadrant View' : 'Maximize Quadrant 3'}
              >
                {focusedQuadrant === 3 ? <Minimize2 className="w-3.5 h-3.5" /> : <Maximize2 className="w-3.5 h-3.5" />}
              </button>
              <InstitutionalVerdictPanel
                verdict={result?.verdict || null}
                caveats={result?.partial_verdict_caveats}
                verificationPassed={result?.verification_passed}
              />
            </div>

            {/* QUADRANT 4: 5-YEAR TRAJECTORY & RISK MATRIX */}
            <div
              className={`bb-panel rounded overflow-hidden flex flex-col relative transition-all ${
                focusedQuadrant === 4
                  ? 'col-span-2 row-span-2 z-20 shadow-2xl border-[var(--bb-amber)]'
                  : focusedQuadrant !== null
                  ? 'hidden'
                  : ''
              }`}
            >
              <button
                type="button"
                onClick={() => toggleQuadrantFocus(4)}
                className="absolute right-2 top-2 z-10 p-1 text-[var(--bb-text-muted)] hover:text-[var(--bb-amber)] bg-[var(--bb-bg-surface)] border border-[var(--bb-border-subtle)] rounded transition-colors"
                title={focusedQuadrant === 4 ? 'Restore 4-Quadrant View' : 'Maximize Quadrant 4'}
              >
                {focusedQuadrant === 4 ? <Minimize2 className="w-3.5 h-3.5" /> : <Maximize2 className="w-3.5 h-3.5" />}
              </button>
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
              onOpenWizard={() => setWizardModalOpen(true)}
              onOpenDevConsole={() => setDevConsoleModalOpen(true)}
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
          <span>TERMINAL MODE: {activeTab.toUpperCase()}</span>
          <span>HOTKEYS: [F1-F9] | [⌘K / ?] COMMAND PALETTE</span>
        </div>
        <div className="flex items-center gap-3">
          <span>THEME: {theme.toUpperCase()}</span>
          <span className="text-[var(--bb-border-mid)]">|</span>
          <span>PIPELINE: 6 AGENTS // 18 SUB-AGENTS</span>
          <span className="text-[var(--bb-green)] flex items-center gap-1">
            <ShieldCheck className="w-3 h-3" /> VERIFICATION GATE: ENFORCED
          </span>
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

      {/* Command Palette & Hotkeys Modal */}
      <CommandPaletteModal
        isOpen={paletteModalOpen}
        onClose={() => setPaletteModalOpen(false)}
        onExecuteCommand={handleExecuteCommand}
        onSelectPreset={handleSelectPreset}
        currentTheme={theme}
        onSelectTheme={(newTheme) => setTheme(newTheme)}
      />

      {/* Cross-Scenario Comparator Diff Modal */}
      <ScenarioComparatorModal
        currentResult={result}
        isOpen={comparatorModalOpen}
        onClose={() => setComparatorModalOpen(false)}
      />

      {/* Developer Workbench Modal */}
      <DeveloperConsoleModal
        isOpen={devConsoleModalOpen}
        onClose={() => setDevConsoleModalOpen(false)}
        activeBrief={currentBrief}
        currentResult={result}
        onSubmitJson={handleSubmit}
      />

      {/* Guided Decision Wizard Modal */}
      <GuidedDecisionWizardModal
        isOpen={wizardModalOpen}
        onClose={() => setWizardModalOpen(false)}
        onLaunchBrief={handleSubmit}
      />
    </div>
  );
};

export const Dashboard: React.FC = () => {
  return (
    <ToastProvider>
      <DashboardView />
    </ToastProvider>
  );
};