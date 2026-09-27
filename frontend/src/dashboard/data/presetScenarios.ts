import type { DecisionResponse, DecisionRequest } from '../api';

export interface PresetScenario {
  id: string;
  code: string;
  title: string;
  category: 'DEFENSE' | 'FINTECH' | 'HEALTHCARE' | 'AUTONOMOUS' | 'ENTERPRISE';
  description: string;
  brief: DecisionRequest;
  result: DecisionResponse;
  trajectoryData: {
    year: string;
    buildTco: number;
    buyTco: number;
    outsourceTco: number;
    buildLockIn: number;
    buyLockIn: number;
    outsourceLockIn: number;
  }[];
  lockInVectors: {
    dimension: string;
    buildScore: number;
    buyScore: number;
    outsourceScore: number;
    criticalNotes: string;
  }[];
}

export const PRESET_SCENARIOS: PresetScenario[] = [
  {
    id: 'defense-tactical-slm',
    code: 'DEF-SLM',
    title: 'Indian Army Signals Division // Tactical Edge SLM',
    category: 'DEFENSE',
    description: 'Sovereign edge language model for offline battlefield reconnaissance & low-bandwidth radio telemetry decoding.',
    brief: {
      entity: 'Indian Army Signals Directorate',
      capability: 'Tactical Small Language Model for Edge Comms & SIGINT',
      options: ['Self-hosted Fine-tuned Open Weights (Llama 3.3 / Sarvam)', 'Licensed Closed-Weights via Sovereign Cloud', 'Outsourced Defense System Integrator Turnkey SLM'],
      data_sovereignty_weight: 'CRITICAL',
      latency_tolerance: 'SUB_20MS',
    },
    trajectoryData: [
      { year: 'Y0 (Deploy)', buildTco: 420, buyTco: 180, outsourceTco: 250, buildLockIn: 1.5, buyLockIn: 4.8, outsourceLockIn: 6.2 },
      { year: 'Y1', buildTco: 510, buyTco: 320, outsourceTco: 410, buildLockIn: 1.8, buyLockIn: 5.9, outsourceLockIn: 7.0 },
      { year: 'Y2', buildTco: 580, buyTco: 490, outsourceTco: 620, buildLockIn: 2.1, buyLockIn: 6.8, outsourceLockIn: 7.9 },
      { year: 'Y3', buildTco: 640, buyTco: 710, outsourceTco: 880, buildLockIn: 2.4, buyLockIn: 7.9, outsourceLockIn: 8.8 },
      { year: 'Y4', buildTco: 690, buyTco: 940, outsourceTco: 1180, buildLockIn: 2.5, buyLockIn: 8.5, outsourceLockIn: 9.3 },
      { year: 'Y5 (EOL)', buildTco: 730, buyTco: 1220, outsourceTco: 1540, buildLockIn: 2.6, buyLockIn: 9.1, outsourceLockIn: 9.7 },
    ],
    lockInVectors: [
      { dimension: 'Data Sovereignty & Air-Gap Compliance', buildScore: 1.2, buyScore: 7.8, outsourceScore: 8.9, criticalNotes: 'Closed APIs cannot operate in Level-5 Air-Gapped Forward Operating Bases.' },
      { dimension: 'Model Weights Portability & Modularity', buildScore: 1.5, buyScore: 8.4, outsourceScore: 9.2, criticalNotes: 'Proprietary runtime bindings prevent migration to indigenously designed NPU accelerators.' },
      { dimension: 'Export Control & BIS Sanction Exposure', buildScore: 2.0, buyScore: 8.9, outsourceScore: 6.5, criticalNotes: 'Foreign vendor license revocations create sudden operational blackout risk.' },
      { dimension: 'Long-term Inference TCO & Scalability', buildScore: 3.4, buyScore: 7.5, outsourceScore: 8.8, criticalNotes: 'Self-hosted quantized 8B models achieve $0.008/hour fixed edge compute cost.' },
      { dimension: 'Talent & Internal Engineering Ownership', buildScore: 6.2, buyScore: 3.1, outsourceScore: 2.0, criticalNotes: 'Self-hosted requires maintaining specialized in-house MLSecOps cadre.' },
    ],
    result: {
      entity: 'Indian Army Signals Directorate',
      capability: 'Tactical Small Language Model for Edge Comms & SIGINT',
      options: ['Self-hosted Fine-tuned Open Weights (Llama 3.3 / Sarvam)', 'Licensed Closed-Weights via Sovereign Cloud', 'Outsourced Defense System Integrator Turnkey SLM'],
      verification_passed: true,
      verification_failed_stage: null,
      partial_verdict_caveats: [
        'Hardware availability: Assumes access to indigenous or non-restricted edge accelerators (e.g. NVIDIA Jetson AGX Orin / Tenstorrent).',
        'Model licensing: Verify open-weights redistribution clauses for defense deployment under specific permissive licenses (Apache 2.0 or custom sovereign weights).',
      ],
      verdict: {
        entity: 'Indian Army Signals Directorate',
        capability: 'Tactical Small Language Model for Edge Comms & SIGINT',
        recommended_path: 'Self-hosted Fine-tuned Open Weights (Llama 3.3 / Sarvam)',
        verdict_summary: 'Self-hosting fine-tuned open-weights models yields an 84% reduction in existential dependency risk and full air-gap compliance. While initial infrastructure capital expenditure is 2.3x higher than closed APIs in Year 0, cumulative 5-year TCO amortizes to 42% lower cost with zero exposure to foreign export control revocations.',
        key_recommendations: [
          'Standardize on GGUF / AWQ 4-bit quantization pipelines to allow deployment across tactical edge radio nodes.',
          'Establish a dedicated Sovereign Fine-Tuning Lab at Mhow to decouple from third-party vendor training pipelines.',
          'Implement an internal air-gapped Hugging Face artifact repository mirrored from verified cryptographic hashes.',
          'Mandate fallback rule-based NLP parsers for tactical communications if edge compute encounters thermal throttling.',
        ],
        path_stances: {
          'Self-hosted Fine-tuned Open Weights': 'STRONGLY RECOMMENDED — Optimal sovereign risk profile with zero foreign telemetry egress.',
          'Licensed Closed-Weights via Sovereign Cloud': 'HIGH RISK — Vulnerable to periodic license validation failure during electronic warfare blackouts.',
          'Outsourced Defense System Integrator': 'CRITICAL LOCK-IN — Creates proprietary runtime dependency and exorbitant recurring SLA maintenance costs.',
        },
        cross_path_comparison: {
          comparative_narrative: 'The sourcing matrix reveals a severe divergence in sovereign operational capability. Closed-weights models introduce non-negotiable telemetry risks and dependency on cloud relay nodes. The open-weights strategy requires front-loading engineering talent but insulates national defense infrastructure permanently.',
          path_comparisons: [
            {
              scenario_name: 'Self-hosted Fine-tuned Open Weights',
              lock_in_count: 1,
              max_severity_score: 2.6,
              key_tradeoffs: ['Requires in-house MLSecOps team', 'Lower recurring token fee', 'Total air-gap execution'],
              path_summary: 'Full control over weights, activations, and fine-tuning pipelines on tactical edge hardware.',
            },
            {
              scenario_name: 'Licensed Closed-Weights via Sovereign Cloud',
              lock_in_count: 4,
              max_severity_score: 8.5,
              key_tradeoffs: ['Fast 2-week time-to-market', 'Foreign API telemetry risk', 'Escalating monthly license fees'],
              path_summary: 'Convenient deployment but exposes command nodes to vendor license terms and sudden price hikes.',
            },
            {
              scenario_name: 'Outsourced Defense System Integrator Turnkey SLM',
              lock_in_count: 5,
              max_severity_score: 9.3,
              key_tradeoffs: ['Single throat to choke', 'Proprietary black-box container', 'Massive migration barrier in Y3'],
              path_summary: 'Total reliance on external contractor for model updates, security patches, and inference adaptations.',
            },
          ],
        },
        explanation_trail: {
          summary: 'Cross-agent verification grounded 14 empirical claims against BIS Entity Lists, Hugging Face Hub open-weight licenses, and defense edge compute benchmarks.',
          sources: [
            'https://huggingface.co/sarvamai/sarvam-2b',
            'https://www.bis.doc.gov/index.php/regulations/export-administration-regulations-ear',
            'https://github.com/ggerganov/llama.cpp (Air-Gapped Edge Inference Benchmarks)',
            'DoD AI Autonomy Strategy Directive 3000.09 (Sovereignty Verification Standards)',
          ],
          steps: [
            { stage: 'Ingestion', claim: 'Sarvam and Llama-3.3 8B provide fully permissible weights for local on-premise execution.', evidence: 'Retrieved Hugging Face Hub model card license metadata and verified Apache 2.0 / Llama-3.3 community grant terms.' },
            { stage: 'Stack-Mapping', claim: 'Inference runtime is decoupled from proprietary CUDA libraries via GGML/VLLM open runtimes.', evidence: 'Stack layer analysis confirms compilation path to ROCm, Metal, and indigenously fabricated RISC-V edge modules.' },
            { stage: 'Scenario-Generation', claim: 'Three canonical sourcing paths identified with distinct sovereignty boundaries.', evidence: 'Enumerated self-hosted, sovereign private cloud proxy, and turnkey defense contractor wrapper.' },
            { stage: 'Outcome-Prediction', claim: '5-year TCO for closed vendor models scales linearly with token volume whereas self-hosted costs flatten.', evidence: 'Extrapolated tactical comms volume (1.2M packets/day) against cloud provider token pricing vs amortized node power.' },
            { stage: 'Dependency-Diagnosis', claim: 'Vendor lock-in score for outsourced turnkey solution reaches critical 9.3/10 severity.', evidence: 'Identified proprietary serialization format that prevents fine-tuning dataset export without vendor assistance.' },
            { stage: 'Orchestrator', claim: 'Self-hosted approach is the only viable path satisfying Indian Defense Air-Gap standards.', evidence: 'Synthesis verified against Stage 1-5 grounded audit evidence with zero unverified claims.' },
          ],
        },
      },
      stage_providers: {
        ingestion: 'nvidia_nim',
        stack_mapping: 'nvidia_nim',
        scenario_generation: 'openrouter',
        outcome_prediction: 'gemini',
        dependency_diagnosis: 'gemini',
        orchestrator: 'deepseek_direct',
      },
      verification_results: [
        { passed: true, confidence: 0.98, agent_stage: 'Ingestion', claim: 'Model open weights available for air-gap distribution', reason: 'Verified against Hugging Face repository hashes and license manifests.', provider: 'nvidia_nim' },
        { passed: true, confidence: 0.95, agent_stage: 'Stack-Mapping', claim: 'Inference runtime independent of foreign cloud APIs', reason: 'Architecture isolates edge tensor engine to local hardware memory.', provider: 'nvidia_nim' },
        { passed: true, confidence: 0.92, agent_stage: 'Outcome-Prediction', claim: 'Self-hosted TCO breaks even with API licenses by Month 14', reason: 'Financial modeling validated against 8B edge node hardware amortization.', provider: 'gemini' },
        { passed: true, confidence: 0.96, agent_stage: 'Dependency-Diagnosis', claim: 'Outsource solution creates proprietary lock-in at data serialization layer', reason: 'Verified against vendor container contract terms and API schema specs.', provider: 'gemini' },
      ],
      recalibration_trail: [],
    },
  },
  {
    id: 'fintech-tier1-rag',
    code: 'FIN-RAG',
    title: 'Tier-1 Investment Bank // Quantitative Wealth Advisory RAG',
    category: 'FINTECH',
    description: 'Ultra-low latency Retrieval-Augmented Generation for algorithmic investment research and SEC/FINRA compliance.',
    brief: {
      entity: 'Global Tier-1 Investment Bank (AMR Capital)',
      capability: 'Regulatory-Compliant Financial Intelligence & Synthesis RAG',
      options: ['In-House Open-Source Vector Stack (Qdrant + Qwen-2.5-Coder)', 'Azure AI Foundry Private VNet Managed Service', 'Third-Party Financial AI SaaS (Bloomberg/FactSet Copilot)'],
      data_sovereignty_weight: 'STANDARD',
      latency_tolerance: 'BALANCED',
    },
    trajectoryData: [
      { year: 'Y0 (Deploy)', buildTco: 680, buyTco: 340, outsourceTco: 290, buildLockIn: 1.8, buyLockIn: 5.2, outsourceLockIn: 6.8 },
      { year: 'Y1', buildTco: 820, buyTco: 610, outsourceTco: 580, buildLockIn: 2.2, buyLockIn: 6.1, outsourceLockIn: 7.6 },
      { year: 'Y2', buildTco: 940, buyTco: 920, outsourceTco: 940, buildLockIn: 2.5, buyLockIn: 6.9, outsourceLockIn: 8.4 },
      { year: 'Y3', buildTco: 1040, buyTco: 1290, outsourceTco: 1380, buildLockIn: 2.8, buyLockIn: 7.7, outsourceLockIn: 9.1 },
      { year: 'Y4', buildTco: 1120, buyTco: 1710, outsourceTco: 1890, buildLockIn: 3.0, buyLockIn: 8.3, outsourceLockIn: 9.5 },
      { year: 'Y5 (EOL)', buildTco: 1190, buyTco: 2180, outsourceTco: 2460, buildLockIn: 3.1, buyLockIn: 8.8, outsourceLockIn: 9.8 },
    ],
    lockInVectors: [
      { dimension: 'Data Privacy & PII / MNPI Leakage Risk', buildScore: 1.4, buyScore: 4.2, outsourceScore: 8.1, criticalNotes: 'Material Non-Public Information (MNPI) must never enter shared cloud training pools.' },
      { dimension: 'Vector DB & Embedding Migration Friction', buildScore: 2.0, buyScore: 6.8, outsourceScore: 8.9, criticalNotes: 'Proprietary embeddings lock millions of financial filings into a single vendor representation space.' },
      { dimension: 'FINRA / SEC Rule 17a-4 Auditability', buildScore: 1.8, buyScore: 5.5, outsourceScore: 7.8, criticalNotes: 'In-house log stores provide immutable cryptographically signed audit logs.' },
      { dimension: 'Latency & Co-location with Order Books', buildScore: 1.2, buyScore: 6.5, outsourceScore: 9.0, criticalNotes: 'In-house stack achieves 8.4ms p99 retrieval latency vs 180ms cloud WAN roundtrip.' },
      { dimension: 'Ongoing Maintenance & SRE Burden', buildScore: 7.4, buyScore: 3.8, outsourceScore: 1.8, criticalNotes: 'Requires dedicated enterprise SRE and high-availability vector cluster maintainers.' },
    ],
    result: {
      entity: 'Global Tier-1 Investment Bank (AMR Capital)',
      capability: 'Regulatory-Compliant Financial Intelligence & Synthesis RAG',
      options: ['In-House Open-Source Vector Stack (Qdrant + Qwen-2.5-Coder)', 'Azure AI Foundry Private VNet Managed Service', 'Third-Party Financial AI SaaS (Bloomberg/FactSet Copilot)'],
      verification_passed: true,
      verification_failed_stage: null,
      partial_verdict_caveats: [
        'Requires continuous index compaction and vector database backup governance to meet SEC Rule 17a-4 retention mandates.',
      ],
      verdict: {
        entity: 'Global Tier-1 Investment Bank (AMR Capital)',
        capability: 'Regulatory-Compliant Financial Intelligence & Synthesis RAG',
        recommended_path: 'In-House Open-Source Vector Stack (Qdrant + Qwen-2.5-Coder)',
        verdict_summary: 'Adopting an in-house open-source vector and embedding stack eliminates catastrophic MNPI confidentiality risks while granting complete control over sub-10ms query latency. Cloud managed services present deceptive initial ease but build severe embedding lock-in.',
        key_recommendations: [
          'Deploy self-hosted Qdrant vector cluster behind strict TLS mTLS with role-based access control.',
          'Standardize embedding representations on open BGE-M3 to avoid vendor-locked dimensional embeddings.',
          'Implement automated immutable audit trail shipping directly to WORM-compliant storage.',
        ],
        path_stances: {
          'In-House Open-Source Vector Stack': 'RECOMMENDED — Zero data leakage risk, sub-10ms retrieval, permanent sovereign IP.',
          'Azure AI Foundry Private VNet': 'MODERATE RISK — Acceptable compliance boundary but high vendor egress and embedding lock-in.',
          'Third-Party Financial AI SaaS': 'UNACCEPTABLE — Severe MNPI contamination risk and vendor pricing extortion in Year 2+.',
        },
        cross_path_comparison: {
          comparative_narrative: 'Data gravity in quantitative finance is absolute. Moving 50 million proprietary research reports and trade memos into a proprietary vendor cloud creates an irreversible lock-in. The in-house open vector stack safeguards institutional alpha.',
          path_comparisons: [
            {
              scenario_name: 'In-House Open-Source Vector Stack',
              lock_in_count: 1,
              max_severity_score: 3.1,
              key_tradeoffs: ['Requires Kubernetes vector SREs', 'Zero third-party data egress', 'Sub-10ms latency'],
              path_summary: 'Full control over vector indices, chunking strategies, and private embedding generation.',
            },
            {
              scenario_name: 'Azure AI Foundry Private VNet Managed Service',
              lock_in_count: 3,
              max_severity_score: 7.7,
              key_tradeoffs: ['Fast enterprise provisioning', 'Proprietary index schema lock-in', 'Cloud API rate limits'],
              path_summary: 'Enterprise SLA support but locks embeddings to Azure proprietary models.',
            },
            {
              scenario_name: 'Third-Party Financial AI SaaS',
              lock_in_count: 5,
              max_severity_score: 9.5,
              key_tradeoffs: ['Zero infra maintenance', 'Extreme MNPI exposure risk', 'Exorbitant per-seat fees ($2,400/user/mo)'],
              path_summary: 'Outsources critical advisory core to black-box vendor with zero exportability of derived weights.',
            },
          ],
        },
        explanation_trail: {
          summary: 'Verified against FINRA Regulatory Notice 24-09, SEC WORM storage standards, and sub-millisecond retrieval benchmarks.',
          sources: [
            'https://www.finra.org/rules-guidance/notices/24-09 (FINRA Artificial Intelligence Guidance)',
            'https://qdrant.tech/benchmarks/ (HNSW Sub-10ms Scale Benchmarks)',
            'SEC Rule 17a-4 Electronic Records Compliance Specification',
          ],
          steps: [
            { stage: 'Ingestion', claim: 'FINRA requires complete reproducibility and auditability of LLM responses in advisory workflows.', evidence: 'Retrieved FINRA Regulatory Notice 24-09 mandates for record-keeping and algorithmic explainability.' },
            { stage: 'Stack-Mapping', claim: 'Embedding layer represents primary vector of lock-in across financial RAG pipelines.', evidence: 'Identified proprietary dimensions (1536-dim vs 1024-dim open BGE) requiring full index recomputation if vendor switches.' },
            { stage: 'Outcome-Prediction', claim: 'Annual seat licensing for financial SaaS exceeds $1.8M/year for 250 quantitative analysts by Year 3.', evidence: 'Extrapolated standard institutional financial copilot pricing tiers.' },
          ],
        },
      },
      stage_providers: {
        ingestion: 'nvidia_nim',
        stack_mapping: 'nvidia_nim',
        scenario_generation: 'gemini',
        outcome_prediction: 'gemini',
        dependency_diagnosis: 'openrouter',
        orchestrator: 'deepseek_direct',
      },
      verification_results: [
        { passed: true, confidence: 0.97, agent_stage: 'Ingestion', claim: 'SEC compliance requirements validated', reason: 'Matched against statutory broker-dealer retention directives.', provider: 'nvidia_nim' },
        { passed: true, confidence: 0.94, agent_stage: 'Dependency-Diagnosis', claim: 'Embedding space vendor lock-in identified', reason: 'Mathematical incompatibility of disparate vector embeddings confirmed.', provider: 'openrouter' },
      ],
      recalibration_trail: [],
    },
  },
  {
    id: 'healthcare-clinical-copilot',
    code: 'MED-AI',
    title: 'Hospital Health Network // Clinical Diagnostic Copilot',
    category: 'HEALTHCARE',
    description: 'Real-time EHR summarization and differential diagnosis assistant compliant with HIPAA and EU MDR Class IIa.',
    brief: {
      entity: 'MetroHealth Regional Hospital System',
      capability: 'HIPAA-Compliant Real-Time Clinical Decision Support Copilot',
      options: ['Self-Hosted Med-PaLM / BioMistral on Dedicated GPU Clusters', 'HIPAA BAA Managed Cloud (AWS HealthLake + Claude)', 'Epic / Cerner Native Embedded AI Add-On Module'],
      data_sovereignty_weight: 'CRITICAL',
      latency_tolerance: 'SUB_20MS',
    },
    trajectoryData: [
      { year: 'Y0 (Deploy)', buildTco: 590, buyTco: 280, outsourceTco: 380, buildLockIn: 1.6, buyLockIn: 5.8, outsourceLockIn: 8.5 },
      { year: 'Y1', buildTco: 710, buyTco: 490, outsourceTco: 640, buildLockIn: 2.0, buyLockIn: 6.7, outsourceLockIn: 8.9 },
      { year: 'Y2', buildTco: 810, buyTco: 740, outsourceTco: 960, buildLockIn: 2.3, buyLockIn: 7.4, outsourceLockIn: 9.2 },
      { year: 'Y3', buildTco: 890, buyTco: 1040, outsourceTco: 1350, buildLockIn: 2.5, buyLockIn: 8.0, outsourceLockIn: 9.6 },
      { year: 'Y4', buildTco: 960, buyTco: 1380, outsourceTco: 1790, buildLockIn: 2.7, buyLockIn: 8.6, outsourceLockIn: 9.8 },
      { year: 'Y5 (EOL)', buildTco: 1020, buyTco: 1780, outsourceTco: 2290, buildLockIn: 2.8, buyLockIn: 9.0, outsourceLockIn: 9.9 },
    ],
    lockInVectors: [
      { dimension: 'HIPAA & Protected Health Information (PHI) Exposure', buildScore: 1.0, buyScore: 5.2, outsourceScore: 8.9, criticalNotes: 'Zero hospital patient data leaves on-premise datacenter boundary.' },
      { dimension: 'Clinical Liability & Hallucination Traceability', buildScore: 1.6, buyScore: 6.9, outsourceScore: 9.1, criticalNotes: 'Proprietary models cannot expose logit probabilities required for diagnostic verification.' },
      { dimension: 'EHR Vendor Integration Lock-In (Epic Cosmos)', buildScore: 3.2, buyScore: 6.0, outsourceScore: 9.8, criticalNotes: 'Epic native module locks health system into closed software ecosystem for 10+ years.' },
      { dimension: 'Clinical Protocol Customization Agility', buildScore: 1.5, buyScore: 7.1, outsourceScore: 8.7, criticalNotes: 'Hospital medical board can directly tune weights for local epidemiology.' },
      { dimension: 'Specialized Biomedical ML Talent Requirement', buildScore: 8.0, buyScore: 3.5, outsourceScore: 1.5, criticalNotes: 'Requires hiring clinical bioinformaticians and medical AI safety auditors.' },
    ],
    result: {
      entity: 'MetroHealth Regional Hospital System',
      capability: 'HIPAA-Compliant Real-Time Clinical Decision Support Copilot',
      options: ['Self-Hosted Med-PaLM / BioMistral on Dedicated GPU Clusters', 'HIPAA BAA Managed Cloud (AWS HealthLake + Claude)', 'Epic / Cerner Native Embedded AI Add-On Module'],
      verification_passed: true,
      verification_failed_stage: null,
      partial_verdict_caveats: [
        'Requires FDA SaMD (Software as a Medical Device) pre-market approval if used for primary autonomous diagnosis rather than clinician copilot advice.',
      ],
      verdict: {
        entity: 'MetroHealth Regional Hospital System',
        capability: 'HIPAA-Compliant Real-Time Clinical Decision Support Copilot',
        recommended_path: 'Self-Hosted Med-PaLM / BioMistral on Dedicated GPU Clusters',
        verdict_summary: 'Self-hosting open biomedical language models guarantees zero PHI leakage, satisfies strict hospital network isolation requirements, and allows logit-level auditability for clinical safety review boards.',
        key_recommendations: [
          'Deploy dual H100 SXM5 nodes in hospital private datacenter behind biometric access perimeter.',
          'Integrate with FHIR v4 API via open-source HAPI FHIR gateway with automated redaction of 18 HIPAA identifiers.',
          'Institute a human-in-the-loop physician sign-off step before any AI summary commits to patient chart.',
        ],
        path_stances: {
          'Self-Hosted BioMistral': 'RECOMMENDED — Absolute patient confidentiality, no vendor telemetry, full clinical logit access.',
          'HIPAA BAA Managed Cloud': 'CAUTION — BAA provides legal shield but cloud latency and terms changes remain risk points.',
          'Epic Native Add-On Module': 'CRITICAL LOCK-IN — Monopolistic EHR pricing escalation with zero portability to other hospital networks.',
        },
        cross_path_comparison: {
          comparative_narrative: 'Clinical AI decisions cannot tolerate opaque model changes. Cloud API vendors frequently update underlying model weights without notice, invalidating clinical trial validations. Self-hosting freezes model state for clinical consistency.',
          path_comparisons: [
            {
              scenario_name: 'Self-Hosted BioMistral on Dedicated GPU Clusters',
              lock_in_count: 1,
              max_severity_score: 2.8,
              key_tradeoffs: ['High initial hardware procurement', 'Zero PHI cloud exposure', 'Complete weight auditability'],
              path_summary: 'Fixed-weight clinical deployment with guaranteed deterministic diagnostic behavior.',
            },
            {
              scenario_name: 'HIPAA BAA Managed Cloud',
              lock_in_count: 3,
              max_severity_score: 8.0,
              key_tradeoffs: ['Fast implementation', 'Unannounced model drift risk', 'Escalating token costs'],
              path_summary: 'Relies on third-party cloud vendor BAA agreements with periodic re-certification.',
            },
            {
              scenario_name: 'Epic / Cerner Native Embedded AI Add-On',
              lock_in_count: 5,
              max_severity_score: 9.8,
              key_tradeoffs: ['Seamless EHR UI embedding', 'Monopoly vendor price hikes', 'Inability to switch EHR'],
              path_summary: 'Deep EHR lock-in creating long-term multimillion dollar license leverage against the hospital system.',
            },
          ],
        },
        explanation_trail: {
          summary: 'Verified against HHS HIPAA Enforcement Rule, FDA Digital Health Policy, and FHIR standard interoperability specifications.',
          sources: [
            'https://www.hhs.gov/hipaa/for-professionals/security/laws-regulations/index.html',
            'https://www.fda.gov/medical-devices/digital-health-center-excellence/software-medical-device-samd',
            'https://hl7.org/fhir/R4/ (Health Level Seven Fast Healthcare Interoperability Resources)',
          ],
          steps: [
            { stage: 'Ingestion', claim: 'HHS OCR enforces multimillion dollar penalties for unauthorized PHI transmission to third-party cloud APIs.', evidence: 'Retrieved enforcement actions against healthcare providers using non-isolated AI analytics.' },
            { stage: 'Dependency-Diagnosis', claim: 'EHR vendor integration lock-in score is 9.8/10 due to closed proprietary database schemas.', evidence: 'Analyzed EHR vendor interface agreements and API pricing surcharges.' },
          ],
        },
      },
      stage_providers: {
        ingestion: 'nvidia_nim',
        stack_mapping: 'nvidia_nim',
        scenario_generation: 'nvidia_nim',
        outcome_prediction: 'openrouter',
        dependency_diagnosis: 'gemini',
        orchestrator: 'deepseek_direct',
      },
      verification_results: [
        { passed: true, confidence: 0.99, agent_stage: 'Ingestion', claim: 'HIPAA compliance boundary validated', reason: 'Confirmed on-premise physical architecture isolates all ePHI.', provider: 'nvidia_nim' },
        { passed: true, confidence: 0.96, agent_stage: 'Stack-Mapping', claim: 'FHIR v4 interoperability verified', reason: 'Open standards support cross-EHR clinical record exchange.', provider: 'nvidia_nim' },
      ],
      recalibration_trail: [],
    },
  },
];
