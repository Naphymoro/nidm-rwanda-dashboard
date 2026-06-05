PUBLICATION_HTML = r"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>NDIM Engine Scientific Publication</title>
    <script>
      window.MathJax = {
        tex: { inlineMath: [["\\(", "\\)"], ["$", "$"]], displayMath: [["$$", "$$"]] },
        svg: { fontCache: "global" }
      };
    </script>
    <script defer src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"></script>
    <style>
      :root {
        --paper: #fbfaf7;
        --panel: #fffdf9;
        --wash: #f1ece3;
        --ink: #14110e;
        --muted: #665b4d;
        --soft: #9a8d78;
        --line: #d6cbbb;
        --accent: #111111;
        --good: #5f7b50;
        --warn: #9b6a2e;
        --bad: #9a4b3c;
        --font-ui: "Myriad Pro", "Myriad Set Pro", "Segoe UI", Arial, sans-serif;
        --font-data: "Cascadia Mono", "JetBrains Mono", Consolas, monospace;
      }
      * { box-sizing: border-box; }
      html { scroll-behavior: smooth; }
      body {
        margin: 0;
        background: var(--paper);
        color: var(--ink);
        font-family: var(--font-ui);
        line-height: 1.55;
      }
      main {
        width: min(1180px, calc(100% - 32px));
        margin: 0 auto;
        padding: 28px 0 80px;
      }
      header {
        border: 1px solid var(--line);
        border-radius: 24px;
        background: linear-gradient(135deg, #fffdf9, #f3ede3);
        padding: clamp(22px, 4vw, 46px);
        box-shadow: 0 20px 70px rgba(20, 17, 14, .08);
      }
      h1, h2, h3 { line-height: 1.08; margin: 0 0 12px; }
      h1 { font-size: clamp(36px, 6vw, 72px); letter-spacing: -.04em; max-width: 950px; }
      h2 { font-size: clamp(24px, 3vw, 36px); }
      h3 { font-size: 20px; margin-top: 16px; }
      p, li { font-size: 17px; color: var(--muted); }
      a { color: var(--ink); font-weight: 800; }
      .mono {
        color: var(--soft);
        font: 800 12px var(--font-data);
        letter-spacing: .14em;
        text-transform: uppercase;
      }
      .lede {
        max-width: 920px;
        font-size: clamp(18px, 2vw, 23px);
      }
      .nav {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-top: 24px;
      }
      .button, button {
        border: 1px solid var(--line);
        border-radius: 12px;
        background: var(--panel);
        color: var(--ink);
        padding: 10px 14px;
        font-weight: 800;
        text-decoration: none;
        cursor: pointer;
      }
      .button.primary, button.primary {
        background: var(--accent);
        color: white;
        border-color: var(--accent);
      }
      .button:hover, button:hover {
        border-color: var(--accent);
      }
      .toolbar {
        position: sticky;
        top: 0;
        z-index: 5;
        margin: 18px 0;
        padding: 12px;
        border: 1px solid var(--line);
        border-radius: 18px;
        background: rgba(251, 250, 247, .94);
        backdrop-filter: blur(16px);
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
        justify-content: space-between;
        align-items: center;
      }
      .toolbar-actions {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
      }
      section, details {
        border: 1px solid var(--line);
        border-radius: 18px;
        background: var(--panel);
        margin: 16px 0;
        padding: clamp(16px, 2vw, 24px);
      }
      details summary {
        cursor: pointer;
        font-size: 22px;
        font-weight: 900;
        line-height: 1.15;
      }
      details[open] summary { margin-bottom: 14px; }
      .callout {
        border-left: 4px solid var(--accent);
        background: var(--wash);
        border-radius: 12px;
        padding: 14px 16px;
        margin: 14px 0;
      }
      .warning {
        border-left-color: var(--warn);
      }
      .grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 14px;
      }
      .triple {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 14px;
      }
      .box {
        border: 1px solid var(--line);
        border-radius: 14px;
        background: var(--paper);
        padding: 14px;
      }
      .box h3 { margin-top: 0; }
      table {
        width: 100%;
        border-collapse: collapse;
        margin: 14px 0;
        background: var(--paper);
        border-radius: 12px;
        overflow: hidden;
      }
      th, td {
        border: 1px solid var(--line);
        padding: 10px;
        text-align: left;
        vertical-align: top;
      }
      th {
        background: var(--wash);
        color: var(--ink);
      }
      code, pre {
        font-family: var(--font-data);
      }
      pre {
        white-space: pre-wrap;
        background: #111827;
        color: #f8fafc;
        border-radius: 14px;
        padding: 14px;
        overflow-x: auto;
      }
      .math-block {
        border: 1px solid var(--line);
        border-radius: 14px;
        background: var(--paper);
        padding: 14px 18px;
        margin: 14px 0;
        overflow-x: auto;
      }
      .status-good { color: var(--good); font-weight: 900; }
      .status-warn { color: var(--warn); font-weight: 900; }
      .status-bad { color: var(--bad); font-weight: 900; }
      .figure-list li { margin-bottom: 8px; }
      .back-top {
        position: fixed;
        right: 18px;
        bottom: 18px;
        z-index: 6;
      }
      @media (max-width: 820px) {
        main { width: min(100% - 20px, 1180px); padding-top: 12px; }
        .grid, .triple { grid-template-columns: 1fr; }
        .toolbar { position: static; }
        p, li { font-size: 16px; }
        table, thead, tbody, tr, th, td { display: block; }
        thead { display: none; }
        td::before {
          content: attr(data-label);
          display: block;
          color: var(--soft);
          font: 800 11px var(--font-data);
          letter-spacing: .08em;
          text-transform: uppercase;
          margin-bottom: 4px;
        }
      }
      @media print {
        .toolbar, .nav, .back-top { display: none; }
        body { background: white; }
        main { width: 100%; padding: 0; }
        section, details, header { page-break-inside: avoid; box-shadow: none; }
        details { display: block; }
        details:not([open]) > * { display: block; }
        details:not([open]) summary { margin-bottom: 14px; }
      }
    </style>
  </head>
  <body id="top">
    <main>
      <header>
        <p class="mono">Scientific Publication</p>
        <h1>NDIM as a cautious, testable methodological contribution.</h1>
        <p class="lede">This page frames the Narrative Diffusion and Inoculation Model as a reproducible research software workflow. It is written for academic collaborators, supervisors, journal reviewers, grant reviewers, and policy research teams.</p>
        <div class="callout warning">
          <p><strong>Scientific boundary:</strong> NDIM is not yet an empirically validated causal model. At the current stage, the defensible claim is that NDIM is a proposed, reproducible, testable methodological framework and research software workflow. Empirical validation requires real field data, double coding, calibration, uncertainty checks, and policy-user evaluation.</p>
        </div>
        <div class="nav">
          <a class="button primary" href="/">Back to tool</a>
          <a class="button" href="/academy">NDIM Academy</a>
          <a class="button" href="/manual">Tool manual</a>
          <a class="button" href="#abstract">Abstract</a>
          <a class="button" href="#equations">Equations</a>
          <a class="button" href="#validation">Validation roadmap</a>
          <a class="button" href="#references">References starter list</a>
        </div>
      </header>

      <div class="toolbar">
        <span class="mono">Publication brief controls</span>
        <div class="toolbar-actions">
          <button class="primary" id="downloadHtml" type="button">Export HTML</button>
          <button id="downloadMarkdown" type="button">Export Markdown outline</button>
          <button id="printPdf" type="button">Print to PDF</button>
        </div>
      </div>

      <section id="positioning">
        <p class="mono">01 / Publication positioning</p>
        <h2>What NDIM is</h2>
        <p>NDIM means <strong>Narrative Diffusion and Inoculation Model</strong>. It is a governed evidence-to-policy workflow. It links community narratives, inoculation theory, compartmental modelling, agent-based modelling, digital twin feedback, Bayesian updating, reinforcement-learning policy optimization, and human-reviewed policy brief generation.</p>
        <p>The strongest present framing is a <strong>Methods article</strong>, <strong>Conceptual Analysis</strong>, or <strong>Policy & Practice Review</strong>. A full empirical Original Research article becomes realistic after validation data are collected and analysed.</p>
        <div class="grid">
          <div class="box">
            <h3>NDIM can claim now</h3>
            <ul>
              <li>A reproducible methodological workflow.</li>
              <li>A software implementation that makes assumptions visible.</li>
              <li>A way to connect narrative governance, inoculation logic, simulation, uncertainty, and policy output.</li>
              <li>A validation roadmap that can be tested by researchers.</li>
            </ul>
          </div>
          <div class="box">
            <h3>NDIM must not claim yet</h3>
            <ul>
              <li>It is not yet a validated causal model.</li>
              <li>It is not yet a tested empirical theory.</li>
              <li>It is not a replacement for field trials or community review.</li>
              <li>It is not sufficient for policy without real validation data and human review.</li>
            </ul>
          </div>
        </div>
      </section>

      <section id="innovation">
        <p class="mono">02 / Scientific innovation</p>
        <h2>Why NDIM is different without pretending to replace prior work</h2>
        <p>Many misinformation models begin after a story has already been simplified into model states such as exposed, infected, corrected, or recovered. That abstraction is useful. It helps researchers study spread, persistence, correction, and decay.</p>
        <p>NDIM starts one step earlier. It asks what the story is, where it came from, who approved it, what meaning it carries, and whether it creates an inoculation opportunity. Only then does the tool translate the evidence into model inputs.</p>
        <table>
          <thead>
            <tr><th>Research tradition</th><th>What it contributes</th><th>How NDIM builds on it</th></tr>
          </thead>
          <tbody>
            <tr><td data-label="Research tradition">SIR/SEIR misinformation models</td><td data-label="What it contributes">Clear state transitions for exposure, spread, correction, and decay.</td><td data-label="How NDIM builds on it">Adds governed narrative intake and inoculation-aware encoding before the compartmental abstraction.</td></tr>
            <tr><td data-label="Research tradition">Rumor diffusion models</td><td data-label="What it contributes">Attention to rumor spread, stifling, forgetting, and correction.</td><td data-label="How NDIM builds on it">Preserves provenance and approval status so not every story is treated as equivalent evidence.</td></tr>
            <tr><td data-label="Research tradition">Social contagion and information cascade models</td><td data-label="What it contributes">Network effects, peer influence, and threshold behavior.</td><td data-label="How NDIM builds on it">Connects peer influence to agent-based adoption and local narrative signals.</td></tr>
            <tr><td data-label="Research tradition">Agent-based adoption models</td><td data-label="What it contributes">Household heterogeneity, local interaction, and decision rules.</td><td data-label="How NDIM builds on it">Feeds narrative-derived trust, barriers, credibility, and social influence into household behavior.</td></tr>
            <tr><td data-label="Research tradition">Digital twin policy simulations</td><td data-label="What it contributes">Scenario testing and feedback between data and model state.</td><td data-label="How NDIM builds on it">Treats the twin as a narrative-sensitive policy simulator, not only a technical system model.</td></tr>
            <tr><td data-label="Research tradition">Inoculation theory studies</td><td data-label="What it contributes">Warning, weak-dose exposure, refutational preemption, resistance, and booster logic.</td><td data-label="How NDIM builds on it">Turns inoculation logic into a testable model intervention that can be examined before, during, and after application.</td></tr>
          </tbody>
        </table>
        <div class="callout">
          <p><strong>Bottom line:</strong> NDIM's innovation is integration. It joins governed narrative evidence, inoculation-aware encoding, coupled simulation, uncertainty learning, and policy-output synthesis in one auditable workflow.</p>
        </div>
      </section>

      <section id="abstract">
        <p class="mono">03 / Candidate manuscript abstract</p>
        <h2>Publication-style abstract</h2>
        <p>Community narratives can shape the adoption of climate, health, and development interventions, yet many modelling approaches translate those narratives into simplified diffusion states before provenance, consent, meaning, and inoculation opportunities are examined. This paper proposes the Narrative Diffusion and Inoculation Model (NDIM), a reproducible methodological framework and research software workflow for linking governed narrative evidence to simulation-informed policy support.</p>
        <p>NDIM combines SDMX-inspired narrative intake, evidence governance, inoculation-aware encoding, compartmental diffusion modelling, agent-based household simulation, digital twin feedback, Bayesian uncertainty updating, reinforcement-learning policy optimization, knowledge-graph synthesis, and human-reviewed policy brief generation. The framework is implemented as an offline-first research application designed to preserve audit trails from field narrative to policy output.</p>
        <p>The expected contribution is methodological: NDIM offers a testable architecture for studying how narratives, misinformation risks, trusted messengers, and pre-bunking strategies may influence adoption pathways. The current implementation should not be interpreted as an empirically validated causal model. Validation will require real field data, double-coded narratives, inter-rater reliability analysis, LLM-versus-human agreement checks, calibration of encoding scores, sensitivity analysis, retrospective comparison, field pilots, and policy-user evaluation.</p>
      </section>

      <details id="manuscript" open>
        <summary>04 / Proposed manuscript structure</summary>
        <h3>Possible titles</h3>
        <ol>
          <li>Narrative Diffusion and Inoculation Model: A Governed Evidence-to-Policy Framework for Adoption Dynamics</li>
          <li>From Community Narratives to Policy Simulation: The NDIM Framework for Inoculation-Aware Decision Support</li>
          <li>Modelling Narrative-Sensitive Adoption: Evidence Governance, Inoculation, Digital Twins, and Policy Optimization in NDIM</li>
        </ol>
        <h3>Publication outline</h3>
        <ol>
          <li>Abstract</li>
          <li>Introduction</li>
          <li>Background and related work</li>
          <li>Conceptual foundations</li>
          <li>NDIM framework</li>
          <li>Evidence governance and SDMX narrative intake</li>
          <li>Narrative encoding</li>
          <li>Compartmental model</li>
          <li>Agent-based model</li>
          <li>Digital twin feedback</li>
          <li>Bayesian uncertainty updating</li>
          <li>Policy optimization</li>
          <li>Inoculation lab</li>
          <li>Research software architecture</li>
          <li>Validation roadmap</li>
          <li>Limitations</li>
          <li>Policy and research implications</li>
          <li>Conclusion</li>
        </ol>
      </details>

      <details id="methodology" open>
        <summary>05 / Methodological contribution</summary>
        <table>
          <thead>
            <tr><th>Component</th><th>Purpose</th><th>Scientific basis</th><th>Current status</th><th>Validation data needed</th><th>Limitations</th></tr>
          </thead>
          <tbody>
            <tr><td data-label="Component">Narrative ingestion</td><td data-label="Purpose">Collect text, CSV, PDF, structured interviews, open stories, focus groups, citizen reports, and social feeds.</td><td data-label="Scientific basis">Qualitative field evidence, narrative inquiry, citizen science.</td><td data-label="Current status">Implemented as a governed intake workflow.</td><td data-label="Validation data needed">Real field narratives across routes and languages.</td><td data-label="Limitations">Quality depends on field protocol, consent, translation, and metadata discipline.</td></tr>
            <tr><td data-label="Component">Evidence governance</td><td data-label="Purpose">Approve, reject, hash, audit, and preserve source context before modelling.</td><td data-label="Scientific basis">Research ethics, data governance, reproducibility.</td><td data-label="Current status">Implemented as local ledger with repository lifecycle.</td><td data-label="Validation data needed">Reviewer logs and governance decisions.</td><td data-label="Limitations">Governance rules must be institutionally reviewed.</td></tr>
            <tr><td data-label="Component">SDMX-inspired metadata</td><td data-label="Purpose">Make place, source, period, language, route, and attributes comparable.</td><td data-label="Scientific basis">Statistical metadata and structured data exchange principles.</td><td data-label="Current status">Implemented as narrative metadata schema and export package.</td><td data-label="Validation data needed">Field use across countries and administrative units.</td><td data-label="Limitations">Not a full SDMX registry yet.</td></tr>
            <tr><td data-label="Component">Inoculation-aware encoding</td><td data-label="Purpose">Convert narratives into trust, barrier, threat, refutability, messenger, and resilience signals.</td><td data-label="Scientific basis">Inoculation theory, misinformation studies, human coding.</td><td data-label="Current status">Implemented as manual, heuristic/LLM, and hybrid encoding.</td><td data-label="Validation data needed">Double-coded narratives and LLM-versus-human agreement.</td><td data-label="Limitations">Scores require calibration and cultural review.</td></tr>
            <tr><td data-label="Component">ODE compartmental model</td><td data-label="Purpose">Represent population-level movement among susceptible, misinformed, trusting, adopters, and resistant groups.</td><td data-label="Scientific basis">Compartmental diffusion and epidemiological modelling.</td><td data-label="Current status">Implemented as model workflow; must keep equation and executable model aligned.</td><td data-label="Validation data needed">Observed adoption and misinformation trajectories.</td><td data-label="Limitations">Population states simplify social complexity.</td></tr>
            <tr><td data-label="Component">Agent-based model</td><td data-label="Purpose">Represent household heterogeneity, peer influence, local trust, and barriers.</td><td data-label="Scientific basis">Agent-based adoption and social influence modelling.</td><td data-label="Current status">Implemented as a simulation stage.</td><td data-label="Validation data needed">Household-level or community-level behavior indicators.</td><td data-label="Limitations">Rules are assumptions until calibrated.</td></tr>
            <tr><td data-label="Component">Digital twin feedback</td><td data-label="Purpose">Combine evidence, model outputs, posterior learning, and intervention tests into scenario comparison.</td><td data-label="Scientific basis">Digital twin decision support and model feedback loops.</td><td data-label="Current status">Implemented as advisory prototype twin.</td><td data-label="Validation data needed">Baseline and post-intervention observations.</td><td data-label="Limitations">Not a real-time operational twin yet.</td></tr>
            <tr><td data-label="Component">Bayesian update</td><td data-label="Purpose">Move from prior assumptions to posterior beliefs as evidence arrives.</td><td data-label="Scientific basis">Bayesian inference and uncertainty learning.</td><td data-label="Current status">Implemented with fallback analytics and posterior summaries.</td><td data-label="Validation data needed">Observed outcomes and uncertainty calibration.</td><td data-label="Limitations">Priors require transparent justification.</td></tr>
            <tr><td data-label="Component">RL optimizer</td><td data-label="Purpose">Compare intervention policies under model reward assumptions.</td><td data-label="Scientific basis">Reinforcement learning for decision support.</td><td data-label="Current status">Implemented as advisory optimizer.</td><td data-label="Validation data needed">Policy costs, outcomes, constraints, and ethical review.</td><td data-label="Limitations">Should not automate policy decisions.</td></tr>
            <tr><td data-label="Component">Knowledge graph</td><td data-label="Purpose">Connect stories, themes, places, messengers, barriers, and intervention ideas.</td><td data-label="Scientific basis">Graph-based knowledge representation.</td><td data-label="Current status">Implemented as synthesis stage.</td><td data-label="Validation data needed">Coded narrative corpus with locations and themes.</td><td data-label="Limitations">Graph structure reflects coding choices.</td></tr>
            <tr><td data-label="Component">Policy brief output</td><td data-label="Purpose">Create a human-readable recommendation with evidence grade, confidence, assumptions, and limitations.</td><td data-label="Scientific basis">Evidence-informed policy and decision support.</td><td data-label="Current status">Implemented as exportable brief.</td><td data-label="Validation data needed">Policy-user evaluation and decision review.</td><td data-label="Limitations">Requires human review before use.</td></tr>
          </tbody>
        </table>
      </details>

      <details id="equations" open>
        <summary>06 / Equations and model formalization</summary>
        <h3>Narrative encoding score</h3>
        <div class="math-block">$$\Phi_n = \sigma(w_E E_n + w_C C_n + w_\tau \tau_n - w_\kappa \kappa_n + b)$$</div>
        <p><strong>Variables:</strong> \(E_n\) is narrative exposure or salience, \(C_n\) is credibility or local grounding, \(\tau_n\) is trust signal, \(\kappa_n\) is barrier or friction, \(w\) values are weights, \(b\) is a baseline, and \(\sigma\) keeps the score between 0 and 1.</p>
        <p><strong>Plain interpretation:</strong> a story becomes more model-relevant when it is salient, credible, and trust-building, and less adoption-supportive when it carries strong barriers.</p>
        <p><strong>Policy implication:</strong> high \(\Phi\) can indicate stories likely to support adoption; high barrier components can indicate where policy must reduce friction.</p>
        <p><strong>Assumptions and limitations:</strong> weights must be justified and calibrated. Until calibration, this is a transparent scoring rule, not proof of causality.</p>

        <h3>S/M/T/I/R compartmental equations</h3>
        <div class="math-block">
          $$\frac{dS}{dt} = -\beta_t S T - \beta_m S M$$
          $$\frac{dM}{dt} = \beta_m S M - \iota M - \mu M$$
          $$\frac{dT}{dt} = \beta_t S T + \iota M - \rho T$$
          $$\frac{dI}{dt} = \rho T - \omega I$$
          $$\frac{dR}{dt} = \mu M + \omega I$$
        </div>
        <p><strong>Variables:</strong> \(S\) is susceptible or undecided population share, \(M\) is misinformation-influenced share, \(T\) is trusting or persuaded share, \(I\) is adopter share, and \(R\) is resistant or removed-from-adoption-flow share. Parameters control trust spread \(\beta_t\), misinformation spread \(\beta_m\), inoculation/refutation \(\iota\), adoption transition \(\rho\), misinformation decay or resistance \(\mu\), and adoption stabilization \(\omega\).</p>
        <p><strong>Plain interpretation:</strong> people move between narrative states. Trust can move people toward adoption. Misinformation can delay or block adoption. Inoculation can move misinformed people back toward trust.</p>
        <p><strong>Policy implication:</strong> policy can be tested as a change to trust spread, misinformation decay, adoption transition, or resistance.</p>
        <p><strong>Assumptions and limitations:</strong> the simple form treats population shares as conserved and homogeneous. Real communities need calibration, heterogeneity, and sensitivity analysis.</p>

        <h3>Agent adoption probability</h3>
        <div class="math-block">$$P(A_i = 1) = \sigma(\alpha_0 + \alpha_1 Trust_i - \alpha_2 Barrier_i + \alpha_3 Peer_i + \alpha_4 Access_i + \alpha_5 Inoculation_i)$$</div>
        <p><strong>Plain interpretation:</strong> a household is more likely to adopt when trust, peer examples, access, and inoculation support increase, and less likely when barriers rise.</p>
        <p><strong>Policy implication:</strong> the agent model helps test whether a policy works differently for households with different trust, access, or peer environments.</p>
        <p><strong>Limitations:</strong> coefficients require empirical calibration. Otherwise, results are scenario explorations.</p>

        <h3>Digital twin feedback equation</h3>
        <div class="math-block">$$\theta_{t+1} = \lambda \theta_t + (1-\lambda)\hat{\theta}_{evidence} + \delta_{policy}$$</div>
        <p><strong>Plain interpretation:</strong> the twin updates model parameters by blending previous assumptions with evidence-derived estimates and policy intervention effects.</p>
        <p><strong>Policy implication:</strong> field evidence and tested intervention narratives can change the simulated adoption pathway.</p>
        <p><strong>Limitations:</strong> this is an advisory feedback loop unless continuously validated against observed outcomes.</p>

        <h3>Bayesian update</h3>
        <div class="math-block">$$p(\theta \mid y) = \frac{p(y \mid \theta)p(\theta)}{p(y)}$$</div>
        <p><strong>Plain interpretation:</strong> a prior is what the model believes before new evidence. A posterior is what the model believes after seeing evidence. The update does not make the model true; it makes uncertainty explicit.</p>
        <p><strong>Policy implication:</strong> policy recommendations should become more cautious when posterior uncertainty is wide.</p>
        <p><strong>Limitations:</strong> weak priors and poor evidence can produce misleading confidence.</p>

        <h3>RL optimizer</h3>
        <div class="math-block">$$Q_{t+1}(s,a) = Q_t(s,a) + \alpha[r + \gamma \max_{a'}Q_t(s',a') - Q_t(s,a)]$$</div>
        <p><strong>Plain interpretation:</strong> the optimizer learns which intervention action appears to perform best under the current reward assumptions.</p>
        <p><strong>Policy implication:</strong> the optimizer can rank candidate interventions, but the final choice must account for cost, ethics, feasibility, equity, and human review.</p>
        <p><strong>Limitations:</strong> reward design can encode bias. The optimizer is decision support, not an automatic policy maker.</p>
      </details>

      <details id="validation" open>
        <summary>07 / Validation roadmap</summary>
        <ol>
          <li><strong>Synthetic stress testing:</strong> confirm that ingestion, governance, encoding, modelling, and export behave as expected across evidence routes.</li>
          <li><strong>Expert review:</strong> ask subject-matter experts to review the theory, assumptions, workflow, and output language.</li>
          <li><strong>Double-coded narrative dataset:</strong> have at least two trained coders score the same narratives.</li>
          <li><strong>Inter-rater reliability:</strong> measure agreement before using scores as model inputs.</li>
          <li><strong>LLM-versus-human agreement:</strong> compare AI pre-codes with human codes and calibrate disagreement.</li>
          <li><strong>Score calibration:</strong> test whether trust, barrier, misinformation, and inoculation scores map to observed outcomes.</li>
          <li><strong>Sensitivity analysis:</strong> vary parameters to identify which assumptions drive results.</li>
          <li><strong>Posterior uncertainty checks:</strong> report intervals and warnings when evidence is thin.</li>
          <li><strong>Retrospective case comparison:</strong> compare NDIM outputs with known historical adoption patterns.</li>
          <li><strong>Field pilot:</strong> collect narratives, run NDIM, and compare predictions with follow-up observations.</li>
          <li><strong>Prospective validation:</strong> pre-register model assumptions and test future outcomes.</li>
          <li><strong>Policy-user evaluation:</strong> test whether researchers and policy makers understand, trust, and appropriately limit the outputs.</li>
        </ol>
      </details>

      <details id="readiness" open>
        <summary>08 / Publication readiness assessment</summary>
        <table>
          <thead><tr><th>Article type</th><th>Fit for NDIM now</th><th>Already ready</th><th>Missing</th><th>Risk of overclaiming</th><th>Recommended next action</th></tr></thead>
          <tbody>
            <tr><td data-label="Article type">Methods article</td><td data-label="Fit now" class="status-good">Strong</td><td data-label="Already ready">Framework, equations, software workflow, reproducibility argument.</td><td data-label="Missing">Validation dataset and independent review.</td><td data-label="Risk" class="status-warn">Moderate</td><td data-label="Next action">Write as proposed method with validation roadmap.</td></tr>
            <tr><td data-label="Article type">Conceptual Analysis</td><td data-label="Fit now" class="status-good">Strong</td><td data-label="Already ready">Theory integration and careful comparison to prior work.</td><td data-label="Missing">Sharper literature review and theoretical positioning.</td><td data-label="Risk" class="status-warn">Moderate</td><td data-label="Next action">Develop narrative theory and inoculation framing.</td></tr>
            <tr><td data-label="Article type">Policy & Practice Review</td><td data-label="Fit now" class="status-good">Good</td><td data-label="Already ready">Policy workflow, evidence governance, ethics, implementation discussion.</td><td data-label="Missing">Practice cases and user feedback.</td><td data-label="Risk" class="status-warn">Moderate</td><td data-label="Next action">Add case use and policy-user review.</td></tr>
            <tr><td data-label="Article type">Brief Research Report</td><td data-label="Fit now" class="status-warn">Possible</td><td data-label="Already ready">Prototype implementation and stress-test corpus.</td><td data-label="Missing">Pilot data or evaluation result.</td><td data-label="Risk" class="status-warn">Moderate-high</td><td data-label="Next action">Run a bounded pilot or expert evaluation.</td></tr>
            <tr><td data-label="Article type">Original Research</td><td data-label="Fit now" class="status-bad">Not yet</td><td data-label="Already ready">Research design direction.</td><td data-label="Missing">Empirical field data, validation, inferential analysis.</td><td data-label="Risk" class="status-bad">High</td><td data-label="Next action">Collect and validate real data first.</td></tr>
            <tr><td data-label="Article type">Data Report</td><td data-label="Fit now" class="status-bad">Not yet</td><td data-label="Already ready">Synthetic stress corpus only.</td><td data-label="Missing">Validated public dataset with consent and documentation.</td><td data-label="Risk" class="status-bad">High</td><td data-label="Next action">Build approved dataset and data dictionary.</td></tr>
          </tbody>
        </table>
      </details>

      <details id="figures" open>
        <summary>09 / Draft figures for publication</summary>
        <ol class="figure-list">
          <li><strong>NDIM evidence-to-policy workflow diagram:</strong> field narrative to governance, encoding, model, twin, learning, synthesis, and policy brief.</li>
          <li><strong>SDMX narrative governance schema:</strong> route, country, administrative unit, period, source, consent, visibility, and review status.</li>
          <li><strong>S/M/T/I/R compartmental model:</strong> state nodes and transition arrows with trust, misinformation, inoculation, adoption, and resistance pathways.</li>
          <li><strong>Agent-based model architecture:</strong> households, peer network, trust, barriers, access, and local messenger influence.</li>
          <li><strong>Digital twin feedback loop:</strong> approved evidence, encoded narratives, model outputs, posterior learning, intervention tests, and updated scenarios.</li>
          <li><strong>Inoculation intervention pathway:</strong> threat recognition, weak-dose claim, refutational preemption, trusted messenger, booster message, and model response.</li>
          <li><strong>Validation roadmap:</strong> synthetic tests to expert review, double coding, calibration, pilot, and prospective validation.</li>
          <li><strong>Policy output evidence chain:</strong> source trail, model assumptions, uncertainty, recommendation, limitations, and human review.</li>
        </ol>
      </details>

      <details id="ethics" open>
        <summary>10 / Research integrity and ethics</summary>
        <ul>
          <li><strong>Consent:</strong> narratives should not enter policy analysis without consent and visibility status.</li>
          <li><strong>Indigenous knowledge governance:</strong> local knowledge needs attribution rules, cultural sensitivity, community validation, and benefit-sharing plans.</li>
          <li><strong>Sensitive narratives:</strong> personal or politically sensitive evidence must be protected and minimized.</li>
          <li><strong>Misinformation risk:</strong> the tool should not amplify harmful claims without containment and review.</li>
          <li><strong>LLM limitations:</strong> AI encoding can assist, but should be audited against human coding and never treated as neutral truth.</li>
          <li><strong>Injection attacks:</strong> malicious or false narratives need detection, hashing, review, and rejection paths.</li>
          <li><strong>Auditability:</strong> every transformation from story to model input should be traceable.</li>
          <li><strong>Data privacy:</strong> support bundles and exports should avoid leaking sensitive evidence by default.</li>
          <li><strong>Human review:</strong> policy output must require human review before action.</li>
          <li><strong>Policy misuse prevention:</strong> low-evidence or high-uncertainty outputs should carry "do not use for policy" warnings.</li>
        </ul>
      </details>

      <details id="references" open>
        <summary>11 / Reference starter list</summary>
        <p>This is a starter bibliography map. It must be verified before manuscript submission. Do not treat placeholders as final citation details.</p>
        <ul>
          <li><strong>Inoculation theory:</strong> McGuire, 1964; inoculation and resistance-to-persuasion literature. Verify exact source details.</li>
          <li><strong>Misinformation inoculation and pre-bunking:</strong> recent psychological and communication studies. Add verified sources after literature review.</li>
          <li><strong>Rumor spreading models:</strong> Daley-Kendall and Maki-Thompson traditions. Verify exact editions and mathematical assumptions.</li>
          <li><strong>SIR/SEIR adaptations:</strong> epidemiological compartmental modelling and misinformation diffusion adaptations. Verify current review papers.</li>
          <li><strong>Social contagion:</strong> threshold models, network diffusion, information cascades, peer effects.</li>
          <li><strong>Agent-based adoption modelling:</strong> household adoption, social influence, energy technology adoption, and behavioral design literature.</li>
          <li><strong>Digital twins for policy:</strong> decision-support twins, scenario modelling, and civic or policy simulation literature.</li>
          <li><strong>Bayesian updating:</strong> Bayesian inference, uncertainty quantification, posterior predictive checks.</li>
          <li><strong>Reinforcement learning for decision support:</strong> RL policy optimization with human-in-the-loop governance.</li>
          <li><strong>Participatory and citizen-science evidence governance:</strong> community knowledge, consent, data sovereignty, and ethical field evidence.</li>
          <li><strong>SDMX and statistical metadata:</strong> official SDMX documentation and statistical data exchange standards.</li>
        </ul>
      </details>
    </main>

    <a class="button back-top" href="#top">Back to top</a>

    <script id="publicationMarkdown" type="text/plain"># NDIM Engine Scientific Publication Brief

## Positioning
NDIM is the Narrative Diffusion and Inoculation Model: a governed evidence-to-policy workflow linking narratives, inoculation theory, compartmental modelling, agent-based modelling, digital twin feedback, Bayesian updating, reinforcement-learning policy optimization, knowledge graphs, and policy brief generation.

Current defensible claim: NDIM is a proposed, reproducible, testable methodological framework and research software workflow. It is not yet an empirically validated causal model.

## Best article types now
- Methods article
- Conceptual Analysis
- Policy & Practice Review

## Article types that require more evidence
- Original Research
- Data Report

## Candidate abstract
Community narratives can shape adoption of climate, health, and development interventions. NDIM proposes a reproducible framework for linking governed narrative evidence to simulation-informed policy support. It combines SDMX-inspired intake, evidence governance, inoculation-aware encoding, compartmental modelling, agent-based modelling, digital twin feedback, Bayesian uncertainty updating, reinforcement-learning policy optimization, knowledge graph synthesis, and policy brief generation. The current contribution is methodological; empirical validation remains required.

## Validation roadmap
Synthetic stress testing; expert review; double-coded narratives; inter-rater reliability; LLM-versus-human agreement; score calibration; sensitivity analysis; posterior uncertainty checks; retrospective comparison; field pilot; prospective validation; policy-user evaluation.

## Research integrity
Consent, indigenous knowledge governance, sensitive narratives, misinformation risk, LLM limitations, injection attacks, auditability, privacy, human review, and misuse prevention must be explicit.
</script>

    <script>
      function downloadText(filename, text, type) {
        const blob = new Blob([text], { type });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        a.remove();
        URL.revokeObjectURL(url);
      }
      document.getElementById("downloadHtml").addEventListener("click", () => {
        downloadText("ndim-scientific-publication-brief.html", "<!doctype html>\\n" + document.documentElement.outerHTML, "text/html");
      });
      document.getElementById("downloadMarkdown").addEventListener("click", () => {
        downloadText("ndim-scientific-publication-outline.md", document.getElementById("publicationMarkdown").textContent.trim() + "\\n", "text/markdown");
      });
      document.getElementById("printPdf").addEventListener("click", () => window.print());
    </script>
  </body>
</html>
"""
