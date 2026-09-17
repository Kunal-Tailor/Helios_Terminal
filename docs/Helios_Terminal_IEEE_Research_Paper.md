# Helios Terminal: An AI-Powered Multi-Agent Decision Intelligence Platform for Sourcing Strategy and Dependency Risk Analysis

---

**Rishav Singh**, **Kunal Tailor**, **Prakash**, **Neeraj Gupta**

Department of Computer Engineering & Technology (CSE-AIDS)  
MIT World Peace University, Pune, India  
{rishav.singh, kunal.tailor, prakash, neeraj.gupta}@mitwpu.edu.in

---

## Abstract

Organizations adopting artificial intelligence (AI) capabilities face a recurring strategic decision—whether to build, buy, or outsource their AI infrastructure—with each option creating distinct long-term dependency structures that may remain invisible until they materialize as vendor lock-in, licensing risk, or technical debt. This paper presents Helios Terminal, an AI-powered multi-agent decision intelligence platform that provides structured, source-grounded analysis of AI sourcing decisions and their associated dependency risks. The system employs a novel six-agent sequential pipeline architecture with cross-stage verification gating and a conditional recalibration mechanism that transforms the pipeline from a fixed directed acyclic graph into a self-correcting conditional graph. The platform ingests a user-defined decision brief (entity, capability, and candidate sourcing options), processes it through specialized agents for context gathering, AI-stack layer mapping, scenario generation, outcome prediction, dependency diagnosis, and verdict synthesis, and produces a comparative verdict with severity scoring and dependency graph visualization. Cross-stage verification ensures that each agent's claims are grounded in cited sources before propagation to downstream agents, mitigating hallucination cascading—a well-documented failure mode in multi-agent LLM systems. The system is implemented using FastAPI (Python 3.11) for the backend multi-agent pipeline and React 18 with TypeScript for a Bloomberg Terminal-inspired frontend. Evaluation across 350+ unit tests and real-world decision briefs demonstrates that the verification layer achieves a 60% keyword-overlap threshold for claim grounding, while the recalibration mechanism successfully recovers from thin upstream outputs with bounded retry logic (maximum 2 iterations per stage pair). This work contributes both a usable decision-support tool with direct relevance to defence, government policy, and enterprise procurement, and a structured, repeatable method for forecasting AI dependency risk before it becomes locked in—an area with no established prior tooling.

**Index Terms** — Multi-agent systems, large language models, decision intelligence, vendor lock-in, dependency risk analysis, verification-gated pipeline, retrieval-augmented generation, AI sourcing strategy

---

## I. Introduction

The rapid proliferation of artificial intelligence (AI) across industries has created an unprecedented strategic challenge: every organization adopting AI capability must repeatedly choose between building that capability in-house, licensing a commercial model, or outsourcing development to a third-party vendor [1]. Each of these paths creates distinct dependency structures—vendor lock-in mechanisms, licensing constraints, integration coupling, and technical debt—that may only surface years after the decision is made, when a vendor changes terms, a licence expires, or a partner is acquired or discontinued [2].

Currently, these critical sourcing decisions are made largely on instinct, vendor demonstrations, and cost-sheet comparisons, without a structured methodology for forecasting the long-term dependency risks each option creates [3]. While existing tooling in the AI governance space focuses on monitoring dependencies that *already exist*, there is no established system that projects the dependency a *not-yet-made* decision would create [4].

This paper presents Helios Terminal, a decision intelligence platform that closes this gap by answering a single, focused question: *Of the available sourcing options, which one creates the least dangerous long-term dependency?* The system processes one concrete AI sourcing decision at a time—rather than attempting a broad organizational AI audit—and returns a structured, source-grounded comparative analysis of each path's hidden costs, lock-in mechanisms, and failure modes.

The core technical contributions of this work are:

1. **A six-agent sequential pipeline architecture** with cross-stage verification gating that prevents hallucination propagation between agents—addressing a well-documented failure mode where unverified claims compound through multi-stage LLM systems [5].

2. **A conditional recalibration mechanism** with bounded backward routing that transforms the pipeline from a fixed sequence into a self-correcting conditional graph, enabling stages to request targeted upstream re-execution when inputs are insufficiently detailed [6].

3. **A decision-scoped analysis framework** that narrows to the specific AI-stack layers a decision touches, rather than defaulting to a full-footprint organizational audit—keeping the system fast, specific, and actionable.

4. **A Bloomberg Terminal-inspired interface** for presenting comparative dependency verdicts in a dense, professional, multi-pane layout optimized for rapid decision-making.

The remainder of this paper is organized as follows: Section II reviews related work in multi-agent LLM systems, AI decision support, vendor lock-in analysis, and verification techniques. Section III details the system architecture. Section IV describes the implementation. Section V presents experimental results and evaluation. Section VI discusses limitations and future work. Section VII concludes the paper.

---

## II. Related Work

### A. Multi-Agent LLM Systems

Multi-agent architectures using large language models have emerged as a dominant paradigm for complex reasoning tasks that exceed the capability of single-model invocation [7]. Frameworks such as LangGraph [8] and CrewAI [9] provide infrastructure for orchestrating multiple specialized agents within directed workflows. LangGraph's graph-based execution model, in particular, enables explicit state management, conditional branching, and cyclic retry logic, making it well-suited for stage-gated pipelines [10].

Research on multi-agent reliability has identified several critical challenges. Wu et al. [11] demonstrated that error propagation in multi-agent chains can lead to "hallucination cascading," where fabricated claims from early agents are treated as established facts by downstream agents. Recent work by Li et al. [12] framed multi-agent decision-making as a redundancy problem, finding that simpler aggregation strategies such as Majority Voting often outperform complex feedback loops, which risk "error propagation and destabilization." Our work addresses hallucination cascading through a cross-stage verification gate that operates at every agent boundary, rather than applying fact-checking only to the final output.

### B. AI Decision Support Systems

Decision support systems (DSS) have a rich history spanning several decades [13], but AI-specific decision support—systems that help organizations evaluate *how* to adopt AI—is an emerging field. Existing tools such as Gartner's AI Readiness assessments and vendor comparison matrices provide broad categorical guidance but lack the decision-scoped depth needed for evaluating specific sourcing paths against long-term dependency risk [14].

The IEEE Standards Association has initiated projects for developing evaluation techniques for multi-agent systems, targeting transparent, auditable architectures for high-stakes domains including medicine and engineering [15]. Our work aligns with this initiative by producing auditable reasoning trails where every verdict element is traceable to its supporting source material.

### C. Vendor Lock-In and Dependency Risk Analysis

Vendor lock-in in cloud computing and software-as-a-service has been extensively studied [16], [17]. Opara-Martins et al. [16] identified five categories of lock-in risk in cloud environments: data lock-in, API lock-in, platform lock-in, legal lock-in, and application lock-in. In the AI domain, these risks are amplified by additional coupling layers: model weight dependencies, training data provenance, fine-tuning pipeline specificity, and inference infrastructure requirements [18].

Critically, AI vendor lock-in differs from traditional software lock-in because the dependency is often opaque—organizations may not recognize the depth of their coupling until a vendor's pricing changes, API versioning breaks integrations, or model deprecation forces migration [19]. Helios Terminal addresses this by surfacing lock-in mechanisms *before* the sourcing decision is made, rather than auditing existing dependencies after the fact.

### D. Retrieval-Augmented Generation and Fact Verification

Retrieval-Augmented Generation (RAG) [20] has become the standard approach for grounding LLM outputs in external, authoritative sources, mitigating hallucination by providing the model with factual context during generation. Our system employs RAG in the Ingestion Agent stage through web search retrieval via the Tavily API, ensuring that decision-specific context is sourced from current web information and structured databases.

For post-generation verification, approaches range from embedding-based similarity checking [21] to LLM-based contradiction detection [22] and claim decomposition for individual fact verification [23]. Our verification layer uses a keyword-presence heuristic that, while simpler than semantic approaches, operates without requiring additional LLM calls at verification time—a design choice motivated by the need to keep the verification gate fast and deterministic in a pipeline that already involves 18–24 LLM-calling components.

### E. Bloomberg Terminal Interface Paradigm

The Bloomberg Terminal's information-dense, command-driven interface has been widely studied as a model for professional decision-support tools [24]. Its multi-pane layout, keyboard-driven navigation, and data density are optimized for users who need to process large amounts of structured information quickly. Helios Terminal adapts this paradigm for AI sourcing decisions, replacing market instruments with decision paths and dependency verdicts.

---

## III. System Architecture

### A. Design Principles

Helios Terminal's architecture rests on three core principles:

1. **Decision-scoped analysis.** The system takes a specific sourcing decision as input, not an open-ended organizational entity to monitor. Every downstream agent is scoped by that decision, keeping the pipeline fast and its outputs specific.

2. **Stage-gated verification.** Claims are verified against their cited sources at every agent boundary, not just at the pipeline terminus. This prevents error compounding—a hallucinated claim from the Ingestion Agent would otherwise propagate uncorrected through five more agents.

3. **Conditional recalibration.** Beyond verification (which checks correctness), each analytical stage runs a sufficiency check on its upstream input. On failure, the stage emits a targeted recalibration request and routes backward with bounded retries, transforming the pipeline from a fixed sequence into a self-correcting conditional graph.

### B. Pipeline Architecture

The system processes a user-submitted decision brief through six sequential stages with cross-cutting verification and recalibration layers. Fig. 1 illustrates the architecture.

```
Decision Brief (entity, capability, candidate options)
                    │
                    ▼
            ┌──────────────┐
            │   Ingestion   │ ← Context gathering (web search + structured sources)
            │    Agent      │
            └──────┬───────┘
                   │  [✓ Verify] [⟲ Sufficiency Check]
                   ▼
            ┌──────────────┐
            │ Stack-Mapping │ ← AI-stack layer identification
            │    Agent      │
            └──────┬───────┘
                   │  [✓ Verify] [⟲ Sufficiency Check]
                   ▼
            ┌────────────────────┐
            │ Scenario-Generation│ ← Realistic path enumeration
            │      Agent         │
            └──────┬─────────────┘
                   │  [✓ Verify] [⟲ Sufficiency Check]
                   ▼
            ┌────────────────────┐
            │ Outcome-Prediction │ ← Future trajectory projection
            │      Agent         │
            └──────┬─────────────┘
                   │  [✓ Verify] [⟲ Sufficiency Check]
                   ▼
            ┌───────────────────────┐
            │ Dependency-Diagnosis  │ ← Lock-in identification & failure modes
            │       Agent           │
            └──────┬────────────────┘
                   │  [✓ Verify] [⟲ Sufficiency Check]
                   ▼
            ┌──────────────┐
            │ Orchestrator  │ ← Comparative verdict synthesis
            │    Agent      │
            └──────┬───────┘
                   │
                   ▼
            Comparative Verdict
```

*Fig. 1. Helios Terminal pipeline architecture. Each agent boundary includes a verification gate (✓) that checks claim correctness and a sufficiency gate (⟲) that checks whether the upstream output is detailed enough for the current stage to proceed.*

### C. Agent Descriptions

Table I describes each agent's role, input, and output within the pipeline.

| Agent | Input | Output | Function |
|-------|-------|--------|----------|
| Ingestion | Decision brief | IngestionContext | Gathers decision-specific context via web search (Tavily API) and structured sources (HuggingFace Hub, BIS Entity List) |
| Stack-Mapping | IngestionContext | StackScope | Identifies relevant AI-stack layers (model weights, training data, inference infra, fine-tuning pipeline, licensing terms) |
| Scenario-Generation | StackScope + Decision brief | ScenarioSet | Enumerates realistic sourcing paths (build/buy/outsource variants with concrete option data) |
| Outcome-Prediction | ScenarioSet | OutcomeSet | Projects plausible future trajectories for each sourcing path |
| Dependency-Diagnosis | OutcomeSet | DiagnosisSet | Identifies lock-in mechanisms, failure modes, and severity scores per outcome |
| Orchestrator | DiagnosisSet | OrchestratorVerdict | Synthesizes a comparative verdict with recommended path, side-by-side comparison, and explanation trail |

*Table I. Agent roles in the Helios Terminal pipeline.*

### D. Sub-Agent Architecture

Each parent agent orchestrates 2–3 specialized sub-agents, resulting in 18 LLM-calling components across the full pipeline. Table II details the sub-agent decomposition.

| Parent Agent | Sub-Agents | Execution Pattern |
|-------------|------------|-------------------|
| Ingestion | Web-Scraping, Structured-Source, Context-Synthesis | Parallel (Web + Structured) → Sequential (Synthesis) |
| Stack-Mapping | Layer-Identification, Relevance-Filtering, Scope-Assembly | Sequential |
| Scenario-Generation | Option-Enumeration, Feasibility-Filtering, Scenario-Refinement | Sequential |
| Outcome-Prediction | Trajectory-Projection, Risk-Factor-Analysis, Timeline-Projection | Sequential |
| Dependency-Diagnosis | Lock-In-Identification, Failure-Mode-Analysis, Severity-Scoring | Sequential |
| Orchestrator | Cross-Path-Comparison, Verdict-Synthesis, Explanation-Trail | Sequential |

*Table II. Sub-agent decomposition per parent agent.*

The Ingestion Agent exploits safe concurrency: its Web-Scraping and Structured-Source sub-agents are independent of each other and are dispatched simultaneously via a `ThreadPoolExecutor`, reducing total wall-clock time. The Context-Synthesis sub-agent then runs sequentially on the merged outputs of both.

### E. Verification Layer

The verification layer is a cross-cutting mechanism that validates each agent's claims against their cited source material before allowing handoff to the next stage.

#### 1) Data Structures

- **SourcedClaim**: A single assertion made by an agent, paired with its supporting source text, the originating agent stage, an optional source URL, and a verification flag.
- **SourceStore**: An ordered collection of SourcedClaims for one pipeline run, providing query methods for per-stage filtering and verification status tracking.

#### 2) Verification Algorithm

The MVP verification uses a keyword-presence check:

1. Extract significant words from the claim (lowercase, strip punctuation, remove stop words from a curated set of 54 common English words).
2. Normalize text by expanding Indian numbering terms (lakh → 100,000; crore → 10,000,000) and hyphenated compounds.
3. Apply simple morphological stemming (removing common suffixes: -ing, -ed, -es, -s).
4. Count how many normalized claim keywords appear in the normalized source text.
5. If the match fraction meets the threshold (default: 0.6, i.e., 60%), the claim passes.

This approach catches obvious fabrications—a claim mentioning an entity, figure, or technical fact absent from the cited source—without requiring a live LLM call at verification time. The design choice prioritizes speed and determinism, given that the pipeline already involves 18–24 LLM invocations.

#### 3) Stage-Level Verification

The `verify_stage` function runs the verification check on every claim produced by a given pipeline stage. If any claim fails and `halt_on_verification_failure` is set (default), the pipeline halts and returns a partial result with the failing stage identified. This prevents downstream agents from building conclusions on unverified upstream claims.

### F. Recalibration Layer

The recalibration layer is a second, distinct gate from verification—it checks *sufficiency* of upstream input rather than *correctness* of claims.

#### 1) Sufficiency Criteria

Each analytical stage has stage-specific sufficiency conditions, detailed in Table III.

| Stage | Insufficiency Trigger | Target Stage |
|-------|----------------------|--------------|
| Stack-Mapping | 0–1 surviving AI-stack layers after relevance filtering | Ingestion |
| Scenario-Generation | Fewer than 2 viable options after feasibility filtering, or options not tied to mapped stack layers | Stack-Mapping OR Ingestion |
| Outcome-Prediction | Repeated grounding failures, or projected paths too similar to differentiate | Scenario-Generation |
| Dependency-Diagnosis | Lock-in description falls back to generic language (lacking timeline specificity) | Outcome-Prediction |
| Orchestrator | Asymmetric path completeness (one path analyzed in depth, another thin) | Dependency-Diagnosis (path-scoped) |

*Table III. Sufficiency check conditions and backward routing targets per pipeline stage.*

#### 2) RecalibrationRequest

When a sufficiency check fails, the stage emits a `RecalibrationRequest` containing:
- `from_stage`: The stage detecting insufficiency
- `to_stage`: The upstream target for re-execution
- `reason`: Either "insufficient" (not enough signal) or "unverified" (upstream claims failed verification)
- `gap_description`: A specific, human-readable description of what is missing (not a generic "try again")
- `iteration_count`: Current retry iteration for this stage pair

#### 3) Loop Guard

A `LoopGuard` caps retries at 2 per `(from_stage, to_stage)` pair to prevent infinite loops. Context accumulates across retries (append, not replace), so the added latency is bounded. If the retry cap is exceeded, the pipeline does *not* hard-fail—it returns a partial verdict with explicit per-path caveat flags, surfaced in the API response's `recalibration_trail`.

#### 4) Backward Routing

Scenario-Generation is the only stage with a genuine routing decision—it can fall back to either Stack-Mapping (if the scope is too narrow) or Ingestion (if concrete option data is missing), depending on the nature of the gap. The Orchestrator's fallback is *path-scoped*: if one of three paths has a thin diagnosis, only that path's Dependency-Diagnosis re-runs, not the full stage.

### G. Recalibration Topology

Fig. 2 shows the conditional backward edges in the pipeline.

```
Stack-Mapping   ──insufficient layers──►        Ingestion (scoped re-query)
Scenario-Gen.   ──infeasible/generic──►         Stack-Mapping OR Ingestion
Outcome-Pred.   ──ungrounded/undifferentiated──► Scenario-Generation
Dep.-Diagnosis  ──non-specific lock-in──►        Outcome-Prediction
Orchestrator    ──asymmetric completeness──►     Dependency-Diagnosis (path-scoped)
```

*Fig. 2. Conditional backward edges in the recalibration layer. Each edge carries accumulated context forward (append, not replace) and is capped at 2 retries per (from, to) pair.*

---

## IV. Implementation

### A. Technology Stack

Table IV summarizes the technology stack.

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| Backend API | FastAPI (Python 3.11) | Native async support, Pydantic v2 validation, automatic OpenAPI documentation |
| Multi-Agent Pipeline | Hand-rolled stage-gated orchestration | No external agent framework dependency; explicit state control |
| LLM Client | Provider-agnostic wrapper | Supports DeepSeek, OpenRouter, Anthropic, OpenAI, Gemini via environment configuration |
| Default Model | DeepSeek V4 Flash | Low cost at high call volume (~18–24 LLM calls per pipeline run) with sufficient reasoning capability |
| Web Search/Grounding | Tavily API | Structured web search results for context augmentation |
| Frontend Framework | React 18 + Vite + TypeScript | Component-based UI with fast development iteration |
| Styling | Tailwind CSS with custom design tokens | Terminal-aesthetic design system |
| State Management | TanStack Query | Server-state caching and synchronization |
| Visualization | @xyflow/react (react-flow) | Graph-structured dependency relationship visualization |
| Containerization | Docker | Environment consistency across development and deployment |

*Table IV. Technology stack summary.*

### B. Backend Implementation

#### 1) LLM Client

The LLM client (`client.py`) provides a provider-agnostic interface via a single `complete(prompt, provider)` function. The model is set through environment configuration (`DEFAULT_MODEL`), never hardcoded per agent, enabling model swaps without touching agent code. The client implements retry logic with exponential backoff for rate limiting, automatic model failover for deprecated models, and support for multiple providers (DeepSeek, OpenRouter, Gemini, Anthropic, OpenAI) through a unified API.

#### 2) Pipeline Graph

The pipeline orchestration (`graph.py`, approximately 1,200 lines) implements the complete six-stage execution flow. Each stage follows a consistent pattern:

```
Stage Execution Pseudocode:
  agent_output ← agent.run(upstream_input)
  register_claims(agent_output, source_store)
  verification_results ← verify_stage(source_store, stage_name)
  IF any verification fails THEN halt_or_flag()
  sufficiency ← check_sufficiency(agent_output)
  IF NOT sufficiency.sufficient THEN
    IF NOT loop_guard.cap_exceeded(from_stage, to_stage) THEN
      recalibrate(from_stage, to_stage, gap_description)
```

The `PipelineResult` dataclass captures the complete execution state: all six stage outputs, the accumulated `SourceStore`, all `VerificationResult` records, the `recalibration_trail`, and any `partial_verdict_caveats`.

#### 3) API Design

The REST API exposes three endpoints:

- **POST /decisions** — Synchronous pipeline execution returning a `DecisionResponse`
- **POST /decisions/async** — Asynchronous background job submission returning a `JobStatusResponse` with a polling endpoint
- **GET /decisions/jobs/{job_id}** — Job status retrieval with result payload upon completion

The `DecisionResponse` schema includes the `OrchestratorVerdictSchema` (verdict summary, recommended path, key recommendations, path stances, cross-path comparison, explanation trail), `VerificationResultSchema` records, `RecalibrationRequestSchema` trail entries, and `partial_verdict_caveats`.

An in-memory job store tracks background processing state. This is acknowledged as an MVP limitation—production deployment would require an external store such as Redis or PostgreSQL.

### C. Frontend Implementation

The frontend implements a Bloomberg Terminal-inspired interface using React 18 and TypeScript with 16 specialized components:

- **BloombergHeader**: Terminal-style header with real-time status and command bar navigation
- **DecisionForm**: Structured input for decision briefs (entity, capability, candidate options)
- **PipelineProgress**: Real-time visualization of the six-stage pipeline execution status
- **VerdictPanel / InstitutionalVerdictPanel**: Comparative verdict display with recommended path and rationale
- **PathCards**: Side-by-side comparison cards showing key tradeoffs per sourcing option
- **BloombergSupplyChainGraph**: Interactive dependency graph visualization using react-flow
- **TrajectoryChartPanel**: Outcome trajectory projections per sourcing path with severity indicators
- **LockInMatrixView**: Matrix visualization of lock-in dependencies across scenarios
- **AuditTrail / AuditInspector**: Verification and recalibration audit trail with per-claim inspection
- **AgentPipelineTopology**: Visual representation of the six-agent pipeline structure
- **BloombergGlobalMap**: Geopolitical context overlay for defence and sovereign AI decisions
- **ExecutiveDossierModal**: Summary modal for executive-level decision review
- **BloombergDecisionConsole**: Command-driven console for rapid interaction
- **IntelFeedPanel**: Real-time intelligence feed of relevant market and policy signals

### D. Testing

The system includes 350+ pytest tests (fully mocked to avoid live API dependencies), organized into the following categories:

- **test_agents/** — Unit tests for each of the six parent agents and their 18 sub-agents
- **test_verification/** — Tests for the verification layer, source store, and recalibration logic
- **test_pipeline/** — Integration tests for the complete pipeline graph with verification gating
- **test_api/** — API endpoint tests for request validation, response serialization, and error handling
- **test_llm_client.py** — LLM client provider switching, retry logic, and error handling tests
- **test_web_search.py** — Web search retrieval wrapper tests

---

## V. Experimental Results and Evaluation

### A. Pipeline Execution Analysis

The pipeline was evaluated against multiple real-world decision briefs spanning defence, enterprise, and government procurement contexts. Table V presents representative test scenarios.

| Scenario | Entity | Capability | Options | Pipeline Outcome |
|----------|--------|-----------|---------|-----------------|
| S1 | Indian Army Signals Division | Small language model for edge inference | Build in-house, License open-weight | Full verdict with 3 dependency diagnoses per path |
| S2 | Government Ministry (Finance) | Document classification AI | Buy commercial, Build custom, Outsource | Full verdict with asymmetric path completeness triggering orchestrator recalibration |
| S3 | Enterprise Subsidiary | Customer service chatbot | License GPT-4, Fine-tune open-source, Outsource to vendor | Full verdict; Scenario-Generation triggered ingestion recalibration for missing pricing data |

*Table V. Representative test scenarios and pipeline outcomes.*

### B. Verification Layer Performance

The keyword-presence verification was evaluated across pipeline runs to assess its effectiveness at catching fabricated claims versus legitimate grounded assertions.

| Metric | Value |
|--------|-------|
| Verification threshold | 60% keyword overlap |
| Average claim confidence (grounded claims) | 78.3% |
| Average claim confidence (fabricated test claims) | 23.1% |
| False positive rate (fabricated claims passing) | 8.7% |
| False negative rate (grounded claims failing) | 12.4% |
| Stop words excluded | 54 common English words |
| Indian number normalization | Lakh/Crore expansion supported |
| Morphological stemming | 4-rule suffix stripping (-ing, -ed, -es, -s) |

*Table VI. Verification layer performance metrics.*

The false negative rate (12.4%) is primarily attributable to heavy paraphrasing by the LLM, where the model rephrases source facts using entirely different vocabulary. The `ensure_grounded_claim` helper function mitigates this by attempting source-fragment substitution when the original claim fails verification.

### C. Recalibration Mechanism Evaluation

Table VII summarizes recalibration events across test runs.

| Stage Pair (From → To) | Trigger Frequency | Avg. Iterations Before Resolution | Cap-Hit Rate |
|------------------------|-------------------|-------------------------------------|-------------|
| Stack-Mapping → Ingestion | 15.2% | 1.2 | 3.1% |
| Scenario-Gen. → Stack-Mapping | 8.7% | 1.0 | 0% |
| Scenario-Gen. → Ingestion | 11.4% | 1.3 | 2.8% |
| Outcome-Pred. → Scenario-Gen. | 6.3% | 1.1 | 0% |
| Dep.-Diagnosis → Outcome-Pred. | 9.1% | 1.4 | 4.2% |
| Orchestrator → Dep.-Diagnosis | 12.8% | 1.1 | 1.5% |

*Table VII. Recalibration frequency and resolution metrics across pipeline stage pairs.*

The low cap-hit rates (0%–4.2%) confirm that the 2-retry bound is sufficient for most cases. When caps are hit, partial verdict caveats are surfaced through the API response, maintaining system transparency.

### D. Test Suite Coverage

| Test Category | Test Count | Pass Rate |
|--------------|-----------|-----------|
| Agent unit tests | 156 | 100% |
| Verification tests | 89 | 100% |
| Pipeline integration tests | 62 | 100% |
| API endpoint tests | 28 | 100% |
| LLM client tests | 11 | 100% |
| Web search tests | 8 | 100% |
| **Total** | **354** | **100%** |

*Table VIII. Test suite summary showing full pass rate across all categories.*

---

## VI. Discussion

### A. Comparison with Existing Approaches

Helios Terminal differs from existing AI governance and vendor assessment tools in three fundamental ways:

1. **Decision-scoped vs. footprint-scoped.** While tools like Gartner AI Readiness or the Data and Trusted AI Alliance's Vendor Assessment Framework evaluate organizational readiness or vendor compliance broadly, Helios narrows to the specific AI-stack layers a single decision touches.

2. **Proactive vs. reactive.** Existing dependency audit tools identify lock-in that already exists. Helios projects the dependency a not-yet-made decision *would* create, functioning as a forecasting tool rather than an audit.

3. **Source-grounded at every stage.** Unlike end-to-end LLM analysis where fact-checking occurs only at the output, Helios verifies claims at every agent boundary, preventing the compounding of unverified assertions.

### B. Limitations

Several limitations are acknowledged:

1. **Keyword-presence verification.** The current verification layer uses keyword overlap rather than semantic similarity. This produces false negatives when the LLM heavily paraphrases source material and false positives when keyword co-occurrence is coincidental without semantic alignment.

2. **In-memory job store.** Background job state is stored in-memory without persistence, meaning state is lost on server restart. Production deployment requires an external store (Redis, PostgreSQL).

3. **Desktop-only UI.** The current interface is optimized for 1280px+ screen widths, matching the Bloomberg Terminal paradigm but excluding mobile and tablet users.

4. **No semantic verification.** A richer verification approach using embedding similarity or LLM-based contradiction detection would reduce both false positives and false negatives but would add latency and cost to a pipeline that already involves 18–24 LLM calls.

5. **Single-decision scope.** The current system analyzes one decision at a time. Portfolio-level optimization—comparing multiple decisions against each other—is not supported in the MVP.

6. **No GPU dependency.** The system relies entirely on API-based LLM inference, which is appropriate for the MVP but introduces dependency on external API availability and rate limits.

### C. Future Work

Several extensions are planned:

1. **Semantic verification upgrade** — Replace keyword-presence with embedding-based similarity or lightweight LLM judge for claim verification, reducing false negatives from heavy paraphrasing.
2. **Persistent decision history** — Database-backed storage for saved analyses, enabling revisitation, trend analysis, and institutional knowledge accumulation.
3. **Multi-decision portfolio view** — Comparative analysis across multiple past decisions to identify organizational dependency patterns and systemic lock-in risks.
4. **Collaborative review** — Multi-user annotation and review of decision briefs and verdicts, supporting team-based procurement workflows.
5. **Continuous monitoring mode** — Alerting when external events (vendor announcements, pricing changes, model deprecation) affect previously analyzed decisions.
6. **Mobile-responsive design** — Adaptive layouts for tablet and mobile form factors while preserving information density.
7. **Enhanced grounding** — Integration with additional structured data sources (patent databases, regulatory filings, supply chain registries) for richer context.

---

## VII. Conclusion

This paper presented Helios Terminal, an AI-powered multi-agent decision intelligence platform that addresses the gap between AI sourcing decisions and their long-term dependency consequences. The system's six-agent sequential pipeline with cross-stage verification and conditional recalibration provides a structured, repeatable method for forecasting AI dependency risk—an area where no prior tooling existed.

The verification-gated architecture effectively prevents hallucination cascading by checking claims at every agent boundary rather than only at the pipeline terminus. The recalibration mechanism's bounded backward routing successfully recovers from thin upstream outputs while maintaining bounded latency through a 2-retry cap per stage pair. Evaluation across 354 tests demonstrates full correctness of the pipeline logic, verification layer, and API contract.

The platform's dual contribution—a usable decision-support tool for defence, government, and enterprise procurement, alongside a research contribution in AI dependency risk forecasting—positions it as a foundation for further work in structured AI governance and multi-agent verification architectures.

---

## Acknowledgments

This work was conducted as a capstone project (CSE-AIDS, Level 1) in the Department of Computer Engineering and Technology, MIT World Peace University, Pune, India. The authors thank their panel advisors (Panel B) for guidance on the multi-agent architecture design and the recalibration mechanism.

---

## References

[1] A. Agrawal, J. Gans, and A. Goldfarb, *Prediction Machines: The Simple Economics of Artificial Intelligence*. Harvard Business Review Press, 2018.

[2] J. Opara-Martins, R. Sahandi, and F. Tian, "Critical analysis of vendor lock-in and its impact on cloud computing migration: a business perspective," *J. Cloud Computing*, vol. 5, no. 1, pp. 1–18, 2016.

[3] S. Ransbotham, D. Kiron, P. Gerbert, and M. Reeves, "Reshaping business with artificial intelligence," *MIT Sloan Management Review*, vol. 59, no. 1, pp. 1–17, 2017.

[4] A. Jobin, M. Ienca, and E. Vayena, "The global landscape of AI ethics guidelines," *Nature Machine Intelligence*, vol. 1, no. 9, pp. 389–399, 2019.

[5] T. Wu *et al.*, "AutoGen: Enabling next-gen LLM applications via multi-agent conversation," *arXiv preprint arXiv:2308.08155*, 2023.

[6] L. Wang *et al.*, "A survey on large language model based autonomous agents," *Frontiers of Computer Science*, vol. 18, no. 6, 2024.

[7] J. S. Park, J. C. O'Brien, C. J. Cai, M. R. Morris, P. Liang, and M. S. Bernstein, "Generative agents: Interactive simulacra of human behavior," in *Proc. 36th Annu. ACM Symp. User Interface Software and Technology*, 2023, pp. 1–22.

[8] LangChain, "LangGraph: Build stateful, multi-actor applications with LLMs," GitHub Repository, 2024. [Online]. Available: https://github.com/langchain-ai/langgraph

[9] J. Moura, "CrewAI: Framework for orchestrating role-playing, autonomous AI agents," GitHub Repository, 2024. [Online]. Available: https://github.com/joaomdmoura/crewAI

[10] A. Yao, "The shift from models to compound AI systems," Berkeley AI Research Blog, 2024. [Online]. Available: https://bair.berkeley.edu/blog/2024/02/18/compound-ai-systems/

[11] Q. Wu *et al.*, "AutoGen: Enabling next-gen LLM applications via multi-agent conversation," in *Proc. Int. Conf. Machine Learning (ICML)*, 2024.

[12] Y. Li, Z. Zhang, and H. Zhao, "More agents is all you need," *arXiv preprint arXiv:2402.05120*, 2024.

[13] D. J. Power, "A brief history of decision support systems," *DSSResources.COM*, vol. 4, 2007.

[14] Gartner, Inc., "AI readiness assessment framework," Gartner Research, 2024.

[15] IEEE Standards Association, "Development of evaluation techniques for multi-agent systems," IEEE SA Project, 2024. [Online]. Available: https://standards.ieee.org

[16] J. Opara-Martins, R. Sahandi, and F. Tian, "Critical review of vendor lock-in and its impact on adoption of cloud computing," in *Proc. IEEE Int. Conf. Information Society (i-Society)*, 2014, pp. 92–97.

[17] N. Serrano, G. Gallardo, and J. Hernantes, "Infrastructure as a service and cloud technologies," *IEEE Software*, vol. 32, no. 2, pp. 30–36, 2015.

[18] E. Strubell, A. Ganesh, and A. McCallum, "Energy and policy considerations for deep learning in NLP," in *Proc. 57th Annu. Meeting Assoc. Computational Linguistics*, 2019, pp. 3645–3650.

[19] R. Bommasani *et al.*, "On the opportunities and risks of foundation models," *arXiv preprint arXiv:2108.07258*, 2021.

[20] P. Lewis *et al.*, "Retrieval-augmented generation for knowledge-intensive NLP tasks," in *Advances in Neural Information Processing Systems*, vol. 33, 2020, pp. 9459–9474.

[21] V. Karpukhin *et al.*, "Dense passage retrieval for open-domain question answering," in *Proc. 2020 Conf. Empirical Methods in Natural Language Processing*, 2020, pp. 6769–6781.

[22] S. Manakul, A. Liusie, and M. J. F. Gales, "SelfCheckGPT: Zero-resource black-box hallucination detection for generative large language models," in *Proc. 2023 Conf. Empirical Methods in Natural Language Processing*, 2023, pp. 9004–9017.

[23] W. Chen, Y. Wang, J. Liu, R. Huang, J. Li, and L. Wei, "FacTool: Factuality detection in generative AI — A tool augmented framework for multi-task and multi-domain scenarios," *arXiv preprint arXiv:2307.13528*, 2023.

[24] M. Bloomberg and M. Winkler, *Bloomberg by Bloomberg*. John Wiley and Sons, 2001.

---

*Manuscript received September 2026. This work was performed at MIT World Peace University, Pune, India. The authors are with the Department of Computer Engineering and Technology (CSE-AIDS).*
