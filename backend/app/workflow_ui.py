WORKFLOW_UI_HTML = r"""<!doctype html>
<html lang="en" data-theme="light">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>NDIM Engine Stepwise Workflow</title>
    <link rel="icon" href="data:," />
    <style>
      :root {
        color-scheme: light;
        --font-ui: "Myriad Pro", "Myriad Set Pro", "Segoe UI", Arial, sans-serif;
        --font-data: "Cascadia Mono", "JetBrains Mono", Consolas, monospace;
        --ink: #14110e;
        --paper: #fbfaf7;
        --wash: #f5f1ea;
        --linen: #eee8dc;
        --sand: #d9cfbf;
        --taupe: #b8aa93;
        --clay: #8f8069;
        --bg: #070a12;
        --panel: #101827;
        --panel-2: #0d1320;
        --card: #141f33;
        --line: rgba(148, 163, 184, .2);
        --line-strong: rgba(109, 141, 255, .42);
        --text: #f4f7fb;
        --muted: #b9c3d1;
        --soft: #7f8da3;
        --blue: #6d8dff;
        --green: #22c55e;
        --amber: #f59e0b;
        --red: #f97316;
        --violet: #a78bfa;
      }
      :root[data-theme="light"] {
        color-scheme: light;
        --bg: #f7f3ed;
        --panel: #fbfaf7;
        --panel-2: #f1ece3;
        --card: #fffdf9;
        --line: rgba(185, 170, 145, .58);
        --line-strong: #14110e;
        --text: #14110e;
        --muted: #6f6250;
        --soft: #b8aa93;
        --blue: #14110e;
        --green: #6d7f59;
        --amber: #b49362;
        --red: #a6654a;
        --violet: #8a7895;
      }
      :root[data-theme="dark"] {
        color-scheme: dark;
        --ink: #f4f0e8;
        --paper: #0d1320;
        --wash: #121826;
        --linen: #1d2738;
        --sand: #3a4254;
        --taupe: #9c907e;
        --clay: #c9bca8;
        --bg: #070a12;
        --panel: #101827;
        --panel-2: #0d1320;
        --card: #141f33;
        --line: rgba(148, 163, 184, .2);
        --line-strong: rgba(242, 236, 225, .62);
        --text: #f4f0e8;
        --muted: #c9bca8;
        --soft: #8f8069;
        --blue: #f4f0e8;
        --green: #22c55e;
        --amber: #d6bd95;
        --red: #f97316;
        --violet: #a78bfa;
      }
      html {
        overflow-x: hidden;
        text-size-adjust: 100%;
        -webkit-text-size-adjust: 100%;
      }
      * { box-sizing: border-box; }
      * { min-width: 0; }
      body {
        margin: 0;
        min-height: 100vh;
        overflow-x: hidden;
        background:
          linear-gradient(180deg, rgba(255, 255, 255, .55), transparent 220px),
          var(--bg);
        color: var(--text);
        font-family: var(--font-ui);
      }
      button, input, textarea, select { font: inherit; }
      input, textarea, select, button {
        max-width: 100%;
      }
      button { cursor: pointer; }
      .app {
        --sidebar-w: 248px;
        display: grid;
        grid-template-columns: var(--sidebar-w) minmax(0, 1fr);
        width: 100%;
        max-width: 100vw;
        min-height: 100vh;
      }
      .sidebar, .reasoning {
        background: var(--panel);
        min-width: 0;
        min-height: 0;
      }
      .sidebar {
        border-right: 1px solid var(--line);
        display: flex;
        flex-direction: column;
      }
      .reasoning {
        position: fixed;
        z-index: 60;
        top: 18px;
        right: 18px;
        bottom: 18px;
        width: min(430px, calc(100vw - 28px));
        border: 1px solid var(--line);
        border-radius: 18px;
        box-shadow: 0 24px 80px rgba(20, 17, 14, .18);
        display: flex;
        flex-direction: column;
        transform: translateX(calc(100% + 28px));
        transition: transform .2s ease;
        overflow: hidden;
      }
      .reasoning.open {
        transform: translateX(0);
      }
      .brand {
        height: 66px;
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 0 16px;
        border-bottom: 1px solid var(--line);
      }
      .mark {
        width: 34px;
        height: 34px;
        display: grid;
        place-items: center;
        border: 1px solid var(--ink);
        border-radius: 99px;
        background: var(--ink);
        color: var(--paper);
        font: 800 12px var(--font-data);
      }
      .brand strong { display: block; line-height: 1; }
      .brand span {
        display: block;
        margin-top: 4px;
        color: var(--soft);
        font: 9px var(--font-data);
        letter-spacing: 1.4px;
        text-transform: uppercase;
        overflow-wrap: anywhere;
      }
      .stepper {
        padding: 14px;
        overflow: auto;
      }
      .eyebrow, .section-label {
        margin: 0 0 8px;
        color: var(--soft);
        font: 10px var(--font-data);
        letter-spacing: 1.3px;
        text-transform: uppercase;
      }
      .step-list {
        display: grid;
        gap: 8px;
      }
      .step-button {
        width: 100%;
        display: grid;
        grid-template-columns: 34px minmax(0, 1fr);
        gap: 10px;
        border: 1px solid var(--line);
        border-radius: 12px;
        background: var(--panel-2);
        color: var(--muted);
        padding: 10px;
        text-align: left;
      }
      .step-button.active {
        border-color: var(--line-strong);
        color: var(--text);
        box-shadow: inset 3px 0 0 var(--line-strong);
      }
      .step-button.done .num {
        color: var(--green);
        border-color: rgba(34, 197, 94, .4);
      }
      .num {
        width: 32px;
        height: 32px;
        display: grid;
        place-items: center;
        border: 1px solid var(--line);
        border-radius: 9px;
        color: var(--blue);
        font: 800 10px var(--font-data);
      }
      .step-button strong {
        display: block;
        font-size: 13px;
        line-height: 1.2;
        overflow-wrap: anywhere;
      }
      .step-button span span {
        display: block;
        margin-top: 3px;
        color: var(--soft);
        font: 10px var(--font-data);
        overflow-wrap: anywhere;
      }
      .sidebar-footer {
        margin-top: auto;
        padding: 12px;
        border-top: 1px solid var(--line);
        display: grid;
        gap: 8px;
      }
      .theme-toggle {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 4px;
        padding: 4px;
        border: 1px solid var(--line);
        border-radius: 10px;
        background: var(--panel-2);
      }
      .theme-toggle button {
        border: 0;
        border-radius: 7px;
        background: transparent;
        color: var(--soft);
        padding: 7px;
        font: 10px var(--font-data);
      }
      .theme-toggle button.active {
        background: var(--card);
        color: var(--text);
        font-weight: 800;
      }
      .main {
        min-width: 0;
        display: flex;
        flex-direction: column;
        max-width: 100vw;
      }
      .topbar {
        min-height: 66px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
        padding: 9px 18px;
        border-bottom: 1px solid var(--line);
        background: var(--panel);
      }
      h1, h2, h3, p { margin-top: 0; }
      h1 {
        margin: 0;
        font-size: 21px;
        line-height: 1.05;
        overflow-wrap: anywhere;
      }
      .topbar p {
        margin: 4px 0 0;
        max-width: 820px;
        color: var(--muted);
        font-size: 12px;
        line-height: 1.35;
      }
      .ndim-background {
        display: none;
      }
      .run-status {
        display: inline-flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 8px;
        border: 1px solid var(--line);
        border-radius: 999px;
        background: var(--card);
        color: var(--muted);
        padding: 8px 12px;
        font: 800 10px var(--font-data);
        text-transform: uppercase;
        white-space: normal;
        line-height: 1.25;
      }
      .dot {
        width: 8px;
        height: 8px;
        border-radius: 99px;
        background: var(--soft);
      }
      .run-status.running .dot { background: var(--amber); }
      .run-status.complete .dot { background: var(--green); }
      .run-status.error .dot { background: var(--red); }
      .content {
        --content-x: 18px;
        overflow: visible;
        padding: 16px var(--content-x) 22px;
        min-width: 0;
      }
      .command-center {
        position: relative;
        z-index: 2;
        max-width: none;
        width: calc(100% + var(--sidebar-w) + (var(--content-x) * 2));
        margin: 0 calc(var(--content-x) * -1) 14px calc((var(--sidebar-w) + var(--content-x)) * -1);
        border: 1px solid var(--line);
        border-left: 0;
        border-right: 0;
        border-radius: 0;
        background: var(--panel);
        box-shadow: 0 28px 80px rgba(41, 33, 24, .08);
        padding: 0;
        overflow: visible;
      }
      .command-center + .stage-card {
        margin-top: 14px;
      }
      .command-head {
        display: grid;
        grid-template-columns: minmax(0, .95fr) minmax(360px, .72fr);
        gap: 14px;
        align-items: start;
        padding: 16px;
      }
      .command-head h2 {
        margin: 0;
        max-width: 820px;
        font-size: clamp(24px, 2.4vw, 34px);
        line-height: 1.05;
        letter-spacing: -.015em;
      }
      .command-head p {
        margin: 10px 0 0;
        max-width: 820px;
        color: var(--muted);
        font-size: 13px;
        line-height: 1.5;
      }
      .current-intel {
        border: 1px solid var(--line);
        border-radius: 14px;
        background: var(--card);
        padding: 12px;
        min-width: 0;
      }
      .hero-side {
        display: grid;
        gap: 10px;
        min-width: 0;
      }
      .current-intel strong {
        display: block;
        margin-top: 8px;
        font-size: 18px;
      }
      .current-intel p {
        margin-top: 6px;
        font-size: 12.5px;
      }
      .workbench-actions {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 10px;
      }
      .workbench-actions .button {
        min-height: 34px;
        padding: 8px 12px;
      }
      .reference-links {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 12px;
      }
      .reference-links .button {
        min-height: 34px;
        padding: 8px 12px;
      }
      .feedback-chain {
        border-top: 1px solid var(--line);
        padding: 12px 16px 14px;
      }
      .chain-grid {
        display: grid;
        grid-template-columns: repeat(6, minmax(0, 1fr));
        gap: 8px;
      }
      .chain-node {
        border: 1px solid var(--line);
        border-radius: 12px;
        background: var(--card);
        padding: 10px;
        min-height: 86px;
      }
      .chain-node.ready {
        border-color: rgba(25, 135, 84, .38);
        box-shadow: inset 0 0 0 1px rgba(25, 135, 84, .08);
      }
      .chain-node span {
        display: block;
        color: var(--soft);
        font: 800 9px var(--font-data);
        letter-spacing: .8px;
        text-transform: uppercase;
      }
      .chain-node strong {
        display: block;
        margin-top: 5px;
        font-size: 13px;
      }
      .chain-node p {
        margin: 5px 0 0;
        color: var(--muted);
        font-size: 11.5px;
        line-height: 1.35;
      }
      .status-chip-row {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 14px;
      }
      .status-chip {
        display: inline-flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 7px;
        border: 1px solid var(--line);
        border-radius: 999px;
        background: var(--card);
        color: var(--muted);
        padding: 7px 10px;
        font: 800 10px var(--font-data);
        letter-spacing: .7px;
        text-transform: uppercase;
        max-width: 100%;
        overflow-wrap: anywhere;
        line-height: 1.25;
      }
      .status-chip::before {
        content: "";
        width: 7px;
        height: 7px;
        border-radius: 99px;
        background: var(--soft);
      }
      .status-chip.ready {
        border-color: rgba(34, 197, 94, .42);
        color: var(--green);
      }
      .status-chip.ready::before { background: var(--green); }
      .status-chip.warn {
        border-color: rgba(245, 158, 11, .45);
        color: var(--amber);
      }
      .status-chip.warn::before { background: var(--amber); }
      .command-metrics {
        display: grid;
        grid-template-columns: repeat(5, minmax(0, 1fr));
        gap: 8px;
        padding: 0 18px 18px;
      }
      .command-metric {
        border: 1px solid var(--line);
        border-radius: 12px;
        background: var(--card);
        padding: 10px;
        min-width: 0;
      }
      .command-metric span {
        display: block;
        color: var(--soft);
        font: 800 9px var(--font-data);
        letter-spacing: 1px;
        text-transform: uppercase;
      }
      .command-metric strong {
        display: block;
        margin-top: 5px;
        overflow-wrap: anywhere;
        white-space: normal;
        line-height: 1.15;
        font: 800 clamp(14px, 1.55vw, 20px) var(--font-data);
      }
      .flow-lane {
        display: grid;
        grid-template-columns: repeat(6, minmax(0, 1fr));
        align-items: center;
        gap: 6px;
        border-bottom: 1px solid var(--line);
        background: color-mix(in srgb, var(--panel) 92%, white);
        padding: 10px 16px;
        overflow: visible;
      }
      .flow-card {
        position: relative;
        width: 100%;
        min-height: 34px;
        display: inline-flex;
        justify-content: center;
        gap: 8px;
        align-items: center;
        border: 1px solid var(--line);
        border-radius: 999px;
        background: var(--card);
        color: var(--muted);
        padding: 5px 9px;
        text-align: center;
        transition: color .16s ease, transform .16s ease;
      }
      .flow-card:hover {
        transform: translateY(-1px);
      }
      .flow-card.active {
        color: var(--text);
        border-color: var(--ink);
        background: var(--panel);
      }
      .flow-card.done { color: var(--text); }
      .flow-card b {
        display: inline-grid;
        place-items: center;
        width: 28px;
        height: 28px;
        border: 1px solid var(--line);
        border-radius: 99px;
        color: var(--soft);
        background: var(--panel);
        font: 800 10px var(--font-data);
      }
      .flow-card.done b {
        border-color: var(--sand);
        background: var(--linen);
        color: var(--ink);
      }
      .flow-card.active b {
        border-color: var(--ink);
        background: var(--ink);
        color: var(--paper);
      }
      .flow-card strong {
        display: block;
        margin-top: 0;
        font-size: 12.5px;
        line-height: 1.2;
      }
      .flow-card small {
        display: none;
        position: absolute;
        z-index: 30;
        top: calc(100% + 8px);
        left: 50%;
        width: min(230px, 80vw);
        transform: translateX(-50%);
        border: 1px solid var(--line);
        border-radius: 10px;
        background: var(--ink);
        color: var(--paper);
        padding: 8px 10px;
        box-shadow: 0 16px 40px rgba(20, 17, 14, .18);
        font: 10px var(--font-data);
        line-height: 1.45;
        text-align: left;
      }
      .flow-card:hover small,
      .flow-card:focus-visible small {
        display: block;
      }
      .ledger-card {
        border: 1px solid var(--line);
        border-radius: 13px;
        background: var(--card);
        padding: 12px;
        min-width: 0;
      }
      .ledger-card h3 {
        margin: 0 0 6px;
        font-size: 15px;
      }
      .ledger-card p {
        margin: 0;
        color: var(--muted);
        font-size: 12.5px;
        line-height: 1.55;
      }
      .ledger-table-wrap {
        width: 100%;
        overflow-x: auto;
        margin-top: 10px;
        border: 1px solid var(--line);
        border-radius: 11px;
        background: var(--panel-2);
      }
      .ledger-table {
        width: 100%;
        min-width: 680px;
        border-collapse: collapse;
        table-layout: fixed;
      }
      .ledger-table th,
      .ledger-table td {
        border-bottom: 1px solid var(--line);
        padding: 8px 9px;
        text-align: left;
        vertical-align: middle;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        font-size: 11.5px;
      }
      .ledger-table th {
        color: var(--soft);
        font: 800 9px var(--font-data);
        letter-spacing: .7px;
        text-transform: uppercase;
        background: var(--card);
      }
      .ledger-table tr:last-child td { border-bottom: 0; }
      .record-link {
        border: 0;
        background: transparent;
        padding: 0;
        color: var(--text);
        font: inherit;
        font-weight: 900;
        text-decoration: underline;
        text-underline-offset: 3px;
        cursor: pointer;
      }
      .mini-trace {
        display: grid;
        gap: 8px;
        margin-top: 8px;
      }
      .mini-trace div {
        border-left: 2px solid var(--line-strong);
        padding-left: 8px;
      }
      .top-actions {
        display: flex;
        align-items: center;
        justify-content: flex-end;
        flex-wrap: wrap;
        gap: 8px;
        min-width: 0;
      }
      .stage-card {
        max-width: none;
        width: 100%;
        margin: 0;
        border: 1px solid var(--line);
        border-radius: 18px;
        background: var(--panel);
        padding: 18px;
      }
      .stage-card h2 {
        margin: 0 0 8px;
        font-size: clamp(24px, 3vw, 38px);
        line-height: 1.05;
      }
      .copy {
        margin: 0 0 16px;
        color: var(--muted);
        font-size: 14px;
        line-height: 1.65;
      }
      .grid-2 {
        display: grid;
        grid-template-columns: minmax(0, 1fr) minmax(320px, .85fr);
        gap: 14px;
      }
      .grid-3 {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 12px;
      }
      .route-tabs {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 12px;
      }
      .route-button {
        min-height: 38px;
        border: 1px solid var(--line);
        border-radius: 999px;
        background: var(--card);
        color: var(--muted);
        padding: 0 13px;
        font-weight: 900;
      }
      .route-button.active {
        border-color: var(--ink);
        background: var(--ink);
        color: var(--paper);
      }
      .route-context {
        margin-top: 12px;
        border: 1px solid var(--line);
        border-radius: 13px;
        background: var(--card);
        padding: 12px;
      }
      .compact-control-grid {
        display: grid;
        grid-template-columns: minmax(0, 1.08fr) minmax(0, .92fr);
        gap: 14px;
        margin-bottom: 14px;
        align-items: stretch;
      }
      .compact-control-grid > .panel {
        height: 100%;
        display: flex;
        flex-direction: column;
      }
      .intake-sequence {
        display: grid;
        gap: 14px;
      }
      .intake-linear-block {
        display: grid;
        gap: 14px;
      }
      .intake-linear-block > .panel {
        margin-top: 0 !important;
      }
      .evidence-body-flow {
        display: grid;
        gap: 14px;
      }
      .evidence-body-flow > .panel {
        margin-top: 0 !important;
      }
      .intake-step-grid,
      .intake-review-grid {
        display: grid;
        grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
        gap: 14px;
        align-items: stretch;
      }
      .intake-step-grid > .panel,
      .intake-review-grid > .panel {
        height: 100%;
      }
      .step-kicker {
        display: block;
        margin-bottom: 8px;
        font: 800 10px var(--font-data);
        letter-spacing: 1.6px;
        text-transform: uppercase;
        color: var(--soft);
      }
      .file-control-panel {
        display: flex;
        flex-direction: column;
        justify-content: space-between;
      }
      .intake-option-strip {
        margin-top: 14px;
        padding-top: 14px;
        border-top: 1px solid var(--line);
      }
      .stage-submit-panel {
        display: flex;
        flex-direction: column;
        justify-content: space-between;
      }
      .stage-submit-panel .button-row {
        margin-top: 16px;
      }
      .post-evidence-review {
        scroll-margin-top: 120px;
      }
      .readiness-panel,
      .repository-pointer-panel {
        scroll-margin-top: 120px;
      }
      .repository-pointer-panel .button-row {
        margin-top: 14px;
      }
      .repository-full-view {
        margin-top: 18px;
        border: 1px solid var(--line);
        border-radius: 24px;
        background: var(--panel);
        box-shadow: var(--shadow);
        padding: clamp(18px, 3vw, 28px);
        scroll-margin-top: 90px;
      }
      .repository-full-head {
        display: flex;
        justify-content: space-between;
        gap: 16px;
        align-items: flex-start;
        margin-bottom: 18px;
      }
      .repository-section {
        border: 1px solid var(--line);
        border-radius: 18px;
        background: var(--card);
        padding: 14px;
        margin-top: 14px;
      }
      .repository-section h3 {
        margin: 0;
      }
      .repository-table-wrap {
        margin-top: 12px;
        overflow-x: auto;
      }
      .repository-table {
        width: 100%;
        border-collapse: collapse;
        min-width: 880px;
      }
      .repository-table th,
      .repository-table td {
        border-bottom: 1px solid var(--line);
        padding: 10px;
        text-align: left;
        vertical-align: top;
      }
      .repository-table th {
        color: var(--soft);
        font: 800 10px var(--font-data);
        letter-spacing: 1.2px;
        text-transform: uppercase;
      }
      .repository-table td {
        color: var(--text);
        font-size: 13px;
      }
      .repository-table tr:last-child td {
        border-bottom: 0;
      }
      .repository-tools {
        display: grid;
        grid-template-columns: minmax(0, 1fr) minmax(320px, .8fr);
        gap: 14px;
        margin: 14px 0;
      }
      .repository-filter-bar {
        border: 1px solid var(--line);
        border-radius: 18px;
        background: var(--card);
        padding: 14px;
      }
      .repository-category-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 10px;
        margin-top: 10px;
      }
      .repository-category {
        border: 1px solid var(--line);
        border-radius: 14px;
        background: var(--panel-2);
        padding: 12px;
      }
      .repository-category span {
        display: block;
        color: var(--soft);
        font: 800 10px var(--font-data);
        letter-spacing: 1px;
        text-transform: uppercase;
      }
      .repository-category strong {
        display: block;
        margin-top: 5px;
        font-size: 20px;
      }
      .master-repo-panel {
        border: 1px solid var(--line);
        border-radius: 18px;
        background: var(--card);
        padding: 14px;
      }
      .pulse-focus {
        outline: 3px solid var(--accent);
        outline-offset: 4px;
        transition: outline-color .2s ease, outline-offset .2s ease;
      }
      .compact-select-row {
        display: grid;
        grid-template-columns: minmax(0, 1fr) auto;
        gap: 8px;
        align-items: end;
        margin-top: 10px;
      }
      .compact-select-row .field {
        margin: 0;
      }
      .select-note {
        margin: 8px 0 0;
        color: var(--muted);
        font-size: 12.5px;
        line-height: 1.5;
      }
      .route-context h3 {
        margin: 0 0 5px;
        font-size: 15px;
      }
      .route-context p {
        margin: 0;
        color: var(--muted);
        font-size: 13px;
        line-height: 1.5;
      }
      .intake-utility-grid {
        display: grid;
        grid-template-columns: minmax(0, .8fr) minmax(0, 1.2fr);
        gap: 14px;
        margin-bottom: 14px;
      }
      .quick-actions {
        display: grid;
        gap: 8px;
      }
      .quick-actions .button,
      .quick-actions .manual-link {
        width: 100%;
        justify-content: center;
      }
      .readiness-list {
        display: grid;
        gap: 8px;
        margin-top: 10px;
      }
      .readiness-row {
        display: grid;
        grid-template-columns: minmax(92px, .42fr) minmax(0, 1fr) auto;
        align-items: center;
        gap: 10px;
        border: 1px solid var(--line);
        border-radius: 10px;
        background: var(--panel-2);
        padding: 9px 10px;
        color: var(--muted);
        font-size: 12px;
      }
      .readiness-row strong {
        color: var(--text);
      }
      .readiness-row span:nth-child(2) {
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
      .readiness-row span:last-child {
        font: 800 10px var(--font-data);
        text-transform: uppercase;
        color: var(--soft);
      }
      .readiness-row.ready span:last-child {
        color: var(--green);
      }
      .record-preview {
        margin-top: 14px;
        border: 1px solid var(--line);
        border-radius: 13px;
        background: var(--card);
        padding: 12px;
      }
      .record-preview blockquote {
        margin: 8px 0 0;
        color: var(--muted);
        font-size: 12.5px;
        line-height: 1.55;
      }
      .field-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 10px;
      }
      .field {
        display: grid;
        gap: 6px;
      }
      label, .mini-label {
        color: var(--soft);
        font: 10px var(--font-data);
        text-transform: uppercase;
        letter-spacing: .8px;
      }
      input, select, textarea {
        width: 100%;
        border: 1px solid var(--line);
        border-radius: 10px;
        background: var(--panel-2);
        color: var(--text);
        outline: none;
      }
      input, select { height: 40px; padding: 0 10px; }
      textarea {
        min-height: 220px;
        resize: vertical;
        padding: 12px;
        font-size: 14px;
        line-height: 1.55;
      }
      input:focus, select:focus, textarea:focus { border-color: var(--blue); }
      .checkbox-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 8px;
      }
      .check-card {
        display: flex;
        align-items: center;
        gap: 8px;
        min-height: 38px;
        border: 1px solid var(--line);
        border-radius: 10px;
        background: var(--panel-2);
        padding: 8px 10px;
        color: var(--muted);
        font-weight: 800;
      }
      .check-card input {
        width: 16px;
        height: 16px;
        padding: 0;
        accent-color: var(--ink);
      }
      .button-row {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 14px;
      }
      .button {
        min-height: 38px;
        border: 1px solid var(--line);
        border-radius: 10px;
        background: var(--panel-2);
        color: var(--muted);
        padding: 0 13px;
        font-weight: 800;
        text-align: center;
        overflow-wrap: anywhere;
        line-height: 1.25;
      }
      .button.primary {
        border-color: transparent;
        background: var(--ink);
        color: var(--paper);
      }
      .button.green {
        border-color: transparent;
        background: var(--green);
        color: white;
      }
      .button:hover {
        border-color: var(--line-strong);
        color: var(--text);
      }
      .button.primary:hover,
      .button.primary:focus,
      .button.primary:active {
        border-color: var(--line-strong);
        background: var(--ink);
        color: var(--paper);
      }
      .button.green:hover,
      .button.green:focus,
      .button.green:active {
        color: white;
      }
      .button:focus-visible,
      .flow-card:focus-visible,
      .step-button:focus-visible,
      .record-link:focus-visible {
        outline: 3px solid var(--amber);
        outline-offset: 3px;
      }
      .button:disabled {
        cursor: not-allowed;
        opacity: .55;
      }
      .option {
        border: 1px solid var(--line);
        border-radius: 14px;
        background: var(--panel-2);
        color: var(--muted);
        padding: 14px;
        text-align: left;
      }
      .option.active {
        border-color: var(--line-strong);
        color: var(--text);
        box-shadow: inset 0 0 0 1px rgba(109, 141, 255, .2);
      }
      .option strong {
        display: block;
        margin-bottom: 6px;
        font-size: 15px;
        overflow-wrap: anywhere;
        line-height: 1.25;
      }
      .option span {
        display: block;
        color: var(--soft);
        font-size: 12.5px;
        line-height: 1.45;
        overflow-wrap: anywhere;
      }
      .panel {
        border: 1px solid var(--line);
        border-radius: 14px;
        background: var(--panel-2);
        padding: 14px;
        min-width: 0;
      }
      .panel h3 {
        margin: 0 0 8px;
        font-size: 16px;
        overflow-wrap: anywhere;
      }
      .panel p {
        margin: 0;
        color: var(--muted);
        font-size: 13px;
        line-height: 1.55;
        overflow-wrap: anywhere;
      }
      .check-list {
        display: grid;
        gap: 8px;
      }
      .check {
        display: grid;
        grid-template-columns: 24px minmax(0, 1fr);
        gap: 8px;
        align-items: start;
        border: 1px solid var(--line);
        border-radius: 10px;
        background: var(--card);
        padding: 9px;
      }
      .check i {
        width: 20px;
        height: 20px;
        display: grid;
        place-items: center;
        border-radius: 99px;
        background: rgba(249, 115, 22, .12);
        color: var(--red);
        font-style: normal;
        font: 800 10px var(--font-data);
      }
      .check.pass i {
        background: rgba(34, 197, 94, .12);
        color: var(--green);
      }
      .check strong {
        display: block;
        font-size: 13px;
      }
      .check span {
        display: block;
        margin-top: 3px;
        color: var(--soft);
        font: 10.5px var(--font-data);
      }
      .table {
        border: 1px solid var(--line);
        border-radius: 12px;
        overflow: hidden;
        background: var(--panel-2);
        max-width: 100%;
      }
      .row {
        display: grid;
        grid-template-columns: .7fr 90px 1fr 80px 80px 80px;
        gap: 10px;
        align-items: center;
        border-top: 1px solid var(--line);
        padding: 10px;
        color: var(--muted);
        font: 11px var(--font-data);
      }
      .row span {
        min-width: 0;
        overflow-wrap: anywhere;
        line-height: 1.35;
      }
      .row:first-child { border-top: 0; }
      .row.head {
        background: var(--card);
        color: var(--soft);
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: .7px;
      }
      .metric-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(min(112px, 100%), 1fr));
        gap: 10px;
      }
      .metric {
        border: 1px solid var(--line);
        border-radius: 12px;
        background: var(--panel-2);
        padding: 12px;
        overflow: hidden;
      }
      .metric strong {
        display: block;
        margin-top: 5px;
        max-width: 100%;
        overflow-wrap: anywhere;
        word-break: normal;
        line-height: 1.12;
        font: 800 clamp(15px, 1.6vw, 22px) var(--font-data);
      }
      .bars {
        display: grid;
        gap: 10px;
      }
      .bar-row {
        display: grid;
        grid-template-columns: minmax(90px, 120px) minmax(0, 1fr) minmax(44px, 60px);
        gap: 10px;
        align-items: center;
        color: var(--muted);
        font-size: 12px;
      }
      .bar-row span {
        min-width: 0;
        overflow-wrap: anywhere;
      }
      .bar-track {
        height: 10px;
        border-radius: 999px;
        background: var(--card);
        overflow: hidden;
      }
      .bar-fill {
        height: 100%;
        border-radius: 999px;
        background: var(--blue);
      }
      .json {
        white-space: pre-wrap;
        word-break: break-word;
        color: var(--muted);
        font: 10.5px var(--font-data);
        line-height: 1.55;
        border: 1px solid var(--line);
        border-radius: 12px;
        background: var(--panel-2);
        padding: 12px;
        max-height: 300px;
        overflow: auto;
      }
      .grid-2 > .json {
        grid-column: 1 / -1;
      }
      .payload-body {
        display: grid;
        gap: 10px;
      }
      .payload-item {
        border: 1px solid var(--line);
        border-radius: 12px;
        background: var(--card);
        padding: 11px;
      }
      .payload-item strong {
        display: block;
        margin-bottom: 5px;
        font-size: 13px;
      }
      .payload-item p {
        margin: 0;
        color: var(--muted);
        font-size: 12.5px;
        line-height: 1.55;
      }
      .governance-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 10px;
        margin: 14px 0;
      }
      .governance-card {
        border: 1px solid var(--line);
        border-radius: 12px;
        background: var(--card);
        padding: 12px;
        min-width: 0;
      }
      .governance-card span {
        display: block;
        color: var(--soft);
        font: 800 9px var(--font-data);
        letter-spacing: .8px;
        text-transform: uppercase;
      }
      .governance-card strong {
        display: block;
        margin-top: 5px;
        overflow: hidden;
        overflow-wrap: anywhere;
        line-height: 1.15;
        font: 800 clamp(14px, 1.35vw, 18px) var(--font-data);
      }
      .record-governance {
        display: grid;
        gap: 9px;
        max-height: 430px;
        overflow: auto;
        padding-right: 3px;
      }
      .record-card {
        border: 1px solid var(--line);
        border-radius: 12px;
        background: var(--card);
        padding: 11px;
      }
      .record-card header {
        display: flex;
        justify-content: space-between;
        gap: 10px;
        align-items: flex-start;
      }
      .record-card h4 {
        margin: 0;
        font-size: 13px;
      }
      .record-card p {
        margin: 8px 0 0;
        color: var(--muted);
        font-size: 12px;
        line-height: 1.5;
      }
      .pill-row {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        margin-top: 8px;
      }
      .pill {
        border: 1px solid var(--line);
        border-radius: 999px;
        background: var(--panel-2);
        color: var(--soft);
        padding: 4px 7px;
        font: 800 9px var(--font-data);
        letter-spacing: .5px;
        text-transform: uppercase;
        max-width: 100%;
        overflow-wrap: anywhere;
        line-height: 1.25;
      }
      .pill.ok { color: var(--green); border-color: rgba(34, 197, 94, .35); }
      .pill.warn { color: var(--amber); border-color: rgba(245, 158, 11, .45); }
      .pill.bad { color: var(--red); border-color: rgba(239, 68, 68, .4); }
      .ledger-list {
        display: grid;
        gap: 8px;
        max-height: 260px;
        overflow: auto;
      }
      .ledger-event {
        border-left: 2px solid var(--line-strong);
        padding-left: 9px;
      }
      .ledger-event strong {
        display: block;
        font-size: 12px;
      }
      .ledger-event span {
        display: block;
        margin-top: 3px;
        color: var(--soft);
        font: 10px var(--font-data);
      }
      .equation {
        border: 1px solid var(--line);
        border-radius: 12px;
        background: var(--panel-2);
        color: var(--text);
        padding: 12px;
        font: 12px var(--font-data);
        line-height: 1.7;
      }
      .equation span {
        color: var(--blue);
      }
      .equation b {
        color: var(--amber);
      }
      .guide-note {
        border: 1px solid var(--line);
        border-left: 3px solid var(--blue);
        border-radius: 12px;
        background: var(--card);
        padding: 12px;
        margin-top: 12px;
      }
      .guide-note.danger {
        border-left-color: var(--red);
      }
      .guide-note strong {
        display: block;
        margin-bottom: 5px;
        font-size: 13px;
      }
      .guide-note p {
        margin: 0;
        color: var(--muted);
        font-size: 12.5px;
        line-height: 1.55;
      }
      .plot-card {
        border: 1px solid var(--line);
        border-radius: 12px;
        background: var(--panel-2);
        padding: 12px;
        margin-top: 14px;
        overflow: hidden;
      }
      .plot-title {
        color: var(--text);
        font-size: 13px;
        font-weight: 800;
        margin-bottom: 8px;
      }
      .plot-card svg {
        display: block;
        width: 100%;
        height: 220px;
      }
      .plot-grid-line {
        stroke: var(--line);
        stroke-width: 1;
      }
      .plot-axis-label {
        fill: var(--soft);
        font: 10px var(--font-data);
      }
      .plot-legend {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-top: 8px;
        color: var(--soft);
        font: 10px var(--font-data);
      }
      .plot-legend span {
        display: inline-flex;
        align-items: center;
        gap: 5px;
      }
      .legend-swatch {
        width: 10px;
        height: 3px;
        border-radius: 99px;
      }
      .insight-list {
        display: grid;
        gap: 10px;
        margin-top: 12px;
      }
      .insight {
        border: 1px solid var(--line);
        border-radius: 12px;
        background: var(--card);
        padding: 12px;
      }
      .insight strong {
        display: block;
        margin-bottom: 5px;
        font-size: 13px;
      }
      .insight p {
        margin: 0;
        color: var(--muted);
        font-size: 12.5px;
        line-height: 1.55;
      }
      .pill-row {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        margin-top: 8px;
      }
      .pill {
        border: 1px solid var(--line);
        border-radius: 999px;
        background: var(--panel-2);
        color: var(--muted);
        padding: 5px 8px;
        font: 10px var(--font-data);
        max-width: 100%;
        overflow-wrap: anywhere;
        line-height: 1.25;
      }
      .kg-svg {
        width: 100%;
        min-height: 340px;
        height: auto;
        border: 1px solid var(--line);
        border-radius: 12px;
        background: var(--panel-2);
      }
      .feed-item, .counter-card {
        border: 1px solid var(--line);
        border-radius: 12px;
        background: var(--card);
        padding: 12px;
      }
      .feed-item + .feed-item, .counter-card + .counter-card { margin-top: 10px; }
      .feed-item p, .counter-card p {
        margin: 6px 0 0;
        color: var(--muted);
        font-size: 12.5px;
        line-height: 1.55;
      }
      .result-note {
        border: 1px solid var(--line);
        border-radius: 12px;
        background: var(--card);
        padding: 12px;
        margin-top: 12px;
      }
      .result-note p {
        margin: 0;
        color: var(--muted);
        font-size: 12.5px;
        line-height: 1.55;
      }
      .compare-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 10px;
        margin-top: 12px;
      }
      .compare-card {
        border: 1px solid var(--line);
        border-radius: 12px;
        background: var(--panel-2);
        padding: 12px;
      }
      .compare-card.active {
        border-color: var(--line-strong);
      }
      .compare-card h3 {
        margin: 0 0 8px;
        font-size: 15px;
      }
      .compare-card p {
        margin: 0;
        color: var(--muted);
        font-size: 12px;
        line-height: 1.5;
      }
      .encoding-queue {
        display: grid;
        gap: 8px;
        max-height: 310px;
        overflow: auto;
        padding-right: 4px;
      }
      .queue-item {
        width: 100%;
        border: 1px solid var(--line);
        border-radius: 12px;
        background: var(--panel-2);
        color: var(--text);
        padding: 10px;
        text-align: left;
      }
      .queue-item.active {
        border-color: var(--line-strong);
        box-shadow: 0 0 0 2px rgba(17, 24, 39, .05);
      }
      .queue-item strong {
        display: block;
        font-size: 12.5px;
      }
      .queue-item span {
        display: block;
        margin-top: 3px;
        color: var(--muted);
        font-size: 11px;
        line-height: 1.45;
      }
      .scorecard-grid {
        display: grid;
        gap: 10px;
        margin-top: 12px;
      }
      .score-rule {
        border: 1px solid var(--line);
        border-radius: 13px;
        background: var(--card);
        padding: 12px;
      }
      .score-rule header {
        display: flex;
        justify-content: space-between;
        gap: 10px;
        align-items: flex-start;
      }
      .score-rule h4 {
        margin: 0;
        font-size: 14px;
      }
      .score-rule code {
        border: 1px solid var(--line);
        border-radius: 999px;
        padding: 3px 7px;
        background: var(--panel-2);
        font: 700 11px var(--font-data);
      }
      .score-rule p {
        margin-top: 8px;
        color: var(--muted);
        font-size: 12.5px;
        line-height: 1.5;
      }
      .score-scale {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 7px;
        margin-top: 10px;
      }
      .score-scale span {
        border: 1px solid var(--line);
        border-radius: 10px;
        background: var(--panel-2);
        padding: 8px;
        color: var(--muted);
        font-size: 11px;
        line-height: 1.35;
      }
      .score-input-row {
        display: grid;
        grid-template-columns: minmax(92px, 120px) minmax(0, 1fr);
        gap: 8px;
        margin-top: 10px;
      }
      .story-card {
        border: 1px solid var(--line);
        border-radius: 12px;
        background: var(--panel-2);
        padding: 12px;
      }
      .story-card blockquote {
        margin: 8px 0 0;
        color: var(--muted);
        font-size: 13px;
        line-height: 1.55;
      }
      .question-stack {
        display: grid;
        gap: 10px;
      }
      .question-card {
        border: 1px solid var(--line);
        border-radius: 13px;
        background: var(--card);
        overflow: hidden;
      }
      .question-card summary {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 10px;
        padding: 12px;
        cursor: pointer;
        list-style: none;
      }
      .question-card summary::-webkit-details-marker { display: none; }
      .question-card h3 {
        margin: 0;
        font-size: 14px;
      }
      .question-card p {
        margin: 0 0 8px;
        color: var(--muted);
        font-size: 12.5px;
        line-height: 1.5;
      }
      .question-body {
        border-top: 1px solid var(--line);
        padding: 0 12px 12px;
      }
      .question-card textarea {
        min-height: 84px;
      }
      .template-table {
        border: 1px solid var(--line);
        border-radius: 12px;
        overflow: hidden;
        background: var(--panel-2);
      }
      .template-row {
        display: grid;
        grid-template-columns: minmax(150px, .8fr) minmax(0, 1fr) 92px;
        gap: 10px;
        align-items: center;
        border-top: 1px solid var(--line);
        padding: 10px;
        color: var(--muted);
        font-size: 12px;
      }
      .template-row span {
        min-width: 0;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        line-height: 1.35;
      }
      .template-row:first-child { border-top: 0; }
      .template-row.head {
        background: var(--card);
        color: var(--soft);
        font: 800 10px var(--font-data);
        letter-spacing: .7px;
        text-transform: uppercase;
      }
      .admin-hint {
        margin: 8px 0 0;
        color: var(--soft);
        font-size: 12.5px;
        line-height: 1.5;
      }
      .manual-link {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-height: 34px;
        border: 1px solid var(--line);
        border-radius: 10px;
        background: var(--panel-2);
        color: var(--muted);
        text-decoration: none;
        padding: 0 12px;
        font-size: 12px;
        font-weight: 800;
        text-align: center;
        overflow-wrap: anywhere;
      }
      .stage-nav {
        max-width: none;
        width: 100%;
        margin: 12px auto 0;
        display: flex;
        justify-content: space-between;
        gap: 10px;
      }
      .context-stage-nav {
        display: flex;
        flex-wrap: wrap;
        justify-content: flex-end;
        gap: 10px;
        margin-top: 14px;
        border: 1px solid var(--line);
        border-radius: 18px;
        background: var(--panel);
        padding: 12px;
      }
      .context-stage-nav .nav-note {
        margin-right: auto;
        color: var(--muted);
        font-size: 13px;
        line-height: 1.45;
      }
      .reason-head {
        border-bottom: 1px solid var(--line);
        padding: 16px;
        flex-shrink: 0;
      }
      .reason-head h2 {
        margin: 0;
        font-size: 18px;
      }
      .reason-body {
        padding: 14px;
        overflow: auto;
        display: grid;
        gap: 10px;
        min-height: 0;
      }
      .trace {
        border: 1px solid var(--line);
        border-radius: 13px;
        background: var(--panel-2);
        padding: 11px;
      }
      .trace-top {
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 10px;
        margin-bottom: 6px;
      }
      .trace strong {
        color: var(--text);
        font-size: 13px;
        overflow-wrap: anywhere;
      }
      .trace small {
        color: var(--blue);
        font: 800 10px var(--font-data);
        text-transform: uppercase;
        overflow-wrap: anywhere;
      }
      .trace p {
        margin: 0;
        color: var(--muted);
        font-size: 12.5px;
        line-height: 1.55;
      }
      .toast {
        position: fixed;
        right: 18px;
        bottom: 18px;
        border: 1px solid var(--line);
        border-radius: 10px;
        background: var(--panel);
        color: var(--text);
        padding: 10px 12px;
        font-size: 12px;
        opacity: 0;
        transform: translateY(8px);
        transition: .16s ease;
      }
      .toast.show { opacity: 1; transform: none; }
      @media (max-width: 1180px) {
        .app {
          --sidebar-w: 220px;
          grid-template-columns: var(--sidebar-w) minmax(0, 1fr);
        }
        .grid-2 { grid-template-columns: 1fr; }
        .command-head, .intake-utility-grid, .compact-control-grid, .intake-step-grid, .intake-review-grid { grid-template-columns: 1fr; }
        .flow-lane { grid-template-columns: repeat(3, minmax(0, 1fr)); }
        .chain-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
      }
      @media (max-width: 980px) {
        .app {
          --sidebar-w: 0px;
          grid-template-columns: 1fr;
        }
        .sidebar {
          border-right: 0;
          border-bottom: 1px solid var(--line);
        }
        .brand {
          min-height: 62px;
        }
        .stepper {
          padding: 10px 12px 12px;
          overflow-x: auto;
          overflow-y: hidden;
          overscroll-behavior-x: contain;
        }
        .step-list {
          display: flex;
          gap: 8px;
          min-width: max-content;
          scroll-snap-type: x proximity;
        }
        .step-button {
          width: 190px;
          scroll-snap-align: start;
        }
        .sidebar-footer {
          grid-template-columns: minmax(0, 1fr) auto;
          align-items: center;
        }
        .reasoning { top: 12px; right: 12px; bottom: 12px; }
        .command-metrics {
          grid-template-columns: repeat(3, minmax(0, 1fr));
        }
        .governance-grid {
          grid-template-columns: repeat(2, minmax(0, 1fr));
        }
      }
      @media (max-width: 760px) {
        .app {
          --sidebar-w: 0px;
          grid-template-columns: 1fr;
        }
        .sidebar { max-height: none; }
        .topbar { align-items: flex-start; flex-direction: column; padding: 16px; }
        .top-actions, .top-actions .button, .run-status { width: 100%; justify-content: center; }
        .content { --content-x: 14px; padding: 14px var(--content-x); }
        .stage-card { border-radius: 14px; }
        .command-center { border-radius: 0; }
        .command-head { padding: 14px; }
        .command-head h2 { font-size: clamp(26px, 9vw, 38px); }
        .flow-lane {
          grid-template-columns: 1fr;
          gap: 8px;
          padding: 12px;
        }
        .chain-grid, .checkbox-grid {
          grid-template-columns: 1fr;
        }
        .flow-card {
          min-height: 48px;
          border: 1px solid var(--line);
          border-radius: 12px;
          background: var(--panel-2);
          padding: 9px;
        }
        .flow-card b {
          width: 34px;
          height: 34px;
        }
        .flow-card strong { font-size: 14px; }
        .flow-card small { display: none !important; }
        .stage-card { padding: 14px; }
        .stage-card h2 { font-size: clamp(24px, 8vw, 34px); }
        .field-grid, .grid-3, .metric-grid, .command-metrics, .governance-grid, .compare-grid, .intake-utility-grid, .compact-control-grid, .intake-step-grid, .intake-review-grid, .compact-select-row { grid-template-columns: 1fr; }
        input, select { min-height: 44px; }
        textarea { min-height: 160px; }
        .button, .manual-link {
          min-height: 44px;
          display: inline-flex;
          align-items: center;
          justify-content: center;
        }
        .row {
          grid-template-columns: 1fr;
          min-width: 0;
          align-items: start;
          gap: 7px;
          border-top: 1px solid var(--line);
          padding: 12px;
        }
        .row.head { display: none; }
        .row span[data-label]::before,
        .template-row span[data-label]::before {
          content: attr(data-label);
          display: block;
          margin-bottom: 3px;
          color: var(--soft);
          font: 800 9px var(--font-data);
          letter-spacing: .7px;
          text-transform: uppercase;
        }
        .template-row {
          grid-template-columns: 1fr;
          align-items: start;
          gap: 8px;
          padding: 12px;
        }
        .template-row.head { display: none; }
        .record-card header,
        .score-rule header,
        .question-card summary {
          flex-direction: column;
          align-items: flex-start;
        }
        .score-scale, .score-input-row, .bar-row {
          grid-template-columns: 1fr;
        }
        .score-scale { gap: 8px; }
        .plot-card { padding: 10px; }
        .kg-svg { min-height: 260px; }
        .table, .template-table { overflow: visible; }
        .ledger-table-wrap { overflow-x: auto; }
        .stage-nav { flex-direction: column; }
      }
      @media (max-width: 520px) {
        .brand { height: auto; align-items: flex-start; padding: 14px; }
        .stepper { padding: 10px; }
        .step-button { width: 174px; grid-template-columns: 30px minmax(0, 1fr); padding: 9px; }
        .sidebar-footer { grid-template-columns: 1fr; }
        .num { width: 28px; height: 28px; }
        .row { grid-template-columns: 1fr; }
        .button, .manual-link { width: 100%; }
        .button-row { width: 100%; display: grid; grid-template-columns: 1fr; }
        .command-head h2 { font-size: clamp(25px, 10vw, 34px); }
        .status-chip { width: 100%; justify-content: center; }
        .current-intel strong { font-size: 16px; }
        .panel, .metric, .score-rule, .record-card, .question-card, .payload-item { border-radius: 11px; }
        .plot-card svg { height: 180px; }
      }
    </style>
  </head>
  <body>
    <div class="app">
      <aside class="sidebar">
        <div class="brand">
          <div class="mark">ND</div>
          <div>
            <strong>NDIM Engine</strong>
            <span>Narrative Diffusion and Inoculation Model</span>
          </div>
        </div>
        <div class="stepper">
          <p class="section-label">Workflow stages</p>
          <div class="step-list" id="stepList"></div>
        </div>
        <div class="sidebar-footer">
          <div class="theme-toggle" id="themeToggle">
            <button data-theme="dark">dark</button>
            <button class="active" data-theme="light">light</button>
          </div>
          <a class="button" href="https://github.com/Naphymoro/nidm-rwanda-dashboard" target="_blank" rel="noreferrer">GitHub source</a>
        </div>
      </aside>

      <main class="main">
        <header class="topbar">
          <div>
            <p class="eyebrow">Grounded evidence engine</p>
            <h1 id="topTitle">Narrative intake</h1>
            <p class="ndim-background">Narrative Diffusion and Inoculation Model workflow: governed evidence, transparent encoding, model feedback, and policy export.</p>
            <p id="topCopy">Start by defining the evidence context, country, location, source, and narrative text.</p>
          </div>
          <div class="top-actions">
            <div class="run-status" id="runStatus"><span class="dot"></span><span>idle</span></div>
          </div>
        </header>
        <section class="content">
          <div id="stagePanel"></div>
          <div class="stage-nav">
            <button class="button" id="backButton" type="button">Back</button>
            <button class="button" id="resetStageButton" type="button">Reset this stage</button>
            <button class="button primary" id="nextButton" type="button">Next</button>
          </div>
        </section>
      </main>

      <aside class="reasoning">
        <div class="reason-head">
          <p class="eyebrow">Activity log</p>
          <h2>System actions</h2>
          <div class="button-row" style="margin-top: 10px;">
            <button class="button" id="clearTrace" type="button">Clear log</button>
            <button class="button" id="closeTraceButton" type="button">Close</button>
          </div>
        </div>
        <div class="reason-body" id="traceBody"></div>
      </aside>
    </div>
    <div class="toast" id="toast">Ready</div>

    <script>
      const steps = [
        { id: "intake", num: "01", title: "Narrative intake", sub: "country, location, evidence" },
        { id: "gate", num: "02", title: "SDMX gate", sub: "validate input contract" },
        { id: "encoding", num: "03", title: "Encoding", sub: "manual, AI, hybrid" },
        { id: "compartmental", num: "04", title: "Compartmental model", sub: "S M T I R population flow" },
        { id: "agents", num: "05", title: "Agent-based model", sub: "households and peer effects" },
        { id: "digital", num: "06", title: "Digital twin", sub: "feedback into model" },
        { id: "bayes", num: "07", title: "Bayesian update", sub: "prior to posterior" },
        { id: "rl", num: "08", title: "RL optimizer", sub: "learn intervention policy" },
        { id: "regional", num: "09", title: "Regional analysis", sub: "isolate or group places" },
        { id: "graph", num: "10", title: "Knowledge graph", sub: "stories, themes, places" },
        { id: "inoculation", num: "11", title: "Inoculation lab", sub: "counter-narratives" },
        { id: "policy", num: "12", title: "Policy output", sub: "recommendation and audit" }
      ];

      const workflowPhases = [
        { icon: "EV", label: "Evidence", detail: "Narratives, context, SDMX gate", step: 0, stages: ["intake", "gate"] },
        { icon: "EN", label: "Encode", detail: "Manual, AI, hybrid scoring", step: 2, stages: ["encoding"] },
        { icon: "MO", label: "Model", detail: "ODE and agent simulation", step: 3, stages: ["compartmental", "agents"] },
        { icon: "LR", label: "Learn", detail: "Twin, posterior, RL loop", step: 5, stages: ["digital", "bayes", "rl"] },
        { icon: "SY", label: "Synthesize", detail: "Regions, graph, inoculation", step: 8, stages: ["regional", "graph", "inoculation"] },
        { icon: "EX", label: "Export", detail: "Policy output and audit", step: 11, stages: ["policy"] }
      ];

      const adminSchemas = {
        Rwanda: {
          levels: [
            { key: "province", label: "Province", placeholder: "e.g., Southern Province" },
            { key: "district", label: "District", placeholder: "e.g., Nyamagabe / Nyaruguru" },
            { key: "sector", label: "Sector / village", placeholder: "e.g., Gasaka sector / village" }
          ],
          language: "rw",
          note: "Rwanda field sheets usually need province, district, then sector/cell/village detail."
        },
        Kenya: {
          levels: [
            { key: "province", label: "County", placeholder: "e.g., Kisumu County" },
            { key: "district", label: "Sub-county", placeholder: "e.g., Nyando" },
            { key: "sector", label: "Ward / village", placeholder: "e.g., Ahero Ward / village" }
          ],
          language: "en",
          note: "Kenya collection is organized by county, sub-county, then ward or village."
        },
        Uganda: {
          levels: [
            { key: "province", label: "Region", placeholder: "e.g., Western Region" },
            { key: "district", label: "District", placeholder: "e.g., Mbarara" },
            { key: "sector", label: "Sub-county / parish / village", placeholder: "e.g., Biharwe parish" }
          ],
          language: "en",
          note: "Uganda forms commonly capture region, district, and sub-county/parish/village."
        },
        Tanzania: {
          levels: [
            { key: "province", label: "Region", placeholder: "e.g., Arusha Region" },
            { key: "district", label: "District / council", placeholder: "e.g., Arumeru District Council" },
            { key: "sector", label: "Ward / village", placeholder: "e.g., Usa River ward" }
          ],
          language: "sw",
          note: "Tanzania field sheets should identify region, district or council, then ward/village."
        },
        Ghana: {
          levels: [
            { key: "province", label: "Region", placeholder: "e.g., Ashanti Region" },
            { key: "district", label: "District / municipal / metropolitan", placeholder: "e.g., Kumasi Metropolitan" },
            { key: "sector", label: "Community / electoral area", placeholder: "e.g., Bantama community" }
          ],
          language: "en",
          note: "Ghana collection is usually region, district/municipal/metropolitan, then community."
        }
      };

      const adminOptions = {
        Rwanda: {
          province: ["Kigali City", "Eastern Province", "Northern Province", "Southern Province", "Western Province"],
          districtByProvince: {
            "Kigali City": ["Gasabo", "Kicukiro", "Nyarugenge"],
            "Eastern Province": ["Bugesera", "Gatsibo", "Kayonza", "Kirehe", "Ngoma", "Nyagatare", "Rwamagana"],
            "Northern Province": ["Burera", "Gakenke", "Gicumbi", "Musanze", "Rulindo"],
            "Southern Province": ["Gisagara", "Huye", "Kamonyi", "Muhanga", "Nyamagabe", "Nyanza", "Nyaruguru", "Ruhango"],
            "Western Province": ["Karongi", "Ngororero", "Nyabihu", "Nyamasheke", "Rubavu", "Rusizi", "Rutsiro"]
          },
          sectorByDistrict: {
            Musanze: ["Busogo", "Cyuve", "Gacaca", "Gashaki", "Kimonyi", "Kinigi", "Muhoza", "Muko", "Musanze", "Nkotsi", "Nyange", "Remera", "Rwaza", "Shingiro"],
            Nyamagabe: ["Buruhukiro", "Cyanika", "Gasaka", "Gatare", "Kaduha", "Kamegeri", "Kibirizi", "Kibumbwe", "Kitabi", "Mbazi", "Mugano", "Musange", "Musebeya", "Mushubi", "Nkomane", "Tare", "Uwinkingi"],
            Nyaruguru: ["Busanze", "Cyahinda", "Kibeho", "Kivu", "Mata", "Muganza", "Munini", "Ngera", "Ngoma", "Nyabimata", "Nyagisozi", "Ruheru", "Ruramba", "Rusenge"]
          }
        },
        Kenya: {
          province: ["Baringo", "Bomet", "Bungoma", "Busia", "Elgeyo-Marakwet", "Embu", "Garissa", "Homa Bay", "Isiolo", "Kajiado", "Kakamega", "Kericho", "Kiambu", "Kilifi", "Kirinyaga", "Kisii", "Kisumu", "Kitui", "Kwale", "Laikipia", "Lamu", "Machakos", "Makueni", "Mandera", "Marsabit", "Meru", "Migori", "Mombasa", "Murang'a", "Nairobi", "Nakuru", "Nandi", "Narok", "Nyamira", "Nyandarua", "Nyeri", "Samburu", "Siaya", "Taita-Taveta", "Tana River", "Tharaka-Nithi", "Trans Nzoia", "Turkana", "Uasin Gishu", "Vihiga", "Wajir", "West Pokot"],
          districtByProvince: {
            Nairobi: ["Dagoretti", "Embakasi", "Kamukunji", "Kasarani", "Kibra", "Lang'ata", "Makadara", "Mathare", "Njiru", "Starehe", "Westlands"],
            Kisumu: ["Kisumu Central", "Kisumu East", "Kisumu West", "Muhoroni", "Nyakach", "Nyando", "Seme"],
            Mombasa: ["Changamwe", "Jomvu", "Kisauni", "Likoni", "Mvita", "Nyali"],
            Nakuru: ["Bahati", "Gilgil", "Kuresoi North", "Kuresoi South", "Molo", "Naivasha", "Nakuru East", "Nakuru West", "Njoro", "Rongai", "Subukia"]
          },
          sectorByDistrict: {
            Nyando: ["Ahero", "Awasi/Onjiko", "East Kano/Wawidhi", "Kabonyo/Kanyagwal", "Kobura"],
            "Kisumu Central": ["Kisumu Central", "Kondele", "Market Milimani", "Migosi", "Nyalenda A", "Railways"],
            Westlands: ["Karura", "Kangemi", "Kilimani", "Kitisuru", "Mountain View", "Parklands/Highridge"],
            Nyali: ["Frere Town", "Kongowea", "Kadzandani", "Mkomani", "Ziwa la Ng'ombe"]
          }
        },
        Uganda: {
          province: ["Central Region", "Eastern Region", "Northern Region", "Western Region"],
          districtByProvince: {
            "Central Region": ["Kampala", "Masaka", "Mukono", "Wakiso"],
            "Eastern Region": ["Jinja", "Mbale", "Soroti", "Tororo"],
            "Northern Region": ["Arua", "Gulu", "Kitgum", "Lira"],
            "Western Region": ["Fort Portal", "Hoima", "Kabale", "Kasese", "Mbarara"]
          },
          sectorByDistrict: {
            Kampala: ["Central Division", "Kawempe Division", "Makindye Division", "Nakawa Division", "Rubaga Division"],
            Mbarara: ["Biharwe", "Kakiika", "Kashare", "Nyakayojo", "Rwanyamahembe"],
            Gulu: ["Bardege-Layibi", "Laroo-Pece", "Paicho", "Unyama"]
          }
        },
        Tanzania: {
          province: ["Arusha", "Dar es Salaam", "Dodoma", "Geita", "Iringa", "Kagera", "Katavi", "Kigoma", "Kilimanjaro", "Lindi", "Manyara", "Mara", "Mbeya", "Morogoro", "Mtwara", "Mwanza", "Njombe", "Pemba North", "Pemba South", "Pwani", "Rukwa", "Ruvuma", "Shinyanga", "Simiyu", "Singida", "Songwe", "Tabora", "Tanga", "Zanzibar North", "Zanzibar South and Central", "Zanzibar Urban West"],
          districtByProvince: {
            Arusha: ["Arusha City", "Arusha District", "Karatu", "Longido", "Meru", "Monduli", "Ngorongoro"],
            "Dar es Salaam": ["Ilala", "Kigamboni", "Kinondoni", "Temeke", "Ubungo"],
            Dodoma: ["Bahi", "Chamwino", "Chemba", "Dodoma City", "Kondoa", "Kongwa", "Mpwapwa"],
            Mwanza: ["Ilemela", "Kwimba", "Magu", "Misungwi", "Nyamagana", "Sengerema", "Ukerewe"]
          },
          sectorByDistrict: {
            "Arusha District": ["Bangata", "Ilkiding'a", "Kimnyaki", "Moivo", "Mwandeti", "Sokoni II"],
            "Arusha City": ["Daraja Mbili", "Elerai", "Kaloleni", "Lemara", "Olasiti", "Sekei"],
            Ilala: ["Buguruni", "Gerezani", "Kariakoo", "Kivukoni", "Tabata", "Upanga East"],
            Ubungo: ["Goba", "Kimara", "Mbezi", "Sinza", "Ubungo"]
          }
        },
        Ghana: {
          province: ["Ahafo", "Ashanti", "Bono", "Bono East", "Central", "Eastern", "Greater Accra", "North East", "Northern", "Oti", "Savannah", "Upper East", "Upper West", "Volta", "Western", "Western North"],
          districtByProvince: {
            Ashanti: ["Adansi Asokwa", "Atwima Nwabiagya", "Ejisu", "Kumasi Metropolitan", "Obuasi Municipal", "Offinso Municipal"],
            "Greater Accra": ["Accra Metropolitan", "Adentan Municipal", "Ashaiman Municipal", "Ga East Municipal", "Ga West Municipal", "Tema Metropolitan"],
            Eastern: ["Akuapim North", "Birim Central", "East Akim", "Kwahu West", "New Juaben South", "Suhum"],
            Northern: ["Gushegu", "Karaga", "Sagnarigu Municipal", "Tamale Metropolitan", "Yendi Municipal"]
          },
          sectorByDistrict: {
            "Kumasi Metropolitan": ["Bantama", "Manhyia", "Nhyiaeso", "Oforikrom", "Subin"],
            "Accra Metropolitan": ["Ablekuma South", "Ashiedu Keteke", "Okaikwei South", "Osu Klottey"],
            "Tamale Metropolitan": ["Gumbihini", "Kalpohin", "Sagnarigu", "Tishigu"]
          }
        }
      };

      const narrativeQuestions = [
        { id: "q1", title: "Q1. Trigger Story", prompt: "Can you tell me about the last time you cooked a main meal? Walk me through what happened from start to finish." },
        { id: "q2", title: "Q2. Change Exposure", prompt: "When did you first hear about pressure cookers, and what did you think at that moment?" },
        { id: "q3", title: "Q3. Social Context / Influence", prompt: "What do people around you say about using pressure cookers? Can you share a specific conversation or example?" },
        { id: "q4", title: "Q4. Decision Tension", prompt: "If you have considered using or not using a pressure cooker, what made that decision difficult?" },
        { id: "q5", title: "Q5. Outcome or Imagined Future", prompt: "How do you think your daily life would change if you used or stopped using a pressure cooker?" }
      ];

      const evidenceModes = [
        { id: "structured_interview", title: "Structured interview", short: "Q1-Q5 field protocol", detail: "Comparable enumerator-led interview data with respondent profile and post-interview coding." },
        { id: "open_story", title: "Open story", short: "Multi-paragraph narrative", detail: "Community account, oral history, meeting note, or lived-experience story without forcing Q1-Q5." },
        { id: "indigenous_knowledge", title: "Indigenous knowledge", short: "Situated community knowledge", detail: "Local practice, seasonal memory, elder testimony, cultural explanation, or ecological observation." },
        { id: "citizen_science", title: "Citizen science report", short: "Community observation", detail: "Crowdsourced observation with place, time, confidence, validation, consent, and review status." },
        { id: "crowd_batch", title: "Crowdsourced batch", short: "Many stories at once", detail: "CSV or text batch from community submissions that needs moderation, deduplication, and approval." },
        { id: "experimental_feed", title: "Social Media Feeds", short: "Social/community feed evidence", detail: "X/Twitter, Facebook, LinkedIn, WhatsApp, YouTube, TikTok, Instagram, radio, community forums, or news comments. These are evidence inputs that must pass governance before modelling." }
      ];

      const socialFeedSources = [
        ["x_twitter", "X / Twitter"],
        ["facebook", "Facebook"],
        ["linkedin", "LinkedIn"],
        ["whatsapp", "WhatsApp"],
        ["youtube", "YouTube"],
        ["tiktok", "TikTok"],
        ["instagram", "Instagram"],
        ["radio_transcript", "Radio transcript"],
        ["community_forum", "Community forum"],
        ["news_comments", "News comments"],
        ["other", "Other"]
      ];

      const manualEncodingVariables = [
        { key: "E", label: "Exposure and emotional intensity", meaning: "How strongly the story exposes a pressure, risk, pain point, hope, fear, or lived event that can move adoption beliefs.", low: "0.00-0.33: passing mention, weak feeling, little lived consequence.", mid: "0.34-0.66: clear experience or tension, but not central to the story.", high: "0.67-1.00: vivid event, repeated pressure, strong fear, urgency, or hope.", example: "Smoke made cooking difficult while the respondent cared for children.", defaultValue: 0.55 },
        { key: "C", label: "Credibility and cultural resonance", meaning: "How believable and locally grounded the evidence is, including whether it comes from trusted people, ordinary practice, or recognizable local experience.", low: "0.00-0.33: abstract claim, unclear source, weak local grounding.", mid: "0.34-0.66: plausible story with some local detail.", high: "0.67-1.00: concrete local detail, trusted source, repeated community meaning.", example: "A neighbor, health worker, elder, or women's group is named as the source.", defaultValue: 0.58 },
        { key: "tau", label: "Trust alignment", meaning: "Whether the story increases trust in clean cooking, pressure cookers, health advice, repair systems, vendors, or public messaging.", low: "0.00-0.33: distrust, fear, rumor, or institutional skepticism dominates.", mid: "0.34-0.66: mixed trust, conditional acceptance, or uncertainty.", high: "0.67-1.00: strong trust in technology, messenger, support, or peer example.", example: "People trust a demonstration because a local health worker explains it.", defaultValue: 0.62 },
        { key: "kappa", label: "Inoculation and resistance potential", meaning: "How useful the story is for pre-bunking misinformation or building resistance to misleading claims.", low: "0.00-0.33: no clear misconception or refutation opportunity.", mid: "0.34-0.66: misconception is present but weakly explained.", high: "0.67-1.00: clear misleading claim plus evidence that can refute it safely.", example: "The story names a safety rumor and describes a trusted correction.", defaultValue: 0.52 },
        { key: "B", label: "Adoption barrier pressure", meaning: "How strongly cost, safety, habit, access, repair, fuel, gendered labor, or knowledge barriers block adoption.", low: "0.00-0.33: few barriers or barriers are already solved.", mid: "0.34-0.66: one important barrier is present but manageable.", high: "0.67-1.00: multiple or severe barriers likely to block adoption.", example: "The respondent wants the device but cost and repair access stop adoption.", defaultValue: 0.40 },
        { key: "S", label: "Social influence strength", meaning: "How much peers, family, leaders, groups, markets, or local networks shape the respondent's belief.", low: "0.00-0.33: mostly individual decision, little social influence.", mid: "0.34-0.66: some peer or family influence.", high: "0.67-1.00: community norms, peer examples, or group pressure dominate.", example: "Neighbors, women's groups, or family members strongly affect the decision.", defaultValue: 0.50 }
      ];

      const state = {
        step: 0,
        status: "idle",
        completed: new Set(),
        meta: {
          country: "Rwanda",
          province: "Northern Province",
          district: "Musanze",
          sector: "",
          language: "en",
          sourceType: "interview",
          sourceName: "community-consultation",
          period: "2026"
        },
        template: {
          evidenceMode: "structured_interview",
          interviewId: "",
          respondentProfile: "",
          decisionMaker: "",
          cookingMethods: "",
          knowledgeType: "",
          knowledgeHolder: "",
          sensitivity: "ordinary",
          communityValidation: "pending",
          attribution: "anonymous",
          translationNotes: "",
          locationPrecision: "approximate",
          observationDate: "",
          contributorType: "",
          citizenConfidence: "medium",
          validationStatus: "pending",
          benefitSharing: "",
          feedSources: [],
          q1: "",
          q2: "",
          q3: "",
          q4: "",
          q5: "",
          tone: "",
          stance: "",
          barrier: "",
          motivator: "",
          socialInfluence: ""
        },
        text: "",
        intakeOption: "manual",
        records: [],
        importedRecords: [],
        selectedRecordId: "",
        governance: {
          reviewer: "research-reviewer",
          reviewerRole: "researcher",
          visibility: "private",
          consent: "restricted_research",
          repositoryMode: "local_project",
          ledger: [],
          lastDigest: "",
          lastAnchoredAt: "",
          injectionThreshold: 0.45
        },
        encodingMode: "hybrid",
        llmProvider: "openai",
        llmConfig: {
          apiKey: "",
          baseUrl: "",
          model: "",
          status: "not_configured"
        },
        manualIndex: 0,
        encodingRuns: {},
        encoderName: "research-encoder",
        manualScores: { E: 0.55, C: 0.58, tau: 0.62, kappa: 0.52, B: 0.40, S: 0.50 },
        manualScorecards: {},
        encoded: [],
        comp: null,
        agents: null,
        digital: null,
        feedback: { observedAdoption: 0.48, trustDelta: 0.05, barrierDelta: -0.04, note: "" },
        bayes: null,
        priors: { trustA: 6, trustB: 4, barrierA: 4, barrierB: 6 },
        rl: null,
        analyticsStatus: null,
        validation: null,
        ledgerSync: null,
        repositoryFilters: {
          status: "all",
          route: "all",
          country: "all",
          admin: "all",
          consent: "all",
          visibility: "all",
          source: "all",
          validation: "all",
          theme: "all",
          master: "all",
          trustMin: "",
          trustMax: "",
          barrierMin: "",
          barrierMax: ""
        },
        masterRepository: {
          status: "not_prepared",
          syncStatus: "local_only",
          target: "master repository export",
          backend: "not_connected",
          reviewer: "master-reviewer",
          role: "institutional reviewer",
          note: "",
          lastPreparedAt: "",
          lastDecisionAt: "",
          anchorHash: "",
          previousHash: "",
          eventHash: "",
          decisionHash: "",
          blockchainStatus: "not_anchored",
          package: null
        },
        regional: null,
        graph: null,
        inoculation: null,
        inoculationApplied: false,
        policy: null,
        repositoryOpen: false,
        trace: [
          ["idle", "Ready to begin", "Choose country/location and paste the narrative evidence. Nothing is sent to the model until the SDMX gate passes."]
        ]
      };

      const $ = (id) => document.getElementById(id);

      function toast(text) {
        $("toast").textContent = text;
        $("toast").classList.add("show");
        clearTimeout(window.__toastTimer);
        window.__toastTimer = setTimeout(() => $("toast").classList.remove("show"), 1400);
      }

      async function apiJson(url, options = {}) {
        const response = await fetch(url, {
          ...options,
          headers: { "Content-Type": "application/json", ...(options.headers || {}) }
        });
        if (!response.ok) throw new Error(`Backend returned ${response.status}`);
        return response.json();
      }

      async function refreshAnalyticsStatus() {
        try {
          state.analyticsStatus = await apiJson("/analytics/status");
        } catch (error) {
          state.analyticsStatus = {
            available: false,
            fallback_available: false,
            warning: "Analytics status endpoint is unavailable.",
            reason: error.message || "unknown error"
          };
        }
        return state.analyticsStatus;
      }

      async function refreshValidationStatus() {
        try {
          state.validation = await apiJson("/validation/status");
        } catch (error) {
          state.validation = {
            status: "unavailable",
            calibrated_for_policy: false,
            warning: error.message || "Validation endpoint is unavailable."
          };
        }
        return state.validation;
      }

      async function evaluateEncodingCalibration() {
        try {
          state.validation = await apiJson("/validation/evaluate", {
            method: "POST",
            body: JSON.stringify(state.encoded || [])
          });
          trace("validation", "Encoding calibration checked", calibrationSummary());
        } catch (error) {
          state.validation = {
            status: "unavailable",
            calibrated_for_policy: false,
            warning: error.message || "Validation evaluation failed."
          };
          trace("validation", "Calibration check failed", state.validation.warning);
        }
        return state.validation;
      }

      async function syncLedgerToBackend(reason = "workflow sync") {
        try {
          const result = await apiJson("/ledger/sync", {
            method: "POST",
            body: JSON.stringify(governanceJson())
          });
          state.ledgerSync = { ...result, at: new Date().toISOString(), reason };
          trace("repository", "Persistent ledger synced", `${reason}: ${result.synced_records} record(s) saved to backend evidence ledger.`);
          return result;
        } catch (error) {
          state.ledgerSync = { error: error.message || "Ledger sync failed", at: new Date().toISOString(), reason };
          trace("repository", "Persistent ledger sync failed", state.ledgerSync.error);
          return null;
        }
      }

      function setStatus(status) {
        state.status = status;
        $("runStatus").className = `run-status ${status}`;
        $("runStatus").querySelector("span:last-child").textContent = status;
      }

      function trace(kind, title, detail) {
        state.trace.unshift([kind, title, detail]);
        renderTrace();
      }

      function renderTrace() {
        $("traceBody").innerHTML = state.trace.map(([kind, title, detail], index) => `
          <div class="trace">
            <div class="trace-top"><strong>${escapeHtml(title)}</strong><small>${escapeHtml(kind)} ${String(index + 1).padStart(2, "0")}</small></div>
            <p>${escapeHtml(detail)}</p>
          </div>
        `).join("");
      }

      function escapeHtml(value) {
        return String(value ?? "").replace(/[&<>"']/g, (char) => ({
          "&": "&amp;",
          "<": "&lt;",
          ">": "&gt;",
          '"': "&quot;",
          "'": "&#039;"
        }[char]));
      }

      function fmtPct(value) {
        return typeof value === "number" ? `${(value * 100).toFixed(1)}%` : "-";
      }

      function avg(values, fallback) {
        const valid = values.filter((value) => typeof value === "number");
        return valid.length ? valid.reduce((sum, value) => sum + value, 0) / valid.length : fallback;
      }

      function clamp01(value, fallback = 0) {
        const num = Number(value);
        if (!Number.isFinite(num)) return fallback;
        return Math.max(0, Math.min(1, num));
      }

      function numberLabel(value, digits = 2) {
        return typeof value === "number" && Number.isFinite(value) ? value.toFixed(digits) : "-";
      }

      function latestModelOutput() {
        return state.digital || state.comp || state.agents || null;
      }

      function modelTypeLabel() {
        const output = latestModelOutput();
        return output?.assumptions?.model_type || output?.model_mode || (state.comp ? "Full NDIM compartment model" : "not run");
      }

      function finalUncertaintySummary() {
        const point = latestModelOutput()?.trajectory?.at(-1);
        if (typeof point?.adoption_lower === "number" && typeof point?.adoption_upper === "number") {
          return `${fmtPct(point.adoption_lower)} to ${fmtPct(point.adoption_upper)} final adoption interval`;
        }
        const lower = state.bayes?.adoptionInterval?.lower;
        const upper = state.bayes?.adoptionInterval?.upper;
        if (typeof lower === "number" && typeof upper === "number") {
          return `${fmtPct(lower)} to ${fmtPct(upper)} posterior adoption interval`;
        }
        return "uncertainty interval not yet estimated";
      }

      function calibrationSummary() {
        const v = state.validation;
        if (!v) return "Validation status has not been loaded yet.";
        if (v.status === "calibrated" || v.status === "needs_review") {
          return `Matched ${v.matched_records || 0} validation record(s); theme F1 ${numberLabel(v.theme_f1)}, trust MAE ${numberLabel(v.trust_mae)}, barrier MAE ${numberLabel(v.barrier_mae)}. ${v.calibrated_for_policy ? "Encoder is within the current validation threshold." : "Human review is still required before policy use."}`;
        }
        if (v.status === "not_evaluated") return v.warning || "No double-coded validation narratives were encoded in this run.";
        if (v.dataset_records) {
          const agreement = v.agreement?.mean_agreement;
          return `${v.dataset_records} double-coded validation narratives available; inter-rater agreement ${numberLabel(agreement)}. Encode validation rows to estimate LLM-versus-human agreement.`;
        }
        return v.warning || v.note || "Validation status pending.";
      }

      function analyticsSummary() {
        const a = state.analyticsStatus;
        if (!a) return "Analytics status has not been checked yet.";
        if (a.available) return "Advanced analytics endpoint is available.";
        return a.warning || a.reason || "Advanced analytics unavailable; deterministic fallback will be labelled.";
      }

      function evidenceGrade() {
        const accepted = approvedRecords().length;
        const encoded = state.encoded.length;
        const calibrated = Boolean(state.validation?.calibrated_for_policy);
        const fullChain = Boolean(state.comp && state.agents && state.digital && state.bayes && state.rl);
        if (accepted >= 10 && encoded >= accepted && calibrated && fullChain) return "A";
        if (accepted >= 5 && encoded >= Math.min(accepted, 5) && fullChain) return "B";
        if (accepted >= 2 && encoded && (state.comp || state.agents)) return "C";
        return "D";
      }

      function confidenceLevel() {
        const grade = evidenceGrade();
        if (grade === "A") return "high";
        if (grade === "B") return "moderate";
        if (grade === "C") return "limited";
        return "exploratory only";
      }

      function policyUseWarning() {
        const accepted = approvedRecords().length;
        const issues = [];
        if (accepted < 5) issues.push("fewer than five accepted evidence records");
        if (!state.encoded.length) issues.push("encoding has not been completed");
        if (!state.comp && !state.agents) issues.push("model simulations have not been run");
        if (!state.bayes) issues.push("posterior uncertainty has not been updated");
        if (!state.validation?.calibrated_for_policy) issues.push("encoder calibration is not yet policy-grade");
        if (issues.length) return `Do not use as a final policy decision yet: ${issues.join("; ")}. Treat this output as a research draft requiring human review.`;
        return "Policy-ready for expert review: evidence, model chain, uncertainty, and validation checks are present. Human approval is still required.";
      }

      function policyDecisionBrief() {
        return {
          confidence_level: confidenceLevel(),
          evidence_grade: evidenceGrade(),
          human_review_required: true,
          policy_use_warning: policyUseWarning(),
          accepted_records: approvedRecords().length,
          rejected_records: rejectedRepositoryRecords().length,
          active_review_records: activeReviewRecords().length,
          model_type_used: modelTypeLabel(),
          validation_status: state.validation?.status || "not_checked",
          validation_summary: calibrationSummary(),
          analytics_status: state.analyticsStatus?.available ? "advanced" : "fallback_or_unavailable",
          analytics_summary: analyticsSummary(),
          uncertainty_summary: finalUncertaintySummary(),
          assumptions: latestModelOutput()?.assumptions || null,
          limitations: [
            "Narratives are not random samples unless the field protocol makes them so.",
            "Hashes prove tamper evidence, not factual truth.",
            "LLM or heuristic scores require human calibration before high-stakes policy use.",
            "Model outputs estimate direction and sensitivity; they do not guarantee adoption outcomes."
          ],
          required_human_review: [
            "Consent and visibility review",
            "Evidence provenance and duplicate review",
            "Encoding calibration against double-coded narratives",
            "Model assumptions and uncertainty review",
            "Policy feasibility and ethics review"
          ]
        };
      }

      function splitNarratives(text) {
        return text
          .split(/\n\s*\n|[\r\n]+/)
          .map((item) => item.trim())
          .filter(Boolean);
      }

      function countrySchema(country = state.meta.country) {
        return adminSchemas[country] || adminSchemas.Rwanda;
      }

      function adminOptionList(levelKey) {
        const options = adminOptions[state.meta.country] || adminOptions.Rwanda;
        if (levelKey === "province") return options.province || [];
        if (levelKey === "district") return options.districtByProvince?.[state.meta.province] || options.district || [];
        if (levelKey === "sector") return options.sectorByDistrict?.[state.meta.district] || options.sector || [];
        return [];
      }

      function renderSelectOptions(options, current, placeholder) {
        const unique = [...new Set(options.filter(Boolean))];
        const hasCurrent = current && unique.includes(current);
        return `
          <option value="">${escapeHtml(placeholder)}</option>
          ${unique.map((option) => `<option ${selectedAttr(option, current)} value="${escapeHtml(option)}">${escapeHtml(option)}</option>`).join("")}
          ${current && !hasCurrent ? `<option selected value="${escapeHtml(current)}">${escapeHtml(current)}</option>` : ""}
          <option ${selectedAttr("Other / not listed", current)} value="Other / not listed">Other / not listed</option>
        `;
      }

      function adminUnitParts() {
        const schema = countrySchema();
        return schema.levels
          .map((level) => ({ ...level, value: state.meta[level.key] || "" }))
          .filter((level) => level.value);
      }

      function adminUnitLabel() {
        const parts = adminUnitParts();
        return parts.map((part) => `${part.label}: ${part.value}`).join(" / ");
      }

      function deepestAdminLevel() {
        const parts = adminUnitParts();
        return parts.length ? parts[parts.length - 1].label : "country";
      }

      function questionBlocks() {
        return narrativeQuestions
          .map((question) => ({
            ...question,
            answer: (state.template[question.id] || "").trim()
          }))
          .filter((question) => question.answer);
      }

      function currentEvidenceMode() {
        return evidenceModes.find((mode) => mode.id === state.template.evidenceMode) || evidenceModes[0];
      }

      function collectionTemplateId() {
        const mode = state.template.evidenceMode || "structured_interview";
        if (mode === "structured_interview") return "clean-cooking-pressure-cooker-q1-q5-v1";
        if (mode === "indigenous_knowledge") return "ndim-indigenous-knowledge-record-v1";
        if (mode === "citizen_science") return "ndim-citizen-science-observation-v1";
        if (mode === "crowd_batch") return "ndim-crowdsourced-batch-v1";
        if (mode === "experimental_feed") return "ndim-social-media-feed-v1";
        return "ndim-open-narrative-v1";
      }

      function narrativeEvidenceTitle() {
        const mode = currentEvidenceMode();
        if (mode.id === "structured_interview") return "Structured interview response";
        if (mode.id === "indigenous_knowledge") return "Indigenous knowledge record";
        if (mode.id === "citizen_science") return "Citizen science observation";
        if (mode.id === "crowd_batch") return "Crowdsourced narrative";
        if (mode.id === "experimental_feed") return "Social media feed item";
        return "Open narrative";
      }

      function narrativeRecord(text, index, extra = {}) {
        const mode = currentEvidenceMode();
        return {
          narrative_id: extra.narrative_id || `ndim-${Date.now()}-${index + 1}`,
          text,
          metadata: {
            source_type: state.meta.sourceType,
            source_name: state.meta.sourceName,
            country: state.meta.country,
            admin_level: deepestAdminLevel(),
            admin_unit: adminUnitLabel(),
            language: state.meta.language,
            interview_id: state.template.interviewId,
            respondent_profile: state.template.respondentProfile,
            primary_decision_maker: state.template.decisionMaker,
            current_cooking_methods: state.template.cookingMethods,
            provenance: {
              period: state.meta.period,
              ui: "stepwise-workflow",
              evidence_mode: mode.id,
              evidence_mode_label: mode.title,
              collection_template: collectionTemplateId(),
              question_id: extra.questionId || null,
              question_title: extra.questionTitle || null,
              knowledge_type: state.template.knowledgeType,
              knowledge_holder: state.template.knowledgeHolder,
              sensitivity: state.template.sensitivity,
              community_validation: state.template.communityValidation,
              attribution: state.template.attribution,
              translation_notes: state.template.translationNotes,
              location_precision: state.template.locationPrecision,
              observation_date: state.template.observationDate,
              contributor_type: state.template.contributorType,
              feed_sources: Array.isArray(state.template.feedSources) ? state.template.feedSources : [],
              citizen_confidence: state.template.citizenConfidence,
              validation_status: state.template.validationStatus,
              benefit_sharing: state.template.benefitSharing,
              consent_tier: state.governance.consent,
              visibility: state.governance.visibility,
              manual_scores: state.manualScores,
              phi: computePhi()
            },
            coding: {
              tone_archetype: state.template.tone,
              adoption_stance: state.template.stance,
              key_barrier: state.template.barrier,
              key_motivator: state.template.motivator,
              social_influence: state.template.socialInfluence
            }
          },
          tags: [
            state.encodingMode,
            state.meta.sourceType,
            mode.id,
            state.template.knowledgeType,
            state.template.communityValidation,
            extra.questionId || "",
            state.template.stance || ""
          ].filter(Boolean)
        };
      }

      function buildRecords() {
        const importedText = state.importedRecords.map((record) => record.text).join("\n\n").trim();
        if (state.importedRecords.length && state.text.trim() === importedText) {
          state.records = state.importedRecords;
          return;
        }
        const useStructuredQuestions = state.template.evidenceMode === "structured_interview" || questionBlocks().length > 0;
        const fromQuestions = useStructuredQuestions ? questionBlocks().map((question, index) =>
          narrativeRecord(`${question.title}: ${question.answer}`, index, {
            narrative_id: `${state.template.interviewId || "field"}-${question.id}-${Date.now()}`,
            questionId: question.id,
            questionTitle: question.title
          })
        ) : [];
        const fromFreeText = splitNarratives(state.text).map((text, index) =>
          narrativeRecord(text, fromQuestions.length + index, { questionId: state.template.evidenceMode, questionTitle: narrativeEvidenceTitle() })
        );
        state.records = [...fromQuestions, ...fromFreeText];
      }

      function stableStringify(value) {
        if (value === null || typeof value !== "object") return JSON.stringify(value);
        if (Array.isArray(value)) return `[${value.map(stableStringify).join(",")}]`;
        return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${stableStringify(value[key])}`).join(",")}}`;
      }

      function fallbackHash(text) {
        let h1 = 0x811c9dc5;
        let h2 = 0x01000193;
        for (let i = 0; i < text.length; i += 1) {
          const code = text.charCodeAt(i);
          h1 ^= code;
          h1 = Math.imul(h1, 0x01000193);
          h2 ^= code + i;
          h2 = Math.imul(h2, 0x811c9dc5);
        }
        return `${(h1 >>> 0).toString(16).padStart(8, "0")}${(h2 >>> 0).toString(16).padStart(8, "0")}`.repeat(4).slice(0, 64);
      }

      async function sha256Hex(text) {
        if (window.crypto?.subtle) {
          const bytes = new TextEncoder().encode(text);
          const digest = await crypto.subtle.digest("SHA-256", bytes);
          return Array.from(new Uint8Array(digest)).map((byte) => byte.toString(16).padStart(2, "0")).join("");
        }
        return fallbackHash(text);
      }

      function shortHash(hash) {
        return hash ? `${hash.slice(0, 12)}...${hash.slice(-8)}` : "not sealed";
      }

      function scanNarrative(record, index = 0) {
        const text = String(record.text || "");
        const lower = text.toLowerCase();
        const injectionPatterns = [
          "ignore previous", "ignore all previous", "system prompt", "developer message",
          "reveal your prompt", "jailbreak", "override instructions", "act as",
          "you are now", "do not follow", "delete the rules", "<script", "base64"
        ];
        const injectionFlags = injectionPatterns.filter((pattern) => lower.includes(pattern));
        const piiFlags = [];
        if (/[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/i.test(text)) piiFlags.push("email-like text");
        if (/(?:\+?\d[\s-]?){8,}/.test(text)) piiFlags.push("phone-or-id-like number");
        if (/\b(?:national id|passport|id number|birth certificate)\b/i.test(text)) piiFlags.push("identity document mention");
        const qualityFlags = [];
        if (text.trim().length < 80) qualityFlags.push("short narrative");
        if (!record.metadata?.source_name) qualityFlags.push("missing source");
        if (!record.metadata?.admin_unit) qualityFlags.push("missing administrative unit");
        const provenance = record.metadata?.provenance || {};
        if (provenance.sensitivity === "sacred_not_shareable") qualityFlags.push("sacred or not-shareable knowledge");
        if (provenance.sensitivity === "restricted" && provenance.visibility === "public") qualityFlags.push("restricted knowledge marked public");
        if (provenance.community_validation === "disputed") qualityFlags.push("disputed community validation");
        if (provenance.evidence_mode === "experimental_feed") qualityFlags.push("social media feed requires extra validation");
        if (/(.)\1{12,}/.test(text)) qualityFlags.push("repeated-character anomaly");
        const normalized = text.toLowerCase().replace(/\s+/g, " ").trim();
        const duplicate = state.records.findIndex((item, itemIndex) =>
          itemIndex !== index && String(item.text || "").toLowerCase().replace(/\s+/g, " ").trim() === normalized
        );
        if (duplicate >= 0) qualityFlags.push(`exact duplicate of observation ${duplicate + 1}`);
        const sensitiveRisk =
          provenance.sensitivity === "sacred_not_shareable" ? 0.55 :
          provenance.sensitivity === "restricted" ? 0.28 :
          provenance.community_validation === "disputed" ? 0.24 :
          provenance.evidence_mode === "experimental_feed" ? 0.18 : 0;
        const risk = Math.min(1, injectionFlags.length * 0.28 + piiFlags.length * 0.18 + qualityFlags.length * 0.08 + sensitiveRisk);
        return {
          risk: Number(risk.toFixed(2)),
          injection_flags: injectionFlags,
          pii_flags: piiFlags,
          quality_flags: qualityFlags,
          recommendation: risk >= state.governance.injectionThreshold ? "review_before_encoding" : "eligible_for_approval"
        };
      }

      async function appendLedger(action, detail, targetHash = "") {
        const previous = state.governance.ledger.at(-1)?.event_hash || "";
        const event = {
          index: state.governance.ledger.length + 1,
          at: new Date().toISOString(),
          actor: state.governance.reviewer || "unknown-reviewer",
          role: state.governance.reviewerRole,
          action,
          detail,
          target_hash: targetHash,
          previous_hash: previous
        };
        event.event_hash = await sha256Hex(stableStringify(event));
        state.governance.ledger.push(event);
        return event;
      }

      async function sealRecords(reason = "evidence staged") {
        for (let index = 0; index < state.records.length; index += 1) {
          const record = state.records[index];
          const base = { narrative_id: record.narrative_id, text: record.text, metadata: record.metadata, tags: record.tags };
          const evidenceHash = await sha256Hex(stableStringify(base));
          const scan = scanNarrative(record, index);
          const previousGovernance = record.governance || {};
          record.governance = {
            content_hash: await sha256Hex(record.text || ""),
            evidence_hash: evidenceHash,
            scan,
            status: previousGovernance.status || "pending_review",
            reviewer: previousGovernance.reviewer || "",
            reviewed_at: previousGovernance.reviewed_at || "",
            reviewer_signature: previousGovernance.reviewer_signature || "",
            review_reason: previousGovernance.review_reason || "",
            committed_at: previousGovernance.committed_at || "",
            commit_signature: previousGovernance.commit_signature || "",
            repository_bucket: previousGovernance.repository_bucket || "",
            uncommitted_at: previousGovernance.uncommitted_at || "",
            visibility: previousGovernance.visibility || state.governance.visibility,
            consent: previousGovernance.consent || state.governance.consent,
            repository_mode: previousGovernance.repository_mode || state.governance.repositoryMode
          };
        }
        const digest = await sha256Hex(stableStringify(state.records.map((record) => ({
          narrative_id: record.narrative_id,
          evidence_hash: record.governance?.evidence_hash,
          status: record.governance?.status,
          visibility: record.governance?.visibility,
          consent: record.governance?.consent
        }))));
        state.governance.lastDigest = digest;
        await appendLedger("seal_batch", `${reason}; ${state.records.length} observation(s) hashed and scanned`, digest);
        return digest;
      }

      function normalizedReviewStatus(status) {
        if (status === "approved") return "approved_pending_commit";
        if (status === "rejected") return "rejected_pending_commit";
        return status;
      }

      function activeReviewRecords() {
        return state.records.filter((record) => ![
          "approved_pending_commit",
          "rejected_pending_commit",
          "accepted_committed",
          "rejected_committed"
        ].includes(record.governance?.status));
      }

      function acceptedRepositoryRecords() {
        return state.records.filter((record) => record.governance?.status === "accepted_committed");
      }

      function rejectedRepositoryRecords() {
        return state.records.filter((record) => record.governance?.status === "rejected_committed");
      }

      function pendingCommitRecords() {
        return state.records.filter((record) => ["approved_pending_commit", "rejected_pending_commit"].includes(record.governance?.status));
      }

      async function setRecordApproval(record, status, reason = "") {
        if (!record.governance?.evidence_hash) await sealRecords("approval pre-seal");
        const nextStatus = normalizedReviewStatus(status);
        const reviewedAt = new Date().toISOString();
        const signature = await sha256Hex([
          state.governance.reviewer,
          state.governance.reviewerRole,
          nextStatus,
          reviewedAt,
          record.governance.evidence_hash
        ].join("|"));
        record.governance.status = nextStatus;
        record.governance.reviewer = state.governance.reviewer;
        record.governance.reviewed_at = reviewedAt;
        record.governance.reviewer_signature = signature;
        record.governance.review_reason = reason || nextStatus;
        record.governance.committed_at = "";
        record.governance.commit_signature = "";
        record.governance.repository_bucket = "";
        record.governance.uncommitted_at = "";
        record.governance.visibility = state.governance.visibility;
        record.governance.consent = state.governance.consent;
        record.governance.repository_mode = state.governance.repositoryMode;
        await appendLedger(`record_${nextStatus}`, `${record.narrative_id}: ${reason || nextStatus}`, record.governance.evidence_hash);
      }

      async function commitReviewedRecords() {
        if (!state.records.length) return { accepted: 0, rejected: 0 };
        if (!state.governance.lastDigest) await sealRecords("commit pre-seal");
        let accepted = 0;
        let rejected = 0;
        for (const record of state.records) {
          const status = record.governance?.status;
          if (!["approved_pending_commit", "rejected_pending_commit"].includes(status)) continue;
          const committedAt = new Date().toISOString();
          const bucket = status === "approved_pending_commit" ? "accepted" : "rejected";
          const finalStatus = bucket === "accepted" ? "accepted_committed" : "rejected_committed";
          const signature = await sha256Hex([
            state.governance.reviewer,
            state.governance.reviewerRole,
            finalStatus,
            committedAt,
            record.governance.evidence_hash
          ].join("|"));
          record.governance.status = finalStatus;
          record.governance.repository_bucket = bucket;
          record.governance.committed_at = committedAt;
          record.governance.commit_signature = signature;
          record.governance.master_repository_status = bucket === "accepted" ? "local_accepted" : "local_rejected";
          record.governance.master_blockchain_status = "not_anchored";
          await appendLedger(`commit_${bucket}`, `${record.narrative_id} committed to ${bucket} repository`, record.governance.evidence_hash);
          if (bucket === "accepted") accepted += 1;
          else rejected += 1;
        }
        if (accepted || rejected) {
          await sealRecords("repository commit update");
          if (acceptedRepositoryRecords().length) state.completed.add("gate");
          else state.completed.delete("gate");
        }
        return { accepted, rejected };
      }

      async function uncommitRecord(record, reason = "manual uncommit") {
        if (!record?.governance) return false;
        const previousStatus = record.governance.status;
        if (!["accepted_committed", "rejected_committed"].includes(previousStatus)) return false;
        record.governance.status = "pending_review";
        record.governance.repository_bucket = "";
        record.governance.uncommitted_at = new Date().toISOString();
        record.governance.master_repository_status = "";
        record.governance.master_anchor_hash = "";
        record.governance.master_event_hash = "";
        record.governance.master_decision_hash = "";
        record.governance.master_reviewed_at = "";
        record.governance.master_reviewer = "";
        record.governance.master_blockchain_status = "not_anchored";
        await appendLedger("record_uncommitted", `${record.narrative_id}: ${reason}; moved from ${previousStatus} back to active review`, record.governance.evidence_hash);
        await sealRecords("repository uncommit update");
        if (!acceptedRepositoryRecords().length) state.completed.delete("gate");
        return true;
      }

      function approvedRecords() {
        return acceptedRepositoryRecords();
      }

      function pendingGovernanceCount() {
        return state.records.filter((record) => record.governance?.status !== "accepted_committed").length;
      }

      function parseCsv(text) {
        const rows = [];
        let row = [];
        let cell = "";
        let quoted = false;
        for (let i = 0; i < text.length; i += 1) {
          const char = text[i];
          const next = text[i + 1];
          if (char === '"' && quoted && next === '"') {
            cell += '"';
            i += 1;
          } else if (char === '"') {
            quoted = !quoted;
          } else if (char === "," && !quoted) {
            row.push(cell.trim());
            cell = "";
          } else if ((char === "\n" || char === "\r") && !quoted) {
            if (char === "\r" && next === "\n") i += 1;
            row.push(cell.trim());
            if (row.some(Boolean)) rows.push(row);
            row = [];
            cell = "";
          } else {
            cell += char;
          }
        }
        row.push(cell.trim());
        if (row.some(Boolean)) rows.push(row);
        if (!rows.length) return [];
        const headers = rows[0].map((item) => item.toLowerCase().replace(/\s+/g, "_"));
        return rows.slice(1).map((cells) => Object.fromEntries(headers.map((key, index) => [key, cells[index] || ""])));
      }

      function splitList(value) {
        return String(value || "")
          .split(/[;|,]/)
          .map((item) => item.trim())
          .filter(Boolean);
      }

      function recordsFromCsv(text, filename) {
        const rows = parseCsv(text);
        return rows.flatMap((row, index) => {
          const country = row.country || state.meta.country;
          const schema = countrySchema(country);
          const evidenceMode = row.evidence_mode || row.record_type || state.template.evidenceMode || "open_story";
          const adminValues = schema.levels.map((level) => {
            const key = level.label.toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_|_$/g, "");
            return row[level.key] || row[key] || row.admin_unit || "";
          }).filter(Boolean);
          const baseMetadata = {
            source_type: row.source_type || sourceTypeForMode(evidenceMode) || state.meta.sourceType || "csv",
            source_name: row.source_name || filename || state.meta.sourceName,
            country,
            admin_level: row.admin_level || schema.levels[Math.min(schema.levels.length - 1, Math.max(0, adminValues.length - 1))]?.label || "admin_unit",
            admin_unit: row.admin_unit || adminValues.join(" / ") || row.district || state.meta.district,
            language: row.language || state.meta.language,
            interview_id: row.interview_id || row.interview || "",
            respondent_profile: row.respondent_profile || "",
            primary_decision_maker: row.primary_decision_maker || "",
            current_cooking_methods: row.current_cooking_methods || "",
            coding: {
              tone_archetype: row.tone_archetype || row.tone || "",
              adoption_stance: row.adoption_stance || "",
              key_barrier: row.key_barrier || "",
              key_motivator: row.key_motivator || "",
              social_influence: row.social_influence || ""
            }
          };
          const baseId = row.narrative_id || row.id || `csv-${Date.now()}-${index + 1}`;
          const makeCsvRecord = (narrative, questionId = row.question_id || row.question || "", questionTitle = "") => ({
            narrative_id: questionId ? `${baseId}-${questionId}` : baseId,
            text: narrative,
            metadata: {
              ...baseMetadata,
              provenance: {
                period: row.period || state.meta.period,
                csv_row: index + 1,
                question_id: questionId,
                question_title: questionTitle,
                ui: "csv-import",
                evidence_mode: evidenceMode,
                evidence_mode_label: evidenceModes.find((mode) => mode.id === evidenceMode)?.title || evidenceMode,
                collection_template: row.collection_template || collectionTemplateId(),
                knowledge_type: row.knowledge_type || "",
                knowledge_holder: row.knowledge_holder || "",
                sensitivity: row.sensitivity || "",
                community_validation: row.community_validation || "",
                attribution: row.attribution || "",
                translation_notes: row.translation_notes || "",
                location_precision: row.location_precision || "",
                observation_date: row.observation_date || row.date || "",
                contributor_type: row.contributor_type || "",
                feed_sources: splitList(row.feed_sources || row.platforms || row.platform || ""),
                citizen_confidence: row.citizen_confidence || row.confidence || "",
                validation_status: row.validation_status || "",
                benefit_sharing: row.benefit_sharing || "",
                consent_tier: row.consent_tier || state.governance.consent,
                visibility: row.visibility || state.governance.visibility
              }
            },
            tags: [state.encodingMode, "csv", evidenceMode, row.knowledge_type || "", row.type || "", questionId].filter(Boolean)
          });
          const questionRecords = narrativeQuestions
            .filter((question) => row[question.id])
            .map((question) => makeCsvRecord(`${question.title}: ${row[question.id]}`, question.id, question.title));
          if (questionRecords.length) return questionRecords;
          const narrative = row.narrative || row.text || row.quote || row.story || row.content || Object.values(row).find((value) => value && value.length > 24) || "";
          return narrative ? [makeCsvRecord(narrative)] : [];
        }).filter((record) => record.text);
      }

      function applyImportedCsvMetadata(row, filename) {
        const evidenceMode = row.evidence_mode || row.record_type || state.template.evidenceMode || "open_story";
        if (evidenceModes.some((mode) => mode.id === evidenceMode)) {
          state.template.evidenceMode = evidenceMode;
        }
        const schema = countrySchema(row.country || state.meta.country);
        state.meta.country = row.country || state.meta.country;
        schema.levels.forEach((level) => {
          const normalized = level.label.toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_|_$/g, "");
          state.meta[level.key] = row[level.key] || row[normalized] || state.meta[level.key] || "";
        });
        state.meta.language = row.language || state.meta.language;
        state.meta.sourceType = row.source_type || sourceTypeForMode(state.template.evidenceMode) || state.meta.sourceType || "csv";
        state.meta.sourceName = row.source_name || filename || state.meta.sourceName;
        state.meta.period = row.period || state.meta.period;
        state.template.interviewId = row.interview_id || row.narrative_id || state.template.interviewId;
        state.template.respondentProfile = row.respondent_profile || state.template.respondentProfile;
        state.template.decisionMaker = row.primary_decision_maker || state.template.decisionMaker;
        state.template.cookingMethods = row.current_cooking_methods || state.template.cookingMethods;
        state.template.knowledgeType = row.knowledge_type || state.template.knowledgeType;
        state.template.knowledgeHolder = row.knowledge_holder || state.template.knowledgeHolder;
        state.template.sensitivity = row.sensitivity || state.template.sensitivity || "ordinary";
        state.template.communityValidation = row.community_validation || state.template.communityValidation || "pending";
        state.template.attribution = row.attribution || state.template.attribution || "anonymous";
        state.template.locationPrecision = row.location_precision || state.template.locationPrecision || "approximate";
        state.template.observationDate = row.observation_date || row.date || state.template.observationDate;
        state.template.contributorType = row.contributor_type || state.template.contributorType;
        state.template.feedSources = splitList(row.feed_sources || row.platforms || row.platform || state.template.feedSources);
        state.template.citizenConfidence = row.citizen_confidence || row.confidence || state.template.citizenConfidence || "medium";
        state.template.validationStatus = row.validation_status || state.template.validationStatus || "pending";
        state.template.translationNotes = row.translation_notes || state.template.translationNotes;
        state.template.benefitSharing = row.benefit_sharing || state.template.benefitSharing;
        state.template.q1 = row.q1 || state.template.q1;
        state.template.q2 = row.q2 || state.template.q2;
        state.template.q3 = row.q3 || state.template.q3;
        state.template.q4 = row.q4 || state.template.q4;
        state.template.q5 = row.q5 || state.template.q5;
        state.template.tone = row.tone_archetype || row.tone || state.template.tone;
        state.template.stance = row.adoption_stance || state.template.stance;
        state.template.barrier = row.key_barrier || state.template.barrier;
        state.template.motivator = row.key_motivator || state.template.motivator;
        state.template.socialInfluence = row.social_influence || state.template.socialInfluence;
      }

      function defaultManualScores() {
        return manualEncodingVariables.reduce((scores, variable) => {
          scores[variable.key] = clamp01(state.manualScores[variable.key] ?? variable.defaultValue, variable.defaultValue);
          return scores;
        }, {});
      }

      function computePhi(scores = state.manualScores) {
        const s = { ...defaultManualScores(), ...(scores || {}) };
        return Number((0.3 * clamp01(s.E) + 0.3 * clamp01(s.C) + 0.2 * clamp01(s.tau) + 0.2 * clamp01(s.kappa)).toFixed(4));
      }

      function reviewableRecords() {
        const approved = approvedRecords();
        return approved.length ? approved : state.records;
      }

      function currentReviewRecord() {
        const records = reviewableRecords();
        if (!records.length) return null;
        return records[Math.min(state.manualIndex, records.length - 1)];
      }

      function ensureManualScorecard(record) {
        if (!record) return null;
        const id = record.narrative_id;
        if (!state.manualScorecards[id]) {
          state.manualScorecards[id] = {
            narrative_id: id,
            encoder: state.encoderName || state.governance.reviewer || "research-encoder",
            status: "unencoded",
            updated_at: "",
            scores: defaultManualScores(),
            notes: {}
          };
        }
        manualEncodingVariables.forEach((variable) => {
          if (typeof state.manualScorecards[id].scores[variable.key] !== "number") {
            state.manualScorecards[id].scores[variable.key] = variable.defaultValue;
          }
          if (typeof state.manualScorecards[id].notes[variable.key] !== "string") {
            state.manualScorecards[id].notes[variable.key] = "";
          }
        });
        return state.manualScorecards[id];
      }

      function encodedFor(mode, narrativeId) {
        return (state.encodingRuns[mode] || []).find((item) => item.narrative_id === narrativeId)
          || (mode === state.encodingMode ? state.encoded.find((item) => item.narrative_id === narrativeId && item.encoding_mode === mode) : null);
      }

      function upsertEncoded(mode, encoded) {
        if (!encoded) return;
        const rows = (state.encodingRuns[mode] || []).filter((item) => item.narrative_id !== encoded.narrative_id);
        state.encodingRuns[mode] = rows.concat(encoded);
        if (state.encodingMode === mode) {
          state.encoded = state.encoded.filter((item) => item.narrative_id !== encoded.narrative_id).concat(encoded);
        }
      }

      function inferManualThemes(record, scores) {
        const text = String(record?.text || "").toLowerCase();
        const themes = [];
        if (scores.B >= 0.55 || /cost|expensive|repair|access|unsafe|safety|habit|fuel|wood|charcoal/.test(text)) themes.push("adoption_barrier");
        if (scores.tau >= 0.58 || /trust|believe|health worker|leader|neighbou?r|demonstration/.test(text)) themes.push("trust");
        if (scores.S >= 0.58 || /people|family|group|community|neighbou?r|leader|women/.test(text)) themes.push("social_influence");
        if (scores.kappa >= 0.58 || /rumou?r|misinformation|false|fear|refut|safe|unsafe/.test(text)) themes.push("inoculation");
        if (scores.E >= 0.60 || /smoke|pain|fear|hope|time|daily|difficult/.test(text)) themes.push("lived_experience");
        return [...new Set(themes)].slice(0, 5).length ? [...new Set(themes)].slice(0, 5) : ["general"];
      }

      function manualEncodedNarrative(record) {
        const card = ensureManualScorecard(record);
        const scores = { ...defaultManualScores(), ...(card?.scores || {}) };
        const phi = computePhi(scores);
        const confidence = Number(avg([scores.C, scores.kappa, scores.S], 0.5).toFixed(3));
        const trust = Number(clamp01(scores.tau).toFixed(3));
        const barrier = Number(clamp01(scores.B).toFixed(3));
        const sentiment = Number(Math.max(-1, Math.min(1, trust + 0.25 * scores.E - barrier)).toFixed(3));
        return {
          narrative_id: record.narrative_id,
          encoding_mode: "manual",
          themes: inferManualThemes(record, scores),
          sentiment,
          adoption_barrier_score: barrier,
          trust_score: trust,
          confidence,
          reviewer_notes: Object.entries(card.notes || {}).filter(([, note]) => note).map(([key, note]) => `${key}: ${note}`).join(" | ") || "Manual scorecard saved without variable-level notes.",
          model_notes: `Researcher-entered numeric scorecard; Phi=${phi.toFixed(4)}; E=${scores.E.toFixed(2)}, C=${scores.C.toFixed(2)}, tau=${scores.tau.toFixed(2)}, kappa=${scores.kappa.toFixed(2)}, B=${scores.B.toFixed(2)}, S=${scores.S.toFixed(2)}.`,
          manual_scorecard: {
            encoder: card.encoder,
            updated_at: card.updated_at,
            scores,
            phi,
            notes: card.notes || {}
          }
        };
      }

      function saveManualScorecard(record, markReviewed = true) {
        const card = ensureManualScorecard(record);
        if (!card) return null;
        card.encoder = state.encoderName || state.governance.reviewer || "research-encoder";
        card.updated_at = new Date().toISOString();
        if (markReviewed) card.status = "manual_reviewed";
        const encoded = manualEncodedNarrative(record);
        upsertEncoded("manual", encoded);
        return encoded;
      }

      function nextUnencodedIndex(records, startIndex = state.manualIndex + 1) {
        if (!records.length) return 0;
        for (let offset = 0; offset < records.length; offset += 1) {
          const index = (startIndex + offset) % records.length;
          const record = records[index];
          const card = record ? state.manualScorecards[record.narrative_id] : null;
          if (!card || card.status !== "manual_reviewed") return index;
        }
        return Math.min(records.length - 1, state.manualIndex);
      }

      function gateChecks() {
        const qCount = questionBlocks().length;
        const adminParts = adminUnitParts();
        const mode = currentEvidenceMode();
        const checks = [
          ["Evidence mode", `${mode.title}: ${mode.short}`, Boolean(state.template.evidenceMode)],
          ["Country", state.meta.country, Boolean(state.meta.country)],
          ["Administrative schema", countrySchema().levels.map((level) => level.label).join(" > "), Boolean(state.meta.country)],
          ["Administrative unit", adminUnitLabel(), adminParts.length >= 2],
          ["Source", `${state.meta.sourceType} / ${state.meta.sourceName}`, Boolean(state.meta.sourceType && state.meta.sourceName)],
          ["Period", state.meta.period, Boolean(state.meta.period)],
          ["Language", state.meta.language, Boolean(state.meta.language)],
          ["Consent and visibility", `${state.governance.consent} / ${state.governance.visibility}`, Boolean(state.governance.consent && state.governance.visibility)]
        ];
        if (state.template.evidenceMode === "structured_interview") {
          checks.push(
            ["Interview ID", state.template.interviewId, Boolean(state.template.interviewId)],
            ["Respondent profile", state.template.respondentProfile, Boolean(state.template.respondentProfile)],
            ["Decision-maker", state.template.decisionMaker, Boolean(state.template.decisionMaker)],
            ["Current cooking method(s)", state.template.cookingMethods, Boolean(state.template.cookingMethods)],
            ["Core narrative questions", `${qCount} of ${narrativeQuestions.length} answered`, qCount > 0]
          );
        }
        if (state.template.evidenceMode === "indigenous_knowledge") {
          checks.push(
            ["Knowledge type", state.template.knowledgeType, Boolean(state.template.knowledgeType)],
            ["Knowledge holder", state.template.knowledgeHolder, Boolean(state.template.knowledgeHolder)],
            ["Sensitivity tier", state.template.sensitivity, Boolean(state.template.sensitivity)],
            ["Community validation", state.template.communityValidation, Boolean(state.template.communityValidation)]
          );
        }
        if (state.template.evidenceMode === "citizen_science") {
          checks.push(
            ["Contributor type", state.template.contributorType, Boolean(state.template.contributorType)],
            ["Observation date", state.template.observationDate || "not set", Boolean(state.template.observationDate)],
            ["Citizen confidence", state.template.citizenConfidence, Boolean(state.template.citizenConfidence)]
          );
        }
        if (state.template.evidenceMode === "crowd_batch") {
          checks.push(
            ["Batch validation status", state.template.validationStatus, Boolean(state.template.validationStatus)],
            ["Attribution preference", state.template.attribution, Boolean(state.template.attribution)]
          );
        }
        if (state.template.evidenceMode === "experimental_feed") {
          checks.push(
            ["Selected platforms", (state.template.feedSources || []).join(", "), Array.isArray(state.template.feedSources) && state.template.feedSources.length > 0],
            ["Feed validation status", state.template.validationStatus, Boolean(state.template.validationStatus)]
          );
        }
        checks.push(["Narrative observations", `${state.records.length} parsed`, state.records.length > 0]);
        return checks;
      }

      function saveIntakeFromDom() {
        ["country", "province", "district", "sector", "language", "sourceType", "sourceName", "period"].forEach((key) => {
          const el = $(key);
          if (el) state.meta[key] = el.value;
        });
        const evidenceModeSelect = $("evidenceModeSelect");
        if (evidenceModeSelect && evidenceModeSelect.value !== state.template.evidenceMode) {
          state.template.evidenceMode = evidenceModeSelect.value;
          state.meta.sourceType = sourceTypeForMode(state.template.evidenceMode);
        }
        Object.keys(state.template).forEach((key) => {
          const el = $(key);
          if (el) state.template[key] = el.value;
        });
        state.template.feedSources = Array.from(document.querySelectorAll("[data-feed-source]:checked")).map((input) => input.value);
        const textEl = $("narrativeText");
        if (textEl) state.text = textEl.value;
      }

      function saveGovernanceFromDom() {
        const mapping = {
          reviewerName: "reviewer",
          reviewerRole: "reviewerRole",
          visibility: "visibility",
          consentTier: "consent",
          repositoryMode: "repositoryMode",
          injectionThreshold: "injectionThreshold"
        };
        Object.entries(mapping).forEach(([id, key]) => {
          const el = $(id);
          if (!el) return;
          state.governance[key] = key === "injectionThreshold" ? Number(el.value) : el.value;
        });
      }

      async function validateIntake() {
        saveIntakeFromDom();
        buildRecords();
        state.encoded = [];
        state.encodingRuns = {};
        state.manualScorecards = {};
        state.manualIndex = 0;
        if (!state.text.trim() && !questionBlocks().length) {
          setStatus("error");
          trace("blocked", "No narrative text", "Answer at least one Q1-Q5 narrative question or paste at least one narrative paragraph before moving to the SDMX gate.");
          toast("Add narrative evidence first");
          return false;
        }
        if (!state.meta.country || !state.meta.sourceName || !state.meta.period) {
          setStatus("error");
          trace("blocked", "Missing metadata", "Country, source name, and period are required for the SDMX input contract.");
          toast("Complete required metadata");
          return false;
        }
        if (state.template.evidenceMode === "structured_interview" && !state.template.interviewId) {
          setStatus("error");
          trace("blocked", "Missing interview ID", "Structured interview mode requires an interview ID so Q1-Q5 answers remain traceable.");
          toast("Add interview ID");
          return false;
        }
        if (state.template.evidenceMode === "indigenous_knowledge" && (!state.template.knowledgeType || !state.template.knowledgeHolder)) {
          setStatus("error");
          trace("blocked", "Missing knowledge metadata", "Indigenous knowledge mode requires a knowledge type and knowledge holder category before review.");
          toast("Complete knowledge metadata");
          return false;
        }
        if (state.template.evidenceMode === "citizen_science" && (!state.template.contributorType || !state.template.observationDate)) {
          setStatus("error");
          trace("blocked", "Missing citizen-science metadata", "Citizen science mode requires contributor type and observation date for validation.");
          toast("Complete citizen report metadata");
          return false;
        }
        state.completed.add("intake");
        state.completed.add("gate");
        setStatus("complete");
        await sealRecords("SDMX gate intake");
        await syncLedgerToBackend("SDMX gate intake");
        trace("intake", "Evidence staged", `${state.records.length} narrative observation(s) prepared for ${state.meta.country}.`);
        trace("gate", "SDMX gate prepared", "The records now carry source, location, language, period, provenance, hashes, scan results, and review status.");
        return true;
      }

      function currentStep() {
        return steps[state.step];
      }

      function goStep(index) {
        state.step = Math.max(0, Math.min(steps.length - 1, index));
        render();
        scrollToActiveStage();
      }

      function scrollToActiveStage() {
        requestAnimationFrame(() => {
          const stage = document.querySelector(".stage-card");
          if (stage) stage.scrollIntoView({ behavior: "smooth", block: "start" });
        });
      }

      function resetCurrentStage() {
        const id = currentStep().id;
        if (id === "intake") {
          state.text = "";
          state.records = [];
          state.importedRecords = [];
          state.encoded = [];
          state.encodingRuns = {};
          state.manualScorecards = {};
          state.manualIndex = 0;
          state.governance.ledger = [];
          state.governance.lastDigest = "";
          state.governance.lastAnchoredAt = "";
          state.completed.delete("intake");
          state.completed.delete("gate");
        } else if (id === "gate") {
          state.records.forEach((record) => {
            if (record.governance) record.governance.status = "pending_review";
          });
          state.completed.delete("gate");
        } else if (id === "encoding") {
          state.encoded = [];
          state.encodingRuns = {};
          state.manualScorecards = {};
          state.manualIndex = 0;
          state.completed.delete("encoding");
        } else if (id === "compartmental") {
          state.comp = null;
          state.completed.delete("compartmental");
        } else if (id === "agents") {
          state.agents = null;
          state.completed.delete("agents");
        } else if (id === "digital") {
          state.digital = null;
          state.completed.delete("digital");
        } else if (id === "bayes") {
          state.bayes = null;
          state.completed.delete("bayes");
        } else if (id === "rl") {
          state.rl = null;
          state.completed.delete("rl");
        } else if (id === "regional") {
          state.regional = null;
          state.completed.delete("regional");
        } else if (id === "graph") {
          state.graph = null;
          state.completed.delete("graph");
        } else if (id === "inoculation") {
          state.inoculation = null;
          state.inoculationApplied = false;
          state.completed.delete("inoculation");
        } else if (id === "policy") {
          state.policy = null;
          state.completed.delete("policy");
        }
        trace("reset", `${currentStep().title} reset`, "This stage output was cleared without deleting unrelated stages.");
        setStatus("idle");
        render();
      }

      async function nextStep() {
        const id = currentStep().id;
        if (state.step === steps.length - 1) {
          if (state.policy) {
            toast("Workflow complete");
            trace("finish", "Workflow complete", "Policy output, audit payload, and export controls are ready. Returning to intake so another evidence route can begin.");
            goStep(0);
          } else {
            const missing = steps.filter((step) => step.id !== "policy" && !state.completed.has(step.id)).map((step) => step.title);
            toast("Run policy output first");
            trace("finish", "Finish blocked", missing.length ? `Complete or review these stages before final export: ${missing.join(", ")}. Then run full policy pipeline.` : "All prior stages are ready. Click Run full policy pipeline in Policy output before finishing.");
            scrollToActiveStage();
          }
          return;
        }
        if (id === "intake" && !await validateIntake()) return;
        if (id === "gate" && !state.completed.has("gate")) {
          if (!await validateIntake()) return;
        }
        if (id === "gate" && !approvedRecords().length) {
          toast("Commit accepted evidence first");
          trace("blocked", "No accepted repository records", "Approve at least one narrative, then click Commit reviewed records so it enters the accepted repository before encoding.");
          return;
        }
        if (id === "encoding" && !state.encoded.length) {
          toast("Run encoding before continuing");
          trace("blocked", "Encoding not run", "Choose manual, AI, or hybrid and run the encoder first.");
          return;
        }
        if (id === "compartmental" && !state.comp) {
          toast("Run compartmental model first");
          trace("blocked", "Compartmental model not run", "The ODE stage needs to run before comparing with the agent model.");
          return;
        }
        if (id === "agents" && !state.agents) {
          toast("Run agent model first");
          trace("blocked", "Agent model not run", "Run the household-level model before producing the policy output.");
          return;
        }
        if (id === "digital" && !state.digital) {
          toast("Apply digital twin feedback first");
          trace("blocked", "Digital twin feedback not applied", "Use the feedback loop to refine the model inputs before Bayesian updating.");
          return;
        }
        if (id === "bayes" && !state.bayes) {
          toast("Run Bayesian update first");
          trace("blocked", "Posterior not computed", "The Bayesian stage should produce posterior trust and barrier priors before RL.");
          return;
        }
        if (id === "rl" && !state.rl) {
          toast("Run RL optimizer first");
          trace("blocked", "RL loop not run", "Run the optimizer so the policy stage can use the learned intervention recommendation.");
          return;
        }
        if (id === "regional" && !state.regional) {
          toast("Run regional analysis first");
          trace("blocked", "Regional analysis not run", "Run place-based analysis so interventions can be crafted for isolated regions or grouped evidence.");
          return;
        }
        if (id === "graph" && !state.graph) {
          toast("Build knowledge graph first");
          trace("blocked", "Knowledge graph not built", "Build the graph to connect stories, themes, locations, and intervention signals.");
          return;
        }
        if (id === "inoculation" && !state.inoculation) {
          toast("Generate inoculation narratives first");
          trace("blocked", "Inoculation lab not run", "Generate pre-bunking and refutation narratives before the final policy output.");
          return;
        }
        goStep(state.step + 1);
      }

      function renderStepList() {
        $("stepList").innerHTML = steps.map((step, index) => `
          <button class="step-button ${index === state.step ? "active" : ""} ${state.completed.has(step.id) ? "done" : ""}" data-step="${index}" type="button">
            <span class="num">${step.num}</span>
            <span><strong>${step.title}</strong><span>${step.sub}</span></span>
          </button>
        `).join("");
        document.querySelectorAll("[data-step]").forEach((button) => {
          button.addEventListener("click", () => goStep(Number(button.dataset.step)));
        });
      }

      function renderCommandCenter() {
        const step = currentStep();
        const readiness = Math.round((state.completed.size / steps.length) * 100);
        const adoption = bestAdoptionSignal();
        const encodedSummary = state.encoded.length ? `${state.encoded.length}/${state.records.length || state.encoded.length}` : "0";
        const topLocation = [state.meta.country, state.meta.district || state.meta.province].filter(Boolean).join(" / ") || "not set";
        return `
          <section class="command-center" aria-label="NDIM command center">
            <div class="flow-lane">
              ${workflowPhases.map(renderFlowCard).join("")}
            </div>
            <div class="command-head">
              <div>
                <p class="eyebrow">Evidence-to-policy workbench</p>
                <h2>Evidence, readiness, and next action in one place</h2>
                <p>Use this workbench to see what evidence exists, whether it has passed governance, which model stage is active, and what must happen next before policy output is credible.</p>
                <div class="reference-links" aria-label="Tool references">
                  <a class="button" href="/manual" target="_blank" rel="noreferrer">Open tool manual</a>
                  <a class="button" href="/stress-test-corpus" target="_blank" rel="noreferrer">Stress-test tutorial</a>
                  <a class="button" href="#narrativeRepository" data-jump-repository>Open narrative repository</a>
                  <button class="button" data-open-full-repository type="button">Open full repository</button>
                </div>
                <div class="status-chip-row">
                  ${statusChip("Evidence staged", state.records.length > 0)}
                  ${statusChip("Approved evidence", approvedRecords().length > 0)}
                  ${statusChip("Tamper seal", Boolean(state.governance.lastDigest))}
                  ${statusChip("Encoding ready", state.encoded.length > 0)}
                  ${statusChip("Model feedback loop", Boolean(state.digital || state.bayes || state.rl))}
                  ${statusChip("Policy audit", Boolean(state.policy))}
                </div>
              </div>
              <div class="hero-side">
                <div class="current-intel">
                  <span class="mini-label">Now running</span>
                  <strong>${escapeHtml(step.num)} ${escapeHtml(step.title)}</strong>
                  <p>${escapeHtml(stageAdvice(step.id))}</p>
                  <div class="workbench-actions">
                    <button class="button primary" id="workbenchRunButton" type="button">Run stage</button>
                    <button class="button" id="workbenchTraceButton" type="button">Activity log</button>
                  </div>
                </div>
                ${renderHeroLedger()}
              </div>
            </div>
            ${renderFeedbackChain()}
            <div class="command-metrics">
              ${commandMetric("Observations", state.records.length || "-")}
              ${commandMetric("Approved", approvedRecords().length || "-")}
              ${commandMetric("Encoded stories", encodedSummary)}
              ${commandMetric("Model signal", adoption)}
              ${commandMetric("Evidence grade", evidenceGrade())}
              ${commandMetric("Validation", state.validation?.status || "checking")}
              ${commandMetric("Evidence seal", shortHash(state.governance.lastDigest))}
            </div>
          </section>
        `;
      }

      function renderFlowCard(phase) {
        const active = phase.stages.includes(currentStep().id);
        const done = phase.stages.every((id) => state.completed.has(id));
        const someDone = phase.stages.some((id) => state.completed.has(id));
        const status = done ? "complete" : someDone ? "in progress" : "pending";
        const detail = `${phase.detail}. Status: ${status}.`;
        return `
          <button class="flow-card ${active ? "active" : ""} ${done ? "done" : ""}" data-flow-step="${phase.step}" type="button" title="${escapeHtml(detail)}" aria-label="${escapeHtml(`${phase.label}: ${detail}`)}">
            <b>${escapeHtml(phase.icon)}</b>
            <span>
              <strong>${escapeHtml(phase.label)}</strong>
              <small>${escapeHtml(detail)}</small>
            </span>
          </button>
        `;
      }

      function commandMetric(label, value) {
        return `<div class="command-metric"><span>${escapeHtml(label)}</span><strong>${escapeHtml(String(value))}</strong></div>`;
      }

      function renderFeedbackChain() {
        const nodes = [
          ["01", "Evidence ledger", state.records.length > 0, "Narratives become governed observations."],
          ["02", "Encoding", state.encoded.length > 0, "Scores become trust, barrier, confidence, and Phi."],
          ["03", "Digital twin", Boolean(state.digital), "Field feedback reruns the model and corrects trajectory."],
          ["04", "Bayes + RL", Boolean(state.bayes || state.rl), "Posterior assumptions and learned intervention policy refine action choice."],
          ["05", "Synthesis", Boolean(state.regional || state.graph || state.inoculation), "Regions, graph, and inoculation drafts interpret where action should differ."],
          ["06", "Policy output", Boolean(state.policy), "Final package uses evidence, twin output, posterior, RL, synthesis, and human review."]
        ];
        return `
          <div class="feedback-chain" aria-label="Model feedback chain">
            <p class="eyebrow">Feedback chain</p>
            <div class="chain-grid">
              ${nodes.map(([num, title, ready, detail]) => `
                <div class="chain-node ${ready ? "ready" : ""}">
                  <span>${escapeHtml(num)} ${ready ? "ready" : "waiting"}</span>
                  <strong>${escapeHtml(title)}</strong>
                  <p>${escapeHtml(detail)}</p>
                </div>
              `).join("")}
            </div>
          </div>
        `;
      }

      function recordRouteLabel(record) {
        const modeId = record?.metadata?.provenance?.evidence_mode || record?.metadata?.evidence_mode || state.template.evidenceMode;
        return evidenceModes.find((mode) => mode.id === modeId)?.title || modeId || "Narrative";
      }

      function recordAdminLabel(record) {
        return record?.metadata?.admin_unit || [record?.metadata?.country, state.meta.district || state.meta.province].filter(Boolean).join(" / ") || "not set";
      }

      function recordSourceLabel(record) {
        return [record?.metadata?.source_type, record?.metadata?.source_name].filter(Boolean).join(" / ") || "source pending";
      }

      function recordStatusLabel(record) {
        const labels = {
          pending_review: "active review",
          approved_pending_commit: "approved / pending commit",
          rejected_pending_commit: "rejected / pending commit",
          accepted_committed: "accepted repository",
          rejected_committed: "rejected repository",
          approved: "approved / legacy",
          rejected: "rejected / legacy"
        };
        const status = record?.governance?.status || "draft";
        return labels[status] || String(status).replace(/_/g, " ");
      }

      function recordHashLabel(record) {
        return shortHash(record?.governance?.evidence_hash || record?.governance?.content_hash || "");
      }

      function renderHeroLedger() {
        const rows = state.records.slice(0, 5);
        const more = Math.max(0, state.records.length - rows.length);
        return `
          <div class="ledger-card" id="narrativeRepository">
            <p class="eyebrow">Narrative repository</p>
            <h3>${state.records.length ? `${state.records.length} record${state.records.length === 1 ? "" : "s"} in active ledger` : "No records staged yet"}</h3>
            <p>${escapeHtml(state.records.length ? "Click a narrative ID to inspect the governed record in the workflow." : "Records appear here only after you upload or manually load evidence, then click Stage and validate.")}</p>
            <div class="ledger-table-wrap">
              <table class="ledger-table">
                <thead><tr><th>Narrative ID</th><th>Route</th><th>Place</th><th>Status</th><th>Seal</th></tr></thead>
                <tbody>
                  ${rows.length ? rows.map((record, index) => `
                    <tr>
                      <td><a class="record-link" href="#record-${encodeURIComponent(record.narrative_id || index)}" data-ledger-record="${escapeHtml(record.narrative_id || "")}">${escapeHtml(record.narrative_id || `record-${index + 1}`)}</a></td>
                      <td title="${escapeHtml(recordRouteLabel(record))}">${escapeHtml(recordRouteLabel(record))}</td>
                      <td title="${escapeHtml(recordAdminLabel(record))}">${escapeHtml(recordAdminLabel(record))}</td>
                      <td title="${escapeHtml(recordStatusLabel(record))}">${escapeHtml(recordStatusLabel(record))}</td>
                      <td title="${escapeHtml(recordHashLabel(record))}">${escapeHtml(recordHashLabel(record))}</td>
                    </tr>
                  `).join("") : `<tr><td colspan="5">Waiting for staged narrative records.</td></tr>`}
                </tbody>
              </table>
            </div>
            ${more ? `<p style="margin-top: 8px;">+${more} more records visible in the SDMX gate.</p>` : ""}
          </div>
        `;
      }

      function renderRepositoryRow(record, section) {
        const index = state.records.indexOf(record);
        const gov = record.governance || {};
        const reason = gov.review_reason || gov.scan?.recommendation || "not reviewed";
        const committed = gov.committed_at ? new Date(gov.committed_at).toLocaleString() : "-";
        const masterStatus = gov.master_repository_status ? String(gov.master_repository_status).replace(/_/g, " ") : "";
        return `
          <tr>
            <td><button class="record-link" data-inspect-record="${index}" type="button">${escapeHtml(record.narrative_id || `record-${index + 1}`)}</button></td>
            <td>${escapeHtml(recordRouteLabel(record))}</td>
            <td title="${escapeHtml(recordAdminLabel(record))}">${escapeHtml(recordAdminLabel(record))}</td>
            <td>${escapeHtml(recordSourceLabel(record))}</td>
            <td>${escapeHtml(recordStatusLabel(record))}</td>
            <td>${escapeHtml(shortHash(gov.evidence_hash || gov.content_hash || ""))}</td>
            <td>${escapeHtml(reason)}${masterStatus ? `<br><small>Master: ${escapeHtml(masterStatus)}</small>` : ""}</td>
            <td>${escapeHtml(committed)}</td>
            <td>
              <div class="button-row" style="margin-top: 0;">
                <button class="button" data-inspect-record="${index}" type="button">Inspect</button>
                ${section === "accepted" || section === "rejected" ? `<button class="button" data-uncommit-record="${index}" type="button">Uncommit</button>` : ""}
              </div>
            </td>
          </tr>
        `;
      }

      function renderRepositorySection(title, description, records, section) {
        return `
          <div class="repository-section">
            <h3>${escapeHtml(title)}</h3>
            <p>${escapeHtml(description)}</p>
            <div class="repository-table-wrap">
              <table class="repository-table">
                <thead><tr><th>Narrative ID</th><th>Route</th><th>Place</th><th>Source</th><th>Status</th><th>Seal</th><th>Decision / reason</th><th>Committed</th><th>Action</th></tr></thead>
                <tbody>
                  ${records.length ? records.map((record) => renderRepositoryRow(record, section)).join("") : `<tr><td colspan="9">No records in this repository section.</td></tr>`}
                </tbody>
              </table>
            </div>
          </div>
        `;
      }

      function renderMasterRepositoryPanel() {
        const eligible = masterEligibleRecords();
        const pkg = state.masterRepository.package;
        const statusLabel = String(state.masterRepository.status || "not_prepared").replace(/_/g, " ");
        const syncLabel = String(state.masterRepository.syncStatus || "local_only").replace(/_/g, " ");
        return `
          <div class="master-repo-panel">
            <div>
              <p class="eyebrow">Federated master repository</p>
              <h3>Prepare accepted local evidence for a governed master repository</h3>
              <p>This keeps NDIM local-first: records are reviewed and committed on this machine first. When a team is ready, accepted records can be packaged as an SDMX-style push bundle for a master repository such as Google Sheets, Google Drive, GitHub, Airtable, Supabase, or an institutional database. No online upload happens from this prototype.</p>
            </div>
            <div class="metric-grid">
              <div class="metric"><span class="mini-label">Eligible accepted records</span><strong>${eligible.length}</strong></div>
              <div class="metric"><span class="mini-label">Master status</span><strong>${escapeHtml(statusLabel)}</strong></div>
              <div class="metric"><span class="mini-label">Sync state</span><strong>${escapeHtml(syncLabel)}</strong></div>
              <div class="metric"><span class="mini-label">Anchor hash</span><strong>${escapeHtml(shortHash(state.masterRepository.anchorHash))}</strong></div>
            </div>
            <div class="field-grid" style="margin-top: 12px;">
              <div class="field"><label for="masterRepositoryTarget">Master repository target</label><input id="masterRepositoryTarget" value="${escapeHtml(state.masterRepository.target)}" placeholder="Google Sheet, Drive folder, GitHub repo, institutional DB..." /></div>
              <div class="field"><label for="masterReviewer">Master reviewer</label><input id="masterReviewer" value="${escapeHtml(state.masterRepository.reviewer)}" /></div>
              <div class="field"><label for="masterReviewerRole">Reviewer role</label><input id="masterReviewerRole" value="${escapeHtml(state.masterRepository.role)}" /></div>
              <div class="field"><label for="masterApprovalNote">Master approval note</label><input id="masterApprovalNote" value="${escapeHtml(state.masterRepository.note)}" placeholder="Why this package should or should not update the master repository" /></div>
            </div>
            <div class="button-row">
              <button class="button primary" id="prepareMasterPush" type="button">Prepare SDMX master push</button>
              <button class="button green" id="approveMasterPush" type="button">Approve master push</button>
              <button class="button" id="rejectMasterPush" type="button">Reject master push</button>
              <button class="button" id="copyMasterPushPackage" type="button">Copy SDMX package</button>
              <button class="button" id="exportMasterPushPackage" type="button">Download SDMX JSON</button>
              <button class="button" id="exportMasterCsv" type="button">Download observation CSV</button>
              <button class="button" id="exportMasterDsd" type="button">Download DSD JSON</button>
            </div>
            <p style="margin-top: 10px;"><strong>Blockchain-ready seal:</strong> NDIM creates a chained hash for the master push package and the master approval decision. Later, that anchor hash can be published to a blockchain or institutional timestamp service without exposing restricted narrative text.</p>
            ${pkg ? `<p><strong>Last package:</strong> ${escapeHtml(pkg.sdmx?.observations?.length || 0)} observation(s), status ${escapeHtml(pkg.master_review_status || "-")}, generated ${escapeHtml(pkg.generated_at || "-")}.</p>` : ""}
          </div>
        `;
      }

      function renderFullRepositoryView() {
        if (!state.repositoryOpen) return "";
        const allRecords = state.records;
        const filtered = filteredRepositoryRecords(allRecords);
        const active = filteredRepositoryRecords(activeReviewRecords());
        const pending = filteredRepositoryRecords(pendingCommitRecords());
        const accepted = filteredRepositoryRecords(acceptedRepositoryRecords());
        const rejected = filteredRepositoryRecords(rejectedRepositoryRecords());
        const eligible = masterEligibleRecords();
        return `
          <section class="repository-full-view" id="fullRepositoryView">
            <div class="repository-full-head">
              <div>
                <p class="eyebrow">Full repository</p>
                <h2>Narrative review, accepted, and rejected repositories</h2>
                <p>Records move from the active approval queue into the accepted or rejected repository only after Commit reviewed records. Accepted local records can then be packaged for a federated master repository with an SDMX structure and tamper-evident approval seal.</p>
              </div>
              <button class="button" data-close-full-repository type="button">Close repository</button>
            </div>
            <div class="metric-grid">
              <div class="metric"><span class="mini-label">Filtered records</span><strong>${filtered.length}</strong></div>
              <div class="metric"><span class="mini-label">Active review</span><strong>${active.length}</strong></div>
              <div class="metric"><span class="mini-label">Waiting commit</span><strong>${pending.length}</strong></div>
              <div class="metric"><span class="mini-label">Accepted</span><strong>${accepted.length}</strong></div>
              <div class="metric"><span class="mini-label">Rejected</span><strong>${rejected.length}</strong></div>
              <div class="metric"><span class="mini-label">Master eligible</span><strong>${eligible.length}</strong></div>
              <div class="metric"><span class="mini-label">Batch seal</span><strong>${escapeHtml(shortHash(state.governance.lastDigest))}</strong></div>
            </div>
            ${renderRepositoryFilters(allRecords)}
            ${renderRepositoryCategories(filtered)}
            ${renderMasterRepositoryPanel()}
            ${renderRepositorySection("Active approval queue", "Records here are staged and governed, but still need a reviewer decision. Click Approve or Reject on a record to remove it from this queue and place it into the reviewed waiting area.", active, "active")}
            ${renderRepositorySection("Reviewed, waiting for commit", "Records here already have an approve or reject decision. Click Commit reviewed records in the SDMX gate to move them into the accepted or rejected repository.", pending, "pending")}
            ${renderRepositorySection("Accepted repository", "These committed records are available for encoding, modelling, synthesis, and policy audit.", accepted, "accepted")}
            ${renderRepositorySection("Rejected repository", "These committed records are preserved for audit but excluded from encoding and modelling until uncommitted and reviewed again.", rejected, "rejected")}
          </section>
        `;
      }

      function statusChip(label, ready) {
        return `<span class="status-chip ${ready ? "ready" : "warn"}">${escapeHtml(label)} ${ready ? "ready" : "waiting"}</span>`;
      }

      function bestAdoptionSignal() {
        const signal = state.digital?.trajectory?.at(-1)?.adoption
          ?? state.agents?.trajectory?.at(-1)?.adoption
          ?? state.comp?.trajectory?.at(-1)?.adoption;
        return typeof signal === "number" ? fmtPct(signal) : "-";
      }

      function evidenceLedgerText() {
        if (!state.records.length) return "No observations staged yet. Start with a text, CSV, JSON, XML, or SDMX-style evidence source and pass it through the gate.";
        const sourceTypes = [...new Set(state.records.map((record) => record.metadata.source_type || "unknown"))].join(", ");
        const places = [...new Set(state.records.map((record) => record.metadata.admin_unit || state.meta.country))].slice(0, 3).join("; ");
        const stats = governanceStats();
        const seal = state.governance.lastDigest ? ` Batch digest ${shortHash(state.governance.lastDigest)}.` : "";
        return `${state.records.length} ${currentEvidenceMode().title.toLowerCase()} observation(s) staged from ${sourceTypes}; ${stats.approved} approved, ${stats.flagged} flagged. Active place lens: ${places || state.meta.country}.${seal}`;
      }

      function stageAdvice(id) {
        const advice = {
          intake: "Create traceable narrative observations before any model receives evidence.",
          gate: "Hash, scan, review, and approve evidence before encoding.",
          encoding: "Compare manual, AI, and hybrid scoring so model inputs are explainable.",
          compartmental: "Run the population ODE view to estimate aggregate diffusion pressure.",
          agents: "Stress-test local household dynamics, peer effects, and network friction.",
          digital: "Feed field observations back into the model before drawing conclusions.",
          bayes: "Turn priors and observations into posterior trust and barrier assumptions.",
          rl: "Let the optimizer test intervention packages while keeping human review in control.",
          regional: "Analyse each region alone or as a grouped evidence set before intervention design.",
          graph: "Connect stories, places, themes, trust, and barriers for qualitative sense-making.",
        inoculation: "Generate pre-bunking and refutation drafts from encoded narrative risk.",
          policy: "Produce the reviewable policy brief, assumptions, and audit payload."
        };
        return advice[id] || "Continue the evidence-to-policy workflow.";
      }

      function bindCommandCenter() {
        const runButton = $("workbenchRunButton");
        if (runButton) runButton.addEventListener("click", runCurrentStageShortcut);
        const traceButton = $("workbenchTraceButton");
        if (traceButton) traceButton.addEventListener("click", () => {
          document.querySelector(".reasoning").classList.toggle("open");
        });
        document.querySelectorAll("[data-jump-repository]").forEach((button) => {
          button.addEventListener("click", (event) => {
            event.preventDefault();
            const repository = $("narrativeRepository");
            if (repository) {
              repository.scrollIntoView({ behavior: "smooth", block: "start" });
              repository.classList.add("pulse-focus");
              window.setTimeout(() => repository.classList.remove("pulse-focus"), 900);
            }
            trace("repository", "Narrative repository opened", state.records.length ? `${state.records.length} staged record(s) are visible in the ledger.` : "The repository is empty until evidence is staged and validated.");
          });
        });
        document.querySelectorAll("[data-open-full-repository]").forEach((button) => {
          button.addEventListener("click", () => {
            state.repositoryOpen = true;
            trace("repository", "Full repository opened", `${activeReviewRecords().length} active, ${acceptedRepositoryRecords().length} accepted, and ${rejectedRepositoryRecords().length} rejected record(s) are available.`);
            render();
            requestAnimationFrame(() => $("fullRepositoryView")?.scrollIntoView({ behavior: "smooth", block: "start" }));
          });
        });
        document.querySelectorAll("[data-close-full-repository]").forEach((button) => {
          button.addEventListener("click", () => {
            state.repositoryOpen = false;
            trace("repository", "Full repository closed", "Returned to the active workflow view.");
            render();
          });
        });
        const repositoryFilterBindings = {
          repoFilterStatus: "status",
          repoFilterRoute: "route",
          repoFilterCountry: "country",
          repoFilterAdmin: "admin",
          repoFilterConsent: "consent",
          repoFilterVisibility: "visibility",
          repoFilterSource: "source",
          repoFilterValidation: "validation",
          repoFilterTheme: "theme",
          repoFilterMaster: "master",
          repoFilterTrustMin: "trustMin",
          repoFilterTrustMax: "trustMax",
          repoFilterBarrierMin: "barrierMin",
          repoFilterBarrierMax: "barrierMax"
        };
        Object.entries(repositoryFilterBindings).forEach(([id, key]) => {
          const input = $(id);
          if (!input) return;
          input.addEventListener("change", () => {
            state.repositoryFilters[key] = input.value;
            render();
            requestAnimationFrame(() => $("fullRepositoryView")?.scrollIntoView({ behavior: "smooth", block: "start" }));
          });
        });
        const resetRepositoryFilters = $("resetRepositoryFilters");
        if (resetRepositoryFilters) resetRepositoryFilters.addEventListener("click", () => {
          state.repositoryFilters = {
            status: "all",
            route: "all",
            country: "all",
            admin: "all",
            consent: "all",
            visibility: "all",
            source: "all",
            validation: "all",
            theme: "all",
            master: "all",
            trustMin: "",
            trustMax: "",
            barrierMin: "",
            barrierMax: ""
          };
          trace("repository", "Repository filters reset", "All repository records are visible again.");
          render();
          requestAnimationFrame(() => $("fullRepositoryView")?.scrollIntoView({ behavior: "smooth", block: "start" }));
        });
        const masterButtons = [
          ["prepareMasterPush", prepareMasterRepositoryPush],
          ["approveMasterPush", () => decideMasterRepositoryPush("approved")],
          ["rejectMasterPush", () => decideMasterRepositoryPush("rejected")],
          ["copyMasterPushPackage", copyMasterRepositoryPackage],
          ["exportMasterPushPackage", exportMasterRepositoryPackage],
          ["exportMasterCsv", exportMasterRepositoryCsv],
          ["exportMasterDsd", exportMasterRepositoryDsd]
        ];
        masterButtons.forEach(([id, handler]) => {
          const button = $(id);
          if (button) button.addEventListener("click", handler);
        });
        document.querySelectorAll("[data-inspect-record]").forEach((button) => {
          button.addEventListener("click", (event) => {
            event.preventDefault();
            const index = Number(button.dataset.inspectRecord);
            const record = state.records[index];
            if (!record) return;
            state.selectedRecordId = record.narrative_id;
            state.manualIndex = Math.max(0, acceptedRepositoryRecords().findIndex((item) => item.narrative_id === record.narrative_id));
            if (state.manualIndex < 0) state.manualIndex = 0;
            trace("repository", "Repository record inspected", `${record.narrative_id} selected. The SDMX gate shows governance details; encoding uses accepted repository records.`);
            goStep(1);
          });
        });
        document.querySelectorAll("[data-uncommit-record]").forEach((button) => {
          button.addEventListener("click", async () => {
            const record = state.records[Number(button.dataset.uncommitRecord)];
            if (!record) return;
            const ok = await uncommitRecord(record);
            if (ok) await syncLedgerToBackend("repository record uncommitted");
            trace("repository", ok ? "Record uncommitted" : "Record not uncommitted", ok ? `${record.narrative_id} moved back into active review.` : `${record.narrative_id} was not in a committed repository.`);
            toast(ok ? "Record back in review" : "Record not committed");
            render();
            requestAnimationFrame(() => $("fullRepositoryView")?.scrollIntoView({ behavior: "smooth", block: "start" }));
          });
        });
        document.querySelectorAll("[data-flow-step]").forEach((button) => {
          button.addEventListener("click", () => goStep(Number(button.dataset.flowStep)));
        });
        document.querySelectorAll("[data-ledger-record]").forEach((link) => {
          link.addEventListener("click", (event) => {
            event.preventDefault();
            const recordId = link.dataset.ledgerRecord;
            const index = state.records.findIndex((record) => record.narrative_id === recordId);
            if (index < 0) return;
            state.selectedRecordId = recordId;
            state.manualIndex = index;
            trace("ledger", "Narrative record selected", `${recordId} is selected for inspection. Open the SDMX gate or encoding stage to review its metadata, seal, and scorecard.`);
            if (state.step === 0) goStep(1);
            else render();
          });
        });
      }

      function syncWorkflowStagesOffset() {
        const stepper = document.querySelector(".stepper");
        const label = document.querySelector(".stepper .section-label");
        const stageCard = document.querySelector(".stage-card");
        if (!stepper || !label || !stageCard) return;
        if (window.innerWidth <= 980) {
          stepper.style.paddingTop = "";
          return;
        }
        stepper.style.paddingTop = "14px";
        requestAnimationFrame(() => {
          const labelTop = label.getBoundingClientRect().top;
          const stageTop = stageCard.getBoundingClientRect().top;
          const nextPadding = Math.max(14, 14 + stageTop - labelTop);
          stepper.style.paddingTop = `${Math.round(nextPadding)}px`;
        });
      }

      function render() {
        const step = currentStep();
        $("topTitle").textContent = step.title;
        $("topCopy").textContent = step.sub;
        renderStepList();
        $("stagePanel").innerHTML = renderCommandCenter() + renderStage(step.id) + renderContextStageNav() + renderFullRepositoryView();
        $("backButton").disabled = state.step === 0;
        $("nextButton").textContent = state.step === steps.length - 1 ? "Finish" : "Next";
        bindCommandCenter();
        bindStage(step.id);
        bindContextStageNav();
        syncWorkflowStagesOffset();
      }

      function renderStage(id) {
        if (id === "intake") return renderIntake();
        if (id === "gate") return renderGate();
        if (id === "encoding") return renderEncoding();
        if (id === "compartmental") return renderCompartmental();
        if (id === "agents") return renderAgents();
        if (id === "digital") return renderDigital();
        if (id === "bayes") return renderBayes();
        if (id === "rl") return renderRL();
        if (id === "regional") return renderRegionalAnalysis();
        if (id === "graph") return renderKnowledgeGraph();
        if (id === "inoculation") return renderInoculationLab();
        return renderPolicy();
      }

      function renderContextStageNav() {
        const next = steps[state.step + 1];
        const isLast = state.step === steps.length - 1;
        const nextLabel = isLast ? "Finish and return to intake" : `Continue to ${next.num} ${next.title}`;
        const note = isLast
          ? "At the end, Finish returns to the beginning so another evidence route can be tested."
          : `Next stage: ${next.title.toLowerCase()}. The page will jump to the active stage top.`;
        return `
          <div class="context-stage-nav" aria-label="Current stage navigation">
            <span class="nav-note">${escapeHtml(note)}</span>
            <button class="button" data-context-back type="button" ${state.step === 0 ? "disabled" : ""}>Back</button>
            <button class="button" data-context-reset type="button">Reset this stage</button>
            <button class="button primary" data-context-next type="button">${escapeHtml(nextLabel)}</button>
          </div>
        `;
      }

      function bindContextStageNav() {
        document.querySelectorAll("[data-context-back]").forEach((button) => {
          button.addEventListener("click", () => goStep(state.step - 1));
        });
        document.querySelectorAll("[data-context-reset]").forEach((button) => {
          button.addEventListener("click", resetCurrentStage);
        });
        document.querySelectorAll("[data-context-next]").forEach((button) => {
          button.addEventListener("click", nextStep);
        });
      }

      function selectedAttr(value, current) {
        return value === current ? "selected" : "";
      }

      function sourceTypeForMode(mode) {
        return {
          structured_interview: "interview",
          open_story: "field_note",
          indigenous_knowledge: "indigenous_knowledge",
          citizen_science: "citizen_report",
          crowd_batch: "csv",
          experimental_feed: "social_feed"
        }[mode] || "field_note";
      }

      function renderAdminFields() {
        const schema = countrySchema();
        return `
          ${schema.levels.map((level) => `
            <div class="field">
              <label for="${level.key}">${escapeHtml(level.label)}</label>
              <select id="${level.key}">
                ${renderSelectOptions(adminOptionList(level.key), state.meta[level.key], `Select ${level.label}`)}
              </select>
            </div>
          `).join("")}
          <div class="field" style="grid-column: 1 / -1;">
            <p class="admin-hint">${escapeHtml(schema.note)}</p>
          </div>
        `;
      }

      function renderQuestionCards() {
        return narrativeQuestions.map((question) => `
          <details class="question-card" ${state.template[question.id] ? "open" : ""}>
            <summary><h3>${escapeHtml(question.title)}</h3><span class="mini-label">${state.template[question.id] ? "answered" : "open"}</span></summary>
            <div class="question-body">
              <p>${escapeHtml(question.prompt)}</p>
              <textarea id="${question.id}" placeholder="Enumerator writes the respondent's story in their own words...">${escapeHtml(state.template[question.id])}</textarea>
            </div>
          </details>
        `).join("");
      }

      function renderCodingFields() {
        return `
          <div class="field-grid">
            <div class="field"><label for="tone">Tone / archetype</label><select id="tone">
              <option value="">Not coded yet</option><option ${selectedAttr("regret", state.template.tone)} value="regret">Regret</option><option ${selectedAttr("triumph", state.template.tone)} value="triumph">Triumph</option><option ${selectedAttr("denial", state.template.tone)} value="denial">Denial</option><option ${selectedAttr("pragmatic", state.template.tone)} value="pragmatic">Pragmatic</option><option ${selectedAttr("anxious", state.template.tone)} value="anxious">Anxious</option>
            </select></div>
            <div class="field"><label for="stance">Adoption stance</label><select id="stance">
              <option value="">Not coded yet</option><option ${selectedAttr("for", state.template.stance)} value="for">For</option><option ${selectedAttr("against", state.template.stance)} value="against">Against</option><option ${selectedAttr("mixed", state.template.stance)} value="mixed">Mixed</option>
            </select></div>
            <div class="field"><label for="barrier">Key barrier</label><select id="barrier">
              <option value="">Not coded yet</option><option ${selectedAttr("cost", state.template.barrier)} value="cost">Cost</option><option ${selectedAttr("safety", state.template.barrier)} value="safety">Safety</option><option ${selectedAttr("habit", state.template.barrier)} value="habit">Habit</option><option ${selectedAttr("knowledge", state.template.barrier)} value="knowledge">Knowledge</option><option ${selectedAttr("access", state.template.barrier)} value="access">Access</option>
            </select></div>
            <div class="field"><label for="motivator">Key motivator</label><select id="motivator">
              <option value="">Not coded yet</option><option ${selectedAttr("time", state.template.motivator)} value="time">Time</option><option ${selectedAttr("fuel_savings", state.template.motivator)} value="fuel_savings">Fuel savings</option><option ${selectedAttr("status", state.template.motivator)} value="status">Status</option><option ${selectedAttr("convenience", state.template.motivator)} value="convenience">Convenience</option><option ${selectedAttr("health", state.template.motivator)} value="health">Health</option>
            </select></div>
            <div class="field"><label for="socialInfluence">Social influence</label><select id="socialInfluence">
              <option value="">Not coded yet</option><option ${selectedAttr("high", state.template.socialInfluence)} value="high">High</option><option ${selectedAttr("medium", state.template.socialInfluence)} value="medium">Medium</option><option ${selectedAttr("low", state.template.socialInfluence)} value="low">Low</option>
            </select></div>
          </div>
        `;
      }

      function renderIntake() {
        const countries = Object.keys(adminSchemas);
        return `
          <section class="stage-card">
            <p class="eyebrow">Stage 1</p>
            <h2>Ingest narratives with context</h2>
            <p class="copy">Choose the evidence route, attach SDMX context, then stage records into the governed narrative ledger.</p>
            <div class="reference-links" style="margin-bottom: 14px;">
              <a class="button" href="/manual" target="_blank" rel="noreferrer">Open tool manual</a>
              <a class="button" href="/stress-test-corpus" target="_blank" rel="noreferrer">Stress-test tutorial</a>
              <a class="button" href="#narrativeRepository" data-jump-repository>Open narrative repository</a>
              <button class="button" data-open-full-repository type="button">Open full repository</button>
            </div>
            <div class="intake-sequence">
              <div class="intake-step-grid">
                <div class="panel">
                  <span class="step-kicker">Step 1 / evidence route</span>
                  <h3>Choose evidence route</h3>
                  ${renderEvidenceModeSelector()}
                </div>
                ${renderIntakeLoadPanel()}
              </div>
              <div class="panel">
                <span class="step-kicker">Step 3 / common SDMX dimensions</span>
                <h3>Common SDMX dimensions</h3>
                <p>These dimensions make every evidence route comparable: place, source, language, period, and administrative level.</p>
                <div style="margin-top: 12px;">${renderCommonEvidenceFields(countries)}</div>
              </div>
              <div class="intake-linear-block">
                <span class="step-kicker">Step 4 / route-specific metadata</span>
                ${renderModeSpecificFields()}
              </div>
              <div class="intake-linear-block">
                <span class="step-kicker">Step 5 / narrative body and route worksheet</span>
                ${renderEvidenceBodyFlow()}
              </div>
              <div class="post-evidence-review">
                <span class="step-kicker">Step 6 / readiness and preview</span>
                ${renderIntakeOperationalPanel()}
              </div>
              <div class="intake-review-grid">
                ${renderStageSubmitPanel()}
                ${renderRepositoryPointerPanel()}
              </div>
            </div>
          </section>
        `;
      }

      function renderEvidenceBodyFlow() {
        const mode = state.template.evidenceMode;
        const narrative = renderNarrativeBox();
        const worksheet = renderModeWorkbench();
        const ordered = mode === "structured_interview"
          ? [worksheet, narrative]
          : [narrative, worksheet];
        return `<div class="evidence-body-flow">${ordered.join("")}</div>`;
      }

      function intakeOptionActionLabel(option = state.intakeOption) {
        return {
          manual: "Open manual",
          corpus: "Open stress-test guide",
          copy: "Copy field template",
          download: "Download CSV template",
          reset: "Reset intake"
        }[option] || "Run intake option";
      }

      function renderIntakeLoadPanel() {
        return `
          <div class="panel file-control-panel">
            <div>
              <span class="step-kicker">Step 2 / load or paste evidence</span>
              <h3>Load evidence file or one sample story</h3>
              <p>For stress tests, click <strong>Open text or CSV file</strong> and choose one file from <code>stress_test_corpus/</code>. TXT, MD, CSV, JSON, XML, and SDMX files are accepted.</p>
              <div class="button-row" style="margin-top: 12px;">
                <label class="button primary" for="fileInput">Open text or CSV file</label>
                <button class="button green" id="loadSample" type="button">Load one sample story</button>
                <input id="fileInput" type="file" accept=".txt,.md,.csv,.json,.xml,.sdmx" hidden />
              </div>
              <p class="select-note">Load one sample story fills a single built-in Rwanda example for manual intake practice. It is not the stress-test corpus.</p>
            </div>
            <div class="intake-option-strip">
              <h3>Intake Option</h3>
              <div class="compact-select-row">
                <div class="field"><label for="intakeOptionSelect">Supporting tool</label><select id="intakeOptionSelect">
                  <option ${selectedAttr("manual", state.intakeOption)} value="manual">Manual</option>
                  <option ${selectedAttr("corpus", state.intakeOption)} value="corpus">Stress-test corpus</option>
                  <option ${selectedAttr("copy", state.intakeOption)} value="copy">Copy field template</option>
                  <option ${selectedAttr("download", state.intakeOption)} value="download">Download CSV template</option>
                  <option ${selectedAttr("reset", state.intakeOption)} value="reset">Reset intake</option>
                </select></div>
                <button class="button" id="runIntakeOption" type="button">${escapeHtml(intakeOptionActionLabel())}</button>
              </div>
              <p class="select-note">Choose a supporting intake helper. The selected label tells you exactly what the button will do.</p>
            </div>
          </div>
        `;
      }

      function renderStageSubmitPanel() {
        return `
          <div class="panel stage-submit-panel">
            <div>
              <span class="step-kicker">Step 7 / stage and validate</span>
              <h3>Stage evidence into the governed ledger</h3>
              <p>After the readiness panel shows the route, place, source, period, and evidence body, stage the record. NDIM then creates narrative observations for the SDMX gate, review queue, hashes, and later encoding.</p>
            </div>
            <div class="button-row">
              <button class="button primary" id="stageEvidence" type="button">Stage and validate</button>
            </div>
          </div>
        `;
      }

      function renderRepositoryPointerPanel() {
        return `
          <div class="panel repository-pointer-panel">
            <div>
              <span class="step-kicker">Step 8 / repository ledger</span>
              <h3>Open the narrative repository</h3>
              <p>${escapeHtml(state.records.length ? "The active ledger is in the workbench at the top of the page. Open it to inspect staged records and click narrative IDs for governed review." : "The repository is empty right now. Upload a corpus file or use the manual sample, then click Stage and validate to create ledger records.")}</p>
            </div>
            <div class="button-row">
              <a class="button" href="#narrativeRepository" data-jump-repository>Open narrative repository</a>
              <button class="button" data-open-full-repository type="button">Open full repository</button>
            </div>
          </div>
        `;
      }

      function renderTemplateContract() {
        const rows = [
          ["Evidence route", currentEvidenceMode().title, Boolean(state.template.evidenceMode)],
          ...countrySchema().levels.map((level) => [level.label, state.meta[level.key], Boolean(state.meta[level.key])]),
          ["Source", `${state.meta.sourceType} / ${state.meta.sourceName}`, Boolean(state.meta.sourceName)],
          ["Period", state.meta.period, Boolean(state.meta.period)],
          ["Language", state.meta.language, Boolean(state.meta.language)],
          ["Consent tier", state.governance.consent, Boolean(state.governance.consent)],
          ["Visibility", state.governance.visibility, Boolean(state.governance.visibility)]
        ];
        if (state.template.evidenceMode === "structured_interview") {
          rows.push(
            ["Interview ID", state.template.interviewId, Boolean(state.template.interviewId)],
            ["Respondent profile", state.template.respondentProfile, Boolean(state.template.respondentProfile)],
            ["Primary decision-maker", state.template.decisionMaker, Boolean(state.template.decisionMaker)],
            ["Current cooking methods", state.template.cookingMethods, Boolean(state.template.cookingMethods)],
            ...narrativeQuestions.map((question) => [question.title, state.template[question.id], Boolean(state.template[question.id])])
          );
        } else if (state.template.evidenceMode === "indigenous_knowledge") {
          rows.push(
            ["Knowledge record ID", state.template.interviewId || "recommended", true],
            ["Knowledge type", state.template.knowledgeType, Boolean(state.template.knowledgeType)],
            ["Knowledge holder", state.template.knowledgeHolder, Boolean(state.template.knowledgeHolder)],
            ["Sensitivity", state.template.sensitivity, Boolean(state.template.sensitivity)],
            ["Community validation", state.template.communityValidation, Boolean(state.template.communityValidation)],
            ["Attribution", state.template.attribution, Boolean(state.template.attribution)]
          );
        } else if (state.template.evidenceMode === "citizen_science") {
          rows.push(
            ["Report ID", state.template.interviewId || "recommended", true],
            ["Contributor type", state.template.contributorType, Boolean(state.template.contributorType)],
            ["Observation date", state.template.observationDate, Boolean(state.template.observationDate)],
            ["Contributor confidence", state.template.citizenConfidence, Boolean(state.template.citizenConfidence)],
            ["Validation status", state.template.validationStatus, Boolean(state.template.validationStatus)]
          );
        } else if (state.template.evidenceMode === "experimental_feed") {
          rows.push(
            ["Feed batch ID", state.template.interviewId || "recommended", true],
            ["Feed sources", (state.template.feedSources || []).join(", "), Array.isArray(state.template.feedSources) && state.template.feedSources.length > 0],
            ["Validation status", state.template.validationStatus, Boolean(state.template.validationStatus)],
            ["Attribution", state.template.attribution || "mode-dependent", true],
            ["Interpretation notes", state.template.translationNotes || "recommended", true]
          );
        } else {
          rows.push(
            ["Record or batch ID", state.template.interviewId || "recommended", true],
            ["Attribution", state.template.attribution || "mode-dependent", true],
            ["Validation status", state.template.validationStatus || "mode-dependent", true],
            ["Interpretation notes", state.template.translationNotes || "optional", true]
          );
        }
        rows.push(
          ["Tone / archetype", state.template.tone || "optional analytic coding", true],
          ["Adoption stance", state.template.stance || "optional analytic coding", true],
          ["Key barrier", state.template.barrier || "optional analytic coding", true],
          ["Key motivator", state.template.motivator || "optional analytic coding", true],
          ["Social influence", state.template.socialInfluence || "optional analytic coding", true]
        );
        return `
          <div class="template-table">
            <div class="template-row head"><span>Template field</span><span>Current value</span><span>Status</span></div>
            ${rows.map(([field, value, pass]) => `
              <div class="template-row">
                <span data-label="Template field">${escapeHtml(field)}</span>
                <span data-label="Current value">${escapeHtml(value || "missing")}</span>
                <span data-label="Status">${pass ? "ready" : "needed"}</span>
              </div>
            `).join("")}
          </div>
        `;
      }

      function isStructuredInterview() {
        return state.template.evidenceMode === "structured_interview";
      }

      function renderCommonEvidenceFields(countries) {
        return `
          <div class="field-grid">
            <div class="field"><label for="country">Country</label><select id="country">${countries.map((country) => `<option ${selectedAttr(country, state.meta.country)}>${country}</option>`).join("")}</select></div>
            ${renderAdminFields()}
            <div class="field"><label for="language">Language</label><select id="language"><option ${selectedAttr("en", state.meta.language)} value="en">English</option><option ${selectedAttr("rw", state.meta.language)} value="rw">Kinyarwanda</option><option ${selectedAttr("fr", state.meta.language)} value="fr">French</option><option ${selectedAttr("sw", state.meta.language)} value="sw">Swahili</option></select></div>
            <div class="field"><label for="sourceType">Source type</label><select id="sourceType"><option ${selectedAttr("field_note", state.meta.sourceType)} value="field_note">Field note</option><option ${selectedAttr("interview", state.meta.sourceType)} value="interview">Interview</option><option ${selectedAttr("focus_group", state.meta.sourceType)} value="focus_group">Focus group</option><option ${selectedAttr("oral_history", state.meta.sourceType)} value="oral_history">Oral history</option><option ${selectedAttr("community_meeting", state.meta.sourceType)} value="community_meeting">Community meeting</option><option ${selectedAttr("citizen_report", state.meta.sourceType)} value="citizen_report">Citizen report</option><option ${selectedAttr("indigenous_knowledge", state.meta.sourceType)} value="indigenous_knowledge">Indigenous knowledge</option><option ${selectedAttr("radio", state.meta.sourceType)} value="radio">Radio transcript</option><option ${selectedAttr("social_feed", state.meta.sourceType)} value="social_feed">Social/community feed</option><option ${selectedAttr("policy_brief", state.meta.sourceType)} value="policy_brief">Policy brief</option><option ${selectedAttr("csv", state.meta.sourceType)} value="csv">CSV extract</option><option ${selectedAttr("sdmx", state.meta.sourceType)} value="sdmx">SDMX exchange</option></select></div>
            <div class="field"><label for="sourceName">Source name</label><input id="sourceName" value="${escapeHtml(state.meta.sourceName)}" /></div>
            <div class="field"><label for="period">Period</label><input id="period" value="${escapeHtml(state.meta.period)}" /></div>
          </div>
        `;
      }

      function renderModeSpecificFields() {
        const mode = state.template.evidenceMode;
        if (mode === "structured_interview") {
          return `
            <div class="panel" style="margin-top: 14px;">
              <h3>Structured interview metadata</h3>
              <p>Use this when an enumerator is collecting Q1-Q5 responses from one respondent or household.</p>
              <div class="field-grid" style="margin-top: 12px;">
                <div class="field"><label for="interviewId">Interview ID</label><input id="interviewId" value="${escapeHtml(state.template.interviewId)}" placeholder="e.g., RW-NYA-001" /></div>
                <div class="field"><label for="respondentProfile">Respondent profile</label><input id="respondentProfile" value="${escapeHtml(state.template.respondentProfile)}" placeholder="age range, gender, occupation" /></div>
                <div class="field"><label for="decisionMaker">Primary cooking decision-maker</label><select id="decisionMaker"><option value="">Select</option><option ${selectedAttr("yes", state.template.decisionMaker)} value="yes">Yes</option><option ${selectedAttr("no", state.template.decisionMaker)} value="no">No</option><option ${selectedAttr("shared", state.template.decisionMaker)} value="shared">Shared decision</option></select></div>
                <div class="field"><label for="cookingMethods">Current cooking method(s)</label><input id="cookingMethods" value="${escapeHtml(state.template.cookingMethods)}" placeholder="charcoal, firewood, LPG..." /></div>
              </div>
            </div>
          `;
        }
        if (mode === "indigenous_knowledge") {
          return `
            <div class="panel" style="margin-top: 14px;">
              <h3>Indigenous knowledge record</h3>
              <p>Capture who holds the knowledge, how sensitive it is, whether the community has validated it, and how it may be attributed.</p>
              <div class="field-grid" style="margin-top: 12px;">
                ${renderRecordIdField("Knowledge record ID", "e.g., IK-RW-MUS-001")}
                ${renderKnowledgeTypeField(true)}
                ${renderKnowledgeHolderField(true)}
                ${renderSensitivityField()}
                ${renderCommunityValidationField()}
                ${renderAttributionField()}
                ${renderLocationPrecisionField()}
                <div class="field"><label for="observationDate">Observation / recall date</label><input id="observationDate" type="date" value="${escapeHtml(state.template.observationDate)}" /></div>
                ${renderTranslationField()}
                ${renderBenefitSharingField()}
              </div>
            </div>
          `;
        }
        if (mode === "citizen_science") {
          return `
            <div class="panel" style="margin-top: 14px;">
              <h3>Citizen science report</h3>
              <p>Use this for community observations that need time, place, contributor confidence, validation, and review before model influence.</p>
              <div class="field-grid" style="margin-top: 12px;">
                ${renderRecordIdField("Report ID", "e.g., CS-RW-MUS-001")}
                ${renderContributorTypeField(true)}
                <div class="field"><label for="observationDate">Observation date</label><input id="observationDate" type="date" value="${escapeHtml(state.template.observationDate)}" /></div>
                ${renderCitizenConfidenceField()}
                ${renderValidationStatusField()}
                ${renderLocationPrecisionField()}
                ${renderKnowledgeTypeField(false)}
                ${renderTranslationField()}
              </div>
            </div>
          `;
        }
        if (mode === "crowd_batch") {
          return `
            <div class="panel" style="margin-top: 14px;">
              <h3>Crowdsourced batch setup</h3>
              <p>Use this for many community submissions. Import CSV or paste one story per paragraph, then approve eligible records in the SDMX gate.</p>
              <div class="field-grid" style="margin-top: 12px;">
                ${renderRecordIdField("Batch ID", "e.g., BATCH-RW-2026-01")}
                ${renderContributorTypeField(false)}
                ${renderValidationStatusField()}
                ${renderAttributionField()}
                ${renderLocationPrecisionField()}
                ${renderBenefitSharingField()}
              </div>
            </div>
          `;
        }
        if (mode === "experimental_feed") {
          return `
            <div class="panel" style="margin-top: 14px;">
              <h3>Social media feed intake</h3>
              <p>Select one or more feed vehicles, then paste one post, comment, transcript excerpt, or moderated summary per line. These are experimental evidence inputs until they pass SDMX governance and human validation.</p>
              ${renderSocialFeedSourceCheckboxes()}
              <div class="field-grid" style="margin-top: 12px;">
                ${renderRecordIdField("Feed batch ID", "e.g., FEED-MUS-RADIO-01")}
                ${renderContributorTypeField(false)}
                <div class="field"><label for="observationDate">Capture date</label><input id="observationDate" type="date" value="${escapeHtml(state.template.observationDate)}" /></div>
                ${renderValidationStatusField()}
                ${renderLocationPrecisionField()}
                ${renderTranslationField()}
              </div>
            </div>
          `;
        }
        return `
          <div class="panel" style="margin-top: 14px;">
            <h3>Open story record</h3>
            <p>Use this for oral histories, field notes, community accounts, and lived-experience stories that do not fit the Q1-Q5 structure.</p>
            <div class="field-grid" style="margin-top: 12px;">
              ${renderRecordIdField("Story ID", "e.g., STORY-RW-MUS-001")}
              ${renderContributorTypeField(false)}
              ${renderAttributionField()}
              ${renderLocationPrecisionField()}
              ${renderKnowledgeTypeField(false)}
              ${renderKnowledgeHolderField(false)}
              ${renderCommunityValidationField()}
              ${renderTranslationField()}
            </div>
          </div>
        `;
      }

      function renderSocialFeedSourceCheckboxes() {
        const selected = new Set(Array.isArray(state.template.feedSources) ? state.template.feedSources : []);
        return `
          <div class="field" style="margin-top: 12px;">
            <label>Feed sources</label>
            <div class="checkbox-grid">
              ${socialFeedSources.map(([value, label]) => `
                <label class="check-card">
                  <input type="checkbox" data-feed-source value="${escapeHtml(value)}" ${selected.has(value) ? "checked" : ""} />
                  <span>${escapeHtml(label)}</span>
                </label>
              `).join("")}
            </div>
          </div>
        `;
      }

      function renderNarrativeBox() {
        const mode = state.template.evidenceMode;
        const placeholder = {
          structured_interview: "Optional extra notes that did not fit Q1-Q5. Separate extra narratives with blank lines...",
          open_story: "Paste the full story in the contributor's own words. Keep sequence, emotion, local terms, and context...",
          indigenous_knowledge: "Record the knowledge carefully: local practice, seasonal memory, elder testimony, cultural explanation, or ecological observation...",
          citizen_science: "Paste the observation: what was seen, where, when, by whom, and how confident the contributor is...",
          crowd_batch: "Paste one submitted story per paragraph, or load a CSV with evidence_mode, country, admin fields, and narrative/text/quote columns...",
          experimental_feed: "Paste one social media post, community comment, radio transcript excerpt, WhatsApp summary, or moderated feed item per line. Each line becomes an observation after governance..."
        }[mode] || "Paste narrative evidence here...";
        return `
          <div class="panel" style="margin-top: 14px;">
            <h3>${escapeHtml(narrativeEvidenceTitle())}</h3>
            <p>${escapeHtml(mode === "structured_interview" ? "The main evidence comes from Q1-Q5 on the right. Use this box for supplementary notes." : "This is the primary evidence body for the selected route.")}</p>
            <textarea id="narrativeText" placeholder="${escapeHtml(placeholder)}" style="margin-top: 12px;">${escapeHtml(state.text)}</textarea>
          </div>
        `;
      }

      function renderModeWorkbench() {
        const mode = state.template.evidenceMode;
        const summary = renderStageCreationSummary();
        if (mode === "structured_interview") {
          return `
            <div class="panel">
              ${summary}
              <h3 style="margin-top: 16px;">Q1-Q5 interview worksheet</h3>
              <p>Use these compact prompts when a field enumerator is collecting comparable clean-cooking stories.</p>
              <div class="question-stack" style="margin-top: 10px;">${renderQuestionCards()}</div>
              <h3 style="margin-top: 16px;">Post-interview coding fields</h3>
              <p>Complete these after the interview; they travel with the records for encoding comparison and policy audit.</p>
              <div style="margin-top: 10px;">${renderCodingFields()}</div>
              <div class="guide-note"><strong>Optional probes for enumerators</strong><p>Can you give an example? What happened next? How did that make you feel? What did others do in that situation?</p></div>
            </div>
          `;
        }
        if (mode === "indigenous_knowledge") {
          return `
            <div class="panel">
              ${summary}
              <h3 style="margin-top: 16px;">Knowledge stewardship prompts</h3>
              <div class="check-list">
                ${knowledgePrompt("Respect", "Is this knowledge ordinary, culturally sensitive, restricted, or not shareable?")}
                ${knowledgePrompt("Validation", "Who can validate or dispute this story inside the community?")}
                ${knowledgePrompt("Attribution", "Should this be anonymous, community-attributed, or contributor-attributed?")}
                ${knowledgePrompt("Use", "Can this influence policy directly, or only guide questions for follow-up?")}
              </div>
              <h3 style="margin-top: 16px;">Optional analytic coding</h3>
              <p>Use coding only after preserving the original meaning and translation notes.</p>
              <div style="margin-top: 10px;">${renderCodingFields()}</div>
            </div>
          `;
        }
        if (mode === "citizen_science") {
          return `
            <div class="panel">
              ${summary}
              <h3 style="margin-top: 16px;">Citizen report checklist</h3>
              <div class="check-list">
                ${knowledgePrompt("Observation", "What exactly was observed, and when?")}
                ${knowledgePrompt("Place", "Is the location exact, approximate, or anonymized?")}
                ${knowledgePrompt("Confidence", "How confident is the contributor, and why?")}
                ${knowledgePrompt("Validation", "Has a moderator, enumerator, or second source reviewed it?")}
              </div>
              <h3 style="margin-top: 16px;">Optional analytic coding</h3>
              <div style="margin-top: 10px;">${renderCodingFields()}</div>
            </div>
          `;
        }
        if (mode === "crowd_batch") {
          return `
            <div class="panel">
              ${summary}
              <h3 style="margin-top: 16px;">Batch ingestion structure</h3>
              <p>Use CSV for many submissions. NDIM splits each row into an observation, then the SDMX gate hashes, scans, and queues records for approval.</p>
              <div class="template-table" style="margin-top: 12px;">
                <div class="template-row head"><span>Column</span><span>Purpose</span><span>Required</span></div>
                ${[
                  ["evidence_mode", "structured_interview, open_story, indigenous_knowledge, citizen_science, crowd_batch, or experimental_feed", "yes"],
                  ["country/admin fields", "Country and country-specific administrative unit columns", "yes"],
                  ["source_name/period/language", "Provenance and SDMX dimensions", "yes"],
                  ["narrative/text/quote", "The submitted story text", "yes"],
                  ["knowledge_type/sensitivity/community_validation", "Governance and indigenous/citizen metadata", "recommended"]
                ].map(([a, b, c]) => `<div class="template-row"><span data-label="Column">${escapeHtml(a)}</span><span data-label="Purpose">${escapeHtml(b)}</span><span data-label="Required">${escapeHtml(c)}</span></div>`).join("")}
              </div>
            </div>
          `;
        }
        if (mode === "experimental_feed") {
          return `
            <div class="panel">
              ${summary}
              <h3 style="margin-top: 16px;">Social media feed rules</h3>
              <div class="check-list">
                ${knowledgePrompt("Not core evidence", "Feed items are sandbox inputs until consent, provenance, and validation rules are satisfied.")}
                ${knowledgePrompt("Counter-feed", "Use these to detect misinformation patterns and draft responses, not to make final policy claims.")}
                ${knowledgePrompt("Promotion path", "A feed item can become core evidence only after review in the SDMX gate.")}
              </div>
            </div>
          `;
        }
        return `
          <div class="panel">
            ${summary}
            <h3 style="margin-top: 16px;">Open story prompts</h3>
            <div class="check-list">
              ${knowledgePrompt("Context", "Who is speaking, where, and what situation produced the story?")}
              ${knowledgePrompt("Meaning", "What local terms, metaphors, memories, or norms matter for interpretation?")}
              ${knowledgePrompt("Tension", "What barrier, trust issue, motivation, or social influence appears in the story?")}
              ${knowledgePrompt("Implication", "What should policy makers learn, and what still needs validation?")}
            </div>
            <h3 style="margin-top: 16px;">Optional analytic coding</h3>
            <div style="margin-top: 10px;">${renderCodingFields()}</div>
          </div>
        `;
      }

      function renderStageCreationSummary() {
        return `
          <h3>What this route creates</h3>
          <p>${escapeHtml(currentEvidenceMode().title)} records become governed NarrativeRecords with evidence mode, country, administrative units, consent, source, period, text, approval status, and mode-specific metadata.</p>
          <div class="metric-grid" style="margin-top: 12px;">
            <div class="metric"><span class="mini-label">Mode</span><strong>${escapeHtml(currentEvidenceMode().title.split(" ")[0])}</strong></div>
            <div class="metric"><span class="mini-label">Admin path</span><strong>${adminUnitParts().length || "-"}</strong></div>
            <div class="metric"><span class="mini-label">Records</span><strong>${state.records.length || "-"}</strong></div>
          </div>
        `;
      }

      function knowledgePrompt(title, copy) {
        return `<div class="check pass"><i>?</i><div><strong>${escapeHtml(title)}</strong><span>${escapeHtml(copy)}</span></div></div>`;
      }

      function renderIntakeOperationalPanel() {
        const preview = state.records[0]?.text || state.text || questionBlocks()[0]?.answer || "";
        const rows = [
          ["Route", currentEvidenceMode().title, Boolean(state.template.evidenceMode)],
          ["Place", adminUnitLabel() || state.meta.country, Boolean(state.meta.country && adminUnitParts().length)],
          ["Source", [state.meta.sourceType, state.meta.sourceName].filter(Boolean).join(" / "), Boolean(state.meta.sourceType && state.meta.sourceName)],
          ["Period", state.meta.period, Boolean(state.meta.period)],
          ["Evidence body", preview ? "present" : "waiting", Boolean(preview)],
          ["Staged records", state.records.length ? `${state.records.length}` : "not staged", state.records.length > 0]
        ];
        return `
          <div class="panel readiness-panel">
            <h3>SDMX readiness and record preview</h3>
            <p>This space now checks whether the intake can become governed narrative observations.</p>
            <div class="readiness-list">
              ${rows.map(([label, value, ready]) => renderReadinessRow(label, value, ready)).join("")}
            </div>
            <div class="record-preview">
              <span class="mini-label">Current evidence body</span>
              <blockquote>${escapeHtml(preview ? preview.slice(0, 420) + (preview.length > 420 ? "..." : "") : "Paste or upload narrative evidence to preview the first record here.")}</blockquote>
            </div>
          </div>
        `;
      }

      function renderReadinessRow(label, value, ready) {
        return `
          <div class="readiness-row ${ready ? "ready" : ""}">
            <strong>${escapeHtml(label)}</strong>
            <span title="${escapeHtml(value || "missing")}">${escapeHtml(value || "missing")}</span>
            <span>${ready ? "ready" : "needed"}</span>
          </div>
        `;
      }

      function renderRecordIdField(label, placeholder) {
        return `<div class="field"><label for="interviewId">${escapeHtml(label)}</label><input id="interviewId" value="${escapeHtml(state.template.interviewId)}" placeholder="${escapeHtml(placeholder)}" /></div>`;
      }

      function renderKnowledgeTypeField(required) {
        return `<div class="field"><label for="knowledgeType">Knowledge / evidence type${required ? "" : " (optional)"}</label><select id="knowledgeType">
          <option value="">Select if relevant</option><option ${selectedAttr("seasonal_memory", state.template.knowledgeType)} value="seasonal_memory">Seasonal memory</option><option ${selectedAttr("cooking_practice", state.template.knowledgeType)} value="cooking_practice">Cooking practice</option><option ${selectedAttr("fuel_ecology", state.template.knowledgeType)} value="fuel_ecology">Fuel ecology</option><option ${selectedAttr("health_observation", state.template.knowledgeType)} value="health_observation">Health observation</option><option ${selectedAttr("social_norm", state.template.knowledgeType)} value="social_norm">Social norm</option><option ${selectedAttr("cultural_explanation", state.template.knowledgeType)} value="cultural_explanation">Cultural explanation</option><option ${selectedAttr("policy_feedback", state.template.knowledgeType)} value="policy_feedback">Policy feedback</option>
        </select></div>`;
      }

      function renderKnowledgeHolderField(required) {
        return `<div class="field"><label for="knowledgeHolder">Knowledge holder / contributor${required ? "" : " (optional)"}</label><select id="knowledgeHolder">
          <option value="">Select if relevant</option><option ${selectedAttr("elder", state.template.knowledgeHolder)} value="elder">Elder</option><option ${selectedAttr("household", state.template.knowledgeHolder)} value="household">Household</option><option ${selectedAttr("women_group", state.template.knowledgeHolder)} value="women_group">Women's group</option><option ${selectedAttr("youth_group", state.template.knowledgeHolder)} value="youth_group">Youth group</option><option ${selectedAttr("community_leader", state.template.knowledgeHolder)} value="community_leader">Community leader</option><option ${selectedAttr("health_worker", state.template.knowledgeHolder)} value="health_worker">Health worker</option><option ${selectedAttr("technician", state.template.knowledgeHolder)} value="technician">Technician</option><option ${selectedAttr("anonymous_citizen", state.template.knowledgeHolder)} value="anonymous_citizen">Anonymous citizen</option>
        </select></div>`;
      }

      function renderSensitivityField() {
        return `<div class="field"><label for="sensitivity">Cultural sensitivity</label><select id="sensitivity"><option ${selectedAttr("ordinary", state.template.sensitivity)} value="ordinary">Ordinary</option><option ${selectedAttr("culturally_sensitive", state.template.sensitivity)} value="culturally_sensitive">Culturally sensitive</option><option ${selectedAttr("restricted", state.template.sensitivity)} value="restricted">Restricted</option><option ${selectedAttr("sacred_not_shareable", state.template.sensitivity)} value="sacred_not_shareable">Sacred / not shareable</option></select></div>`;
      }

      function renderCommunityValidationField() {
        return `<div class="field"><label for="communityValidation">Community validation</label><select id="communityValidation"><option ${selectedAttr("pending", state.template.communityValidation)} value="pending">Pending</option><option ${selectedAttr("community_validated", state.template.communityValidation)} value="community_validated">Community validated</option><option ${selectedAttr("disputed", state.template.communityValidation)} value="disputed">Disputed</option><option ${selectedAttr("needs_follow_up", state.template.communityValidation)} value="needs_follow_up">Needs follow-up</option></select></div>`;
      }

      function renderAttributionField() {
        return `<div class="field"><label for="attribution">Attribution preference</label><select id="attribution"><option ${selectedAttr("anonymous", state.template.attribution)} value="anonymous">Anonymous</option><option ${selectedAttr("community_named", state.template.attribution)} value="community_named">Community named</option><option ${selectedAttr("contributor_named", state.template.attribution)} value="contributor_named">Contributor named</option><option ${selectedAttr("do_not_attribute", state.template.attribution)} value="do_not_attribute">Do not attribute</option></select></div>`;
      }

      function renderLocationPrecisionField() {
        return `<div class="field"><label for="locationPrecision">Location precision</label><select id="locationPrecision"><option ${selectedAttr("exact", state.template.locationPrecision)} value="exact">Exact</option><option ${selectedAttr("approximate", state.template.locationPrecision)} value="approximate">Approximate</option><option ${selectedAttr("anonymized", state.template.locationPrecision)} value="anonymized">Anonymized</option></select></div>`;
      }

      function renderContributorTypeField(required) {
        return `<div class="field"><label for="contributorType">Contributor type${required ? "" : " (optional)"}</label><select id="contributorType"><option value="">Select if relevant</option><option ${selectedAttr("citizen", state.template.contributorType)} value="citizen">Citizen</option><option ${selectedAttr("enumerator", state.template.contributorType)} value="enumerator">Enumerator</option><option ${selectedAttr("community_moderator", state.template.contributorType)} value="community_moderator">Community moderator</option><option ${selectedAttr("researcher", state.template.contributorType)} value="researcher">Researcher</option><option ${selectedAttr("policy_officer", state.template.contributorType)} value="policy_officer">Policy officer</option></select></div>`;
      }

      function renderCitizenConfidenceField() {
        return `<div class="field"><label for="citizenConfidence">Contributor confidence</label><select id="citizenConfidence"><option ${selectedAttr("low", state.template.citizenConfidence)} value="low">Low</option><option ${selectedAttr("medium", state.template.citizenConfidence)} value="medium">Medium</option><option ${selectedAttr("high", state.template.citizenConfidence)} value="high">High</option></select></div>`;
      }

      function renderValidationStatusField() {
        return `<div class="field"><label for="validationStatus">Validation status</label><select id="validationStatus"><option ${selectedAttr("pending", state.template.validationStatus)} value="pending">Pending</option><option ${selectedAttr("triangulated", state.template.validationStatus)} value="triangulated">Triangulated</option><option ${selectedAttr("moderator_reviewed", state.template.validationStatus)} value="moderator_reviewed">Moderator reviewed</option><option ${selectedAttr("rejected", state.template.validationStatus)} value="rejected">Rejected</option></select></div>`;
      }

      function renderTranslationField() {
        return `<div class="field" style="grid-column: 1 / -1;"><label for="translationNotes">Translation / interpretation notes</label><input id="translationNotes" value="${escapeHtml(state.template.translationNotes)}" placeholder="local terms, translator notes, contested meanings..." /></div>`;
      }

      function renderBenefitSharingField() {
        return `<div class="field" style="grid-column: 1 / -1;"><label for="benefitSharing">Benefit sharing / community return note</label><input id="benefitSharing" value="${escapeHtml(state.template.benefitSharing)}" placeholder="how insights will be returned to contributors or community reviewers..." /></div>`;
      }

      function renderEvidenceModeSelector() {
        const selected = currentEvidenceMode();
        return `
          <div class="field" style="margin-top: 10px;"><label for="evidenceModeSelect">Evidence route</label><select id="evidenceModeSelect">
            ${evidenceModes.map((mode) => `<option ${selectedAttr(mode.id, state.template.evidenceMode)} value="${escapeHtml(mode.id)}">${escapeHtml(mode.title)}</option>`).join("")}
          </select></div>
          <div class="route-context">
            <h3>${escapeHtml(selected.title)}</h3>
            <p>${escapeHtml(`${selected.short}. ${selected.detail}`)}</p>
          </div>
        `;
      }

      function renderNarrativeCommonsFields() {
        const mode = state.template.evidenceMode;
        const showKnowledge = mode === "indigenous_knowledge" || mode === "open_story";
        const showCitizen = mode === "citizen_science" || mode === "crowd_batch";
        const showBatch = mode === "crowd_batch" || mode === "experimental_feed";
        return `
          <div class="panel" style="margin-top: 14px;">
            <h3>Narrative Commons metadata</h3>
            <p>These fields let NDIM handle indigenous knowledge, citizen science, and crowdsourced evidence as situated knowledge rather than anonymous text.</p>
            <div class="field-grid" style="margin-top: 12px;">
              <div class="field"><label for="knowledgeType">Knowledge / evidence type</label><select id="knowledgeType">
                <option value="">Select if relevant</option>
                <option ${selectedAttr("seasonal_memory", state.template.knowledgeType)} value="seasonal_memory">Seasonal memory</option>
                <option ${selectedAttr("cooking_practice", state.template.knowledgeType)} value="cooking_practice">Cooking practice</option>
                <option ${selectedAttr("fuel_ecology", state.template.knowledgeType)} value="fuel_ecology">Fuel ecology</option>
                <option ${selectedAttr("health_observation", state.template.knowledgeType)} value="health_observation">Health observation</option>
                <option ${selectedAttr("social_norm", state.template.knowledgeType)} value="social_norm">Social norm</option>
                <option ${selectedAttr("cultural_explanation", state.template.knowledgeType)} value="cultural_explanation">Cultural explanation</option>
                <option ${selectedAttr("policy_feedback", state.template.knowledgeType)} value="policy_feedback">Policy feedback</option>
              </select></div>
              <div class="field"><label for="knowledgeHolder">Knowledge holder / contributor</label><select id="knowledgeHolder">
                <option value="">Select if relevant</option>
                <option ${selectedAttr("elder", state.template.knowledgeHolder)} value="elder">Elder</option>
                <option ${selectedAttr("household", state.template.knowledgeHolder)} value="household">Household</option>
                <option ${selectedAttr("women_group", state.template.knowledgeHolder)} value="women_group">Women's group</option>
                <option ${selectedAttr("youth_group", state.template.knowledgeHolder)} value="youth_group">Youth group</option>
                <option ${selectedAttr("community_leader", state.template.knowledgeHolder)} value="community_leader">Community leader</option>
                <option ${selectedAttr("health_worker", state.template.knowledgeHolder)} value="health_worker">Health worker</option>
                <option ${selectedAttr("technician", state.template.knowledgeHolder)} value="technician">Technician</option>
                <option ${selectedAttr("anonymous_citizen", state.template.knowledgeHolder)} value="anonymous_citizen">Anonymous citizen</option>
              </select></div>
              <div class="field"><label for="sensitivity">Cultural sensitivity</label><select id="sensitivity">
                <option ${selectedAttr("ordinary", state.template.sensitivity)} value="ordinary">Ordinary</option>
                <option ${selectedAttr("culturally_sensitive", state.template.sensitivity)} value="culturally_sensitive">Culturally sensitive</option>
                <option ${selectedAttr("restricted", state.template.sensitivity)} value="restricted">Restricted</option>
                <option ${selectedAttr("sacred_not_shareable", state.template.sensitivity)} value="sacred_not_shareable">Sacred / not shareable</option>
              </select></div>
              <div class="field"><label for="communityValidation">Community validation</label><select id="communityValidation">
                <option ${selectedAttr("pending", state.template.communityValidation)} value="pending">Pending</option>
                <option ${selectedAttr("community_validated", state.template.communityValidation)} value="community_validated">Community validated</option>
                <option ${selectedAttr("disputed", state.template.communityValidation)} value="disputed">Disputed</option>
                <option ${selectedAttr("needs_follow_up", state.template.communityValidation)} value="needs_follow_up">Needs follow-up</option>
              </select></div>
              <div class="field"><label for="attribution">Attribution preference</label><select id="attribution">
                <option ${selectedAttr("anonymous", state.template.attribution)} value="anonymous">Anonymous</option>
                <option ${selectedAttr("community_named", state.template.attribution)} value="community_named">Community named</option>
                <option ${selectedAttr("contributor_named", state.template.attribution)} value="contributor_named">Contributor named</option>
                <option ${selectedAttr("do_not_attribute", state.template.attribution)} value="do_not_attribute">Do not attribute</option>
              </select></div>
              <div class="field"><label for="locationPrecision">Location precision</label><select id="locationPrecision">
                <option ${selectedAttr("exact", state.template.locationPrecision)} value="exact">Exact</option>
                <option ${selectedAttr("approximate", state.template.locationPrecision)} value="approximate">Approximate</option>
                <option ${selectedAttr("anonymized", state.template.locationPrecision)} value="anonymized">Anonymized</option>
              </select></div>
              <div class="field"><label for="observationDate">Observation date</label><input id="observationDate" type="date" value="${escapeHtml(state.template.observationDate)}" /></div>
              <div class="field"><label for="contributorType">Contributor type</label><select id="contributorType">
                <option value="">Select if relevant</option>
                <option ${selectedAttr("citizen", state.template.contributorType)} value="citizen">Citizen</option>
                <option ${selectedAttr("enumerator", state.template.contributorType)} value="enumerator">Enumerator</option>
                <option ${selectedAttr("community_moderator", state.template.contributorType)} value="community_moderator">Community moderator</option>
                <option ${selectedAttr("researcher", state.template.contributorType)} value="researcher">Researcher</option>
                <option ${selectedAttr("policy_officer", state.template.contributorType)} value="policy_officer">Policy officer</option>
              </select></div>
              <div class="field"><label for="citizenConfidence">Contributor confidence</label><select id="citizenConfidence">
                <option ${selectedAttr("low", state.template.citizenConfidence)} value="low">Low</option>
                <option ${selectedAttr("medium", state.template.citizenConfidence)} value="medium">Medium</option>
                <option ${selectedAttr("high", state.template.citizenConfidence)} value="high">High</option>
              </select></div>
              <div class="field"><label for="validationStatus">Validation status</label><select id="validationStatus">
                <option ${selectedAttr("pending", state.template.validationStatus)} value="pending">Pending</option>
                <option ${selectedAttr("triangulated", state.template.validationStatus)} value="triangulated">Triangulated</option>
                <option ${selectedAttr("moderator_reviewed", state.template.validationStatus)} value="moderator_reviewed">Moderator reviewed</option>
                <option ${selectedAttr("rejected", state.template.validationStatus)} value="rejected">Rejected</option>
              </select></div>
              <div class="field" style="grid-column: 1 / -1;"><label for="translationNotes">Translation / interpretation notes</label><input id="translationNotes" value="${escapeHtml(state.template.translationNotes)}" placeholder="local terms, translator notes, contested meanings..." /></div>
              <div class="field" style="grid-column: 1 / -1;"><label for="benefitSharing">Benefit sharing / community return note</label><input id="benefitSharing" value="${escapeHtml(state.template.benefitSharing)}" placeholder="how insights will be returned to contributors or community reviewers..." /></div>
            </div>
            <div class="guide-note">
              <strong>${showKnowledge ? "Indigenous knowledge handling" : showCitizen ? "Citizen science handling" : showBatch ? "Crowdsourced evidence handling" : "Narrative evidence handling"}</strong>
              <p>${showKnowledge ? "Respect sensitivity, attribution, and community validation before using knowledge for policy claims." : showCitizen ? "Treat citizen reports as observations that need time, place, confidence, and validation before model influence." : showBatch ? "Batch evidence should pass moderation, duplicate checks, and approval before entering the shared corpus." : "Open stories remain valid evidence when provenance, consent, and interpretation notes are preserved."}</p>
            </div>
          </div>
        `;
      }

      function governanceStats() {
        const total = state.records.length;
        const approved = approvedRecords().length;
        const rejected = rejectedRepositoryRecords().length;
        const pendingCommit = pendingCommitRecords().length;
        const active = activeReviewRecords().length;
        const flagged = state.records.filter((record) => (record.governance?.scan?.risk || 0) >= state.governance.injectionThreshold).length;
        return { total, approved, rejected, pendingCommit, active, pending: Math.max(0, active - pendingCommit), flagged };
      }

      function recordStatusGroup(record) {
        const status = record?.governance?.status || "pending_review";
        if (status === "accepted_committed") return "accepted";
        if (status === "rejected_committed") return "rejected";
        if (status === "approved_pending_commit" || status === "rejected_pending_commit") return "pending_commit";
        return "active_review";
      }

      function recordEncoded(record) {
        return (state.encoded || []).find((item) => item.narrative_id === record?.narrative_id)
          || Object.values(state.encodingRuns || {}).flat().find((item) => item.narrative_id === record?.narrative_id)
          || null;
      }

      function recordThemes(record) {
        const encoded = recordEncoded(record);
        const coding = record?.metadata?.coding || {};
        const provenance = record?.metadata?.provenance || {};
        return [...new Set([
          ...(encoded?.themes || []),
          coding.key_barrier,
          coding.key_motivator,
          provenance.knowledge_type,
          provenance.evidence_mode,
          ...(record?.tags || [])
        ].filter(Boolean).map((item) => String(item).replace(/_/g, " ")))];
      }

      function repositoryFilterOption(values, current, label = "All") {
        const unique = [...new Set(values.filter(Boolean).map(String))].sort((a, b) => a.localeCompare(b));
        return `<option value="all">${escapeHtml(label)}</option>${unique.map((value) => `<option ${selectedAttr(value, current)} value="${escapeHtml(value)}">${escapeHtml(value)}</option>`).join("")}`;
      }

      function filterMatch(value, wanted) {
        return !wanted || wanted === "all" || String(value || "") === wanted;
      }

      function filteredRepositoryRecords(records) {
        const f = state.repositoryFilters;
        return records.filter((record) => {
          const encoded = recordEncoded(record) || {};
          const themes = recordThemes(record);
          const provenance = record.metadata?.provenance || {};
          const validation = provenance.validation_status || state.template.validationStatus || "";
          const trust = typeof encoded.trust_score === "number" ? encoded.trust_score : null;
          const barrier = typeof encoded.adoption_barrier_score === "number" ? encoded.adoption_barrier_score : null;
          const trustMin = f.trustMin === "" ? null : Number(f.trustMin);
          const trustMax = f.trustMax === "" ? null : Number(f.trustMax);
          const barrierMin = f.barrierMin === "" ? null : Number(f.barrierMin);
          const barrierMax = f.barrierMax === "" ? null : Number(f.barrierMax);
          if (!filterMatch(recordStatusGroup(record), f.status)) return false;
          if (!filterMatch(record.metadata?.provenance?.evidence_mode || state.template.evidenceMode, f.route)) return false;
          if (!filterMatch(record.metadata?.country, f.country)) return false;
          if (!filterMatch(recordAdminLabel(record), f.admin)) return false;
          if (!filterMatch(record.governance?.consent || provenance.consent_tier, f.consent)) return false;
          if (!filterMatch(record.governance?.visibility || provenance.visibility, f.visibility)) return false;
          if (!filterMatch(record.metadata?.source_type, f.source)) return false;
          if (!filterMatch(validation, f.validation)) return false;
          if (!filterMatch(record.governance?.master_repository_status || "not_prepared", f.master)) return false;
          if (f.theme !== "all" && !themes.includes(f.theme)) return false;
          if (trustMin !== null && (trust === null || trust < trustMin)) return false;
          if (trustMax !== null && (trust === null || trust > trustMax)) return false;
          if (barrierMin !== null && (barrier === null || barrier < barrierMin)) return false;
          if (barrierMax !== null && (barrier === null || barrier > barrierMax)) return false;
          return true;
        });
      }

      function repositoryCategoryStats(records = state.records) {
        const rows = records.map((record) => ({ record, encoded: recordEncoded(record), themes: recordThemes(record) }));
        const topThemes = topItems(rows.flatMap((row) => row.themes), 6);
        return {
          topThemes,
          highBarrier: rows.filter((row) => (row.encoded?.adoption_barrier_score || 0) >= 0.6).length,
          highTrust: rows.filter((row) => (row.encoded?.trust_score || 0) >= 0.65).length,
          inoculationOpportunity: rows.filter((row) => row.themes.some((theme) => /inoculation|misinformation|safety|rumou?r/i.test(theme))).length,
          indigenous: rows.filter((row) => /indigenous/i.test(row.record.metadata?.provenance?.evidence_mode || "")).length,
          socialFeeds: rows.filter((row) => /feed|social/i.test(row.record.metadata?.provenance?.evidence_mode || "")).length
        };
      }

      function renderRepositoryFilters(allRecords) {
        const f = state.repositoryFilters;
        const themes = [...new Set(allRecords.flatMap(recordThemes))];
        return `
          <div class="repository-filter-bar">
            <h3>Repository filters</h3>
            <p>Filters help explore the repository by governance state, place, source, route, and encoded themes. They do not change approval or commit status.</p>
            <div class="field-grid" style="margin-top: 12px;">
              <div class="field"><label for="repoFilterStatus">Approval status</label><select id="repoFilterStatus">
                <option ${selectedAttr("all", f.status)} value="all">All statuses</option>
                <option ${selectedAttr("active_review", f.status)} value="active_review">Active review</option>
                <option ${selectedAttr("pending_commit", f.status)} value="pending_commit">Reviewed, waiting commit</option>
                <option ${selectedAttr("accepted", f.status)} value="accepted">Accepted repository</option>
                <option ${selectedAttr("rejected", f.status)} value="rejected">Rejected repository</option>
              </select></div>
              <div class="field"><label for="repoFilterRoute">Evidence route</label><select id="repoFilterRoute">${repositoryFilterOption(allRecords.map((record) => record.metadata?.provenance?.evidence_mode || state.template.evidenceMode), f.route, "All routes")}</select></div>
              <div class="field"><label for="repoFilterCountry">Country</label><select id="repoFilterCountry">${repositoryFilterOption(allRecords.map((record) => record.metadata?.country), f.country, "All countries")}</select></div>
              <div class="field"><label for="repoFilterAdmin">Administrative unit</label><select id="repoFilterAdmin">${repositoryFilterOption(allRecords.map(recordAdminLabel), f.admin, "All places")}</select></div>
              <div class="field"><label for="repoFilterConsent">Consent tier</label><select id="repoFilterConsent">${repositoryFilterOption(allRecords.map((record) => record.governance?.consent || record.metadata?.provenance?.consent_tier), f.consent, "All consent")}</select></div>
              <div class="field"><label for="repoFilterVisibility">Visibility</label><select id="repoFilterVisibility">${repositoryFilterOption(allRecords.map((record) => record.governance?.visibility || record.metadata?.provenance?.visibility), f.visibility, "All visibility")}</select></div>
              <div class="field"><label for="repoFilterSource">Source type</label><select id="repoFilterSource">${repositoryFilterOption(allRecords.map((record) => record.metadata?.source_type), f.source, "All sources")}</select></div>
              <div class="field"><label for="repoFilterValidation">Validation status</label><select id="repoFilterValidation">${repositoryFilterOption(allRecords.map((record) => record.metadata?.provenance?.validation_status), f.validation, "All validation")}</select></div>
              <div class="field"><label for="repoFilterTheme">Common theme</label><select id="repoFilterTheme">${repositoryFilterOption(themes, f.theme, "All themes")}</select></div>
              <div class="field"><label for="repoFilterMaster">Master push status</label><select id="repoFilterMaster">${repositoryFilterOption(allRecords.map((record) => record.governance?.master_repository_status || "not_prepared"), f.master, "All master statuses")}</select></div>
              <div class="field"><label for="repoFilterTrustMin">Trust min</label><input id="repoFilterTrustMin" type="number" min="0" max="1" step="0.05" value="${escapeHtml(f.trustMin)}" placeholder="0.00" /></div>
              <div class="field"><label for="repoFilterTrustMax">Trust max</label><input id="repoFilterTrustMax" type="number" min="0" max="1" step="0.05" value="${escapeHtml(f.trustMax)}" placeholder="1.00" /></div>
              <div class="field"><label for="repoFilterBarrierMin">Barrier min</label><input id="repoFilterBarrierMin" type="number" min="0" max="1" step="0.05" value="${escapeHtml(f.barrierMin)}" placeholder="0.00" /></div>
              <div class="field"><label for="repoFilterBarrierMax">Barrier max</label><input id="repoFilterBarrierMax" type="number" min="0" max="1" step="0.05" value="${escapeHtml(f.barrierMax)}" placeholder="1.00" /></div>
            </div>
            <div class="button-row"><button class="button" id="resetRepositoryFilters" type="button">Reset filters</button></div>
          </div>
        `;
      }

      function renderRepositoryCategories(records) {
        const stats = repositoryCategoryStats(records);
        return `
          <div class="repository-filter-bar">
            <h3>Repository categories</h3>
            <p>These summaries help researchers find reusable evidence patterns before modelling or policy drafting.</p>
            <div class="repository-category-grid">
              <div class="repository-category"><span>Top themes</span><strong>${escapeHtml(stats.topThemes.join(", ") || "-")}</strong></div>
              <div class="repository-category"><span>High-barrier narratives</span><strong>${stats.highBarrier}</strong></div>
              <div class="repository-category"><span>High-trust narratives</span><strong>${stats.highTrust}</strong></div>
              <div class="repository-category"><span>Inoculation opportunities</span><strong>${stats.inoculationOpportunity}</strong></div>
              <div class="repository-category"><span>Indigenous knowledge</span><strong>${stats.indigenous}</strong></div>
              <div class="repository-category"><span>Social/feed records</span><strong>${stats.socialFeeds}</strong></div>
            </div>
          </div>
        `;
      }

      function masterEligibleRecords() {
        return acceptedRepositoryRecords().filter((record) => !["master_rejected", "master_synced"].includes(record.governance?.master_repository_status || "local_accepted"));
      }

      function sdmxCodelists(records = acceptedRepositoryRecords()) {
        const values = (getter) => [...new Set(records.map(getter).filter(Boolean).map(String))].sort();
        return {
          evidence_route: evidenceModes.map((mode) => ({ id: mode.id, name: mode.title })),
          country: values((record) => record.metadata?.country).map((id) => ({ id, name: id })),
          admin_unit: values(recordAdminLabel).map((id) => ({ id, name: id })),
          source_type: values((record) => record.metadata?.source_type).map((id) => ({ id, name: id })),
          consent_tier: values((record) => record.governance?.consent || record.metadata?.provenance?.consent_tier).map((id) => ({ id, name: id })),
          visibility_tier: values((record) => record.governance?.visibility || record.metadata?.provenance?.visibility).map((id) => ({ id, name: id })),
          review_status: ["local_accepted", "master_push_prepared", "master_review_pending", "master_approved", "master_rejected", "master_synced"].map((id) => ({ id, name: id.replace(/_/g, " ") })),
          themes: [...new Set(records.flatMap(recordThemes))].sort().map((id) => ({ id, name: id }))
        };
      }

      function sdmxDsd(records = acceptedRepositoryRecords()) {
        return {
          id: "NDIM_NARRATIVE_MASTER_PUSH_DSD",
          version: "1.0",
          agency: "NDIM Engine local-first federation",
          structure_type: "SDMX Data Structure Definition (DSD-like JSON)",
          dimensions: ["country", "admin_unit", "period", "language", "evidence_route"],
          attributes: ["source_type", "source_name", "consent_tier", "visibility_tier", "reviewer", "sensitivity", "validation_status", "master_review_status"],
          measures: ["narrative_text_policy", "themes", "trust_score", "barrier_score", "confidence", "content_hash", "evidence_hash"],
          codelists: sdmxCodelists(records)
        };
      }

      function sdmxObservations(records = acceptedRepositoryRecords()) {
        return records.map((record) => {
          const encoded = recordEncoded(record) || {};
          const provenance = record.metadata?.provenance || {};
          return {
            narrative_id: record.narrative_id,
            country: record.metadata?.country || "",
            admin_unit: recordAdminLabel(record),
            period: provenance.period || state.meta.period || "",
            language: record.metadata?.language || state.meta.language || "",
            evidence_route: provenance.evidence_mode || state.template.evidenceMode,
            source_type: record.metadata?.source_type || "",
            source_name: record.metadata?.source_name || "",
            consent_tier: record.governance?.consent || provenance.consent_tier || "",
            visibility_tier: record.governance?.visibility || provenance.visibility || "",
            reviewer: record.governance?.reviewer || "",
            sensitivity: provenance.sensitivity || "",
            validation_status: provenance.validation_status || "",
            master_review_status: record.governance?.master_repository_status || "local_accepted",
            narrative_text_policy: record.governance?.visibility === "public" ? "text_available_if_consent_allows" : "protected_text_local_only",
            narrative_text: record.governance?.visibility === "public" ? record.text : "",
            themes: recordThemes(record),
            trust_score: encoded.trust_score ?? null,
            barrier_score: encoded.adoption_barrier_score ?? null,
            confidence: encoded.confidence ?? null,
            content_hash: record.governance?.content_hash || "",
            evidence_hash: record.governance?.evidence_hash || "",
            route_metadata: provenance,
            uncommit_history: record.governance?.uncommit_history || []
          };
        });
      }

      function buildMasterPushPackage(status = state.masterRepository.status || "master_review_pending") {
        const records = masterEligibleRecords();
        return {
          schema: "ndim-master-repository-sdmx-push-v1",
          note: "Local-first export package for updating a master narrative repository such as Google Sheets, Google Drive, GitHub, Airtable, Supabase, or an institutional database. No upload occurs without a configured backend.",
          generated_at: new Date().toISOString(),
          target: state.masterRepository.target,
          backend: state.masterRepository.backend,
          master_review_status: status,
          local_repository: {
            accepted_records: acceptedRepositoryRecords().length,
            eligible_for_master_push: records.length,
            batch_digest: state.governance.lastDigest
          },
          master_reviewer: {
            name: state.masterRepository.reviewer,
            role: state.masterRepository.role,
            note: state.masterRepository.note
          },
          blockchain_ready_anchor: {
            blockchain_status: state.masterRepository.blockchainStatus || "not_anchored",
            previous_hash: state.masterRepository.previousHash || state.governance.ledger.at(-1)?.event_hash || "",
            anchor_hash: state.masterRepository.anchorHash || "",
            event_hash: state.masterRepository.eventHash || "",
            decision_hash: state.masterRepository.decisionHash || ""
          },
          sdmx: {
            dsd: sdmxDsd(records),
            observations: sdmxObservations(records)
          }
        };
      }

      function masterCsvObservations(records = masterEligibleRecords()) {
        const rows = sdmxObservations(records);
        const headers = ["narrative_id", "country", "admin_unit", "period", "language", "evidence_route", "source_type", "source_name", "consent_tier", "visibility_tier", "reviewer", "sensitivity", "validation_status", "master_review_status", "narrative_text_policy", "themes", "trust_score", "barrier_score", "confidence", "content_hash", "evidence_hash"];
        const cell = (value) => `"${String(Array.isArray(value) ? value.join(";") : value ?? "").replace(/"/g, '""')}"`;
        return `${headers.map(cell).join(",")}\n${rows.map((row) => headers.map((header) => cell(row[header])).join(",")).join("\n")}\n`;
      }

      function saveMasterRepositoryFromDom() {
        const reviewer = $("masterReviewer");
        const role = $("masterReviewerRole");
        const note = $("masterApprovalNote");
        const target = $("masterRepositoryTarget");
        if (reviewer) state.masterRepository.reviewer = reviewer.value || state.masterRepository.reviewer;
        if (role) state.masterRepository.role = role.value || state.masterRepository.role;
        if (note) state.masterRepository.note = note.value || "";
        if (target) state.masterRepository.target = target.value || state.masterRepository.target;
      }

      async function prepareMasterRepositoryPush() {
        saveMasterRepositoryFromDom();
        const records = masterEligibleRecords();
        if (!records.length) {
          toast("No accepted records to push");
          trace("master repository", "Master push blocked", "Only accepted local repository records are eligible for master repository export.");
          return null;
        }
        const preparedAt = new Date().toISOString();
        state.masterRepository.status = "master_review_pending";
        state.masterRepository.syncStatus = "ready_for_master_review";
        state.masterRepository.lastPreparedAt = preparedAt;
        state.masterRepository.previousHash = state.governance.ledger.at(-1)?.event_hash || "";
        records.forEach((record) => {
          record.governance.master_repository_status = "master_review_pending";
          record.governance.master_blockchain_status = "not_anchored";
        });
        let payload = buildMasterPushPackage("master_review_pending");
        const anchorHash = await sha256Hex(stableStringify(payload));
        const eventHash = await sha256Hex(stableStringify({
          action: "master_push_prepared",
          at: preparedAt,
          previous_hash: state.masterRepository.previousHash,
          anchor_hash: anchorHash,
          reviewer: state.masterRepository.reviewer,
          records: records.map((record) => record.narrative_id)
        }));
        state.masterRepository.anchorHash = anchorHash;
        state.masterRepository.eventHash = eventHash;
        state.masterRepository.blockchainStatus = "not_anchored";
        records.forEach((record) => {
          record.governance.master_anchor_hash = anchorHash;
          record.governance.master_event_hash = eventHash;
        });
        payload = buildMasterPushPackage("master_review_pending");
        state.masterRepository.package = payload;
        await appendLedger("master_push_prepared", `${records.length} accepted record(s) packaged for SDMX master repository review; anchor ${shortHash(anchorHash)}`, anchorHash);
        await syncLedgerToBackend("master repository push prepared");
        trace("master repository", "Master push prepared", "The package is SDMX-style, blockchain-ready, and waiting for master-level approval. No online upload was performed.");
        toast("Master push prepared");
        render();
        return payload;
      }

      async function decideMasterRepositoryPush(decision) {
        saveMasterRepositoryFromDom();
        if (!state.masterRepository.package) {
          const prepared = await prepareMasterRepositoryPush();
          if (!prepared) return;
        }
        const status = decision === "approved" ? "master_approved" : "master_rejected";
        const decidedAt = new Date().toISOString();
        const decisionHash = await sha256Hex(stableStringify({
          status,
          at: decidedAt,
          reviewer: state.masterRepository.reviewer,
          role: state.masterRepository.role,
          note: state.masterRepository.note,
          anchor_hash: state.masterRepository.anchorHash,
          previous_hash: state.masterRepository.eventHash
        }));
        state.masterRepository.status = status;
        state.masterRepository.syncStatus = decision === "approved" ? "approved_ready_for_upload" : "rejected_not_for_upload";
        state.masterRepository.lastDecisionAt = decidedAt;
        state.masterRepository.decisionHash = decisionHash;
        masterEligibleRecords().forEach((record) => {
          record.governance.master_repository_status = status;
          record.governance.master_reviewer = state.masterRepository.reviewer;
          record.governance.master_reviewed_at = decidedAt;
          record.governance.master_decision_hash = decisionHash;
          record.governance.master_blockchain_status = "not_anchored";
        });
        state.masterRepository.package = buildMasterPushPackage(status);
        await appendLedger(`master_${decision}`, `Master repository ${decision}: ${state.masterRepository.note || "no note"}`, decisionHash);
        await syncLedgerToBackend(`master repository ${decision}`);
        trace("master repository", `Master push ${decision}`, `Decision hash ${shortHash(decisionHash)} is chained to the local evidence ledger. Blockchain status remains not anchored.`);
        toast(`Master push ${decision}`);
        render();
      }

      async function ensureMasterPackageReady() {
        if (!state.masterRepository.package) return prepareMasterRepositoryPush();
        return state.masterRepository.package;
      }

      async function copyMasterRepositoryPackage() {
        const pkg = await ensureMasterPackageReady();
        if (!pkg) return;
        const copied = await copyText(JSON.stringify(pkg, null, 2), `ndim-master-sdmx-push-${Date.now()}.json`, "application/json");
        toast(copied ? "Master package copied" : "Copy blocked; package downloaded");
      }

      async function exportMasterRepositoryPackage() {
        const pkg = await ensureMasterPackageReady();
        if (!pkg) return;
        downloadText(`ndim-master-sdmx-push-${Date.now()}.json`, JSON.stringify(pkg, null, 2), "application/json");
        trace("master repository", "SDMX master package exported", "Downloaded the JSON SDMX push package. It is ready for upload to a configured master repository after master approval.");
        toast("SDMX package downloaded");
      }

      async function exportMasterRepositoryCsv() {
        const pkg = await ensureMasterPackageReady();
        if (!pkg) return;
        downloadText(`ndim-master-observations-${Date.now()}.csv`, masterCsvObservations(), "text/csv");
        trace("master repository", "CSV observation table exported", "Downloaded the SDMX-style observation table for Google Sheets or another master repository.");
        toast("CSV observation table downloaded");
      }

      async function exportMasterRepositoryDsd() {
        const pkg = await ensureMasterPackageReady();
        if (!pkg) return;
        downloadText(`ndim-master-structure-${Date.now()}.dsd.json`, JSON.stringify(sdmxDsd(masterEligibleRecords()), null, 2), "application/json");
        trace("master repository", "DSD structure exported", "Downloaded the DSD-like structure JSON with dimensions, attributes, measures, and code lists.");
        toast("DSD structure downloaded");
      }

      function renderGovernanceControls() {
        const stats = governanceStats();
        return `
          <div class="panel">
            <h3>Evidence governance controls</h3>
            <p>Every staged observation is hashed, scanned, assigned a visibility tier, and held for approval before encoding. Hashes prove tamper evidence; reviewer approval and provenance still decide whether evidence is trusted.</p>
            <div class="field-grid" style="margin-top: 12px;">
              <div class="field"><label for="reviewerName">Reviewer</label><input id="reviewerName" value="${escapeHtml(state.governance.reviewer)}" /></div>
              <div class="field"><label for="reviewerRole">Reviewer role</label><select id="reviewerRole">
                <option ${selectedAttr("researcher", state.governance.reviewerRole)} value="researcher">Researcher</option>
                <option ${selectedAttr("field_supervisor", state.governance.reviewerRole)} value="field_supervisor">Field supervisor</option>
                <option ${selectedAttr("ethics_reviewer", state.governance.reviewerRole)} value="ethics_reviewer">Ethics reviewer</option>
                <option ${selectedAttr("government_policy_team", state.governance.reviewerRole)} value="government_policy_team">Government policy team</option>
              </select></div>
              <div class="field"><label for="visibility">Output visibility</label><select id="visibility">
                <option ${selectedAttr("private", state.governance.visibility)} value="private">Private project only</option>
                <option ${selectedAttr("team", state.governance.visibility)} value="team">Team only</option>
                <option ${selectedAttr("institution", state.governance.visibility)} value="institution">Institution only</option>
                <option ${selectedAttr("consortium", state.governance.visibility)} value="consortium">Consortium</option>
                <option ${selectedAttr("public", state.governance.visibility)} value="public">Public approved corpus</option>
              </select></div>
              <div class="field"><label for="repositoryMode">Repository target</label><select id="repositoryMode">
                <option ${selectedAttr("local_project", state.governance.repositoryMode)} value="local_project">Local project</option>
                <option ${selectedAttr("federated_pending", state.governance.repositoryMode)} value="federated_pending">Federated registry queue</option>
                <option ${selectedAttr("shared_drive_export", state.governance.repositoryMode)} value="shared_drive_export">Shared drive export</option>
              </select></div>
              <div class="field"><label for="consentTier">Consent tier</label><select id="consentTier">
                <option ${selectedAttr("restricted_research", state.governance.consent)} value="restricted_research">Restricted research</option>
                <option ${selectedAttr("anonymized_research", state.governance.consent)} value="anonymized_research">Anonymized research</option>
                <option ${selectedAttr("policy_internal", state.governance.consent)} value="policy_internal">Policy internal</option>
                <option ${selectedAttr("public_release", state.governance.consent)} value="public_release">Public release</option>
              </select></div>
              <div class="field"><label for="injectionThreshold">Review threshold</label><input id="injectionThreshold" type="number" min="0" max="1" step="0.05" value="${state.governance.injectionThreshold}" /></div>
            </div>
            <div class="governance-grid">
              <div class="governance-card"><span>Total records</span><strong>${stats.total}</strong></div>
              <div class="governance-card"><span>Accepted</span><strong>${stats.approved}</strong></div>
              <div class="governance-card"><span>Pending commit</span><strong>${stats.pendingCommit}</strong></div>
              <div class="governance-card"><span>Flagged</span><strong>${stats.flagged}</strong></div>
              <div class="governance-card"><span>Batch digest</span><strong>${shortHash(state.governance.lastDigest)}</strong></div>
            </div>
            <div class="button-row">
              <button class="button" id="sealEvidence" type="button">Re-seal and scan</button>
              <button class="button green" id="approveEligible" type="button">Mark eligible approved</button>
              <button class="button" id="rejectFlagged" type="button">Reject flagged</button>
              <button class="button primary" id="commitReviewed" type="button">Commit reviewed records</button>
              <button class="button" id="copyLedger" type="button">Copy audit ledger</button>
              <button class="button" id="downloadLedger" type="button">Download ledger</button>
            </div>
          </div>
        `;
      }

      function renderRecordGovernance() {
        if (!state.records.length) return '<p>Stage evidence first to create governance records.</p>';
        const queue = activeReviewRecords();
        if (!queue.length) return '<p>The active approval queue is empty. Records you approved or rejected are now waiting for commit, or they have already moved into the accepted/rejected repository. Open the full repository to inspect them.</p>';
        return `<div class="record-governance">${queue.map((record) => {
          const index = state.records.indexOf(record);
          const gov = record.governance || {};
          const scan = gov.scan || scanNarrative(record, index);
          const status = gov.status || "pending_review";
          const statusClass = status === "approved_pending_commit" ? "ok" : status === "rejected_pending_commit" ? "bad" : "warn";
          const riskClass = scan.risk >= state.governance.injectionThreshold ? "bad" : scan.risk > 0.2 ? "warn" : "ok";
          const flags = [...(scan.injection_flags || []), ...(scan.pii_flags || []), ...(scan.quality_flags || [])];
          return `
            <article class="record-card">
              <header>
                <div>
                  <h4>Observation ${index + 1}: ${escapeHtml(record.metadata?.provenance?.question_title || record.narrative_id)}</h4>
                  <p>${escapeHtml(record.text.slice(0, 170))}${record.text.length > 170 ? "..." : ""}</p>
                </div>
                <span class="pill ${statusClass}">${escapeHtml(recordStatusLabel(record))}</span>
              </header>
              <div class="pill-row">
                <span class="pill ${riskClass}">risk ${scan.risk.toFixed(2)}</span>
                <span class="pill">hash ${escapeHtml(shortHash(gov.evidence_hash))}</span>
                <span class="pill">${escapeHtml(gov.visibility || state.governance.visibility)}</span>
                <span class="pill">${escapeHtml(gov.consent || state.governance.consent)}</span>
              </div>
              <p>${flags.length ? `Flags: ${escapeHtml(flags.join("; "))}` : "No injection, PII, duplicate, or minimum-quality flags detected."}</p>
              ${gov.review_reason ? `<p>Review decision: ${escapeHtml(gov.review_reason)}${status.includes("pending_commit") ? " (waiting for commit)" : ""}</p>` : ""}
              ${gov.reviewer_signature ? `<p>Reviewer signature: <span class="pill ok">${escapeHtml(shortHash(gov.reviewer_signature))}</span></p>` : ""}
              <div class="button-row">
                <button class="button green" data-approve-record="${index}" type="button">Approve</button>
                <button class="button" data-reject-record="${index}" type="button">Reject</button>
              </div>
            </article>
          `;
        }).join("")}</div>`;
      }

      function renderPendingCommitSummary() {
        const pending = pendingCommitRecords();
        if (!pending.length) {
          return '<p>No reviewed records are waiting for commit. Approve or reject records in the active queue first.</p>';
        }
        return `
          <div class="repository-table-wrap" style="margin-top: 12px;">
            <table class="repository-table">
              <thead><tr><th>Narrative ID</th><th>Decision</th><th>Reviewer</th><th>Reason</th></tr></thead>
              <tbody>
                ${pending.map((record) => `
                  <tr>
                    <td>${escapeHtml(record.narrative_id)}</td>
                    <td>${escapeHtml(recordStatusLabel(record))}</td>
                    <td>${escapeHtml(record.governance?.reviewer || state.governance.reviewer)}</td>
                    <td>${escapeHtml(record.governance?.review_reason || "reviewed")}</td>
                  </tr>
                `).join("")}
              </tbody>
            </table>
          </div>
        `;
      }

      function renderLedger() {
        if (!state.governance.ledger.length) return "<p>No ledger events yet. Stage evidence or approve records to create entries.</p>";
        return `<div class="ledger-list">${state.governance.ledger.slice().reverse().map((event) => `
          <div class="ledger-event">
            <strong>${String(event.index).padStart(2, "0")} ${escapeHtml(event.action)}</strong>
            <span>${escapeHtml(event.at)} | ${escapeHtml(event.actor)} | hash ${escapeHtml(shortHash(event.event_hash))}</span>
            <p>${escapeHtml(event.detail)}</p>
          </div>
        `).join("")}</div>`;
      }

      function renderGate() {
        const checks = gateChecks();
        return `
          <section class="stage-card">
            <p class="eyebrow">Stage 2</p>
            <h2>SDMX gate</h2>
            <p class="copy">The gate converts interviews, open stories, indigenous knowledge, citizen observations, and crowdsourced batches into a traceable SDMX-style observation contract before they can influence encoding or models.</p>
            <div class="button-row" style="margin-top: 0; margin-bottom: 14px;">
              <button class="button" id="copyGateTemplate" type="button">Copy field template</button>
              <button class="button" id="downloadGateCsv" type="button">Download CSV template</button>
            </div>
            ${renderGovernanceControls()}
            <div class="grid-2">
              <div class="check-list">
                ${checks.map(([label, value, pass]) => `
                  <div class="check ${pass ? "pass" : ""}"><i>${pass ? "OK" : "!"}</i><div><strong>${escapeHtml(label)}</strong><span>${escapeHtml(value || "missing")}</span></div></div>
                `).join("")}
                <div class="panel">
                  <h3>Collection template contract</h3>
                  <p>This table shows the current evidence contract. Q1-Q5 answers, open narratives, indigenous knowledge records, and citizen reports all become governed records for later stages.</p>
                  ${renderTemplateContract()}
                </div>
              </div>
              <div class="panel">
                <h3>Observation payload explained</h3>
                <div class="payload-body">${renderPayloadBody()}</div>
              </div>
            </div>
            <div class="grid-2" style="margin-top: 14px;">
              <div class="panel">
                <h3>Approval queue</h3>
                <p>Approve or reject records first, then click Commit reviewed records. Committed accepted records move into the accepted repository and become available for encoding; committed rejected records move into the rejected repository.</p>
                <div style="margin-top: 12px;">${renderRecordGovernance()}</div>
              </div>
              <div class="panel">
                <h3>Reviewed, waiting for commit</h3>
                <p>Once a record is approved or rejected it leaves the active queue and waits here. Commit reviewed records moves it into the accepted or rejected repository.</p>
                <div style="margin-top: 12px;">${renderPendingCommitSummary()}</div>
              </div>
            </div>
            <div class="grid-2" style="margin-top: 14px;">
              <div class="panel">
                <h3>Tamper-evident audit ledger</h3>
                <p>Each event is chained to the previous event hash. Later blockchain anchoring can publish the latest batch digest without exposing raw narratives.</p>
                <div style="margin-top: 12px;">${renderLedger()}</div>
              </div>
              <div class="panel">
                <h3>Repository next step</h3>
                <p>Open the full repository to filter narratives by route, place, consent, visibility, source, theme, trust, barrier strength, and master repository push status.</p>
                <div class="button-row">
                  <button class="button primary" data-open-full-repository type="button">Open full repository</button>
                </div>
              </div>
            </div>
          </section>
        `;
      }

      function renderPayloadBody() {
        if (!state.records.length) return '<div class="payload-item"><strong>No observations yet</strong><p>Return to intake, add narratives, and stage the evidence.</p></div>';
        return state.records.slice(0, 6).map((record, index) => `
          <div class="payload-item">
            <strong>Observation ${index + 1}: ${escapeHtml(record.metadata.country)} / ${escapeHtml(record.metadata.admin_unit || "national")}</strong>
            <p><b>Mode:</b> ${escapeHtml(record.metadata.provenance?.evidence_mode_label || "Narrative")}. <b>Question/type:</b> ${escapeHtml(record.metadata.provenance?.question_title || record.metadata.provenance?.knowledge_type || "Narrative")}. <b>Interview:</b> ${escapeHtml(record.metadata.interview_id || "not set")}. <b>Source:</b> ${escapeHtml(record.metadata.source_type)} from ${escapeHtml(record.metadata.source_name)}. <b>Language:</b> ${escapeHtml(record.metadata.language)}. <b>Text:</b> ${escapeHtml(record.text.slice(0, 220))}${record.text.length > 220 ? "..." : ""}</p>
            <p><b>Knowledge governance:</b> sensitivity ${escapeHtml(record.metadata.provenance?.sensitivity || "-")} | community validation ${escapeHtml(record.metadata.provenance?.community_validation || "-")} | attribution ${escapeHtml(record.metadata.provenance?.attribution || "-")}</p>
            <p><b>Governance:</b> ${escapeHtml(record.governance?.status || "pending review")} | evidence hash ${escapeHtml(shortHash(record.governance?.evidence_hash || ""))} | visibility ${escapeHtml(record.governance?.visibility || state.governance.visibility)}</p>
          </div>
        `).join("") + (state.records.length > 6 ? `<div class="payload-item"><strong>${state.records.length - 6} more observations</strong><p>They are included in batch encoding and modelling.</p></div>` : "");
      }

      function renderEncoding() {
        const record = currentReviewRecord();
        const card = ensureManualScorecard(record);
        const records = reviewableRecords();
        const reviewed = records.filter((item) => state.manualScorecards[item.narrative_id]?.status === "manual_reviewed").length;
        return `
          <section class="stage-card">
            <p class="eyebrow">Stage 3</p>
            <h2>Story-by-story encoding</h2>
            <p class="copy">Each approved narrative is encoded as its own scientific observation. Manual scoring now uses explicit numeric entries and coding rules, while AI and hybrid modes can still pre-code or compare results.</p>
            <div class="grid-3">
              ${renderEncodingOption("manual", "Manual / rule-based", "Transparent local scoring. Good for audits, offline review, and when no model key is configured.")}
              ${renderEncodingOption("ai", "AI encoder", "Uses the backend OpenAI path when OPENAI_API_KEY is configured; otherwise falls back safely.")}
              ${renderEncodingOption("hybrid", "Hybrid review", "AI/fallback score plus a human-review flag before the model uses it.")}
            </div>
            <div class="grid-2" style="margin-top: 14px;">
              <div class="panel">
                <h3>Manual researcher scorecard</h3>
                <p>Score the current story from 0 to 1. Write short justifications so another researcher can audit why each value was chosen.</p>
                ${renderStoryNavigator()}
                <div class="field-grid" style="margin-top: 12px;">
                  <div class="field"><label for="encoderName">Encoder name or ID</label><input id="encoderName" value="${escapeHtml(state.encoderName)}" placeholder="e.g., coder-01" /></div>
                  <div class="field"><label>Manual batch progress</label><input value="${reviewed} of ${records.length} reviewed" disabled /></div>
                </div>
                ${renderManualScorecard(record, card)}
              </div>
              <div>
                <div class="panel" style="margin-bottom: 14px;">
                  <h3>Batch review queue</h3>
                  <p>A CSV import becomes a queue of individual narratives. Use the queue or Next buttons to encode story by story; batch runs only automate scoring, they do not merge the stories.</p>
                  ${renderEncodingQueue()}
                </div>
                ${renderLLMSettings()}
                <div class="button-row" style="margin-top: 0;">
                  <button class="button primary" id="runEncoding" type="button">Run selected encoder</button>
                  <button class="button green" id="runCurrentEncoding" type="button">Encode current then next</button>
                  <button class="button" id="runAllEncodingModes" type="button">Compare all modes</button>
                  <button class="button" id="resetEncoding" type="button">Reset encoding</button>
                </div>
                ${renderEncodingTable()}
                ${renderEncodingComparison()}
              </div>
            </div>
          </section>
        `;
      }

      function renderEncodingOption(id, title, copy) {
        return `<button class="option ${state.encodingMode === id ? "active" : ""}" data-mode="${id}" type="button"><strong>${title}</strong><span>${copy}</span></button>`;
      }

      function llmProviderDefaults(provider = state.llmProvider) {
        return {
          openai: { model: "gpt-4o-mini", baseUrl: "", keyLabel: "OpenAI API key" },
          "azure-openai": { model: "deployment-name", baseUrl: "https://RESOURCE.openai.azure.com/openai/deployments/DEPLOYMENT", keyLabel: "Azure OpenAI key" },
          anthropic: { model: "claude-3-5-haiku-latest", baseUrl: "", keyLabel: "Anthropic API key" },
          gemini: { model: "gemini-1.5-flash", baseUrl: "https://generativelanguage.googleapis.com/v1beta", keyLabel: "Gemini API key" },
          openrouter: { model: "openai/gpt-4o-mini", baseUrl: "https://openrouter.ai/api/v1", keyLabel: "OpenRouter key" },
          mistral: { model: "mistral-small-latest", baseUrl: "https://api.mistral.ai/v1", keyLabel: "Mistral key" },
          ollama: { model: "llama3.1", baseUrl: "http://127.0.0.1:11434/api/chat", keyLabel: "No key needed" },
          lmstudio: { model: "local-model", baseUrl: "http://127.0.0.1:1234/v1", keyLabel: "No key needed" },
          "openai-compatible": { model: "local-model", baseUrl: "http://127.0.0.1:8000/v1", keyLabel: "Optional compatible API key" },
          local: { model: "llama3.1", baseUrl: "http://127.0.0.1:11434/api/chat", keyLabel: "No key needed" },
          deterministic: { model: "rule-based", baseUrl: "", keyLabel: "No key needed" }
        }[provider] || { model: "local-model", baseUrl: "", keyLabel: "API key" };
      }

      function llmStatusLabel() {
        const local = ["ollama", "lmstudio", "local", "deterministic"].includes(state.llmProvider);
        if (state.llmProvider === "deterministic") return "offline deterministic fallback";
        if (local) return "local endpoint; key not required";
        if (state.llmConfig.apiKey.trim()) return "session key configured";
        return "no session key; backend will try environment key or fallback";
      }

      function publicLlmConfig() {
        const defaults = llmProviderDefaults();
        return {
          provider: state.llmProvider,
          model: state.llmConfig.model || defaults.model,
          base_url_configured: Boolean(state.llmConfig.baseUrl || defaults.baseUrl),
          api_key_configured: Boolean(state.llmConfig.apiKey.trim()),
          credential_scope: state.llmConfig.apiKey.trim() ? "session_only_bring_your_own_key" : "environment_or_local_fallback",
          secret_stored: false
        };
      }

      function saveLlmConfigFromDom() {
        const providerEl = $("llmProvider");
        if (providerEl) state.llmProvider = providerEl.value;
        if ($("llmModel")) state.llmConfig.model = $("llmModel").value;
        if ($("llmBaseUrl")) state.llmConfig.baseUrl = $("llmBaseUrl").value;
        if ($("llmApiKey")) state.llmConfig.apiKey = $("llmApiKey").value;
        state.llmConfig.status = llmStatusLabel();
      }

      function llmRequestHeaders() {
        saveLlmConfigFromDom();
        const defaults = llmProviderDefaults();
        const headers = {
          "Content-Type": "application/json",
          "X-NDIM-LLM-Provider": state.llmProvider
        };
        const key = state.llmConfig.apiKey.trim();
        const model = (state.llmConfig.model || defaults.model || "").trim();
        const baseUrl = (state.llmConfig.baseUrl || defaults.baseUrl || "").trim();
        if (key) headers["X-NDIM-LLM-Key"] = key;
        if (model) headers["X-NDIM-LLM-Model"] = model;
        if (baseUrl) headers["X-NDIM-LLM-Base-URL"] = baseUrl;
        return headers;
      }

      function renderLLMSettings() {
        const defaults = llmProviderDefaults();
        return `
          <div class="panel" style="margin-bottom: 14px;">
            <h3>Bring your own LLM</h3>
            <p>Each user can choose a provider and enter a session-only key. The key is sent to the backend only during encoding, never printed in logs, and never included in policy JSON.</p>
            <div class="field-grid" style="margin-top: 12px;">
              <div class="field"><label for="llmProvider">Provider</label><select id="llmProvider">
                <option ${selectedAttr("openai", state.llmProvider)} value="openai">OpenAI</option>
                <option ${selectedAttr("anthropic", state.llmProvider)} value="anthropic">Anthropic</option>
                <option ${selectedAttr("gemini", state.llmProvider)} value="gemini">Gemini</option>
                <option ${selectedAttr("azure-openai", state.llmProvider)} value="azure-openai">Azure OpenAI</option>
                <option ${selectedAttr("openrouter", state.llmProvider)} value="openrouter">OpenRouter</option>
                <option ${selectedAttr("mistral", state.llmProvider)} value="mistral">Mistral</option>
                <option ${selectedAttr("ollama", state.llmProvider)} value="ollama">Ollama local</option>
                <option ${selectedAttr("lmstudio", state.llmProvider)} value="lmstudio">LM Studio local</option>
                <option ${selectedAttr("openai-compatible", state.llmProvider)} value="openai-compatible">OpenAI-compatible URL</option>
                <option ${selectedAttr("deterministic", state.llmProvider)} value="deterministic">Deterministic fallback</option>
              </select></div>
              <div class="field"><label for="llmModel">Model or deployment</label><input id="llmModel" value="${escapeHtml(state.llmConfig.model || defaults.model)}" placeholder="${escapeHtml(defaults.model)}" /></div>
              <div class="field"><label for="llmBaseUrl">Endpoint / base URL</label><input id="llmBaseUrl" value="${escapeHtml(state.llmConfig.baseUrl || defaults.baseUrl)}" placeholder="${escapeHtml(defaults.baseUrl || "provider default")}" /></div>
              <div class="field"><label for="llmApiKey">${escapeHtml(defaults.keyLabel)}</label><input id="llmApiKey" type="password" value="${escapeHtml(state.llmConfig.apiKey)}" placeholder="session only; leave blank for env/local/fallback" autocomplete="off" /></div>
            </div>
            <div class="pill-row" style="margin-top: 10px;">
              <span class="pill">${escapeHtml(llmStatusLabel())}</span>
              <span class="pill">secret stored: no</span>
              <span class="pill">manual encoding always available</span>
            </div>
          </div>
        `;
      }

      function renderManualScorecard(record, card) {
        if (!record || !card) {
          const defaults = defaultManualScores();
          return `
            <div class="story-card" style="margin-top: 12px;"><strong>No story selected</strong><blockquote>Stage and approve evidence first. Imported CSV rows will appear here one story at a time. The rubric below is still shown so coders know the scoring rules before they begin.</blockquote></div>
            <div class="scorecard-grid">
              ${manualEncodingVariables.map((variable) => renderScoreRule(variable, defaults, {})).join("")}
            </div>
          `;
        }
        const scores = { ...defaultManualScores(), ...(card.scores || {}) };
        const phi = computePhi(scores);
        return `
          <div class="metric-grid" style="margin-top: 12px;">
            <div class="metric"><span class="mini-label">Phi</span><strong>${phi.toFixed(4)}</strong></div>
            <div class="metric"><span class="mini-label">Trust</span><strong>${scores.tau.toFixed(2)}</strong></div>
            <div class="metric"><span class="mini-label">Barrier</span><strong>${scores.B.toFixed(2)}</strong></div>
          </div>
          <div class="scorecard-grid">
            ${manualEncodingVariables.map((variable) => renderScoreRule(variable, scores, card.notes || {})).join("")}
          </div>
          <div class="guide-note" style="margin-top: 12px;">
            <strong>Manual encoding rule</strong>
            <p>Use the narrative text as evidence. Do not score based on what you hope the respondent means. If uncertain, use the middle range and explain uncertainty in the note.</p>
          </div>
        `;
      }

      function renderScoreRule(variable, scores, notes) {
        const value = clamp01(scores[variable.key] ?? variable.defaultValue, variable.defaultValue);
        return `
          <article class="score-rule">
            <header>
              <h4>${escapeHtml(variable.label)}</h4>
              <code>${escapeHtml(variable.key)}</code>
            </header>
            <p>${escapeHtml(variable.meaning)}</p>
            <div class="score-scale">
              <span><b>Low</b><br/>${escapeHtml(variable.low)}</span>
              <span><b>Medium</b><br/>${escapeHtml(variable.mid)}</span>
              <span><b>High</b><br/>${escapeHtml(variable.high)}</span>
            </div>
            <p><b>Evidence example:</b> ${escapeHtml(variable.example)}</p>
            <div class="score-input-row">
              <div class="field"><label for="score-${escapeHtml(variable.key)}">Score</label><input id="score-${escapeHtml(variable.key)}" type="number" min="0" max="1" step="0.01" value="${value.toFixed(2)}" data-score="${escapeHtml(variable.key)}" /></div>
              <div class="field"><label for="note-${escapeHtml(variable.key)}">Justification</label><input id="note-${escapeHtml(variable.key)}" value="${escapeHtml(notes[variable.key] || "")}" placeholder="brief evidence quote or coding reason..." data-score-note="${escapeHtml(variable.key)}" /></div>
            </div>
          </article>
        `;
      }

      function renderEncodingQueue() {
        const records = reviewableRecords();
        if (!records.length) return '<p>No approved records are ready. Pass the SDMX gate and approve evidence first.</p>';
        return `<div class="encoding-queue">${records.map((record, index) => {
          const card = state.manualScorecards[record.narrative_id];
          const manual = card?.status === "manual_reviewed";
          const ai = Boolean(encodedFor("ai", record.narrative_id));
          const hybrid = Boolean(encodedFor("hybrid", record.narrative_id));
          const active = index === Math.min(state.manualIndex, records.length - 1);
          const label = manual ? "manual reviewed" : ai || hybrid ? "LLM pre-coded" : "unencoded";
          return `
            <button class="queue-item ${active ? "active" : ""}" data-select-story="${index}" type="button">
              <strong>${String(index + 1).padStart(2, "0")} ${escapeHtml(record.metadata?.provenance?.question_title || record.narrative_id)}</strong>
              <span>${escapeHtml(label)} | manual ${manual ? "yes" : "no"} | AI ${ai ? "yes" : "no"} | hybrid ${hybrid ? "yes" : "no"}</span>
              <span>${escapeHtml(record.text.slice(0, 130))}${record.text.length > 130 ? "..." : ""}</span>
            </button>
          `;
        }).join("")}</div>`;
      }

      function renderStoryNavigator() {
        const reviewable = reviewableRecords();
        const record = reviewable[Math.min(state.manualIndex, Math.max(0, reviewable.length - 1))];
        if (!record) return '<div class="story-card"><strong>No current story</strong><blockquote>Stage evidence first, then use Encode current story for manual review.</blockquote></div>';
        return `
          <div class="story-card">
            <span class="mini-label">Story ${Math.min(state.manualIndex + 1, reviewable.length)} of ${reviewable.length}${approvedRecords().length ? " approved" : ""}</span>
            <strong>${escapeHtml(record.narrative_id)}</strong>
            <blockquote>${escapeHtml(record.text.slice(0, 280))}${record.text.length > 280 ? "..." : ""}</blockquote>
            <div class="button-row">
              <button class="button" id="prevStory" type="button">Previous story</button>
              <button class="button" id="nextStory" type="button">Next story</button>
            </div>
          </div>
        `;
      }

      function renderEncodingTable() {
        const head = '<div class="row head"><span>ID</span><span>Mode</span><span>Themes</span><span>Trust</span><span>Barrier</span><span>Conf.</span></div>';
        if (!state.encoded.length) {
          return `<div class="table">${head}<div class="row"><span data-label="ID">No encoding yet</span><span data-label="Mode">-</span><span data-label="Themes">-</span><span data-label="Trust">-</span><span data-label="Barrier">-</span><span data-label="Confidence">-</span></div></div>`;
        }
        return `<div class="table">${head}${state.encoded.map((item) => `
          <div class="row">
            <span data-label="ID">${escapeHtml(item.narrative_id)}</span>
            <span data-label="Mode">${escapeHtml(item.encoding_mode)}</span>
            <span data-label="Themes">${escapeHtml((item.themes || ["general"]).join(", "))}</span>
            <span data-label="Trust">${typeof item.trust_score === "number" ? item.trust_score.toFixed(2) : "-"}</span>
            <span data-label="Barrier">${typeof item.adoption_barrier_score === "number" ? item.adoption_barrier_score.toFixed(2) : "-"}</span>
            <span data-label="Confidence">${typeof item.confidence === "number" ? item.confidence.toFixed(2) : "-"}</span>
          </div>
        `).join("")}</div>`;
      }

      function renderEncodingComparison() {
        const modes = Object.keys(state.encodingRuns);
        const record = currentReviewRecord();
        const currentRows = record ? modes.map((mode) => [mode, encodedFor(mode, record.narrative_id)]).filter(([, item]) => item) : [];
        const currentBlock = currentRows.length ? `
          <div class="compare-grid">
            ${currentRows.map(([mode, item]) => `
              <div class="compare-card ${state.encodingMode === mode ? "active" : ""}">
                <h3>${escapeHtml(mode)} current story</h3>
                <p>Trust ${Number(item.trust_score ?? 0).toFixed(2)} / Barrier ${Number(item.adoption_barrier_score ?? 0).toFixed(2)} / Confidence ${Number(item.confidence ?? 0).toFixed(2)}</p>
                <p>Themes: ${escapeHtml((item.themes || ["general"]).join(", "))}</p>
                <p>${escapeHtml(item.model_notes || item.reviewer_notes || "No notes returned.")}</p>
              </div>
            `).join("")}
          </div>
        ` : "";
        if (modes.length < 2) return currentBlock;
        return `
          ${currentBlock}
          <div class="compare-grid">
            ${modes.map((mode) => {
              const rows = state.encodingRuns[mode] || [];
              const trust = avg(rows.map((item) => item.trust_score), 0);
              const barrier = avg(rows.map((item) => item.adoption_barrier_score), 0);
              const conf = avg(rows.map((item) => item.confidence), 0);
              const themes = [...new Set(rows.flatMap((item) => item.themes || []))].slice(0, 5).join(", ") || "general";
              return `<div class="compare-card ${state.encodingMode === mode ? "active" : ""}"><h3>${escapeHtml(mode)} batch average</h3><p>Trust ${trust.toFixed(2)} / Barrier ${barrier.toFixed(2)} / Confidence ${conf.toFixed(2)}</p><p>Themes: ${escapeHtml(themes)}</p></div>`;
            }).join("")}
          </div>
        `;
      }

      function renderCompartmental() {
        const last = state.comp?.trajectory?.at(-1);
        return `
          <section class="stage-card">
            <p class="eyebrow">Stage 4</p>
            <h2>Compartmental model</h2>
            <p class="copy">Run the population model. It is the high-level S/M/T/I/R view of adoption, misinformation, truth alignment, inoculation, and durable resistance to misinformation.</p>
            <div class="grid-2">
              <div class="panel">
                <h3>S/M/T/I/R meaning</h3>
                <div class="equation"><span>dS/dt</span> = - beta_m S M - beta_t S T - iota S<br/><span>dT/dt</span> = beta_t S T + rho M - mu T<br/><span>dR/dt</span> = gamma I + eta T<br/><b>Phi</b> changes beta_t, rho, and iota through narrative strength.</div>
                <div class="guide-note"><strong>Guiding note</strong><p>Read this as the executable NDIM compartment model. The backend now carries S, M, T, I, and R compartments plus an adoption signal and uncertainty band. If a future endpoint falls back to a prototype curve, the model type label will say so clearly.</p></div>
                <div class="check-list">
                  ${["S Susceptible households", "M Misinformed households", "T Truth-aligned households", "I Inoculated households", "R Resistant or durable adoption belief"].map((item) => `<div class="check pass"><i>--</i><div><strong>${item}</strong><span>Tracked by the scientific model layer.</span></div></div>`).join("")}
                </div>
                <div class="button-row"><button class="button primary" id="runCompartmental" type="button">Run compartmental model</button></div>
              </div>
              <div class="panel">
                <h3>Population output</h3>
                <div class="metric-grid">
                  <div class="metric"><span class="mini-label">Final adoption</span><strong>${fmtPct(last?.adoption)}</strong></div>
                  <div class="metric"><span class="mini-label">Model type</span><strong>${escapeHtml(state.comp?.assumptions?.model_type || "Full NDIM compartment model")}</strong></div>
                  <div class="metric"><span class="mini-label">Uncertainty</span><strong>${escapeHtml(finalUncertaintySummary())}</strong></div>
                </div>
                <div class="template-table" style="margin-top: 12px;">
                  <div class="template-row head"><span>Compartment</span><span>Final share</span><span>Interpretation</span></div>
                  <div class="template-row"><span data-label="Compartment">S susceptible</span><span data-label="Final share">${fmtPct(last?.S)}</span><span data-label="Interpretation">still reachable or undecided</span></div>
                  <div class="template-row"><span data-label="Compartment">M misinformed</span><span data-label="Final share">${fmtPct(last?.M)}</span><span data-label="Interpretation">barrier or rumour pressure</span></div>
                  <div class="template-row"><span data-label="Compartment">T truth-aligned</span><span data-label="Final share">${fmtPct(last?.T)}</span><span data-label="Interpretation">trust-aligned clean-cooking signal</span></div>
                  <div class="template-row"><span data-label="Compartment">I inoculated</span><span data-label="Final share">${fmtPct(last?.I)}</span><span data-label="Interpretation">resistant to misinformation after correction</span></div>
                  <div class="template-row"><span data-label="Compartment">R resistant</span><span data-label="Final share">${fmtPct(last?.R)}</span><span data-label="Interpretation">durably aligned adoption belief</span></div>
                </div>
                <div class="bars" style="margin-top: 14px;">${renderTrajectoryBars(state.comp?.trajectory)}</div>
                ${renderLinePlot("Population adoption trajectory", state.comp?.trajectory, "adoption", "var(--blue)", "day")}
                ${renderUncertaintyLinePlot("Adoption uncertainty band", state.comp?.trajectory)}
                ${renderResultNote("compartmental")}
              </div>
            </div>
          </section>
        `;
      }

      function renderAgents() {
        const last = state.agents?.trajectory?.at(-1);
        return `
          <section class="stage-card">
            <p class="eyebrow">Stage 5</p>
            <h2>Agent-based model</h2>
            <p class="copy">Run the household-level model. It checks how peer effects, trust, and media exposure may differ from the aggregate ODE curve.</p>
            <div class="grid-2">
              <div class="panel">
                <h3>Agent configuration</h3>
                <div class="equation"><span>P(adopt_i)</span> = sigmoid(trust_i + peer_effect * sum_j A_ij adopt_j + media_i - barrier_i)<br/><span>degree_i</span> = sum_j A_ij<br/><span>trust_next</span> = trust + outreach + posterior_update</div>
                <div class="guide-note"><strong>Guiding note</strong><p>The agent model asks whether local peer dynamics tell a different story from the population curve. If ABM adoption is lower than ODE adoption, district-level friction or network clustering may be hiding in the aggregate model.</p></div>
                <div class="field-grid">
                  <div class="field"><label for="peerEffect">Peer effect</label><input id="peerEffect" type="number" min="0" max="1" step="0.01" value="0.08" /></div>
                  <div class="field"><label for="mediaEffect">Media effect</label><input id="mediaEffect" type="number" min="0" max="1" step="0.01" value="0.05" /></div>
                </div>
                <div class="button-row"><button class="button primary" id="runAgents" type="button">Run agent model</button></div>
              </div>
              <div class="panel">
                <h3>Household dynamics output</h3>
                <div class="metric-grid">
                  <div class="metric"><span class="mini-label">Final adoption</span><strong>${fmtPct(last?.adoption)}</strong></div>
                  <div class="metric"><span class="mini-label">Model mode</span><strong>ABM</strong></div>
                  <div class="metric"><span class="mini-label">Signal</span><strong>${state.agents ? compareModels() : "-"}</strong></div>
                </div>
                <div class="bars" style="margin-top: 14px;">${renderTrajectoryBars(state.agents?.trajectory)}</div>
                ${renderLinePlot("Household adoption trajectory", state.agents?.trajectory, "adoption", "var(--green)", "day")}
                ${renderDualLinePlot("ODE versus agent model", state.comp?.trajectory, state.agents?.trajectory, "adoption", ["ODE population", "Agent households"], ["var(--blue)", "var(--green)"])}
                ${renderResultNote("agents")}
              </div>
            </div>
          </section>
        `;
      }

      function renderDigital() {
        const last = state.digital?.trajectory?.at(-1);
        return `
          <section class="stage-card">
            <p class="eyebrow">Stage 6</p>
            <h2>Digital twin feedback loop</h2>
            <p class="copy">This is where field feedback informs the next model run. Observed adoption, trust shifts, and barrier shifts refine model parameters.</p>
            <div class="grid-2">
              <div class="panel">
                <h3>Feedback input</h3>
                <div class="field-grid">
                  <div class="field"><label for="observedAdoption">Observed adoption</label><input id="observedAdoption" type="number" min="0" max="1" step="0.01" value="${state.feedback.observedAdoption}" /></div>
                  <div class="field"><label for="trustDelta">Trust shift</label><input id="trustDelta" type="number" min="-1" max="1" step="0.01" value="${state.feedback.trustDelta}" /></div>
                  <div class="field"><label for="barrierDelta">Barrier shift</label><input id="barrierDelta" type="number" min="-1" max="1" step="0.01" value="${state.feedback.barrierDelta}" /></div>
                  <div class="field"><label for="feedbackNote">Feedback note</label><input id="feedbackNote" value="${escapeHtml(state.feedback.note)}" placeholder="district feedback, survey note..." /></div>
                </div>
                <div class="equation" style="margin-top: 12px;"><span>theta_next</span> = theta_model + lambda(field_observed - model_predicted)<br/><span>trust_next</span> = trust + trust_shift<br/><span>barrier_next</span> = barrier + barrier_shift</div>
                <div class="guide-note"><strong>Guiding note</strong><p>This stage closes the scientific loop. A digital twin is useful only when field observations can correct the model. Here the observed adoption level becomes a new starting condition and trust/barrier shifts alter the next model parameters.</p></div>
                ${renderDigitalFeedbackChain()}
                <div class="button-row"><button class="button primary" id="runDigital" type="button">Apply feedback and rerun twin</button></div>
              </div>
              <div class="panel">
                <h3>Digital twin output</h3>
                <div class="metric-grid">
                  <div class="metric"><span class="mini-label">Refined adoption</span><strong>${fmtPct(last?.adoption)}</strong></div>
                  <div class="metric"><span class="mini-label">Observed adoption</span><strong>${fmtPct(state.feedback.observedAdoption)}</strong></div>
                  <div class="metric"><span class="mini-label">Feedback status</span><strong>${state.digital ? "applied" : "-"}</strong></div>
                </div>
                <div class="bars" style="margin-top: 14px;">${renderTrajectoryBars(state.digital?.trajectory)}</div>
                ${renderDualLinePlot("Baseline versus feedback-adjusted twin", state.comp?.trajectory, state.digital?.trajectory, "adoption", ["baseline ODE", "feedback twin"], ["var(--blue)", "var(--amber)"])}
                ${renderResultNote("digital")}
              </div>
            </div>
          </section>
        `;
      }

      function renderBayes() {
        const b = state.bayes;
        return `
          <section class="stage-card">
            <p class="eyebrow">Stage 7</p>
            <h2>Bayesian prior to posterior update</h2>
            <p class="copy">Priors hold what the model believed before feedback. Posterior values update those beliefs after observed adoption and trust feedback.</p>
            <div class="grid-2">
              <div class="panel">
                <h3>Prior settings</h3>
                <div class="field-grid">
                  <div class="field"><label for="trustA">Trust alpha</label><input id="trustA" type="number" min="1" step="1" value="${state.priors.trustA}" /></div>
                  <div class="field"><label for="trustB">Trust beta</label><input id="trustB" type="number" min="1" step="1" value="${state.priors.trustB}" /></div>
                  <div class="field"><label for="barrierA">Barrier alpha</label><input id="barrierA" type="number" min="1" step="1" value="${state.priors.barrierA}" /></div>
                  <div class="field"><label for="barrierB">Barrier beta</label><input id="barrierB" type="number" min="1" step="1" value="${state.priors.barrierB}" /></div>
                </div>
                <div class="equation" style="margin-top: 12px;"><span>prior</span> = Beta(alpha, beta)<br/><span>posterior</span> = Beta(alpha + successes, beta + failures)<br/><span>E[p]</span> = alpha / (alpha + beta)</div>
                <div class="guide-note"><strong>Guiding note</strong><p>The prior is your starting belief. The posterior is the same belief after evidence is counted. Higher trust posterior raises adoption pressure; higher barrier posterior dampens adoption pressure and makes aggressive policies riskier.</p></div>
                <div class="button-row"><button class="button primary" id="runBayes" type="button">Update posterior</button></div>
              </div>
              <div class="panel">
                <h3>Posterior output</h3>
                <div class="metric-grid">
                  <div class="metric"><span class="mini-label">Trust posterior</span><strong>${fmtPct(b?.trustMean)}</strong></div>
                  <div class="metric"><span class="mini-label">Barrier posterior</span><strong>${fmtPct(b?.barrierMean)}</strong></div>
                  <div class="metric"><span class="mini-label">Evidence weight</span><strong>${b?.trials || "-"}</strong></div>
                  <div class="metric"><span class="mini-label">Backend</span><strong>${b ? (b.fallback ? "fallback" : "advanced") : "-"}</strong></div>
                </div>
                <p class="copy" style="margin-top: 12px;">Posterior values feed the RL optimizer and final policy run as refined trust and barrier parameters. ${escapeHtml(b?.backendWarning || analyticsSummary())}</p>
                <div class="template-table" style="margin-top: 12px;">
                  <div class="template-row head"><span>Posterior item</span><span>Value</span><span>Use</span></div>
                  <div class="template-row"><span data-label="Posterior item">Adoption interval</span><span data-label="Value">${escapeHtml(finalUncertaintySummary())}</span><span data-label="Use">policy confidence and sensitivity</span></div>
                  <div class="template-row"><span data-label="Posterior item">Beta diffusion</span><span data-label="Value">${numberLabel(b?.ndimParameters?.beta?.mean)}</span><span data-label="Use">truth/adoption diffusion pressure</span></div>
                  <div class="template-row"><span data-label="Posterior item">Gamma support</span><span data-label="Value">${numberLabel(b?.ndimParameters?.gamma?.mean)}</span><span data-label="Use">support or intervention lift</span></div>
                  <div class="template-row"><span data-label="Posterior item">Delta decay</span><span data-label="Value">${numberLabel(b?.ndimParameters?.delta?.mean)}</span><span data-label="Use">barrier or decay pressure</span></div>
                </div>
                ${renderPosteriorPlot("Trust prior and posterior", state.priors.trustA, state.priors.trustB, b?.trustAlpha, b?.trustBeta, "var(--blue)")}
                ${renderPosteriorPlot("Barrier prior and posterior", state.priors.barrierA, state.priors.barrierB, b?.barrierAlpha, b?.barrierBeta, "var(--red)")}
                ${renderResultNote("bayes")}
              </div>
            </div>
          </section>
        `;
      }

      function renderRL() {
        const rl = state.rl;
        return `
          <section class="stage-card">
            <p class="eyebrow">Stage 8</p>
            <h2>RL optimizer loop</h2>
            <p class="copy">The optimizer tests intervention packages and learns which action maximizes adoption while penalizing cost and barrier risk.</p>
            <div class="grid-2">
              <div class="panel">
                <h3>Q-learning setup</h3>
                <div class="field-grid">
                  <div class="field"><label for="episodes">Episodes</label><input id="episodes" type="number" min="20" max="500" step="10" value="120" /></div>
                  <div class="field"><label for="learningRate">Learning rate</label><input id="learningRate" type="number" min="0.01" max="1" step="0.01" value="0.18" /></div>
                  <div class="field"><label for="discount">Discount</label><input id="discount" type="number" min="0.1" max="0.99" step="0.01" value="0.88" /></div>
                  <div class="field"><label for="epsilon">Exploration</label><input id="epsilon" type="number" min="0" max="1" step="0.01" value="0.16" /></div>
                </div>
                <div class="equation" style="margin-top: 12px;"><span>Q(s,a)</span> <- Q(s,a) + alpha [reward + gamma max Q(s',a') - Q(s,a)]<br/><span>reward</span> = adoption_gain - cost_penalty - barrier_penalty</div>
                <div class="guide-note"><strong>Guiding note</strong><p>RL is not replacing policy judgment. It is stress-testing intervention packages. If the reward curve stabilizes and one action dominates the Q table, the policy option is more robust; if rewards jump around, the model is still uncertain.</p></div>
                <div class="button-row"><button class="button primary" id="runRL" type="button">Run RL loop</button></div>
              </div>
              <div class="panel">
                <h3>Optimizer output</h3>
                <div class="metric-grid">
                  <div class="metric"><span class="mini-label">Best action</span><strong>${rl?.bestAction || "-"}</strong></div>
                  <div class="metric"><span class="mini-label">Best reward</span><strong>${typeof rl?.bestReward === "number" ? rl.bestReward.toFixed(3) : "-"}</strong></div>
                  <div class="metric"><span class="mini-label">Episodes</span><strong>${rl?.episodes || "-"}</strong></div>
                  <div class="metric"><span class="mini-label">Optimizer</span><strong>${rl ? (rl.fallback ? "fallback" : "advanced") : "-"}</strong></div>
                </div>
                <p class="copy" style="margin-top: 12px;">${escapeHtml(rl?.note || analyticsSummary())}</p>
                <div class="bars" style="margin-top: 14px;">${renderRLBars()}</div>
                ${renderLinePlot("Reward learning curve", rl?.history, "reward", "var(--violet)", "episode")}
                ${renderResultNote("rl")}
              </div>
            </div>
          </section>
        `;
      }

      function renderRegionalAnalysis() {
        const rows = state.regional?.rows || computeRegionalRows();
        const strongest = rows.slice().sort((a, b) => b.trust - a.trust)[0];
        const risk = rows.slice().sort((a, b) => b.barrier - a.barrier)[0];
        return `
          <section class="stage-card">
            <p class="eyebrow">Stage 9</p>
            <h2>Regional analysis</h2>
            <p class="copy">Analyse places in isolation or as a group before crafting interventions. This is where a national story becomes a district-sensitive policy plan.</p>
            <div class="grid-2">
              <div class="panel">
                <h3>Analysis setup</h3>
                <div class="field-grid">
                  <div class="field"><label for="regionalMode">Analysis mode</label><select id="regionalMode"><option value="isolated">Isolate each region</option><option value="grouped">Group all regions</option></select></div>
                  <div class="field"><label for="regionalTarget">Target lens</label><select id="regionalTarget"><option value="barrier">Barrier reduction</option><option value="trust">Trust building</option><option value="diffusion">Peer diffusion</option></select></div>
                </div>
                <div class="equation" style="margin-top: 12px;"><span>regional_score_r</span> = mean(Phi_i, trust_i, barrier_i | location=r)<br/><span>intervention_r</span> = argmax expected adoption gain subject to feasibility and risk</div>
                <div class="guide-note"><strong>Guiding note</strong><p>Use isolated mode when one district needs its own intervention. Use grouped mode when you want a national or cross-district campaign shaped by all evidence.</p></div>
                <div class="button-row"><button class="button primary" id="runRegional" type="button">Run regional analysis</button></div>
              </div>
              <div class="panel">
                <h3>Regional signal</h3>
                <div class="metric-grid">
                  <div class="metric"><span class="mini-label">Regions</span><strong>${rows.length || "-"}</strong></div>
                  <div class="metric"><span class="mini-label">Strongest trust</span><strong>${strongest ? strongest.region.split(" / ").slice(-1)[0] : "-"}</strong></div>
                  <div class="metric"><span class="mini-label">Highest barrier</span><strong>${risk ? risk.region.split(" / ").slice(-1)[0] : "-"}</strong></div>
                </div>
                ${renderRegionalRows(rows)}
              </div>
            </div>
          </section>
        `;
      }

      function renderKnowledgeGraph() {
        const graph = state.graph || buildKnowledgeGraph();
        return `
          <section class="stage-card">
            <p class="eyebrow">Stage 10</p>
            <h2>Knowledge graph</h2>
            <p class="copy">Study stories from the same location by connecting places, narratives, themes, trust, barriers, and candidate interventions.</p>
            <div class="grid-2">
              <div class="panel">
                <h3>Graph theory lens</h3>
                <div class="equation"><span>G</span> = (V, E)<br/><span>degree(v)</span> = sum_j A_vj<br/><span>theme_centrality</span> = degree(theme) / max_degree</div>
                <div class="guide-note"><strong>Guiding note</strong><p>High-degree themes are repeated across many stories or locations. They are not automatically true, but they are useful places to investigate because they organize local meaning.</p></div>
                <div class="button-row"><button class="button primary" id="buildGraph" type="button">Build knowledge graph</button></div>
                ${renderGraphStoryGroups()}
              </div>
              <div class="panel">
                <h3>Story graph</h3>
                ${renderKnowledgeGraphSvg(graph)}
                <div class="pill-row">
                  <span class="pill">locations ${graph.nodes.filter((n) => n.kind === "location").length}</span>
                  <span class="pill">themes ${graph.nodes.filter((n) => n.kind === "theme").length}</span>
                  <span class="pill">edges ${graph.edges.length}</span>
                </div>
              </div>
            </div>
          </section>
        `;
      }

      function renderInoculationLab() {
        const items = state.inoculation?.items || [];
        return `
          <section class="stage-card">
            <p class="eyebrow">Stage 11</p>
            <h2>Inoculation lab</h2>
            <p class="copy">Show inoculation theory at work. The selected LLM provider is used as the intended generation path; if no model key is configured, the browser produces transparent deterministic drafts from the encoded evidence.</p>
            <div class="grid-2">
              <div class="panel">
                <h3>Inoculation recipe</h3>
                <div class="equation"><span>inoculation_message</span> = warning + weakened misinformation + refutation + trusted messenger + efficacy cue<br/><span>resistance_gain</span> = threat_awareness * refutation_quality * source_trust</div>
                <div class="guide-note"><strong>Guiding note</strong><p>Good inoculation does not simply deny a false claim. It gives people a small preview of the misleading argument, explains the manipulation, then offers a trusted and practical alternative.</p></div>
                <div class="field-grid" style="margin-top: 12px;">
                  <div class="field"><label for="inoculationAudience">Audience</label><select id="inoculationAudience"><option value="households">Households</option><option value="community_leaders">Community leaders</option><option value="health_workers">Health workers</option><option value="policy_makers">Policy makers</option></select></div>
                  <div class="field"><label for="inoculationTone">Tone</label><select id="inoculationTone"><option value="clear">Clear and practical</option><option value="warm">Warm and local</option><option value="technical">Technical evidence</option></select></div>
                </div>
                <div class="button-row"><button class="button primary" id="runInoculation" type="button">Generate inoculation narratives</button></div>
              </div>
              <div class="panel">
                <h3>Generated counter-narratives</h3>
                ${items.length ? items.map(renderCounterCard).join("") : '<p>Run the lab to generate pre-bunking, refutation, and counter-feed drafts from the encoded narratives.</p>'}
              </div>
            </div>
            <div style="margin-top: 14px;">${renderVaccineImpact()}</div>
          </section>
        `;
      }

      function renderDigitalFeedbackChain() {
        const rows = [
          ["Accepted evidence", approvedRecords().length ? `${approvedRecords().length} committed record(s)` : "waiting"],
          ["Encoded narratives", state.encoded.length ? `${state.encoded.length} encoded story input(s)` : "waiting"],
          ["Compartmental ODE", state.comp ? "baseline population curve ready" : "waiting"],
          ["Agent-based model", state.agents ? "household curve ready" : "waiting"],
          ["Bayesian posterior", state.bayes ? `trust ${fmtPct(state.bayes.trustMean)}, barrier ${fmtPct(state.bayes.barrierMean)}` : "waiting"],
          ["RL optimizer", state.rl ? state.rl.bestAction : "waiting"],
          ["Inoculation lab", state.inoculationApplied ? `narrative vaccine applied (${fmtPct(state.inoculation?.interventionStrength)})` : state.inoculation ? "vaccine generated, not applied" : "waiting"]
        ];
        return `
          <div class="template-table" style="margin-top: 12px;">
            <div class="template-row head"><span>Feedback source</span><span>Digital twin input</span><span>Status</span></div>
            ${rows.map(([source, value]) => `<div class="template-row"><span data-label="Feedback source">${escapeHtml(source)}</span><span data-label="Digital twin input">${escapeHtml(value)}</span><span data-label="Status">${value === "waiting" ? "pending" : "active"}</span></div>`).join("")}
          </div>
        `;
      }

      function renderPolicy() {
        const summary = state.policy?.summary || {};
        const brief = policyDecisionBrief();
        return `
          <section class="stage-card">
            <p class="eyebrow">Stage 12</p>
            <h2>Policy output and audit</h2>
            <p class="copy">This stage creates a reviewable decision output rather than a black-box answer. It uses approved evidence, encoded model inputs, digital twin feedback, posterior/RL learning, regional analysis, graph insights, inoculation drafts, and human review.</p>
            <div class="button-row" style="margin-top: 0; margin-bottom: 14px;">
              <button class="button green" id="runPolicy" type="button">Run full policy pipeline</button>
              <button class="button primary" id="downloadPolicyHtml" type="button">Download HTML brief</button>
              <button class="button" id="printPolicyPdf" type="button">Open PDF view</button>
              <button class="button" id="copyPolicy" type="button">Copy JSON</button>
              <button class="button" id="downloadPolicyJson" type="button">Download JSON</button>
              <button class="button" id="copyPolicyBrief" type="button">Copy brief</button>
            </div>
            <div class="metric-grid">
              <div class="metric"><span class="mini-label">Final adoption</span><strong>${fmtPct(summary.final_adoption)}</strong></div>
              <div class="metric"><span class="mini-label">Average trust</span><strong>${fmtPct(summary.average_trust)}</strong></div>
              <div class="metric"><span class="mini-label">Average barrier</span><strong>${fmtPct(summary.average_barrier)}</strong></div>
              <div class="metric"><span class="mini-label">Evidence grade</span><strong>${escapeHtml(brief.evidence_grade)}</strong></div>
              <div class="metric"><span class="mini-label">Confidence</span><strong>${escapeHtml(brief.confidence_level)}</strong></div>
            </div>
            <div class="grid-2" style="margin-top: 14px;">
              <div class="panel">
                <h3>Decision brief readiness</h3>
                <div class="guide-note ${brief.evidence_grade === "D" ? "danger" : ""}"><strong>${brief.evidence_grade === "D" ? "Policy warning" : "Policy readiness"}</strong><p>${escapeHtml(brief.policy_use_warning)}</p></div>
                <div class="template-table" style="margin-top: 12px;">
                  <div class="template-row head"><span>Review item</span><span>Status</span><span>Meaning</span></div>
                  <div class="template-row"><span data-label="Review item">Evidence grade</span><span data-label="Status">${escapeHtml(brief.evidence_grade)}</span><span data-label="Meaning">strength of evidence chain</span></div>
                  <div class="template-row"><span data-label="Review item">Model used</span><span data-label="Status">${escapeHtml(brief.model_type_used)}</span><span data-label="Meaning">backend equation family</span></div>
                  <div class="template-row"><span data-label="Review item">Validation</span><span data-label="Status">${escapeHtml(brief.validation_status)}</span><span data-label="Meaning">${escapeHtml(brief.validation_summary)}</span></div>
                  <div class="template-row"><span data-label="Review item">Uncertainty</span><span data-label="Status">${escapeHtml(brief.uncertainty_summary)}</span><span data-label="Meaning">scenario confidence band</span></div>
                </div>
              </div>
              <div class="panel">
                <h3>Recommendation draft</h3>
                <p>${policyNarrative()}</p>
                <div class="template-table" style="margin-top: 12px;">
                  <div class="template-row head"><span>Output section</span><span>Format</span><span>Source</span></div>
                  <div class="template-row"><span data-label="Output section">Policy brief</span><span data-label="Format">HTML file + PDF-ready print view + Markdown copy</span><span data-label="Source">recommendation, synthesis, human review</span></div>
                  <div class="template-row"><span data-label="Output section">Audit payload</span><span data-label="Format">JSON schema ndim-policy-output-v1 for audit only</span><span data-label="Source">evidence ledger, hashes, models, posterior, RL</span></div>
                  <div class="template-row"><span data-label="Output section">Evidence ledger</span><span data-label="Format">JSON table inside payload</span><span data-label="Source">approved narrative records</span></div>
                </div>
              </div>
              <div class="json">${escapeHtml(JSON.stringify(policyJson(), null, 2))}</div>
            </div>
          </section>
        `;
      }

      function renderTrajectoryBars(trajectory) {
        if (!trajectory || !trajectory.length) return '<p>Run this model to show trajectory samples.</p>';
        const picks = [0, Math.floor(trajectory.length / 3), Math.floor(trajectory.length * 2 / 3), trajectory.length - 1]
          .map((index) => trajectory[index]);
        return picks.map((point) => `
          <div class="bar-row">
            <span>day ${Math.round(point.day)}</span>
            <div class="bar-track"><div class="bar-fill" style="width:${Math.max(2, point.adoption * 100)}%"></div></div>
            <span>${fmtPct(point.adoption)}</span>
          </div>
        `).join("");
      }

      function plotValueLabel(value, key) {
        if (typeof value !== "number" || Number.isNaN(value)) return "-";
        return key === "adoption" ? fmtPct(value) : value.toFixed(2);
      }

      function polylinePoints(series, yKey, xKey, minY, maxY, maxX, w = 640, h = 220, pad = 30) {
        const spread = Math.max(0.0001, maxY - minY);
        return series.map((point, index) => {
          const xValue = Number(point[xKey] ?? index);
          const yValue = Number(point[yKey]);
          const x = pad + (xValue / Math.max(1, maxX)) * (w - pad * 2);
          const y = h - pad - ((yValue - minY) / spread) * (h - pad * 2);
          return `${x.toFixed(1)},${y.toFixed(1)}`;
        }).join(" ");
      }

      function renderPlotFrame(title, body, legend = "", topLabel = "", bottomLabel = "") {
        return `
          <div class="plot-card">
            <div class="plot-title">${escapeHtml(title)}</div>
            <svg viewBox="0 0 640 220" role="img" aria-label="${escapeHtml(title)}">
              <line class="plot-grid-line" x1="30" x2="610" y1="30" y2="30"></line>
              <line class="plot-grid-line" x1="30" x2="610" y1="110" y2="110"></line>
              <line class="plot-grid-line" x1="30" x2="610" y1="190" y2="190"></line>
              <line class="plot-grid-line" x1="30" x2="30" y1="30" y2="190"></line>
              <text class="plot-axis-label" x="36" y="25">${escapeHtml(topLabel)}</text>
              <text class="plot-axis-label" x="36" y="207">${escapeHtml(bottomLabel)}</text>
              ${body}
            </svg>
            ${legend}
          </div>
        `;
      }

      function renderLinePlot(title, points, yKey = "adoption", color = "var(--blue)", xKey = "day") {
        const series = (points || []).filter((point) => typeof point?.[yKey] === "number");
        if (series.length < 2) return `<div class="plot-card"><div class="plot-title">${escapeHtml(title)}</div><p>Run this stage to draw the scientific curve.</p></div>`;
        const yValues = series.map((point) => Number(point[yKey]));
        const minY = Math.min(0, ...yValues);
        const maxY = Math.max(0.01, ...yValues);
        const maxX = Math.max(...series.map((point, index) => Number(point[xKey] ?? index)), 1);
        const pointsString = polylinePoints(series, yKey, xKey, minY, maxY, maxX);
        const body = `<polyline points="${pointsString}" fill="none" stroke="${color}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"></polyline>`;
        const legend = `<div class="plot-legend"><span><i class="legend-swatch" style="background:${color}"></i>${escapeHtml(yKey)} over ${escapeHtml(xKey)}</span></div>`;
        return renderPlotFrame(title, body, legend, plotValueLabel(maxY, yKey), plotValueLabel(minY, yKey));
      }

      function renderUncertaintyLinePlot(title, points) {
        const series = (points || []).filter((point) => typeof point?.adoption === "number" && typeof point?.adoption_lower === "number" && typeof point?.adoption_upper === "number");
        if (series.length < 2) return `<div class="plot-card"><div class="plot-title">${escapeHtml(title)}</div><p>Run a model with uncertainty output to draw lower and upper bands.</p></div>`;
        const yValues = series.flatMap((point) => [point.adoption_lower, point.adoption, point.adoption_upper]).map(Number);
        const minY = Math.min(0, ...yValues);
        const maxY = Math.max(0.01, ...yValues);
        const maxX = Math.max(...series.map((point, index) => Number(point.day ?? index)), 1);
        const lower = polylinePoints(series, "adoption_lower", "day", minY, maxY, maxX);
        const mean = polylinePoints(series, "adoption", "day", minY, maxY, maxX);
        const upper = polylinePoints(series, "adoption_upper", "day", minY, maxY, maxX);
        const body = `
          <polyline points="${lower}" fill="none" stroke="var(--soft)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="7 7"></polyline>
          <polyline points="${mean}" fill="none" stroke="var(--blue)" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"></polyline>
          <polyline points="${upper}" fill="none" stroke="var(--soft)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="7 7"></polyline>
        `;
        const legend = '<div class="plot-legend"><span><i class="legend-swatch" style="background:var(--blue)"></i>mean adoption</span><span><i class="legend-swatch" style="background:var(--soft)"></i>lower / upper interval</span></div>';
        return renderPlotFrame(title, body, legend, plotValueLabel(maxY, "adoption"), plotValueLabel(minY, "adoption"));
      }

      function renderDualLinePlot(title, first, second, yKey = "adoption", labels = ["first", "second"], colors = ["var(--blue)", "var(--green)"]) {
        const a = (first || []).filter((point) => typeof point?.[yKey] === "number");
        const b = (second || []).filter((point) => typeof point?.[yKey] === "number");
        if (a.length < 2 || b.length < 2) return `<div class="plot-card"><div class="plot-title">${escapeHtml(title)}</div><p>Run the needed upstream stages to compare curves.</p></div>`;
        const yValues = a.concat(b).map((point) => Number(point[yKey]));
        const minY = Math.min(0, ...yValues);
        const maxY = Math.max(0.01, ...yValues);
        const maxX = Math.max(...a.concat(b).map((point, index) => Number(point.day ?? index)), 1);
        const lineA = polylinePoints(a, yKey, "day", minY, maxY, maxX);
        const lineB = polylinePoints(b, yKey, "day", minY, maxY, maxX);
        const body = `
          <polyline points="${lineA}" fill="none" stroke="${colors[0]}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"></polyline>
          <polyline points="${lineB}" fill="none" stroke="${colors[1]}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="8 8"></polyline>
        `;
        const legend = `<div class="plot-legend"><span><i class="legend-swatch" style="background:${colors[0]}"></i>${escapeHtml(labels[0])}</span><span><i class="legend-swatch" style="background:${colors[1]}"></i>${escapeHtml(labels[1])}</span></div>`;
        return renderPlotFrame(title, body, legend, plotValueLabel(maxY, yKey), plotValueLabel(minY, yKey));
      }

      function renderTripleLinePlot(title, first, second, third, yKey = "adoption", labels = ["before", "during", "after"], colors = ["var(--blue)", "var(--amber)", "var(--green)"]) {
        const series = [first, second, third].map((items) => (items || []).filter((point) => typeof point?.[yKey] === "number"));
        if (series.some((items) => items.length < 2)) return `<div class="plot-card"><div class="plot-title">${escapeHtml(title)}</div><p>Run the baseline model and apply the narrative vaccine to draw before, during, and after curves.</p></div>`;
        const all = series.flat();
        const yValues = all.map((point) => Number(point[yKey]));
        const minY = Math.min(0, ...yValues);
        const maxY = Math.max(0.01, ...yValues);
        const maxX = Math.max(...all.map((point, index) => Number(point.day ?? index)), 1);
        const body = series.map((items, index) => `
          <polyline points="${polylinePoints(items, yKey, "day", minY, maxY, maxX)}" fill="none" stroke="${colors[index]}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" ${index === 1 ? 'stroke-dasharray="8 8"' : ""}></polyline>
        `).join("");
        const legend = `<div class="plot-legend">${labels.map((label, index) => `<span><i class="legend-swatch" style="background:${colors[index]}"></i>${escapeHtml(label)}</span>`).join("")}</div>`;
        return renderPlotFrame(title, body, legend, plotValueLabel(maxY, yKey), plotValueLabel(minY, yKey));
      }

      function betaSamples(alpha, beta) {
        return Array.from({ length: 99 }, (_, index) => {
          const x = (index + 1) / 100;
          return { x, y: Math.pow(x, Math.max(0, alpha - 1)) * Math.pow(1 - x, Math.max(0, beta - 1)) };
        });
      }

      function betaPath(samples, maxY) {
        const w = 640;
        const h = 220;
        const pad = 30;
        return samples.map((point) => {
          const x = pad + point.x * (w - pad * 2);
          const y = h - pad - (point.y / Math.max(0.0001, maxY)) * (h - pad * 2);
          return `${x.toFixed(1)},${y.toFixed(1)}`;
        }).join(" ");
      }

      function renderPosteriorPlot(title, priorA, priorB, postA, postB, color = "var(--blue)") {
        if (typeof postA !== "number" || typeof postB !== "number") return `<div class="plot-card"><div class="plot-title">${escapeHtml(title)}</div><p>Run the Bayesian update to draw prior and posterior distributions.</p></div>`;
        const prior = betaSamples(priorA, priorB);
        const posterior = betaSamples(postA, postB);
        const maxY = Math.max(...prior.concat(posterior).map((point) => point.y), 0.0001);
        const body = `
          <polyline points="${betaPath(prior, maxY)}" fill="none" stroke="var(--soft)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="7 7"></polyline>
          <polyline points="${betaPath(posterior, maxY)}" fill="none" stroke="${color}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"></polyline>
        `;
        const legend = `<div class="plot-legend"><span><i class="legend-swatch" style="background:var(--soft)"></i>prior Beta(${priorA}, ${priorB})</span><span><i class="legend-swatch" style="background:${color}"></i>posterior Beta(${postA}, ${postB})</span></div>`;
        return renderPlotFrame(title, body, legend, "density", "0 to 1 probability");
      }

      function encodedById() {
        return Object.fromEntries((state.encoded || []).map((item) => [item.narrative_id, item]));
      }

      function computeRegionalRows() {
        const byId = encodedById();
        const groups = new Map();
        state.records.forEach((record) => {
          const region = record.metadata?.admin_unit || record.metadata?.country || "Unassigned location";
          const encoded = byId[record.narrative_id] || {};
          if (!groups.has(region)) groups.set(region, { region, count: 0, trust: [], barrier: [], confidence: [], themes: [], stories: [] });
          const row = groups.get(region);
          row.count += 1;
          row.trust.push(encoded.trust_score);
          row.barrier.push(encoded.adoption_barrier_score);
          row.confidence.push(encoded.confidence);
          row.themes.push(...(encoded.themes || ["general"]));
          row.stories.push(record.text);
        });
        return Array.from(groups.values()).map((row) => ({
          ...row,
          trust: avg(row.trust, 0.6),
          barrier: avg(row.barrier, 0.35),
          confidence: avg(row.confidence, 0.5),
          themes: topItems(row.themes, 4)
        }));
      }

      function topItems(items, limit = 5) {
        const counts = {};
        items.filter(Boolean).forEach((item) => { counts[item] = (counts[item] || 0) + 1; });
        return Object.entries(counts).sort((a, b) => b[1] - a[1]).slice(0, limit).map(([name]) => name);
      }

      function recommendIntervention(row, target = "barrier") {
        if (!row) return "Collect enough encoded evidence before choosing an intervention.";
        if (target === "trust" || row.trust < 0.52) return "Use trusted messengers: health workers, local leaders, and peer households should lead correction and demonstration.";
        if (target === "diffusion" || row.trust > 0.62 && row.barrier < 0.45) return "Use peer diffusion: demonstrations, testimonials, and visible early adopters can spread the adoption story.";
        if (row.barrier > 0.48) return "Reduce friction first: pair narrative correction with practical cost, fuel, or access support.";
        return "Use a balanced intervention: light correction, peer proof, and field follow-up.";
      }

      function renderRegionalRows(rows) {
        if (!rows.length) return '<p>Run encoding first so regional evidence can be grouped and compared.</p>';
        return `<div class="insight-list">${rows.map((row) => `
          <div class="insight">
            <strong>${escapeHtml(row.region)} (${row.count} stories)</strong>
            <p>Trust ${row.trust.toFixed(2)}, barrier ${row.barrier.toFixed(2)}, confidence ${row.confidence.toFixed(2)}. Implication: ${escapeHtml(recommendIntervention(row, state.regional?.target || "barrier"))}</p>
            <div class="pill-row">${row.themes.map((theme) => `<span class="pill">${escapeHtml(theme)}</span>`).join("")}</div>
          </div>
        `).join("")}</div>`;
      }

      function buildKnowledgeGraph() {
        const rows = computeRegionalRows();
        const nodes = [];
        const edges = [];
        const addNode = (id, label, kind) => {
          if (!nodes.some((node) => node.id === id)) nodes.push({ id, label, kind, degree: 0 });
        };
        rows.forEach((row) => {
          const regionId = `region:${row.region}`;
          addNode(regionId, row.region.split(" / ").slice(-1)[0], "location");
          row.themes.forEach((theme) => {
            const themeId = `theme:${theme}`;
            addNode(themeId, theme, "theme");
            edges.push({ from: regionId, to: themeId, label: "theme" });
          });
          const trustId = row.trust >= 0.6 ? "signal:high trust" : "signal:trust risk";
          const barrierId = row.barrier >= 0.45 ? "signal:barrier risk" : "signal:low barrier";
          addNode(trustId, trustId.replace("signal:", ""), "signal");
          addNode(barrierId, barrierId.replace("signal:", ""), "signal");
          edges.push({ from: regionId, to: trustId, label: "trust" });
          edges.push({ from: regionId, to: barrierId, label: "barrier" });
        });
        edges.forEach((edge) => {
          const a = nodes.find((node) => node.id === edge.from);
          const b = nodes.find((node) => node.id === edge.to);
          if (a) a.degree += 1;
          if (b) b.degree += 1;
        });
        return { nodes, edges };
      }

      function renderKnowledgeGraphSvg(graph) {
        if (!graph.nodes.length) return '<p>Run encoding first, then build the graph.</p>';
        const w = 640;
        const h = 340;
        const cx = w / 2;
        const cy = h / 2;
        const r = 130;
        const pos = {};
        graph.nodes.forEach((node, index) => {
          const angle = (Math.PI * 2 * index) / Math.max(1, graph.nodes.length);
          const radius = node.kind === "location" ? r * 0.75 : r;
          pos[node.id] = { x: cx + Math.cos(angle) * radius, y: cy + Math.sin(angle) * radius };
        });
        const edgeSvg = graph.edges.map((edge) => {
          const a = pos[edge.from];
          const b = pos[edge.to];
          return `<line x1="${a.x.toFixed(1)}" y1="${a.y.toFixed(1)}" x2="${b.x.toFixed(1)}" y2="${b.y.toFixed(1)}" stroke="var(--line)" stroke-width="1.5"></line>`;
        }).join("");
        const nodeSvg = graph.nodes.map((node) => {
          const p = pos[node.id];
          const color = node.kind === "location" ? "var(--blue)" : node.kind === "theme" ? "var(--amber)" : "var(--green)";
          const size = 8 + Math.min(10, node.degree * 2);
          return `<g><circle cx="${p.x.toFixed(1)}" cy="${p.y.toFixed(1)}" r="${size}" fill="${color}" opacity=".9"></circle><text x="${(p.x + size + 4).toFixed(1)}" y="${(p.y + 4).toFixed(1)}" fill="var(--muted)" font-size="10" font-family="var(--font-data)">${escapeHtml(node.label.slice(0, 22))}</text></g>`;
        }).join("");
        return `<svg class="kg-svg" viewBox="0 0 ${w} ${h}" role="img" aria-label="Knowledge graph">${edgeSvg}${nodeSvg}</svg>`;
      }

      function renderGraphStoryGroups() {
        const rows = computeRegionalRows();
        if (!rows.length) return "";
        return `<div class="insight-list">${rows.map((row) => `
          <div class="insight">
            <strong>${escapeHtml(row.region)}</strong>
            <p>${escapeHtml(row.stories[0]?.slice(0, 170) || "No story text available")}${row.stories[0]?.length > 170 ? "..." : ""}</p>
          </div>
        `).join("")}</div>`;
      }

      function dominantBarrier() {
        const rows = computeRegionalRows();
        const risk = rows.slice().sort((a, b) => b.barrier - a.barrier)[0];
        const themes = topItems((state.encoded || []).flatMap((item) => item.themes || []), 4);
        return { region: risk?.region || state.meta.district || state.meta.country, barrier: risk?.barrier || 0.35, themes };
      }

      function renderCounterCard(item) {
        return `
          <div class="counter-card">
            <span class="mini-label">${escapeHtml(item.type)} / ${escapeHtml(item.audience)}</span>
            <strong>${escapeHtml(item.title)}</strong>
            <p>${escapeHtml(item.text)}</p>
            <div class="pill-row">${item.components.map((part) => `<span class="pill">${escapeHtml(part)}</span>`).join("")}</div>
          </div>
        `;
      }

      function estimateInoculationStrength() {
        const barrier = avg(state.encoded.map((item) => item.adoption_barrier_score), 0.35);
        const trust = avg(state.encoded.map((item) => item.trust_score), 0.6);
        const confidence = avg(state.encoded.map((item) => item.confidence), 0.5);
        const inoculationThemes = state.encoded.filter((item) => (item.themes || []).some((theme) => /inoculation|safety|trust|social/i.test(theme))).length;
        const themeDensity = state.encoded.length ? inoculationThemes / state.encoded.length : 0.25;
        return clamp01(0.16 + barrier * 0.18 + trust * 0.16 + confidence * 0.14 + themeDensity * 0.16, 0.32);
      }

      function adjustedVaccineTrajectory(base, strength, phase = "during", agent = false) {
        if (!base?.length) return [];
        const liftBase = strength * (agent ? 0.115 : 0.095);
        const phaseLift = phase === "after" ? liftBase * 1.45 : liftBase;
        return base.map((point, index) => {
          const progress = index / Math.max(1, base.length - 1);
          const onset = phase === "during"
            ? Math.max(0, Math.min(1, (progress - 0.18) / 0.55))
            : Math.max(0, Math.min(1, (progress - 0.08) / 0.65));
          const decayProtection = phase === "after" ? 0.72 + 0.28 * progress : 1;
          const adoption = clamp01(point.adoption + phaseLift * onset * decayProtection * (1 - point.adoption), point.adoption);
          return { ...point, adoption };
        });
      }

      function buildInoculationVaccine(strength = estimateInoculationStrength()) {
        const compBefore = state.comp?.trajectory || [];
        const agentBefore = state.agents?.trajectory || [];
        return {
          strength,
          compartmental: compBefore.length ? {
            before: compBefore,
            during: adjustedVaccineTrajectory(compBefore, strength, "during", false),
            after: adjustedVaccineTrajectory(compBefore, strength, "after", false)
          } : null,
          agent_based: agentBefore.length ? {
            before: agentBefore,
            during: adjustedVaccineTrajectory(agentBefore, strength, "during", true),
            after: adjustedVaccineTrajectory(agentBefore, strength, "after", true)
          } : null
        };
      }

      function renderVaccineRows(vaccine) {
        const sections = [
          ["Compartmental ODE", vaccine?.compartmental],
          ["Agent-based model", vaccine?.agent_based]
        ];
        return `
          <div class="template-table" style="margin-top: 12px;">
            <div class="template-row head"><span>Model</span><span>Before</span><span>During / after</span></div>
            ${sections.map(([label, scenario]) => {
              const before = scenario?.before?.at(-1)?.adoption;
              const during = scenario?.during?.at(-1)?.adoption;
              const after = scenario?.after?.at(-1)?.adoption;
              return `<div class="template-row"><span data-label="Model">${escapeHtml(label)}</span><span data-label="Before">${fmtPct(before)}</span><span data-label="During / after">${fmtPct(during)} / ${fmtPct(after)}</span></div>`;
            }).join("")}
          </div>
        `;
      }

      function renderVaccineImpact() {
        if (!state.inoculation?.items?.length) {
          return `<div class="panel"><h3>Narrative vaccine model effect</h3><p>Generate inoculation narratives after the ODE and agent models have run. NDIM will estimate intervention strength and show before, during, and after adoption pathways.</p></div>`;
        }
        const vaccine = state.inoculation.vaccine || buildInoculationVaccine(state.inoculation.interventionStrength || estimateInoculationStrength());
        const missing = !vaccine.compartmental && !vaccine.agent_based;
        return `
          <div class="panel">
            <h3>Narrative vaccine model effect</h3>
            <p>The inoculation draft is treated as a controlled narrative intervention. It raises trust/resistance, reduces barrier pressure, and can be applied to the digital twin before the policy brief is generated.</p>
            <div class="metric-grid" style="margin-top: 12px;">
              <div class="metric"><span class="mini-label">Intervention strength</span><strong>${fmtPct(vaccine.strength)}</strong></div>
              <div class="metric"><span class="mini-label">Twin status</span><strong>${state.inoculationApplied ? "applied" : "waiting"}</strong></div>
              <div class="metric"><span class="mini-label">Models ready</span><strong>${missing ? "run ODE/ABM" : "yes"}</strong></div>
            </div>
            ${renderVaccineRows(vaccine)}
            <div class="button-row" style="margin-top: 12px;">
              <button class="button primary" id="applyInoculationVaccine" type="button" ${missing ? "disabled" : ""}>Apply narrative vaccine to digital twin</button>
            </div>
            ${renderTripleLinePlot("ODE before, during, and after inoculation", vaccine.compartmental?.before, vaccine.compartmental?.during, vaccine.compartmental?.after, "adoption", ["before", "during", "after"], ["var(--blue)", "var(--amber)", "var(--green)"])}
            ${renderTripleLinePlot("Agent model before, during, and after inoculation", vaccine.agent_based?.before, vaccine.agent_based?.during, vaccine.agent_based?.after, "adoption", ["before", "during", "after"], ["var(--violet)", "var(--amber)", "var(--green)"])}
            <div class="guide-note"><strong>Interpretation</strong><p>If the after curve is higher than before, the inoculation message is functioning as a protective narrative intervention. It should still be field-tested before deployment because the model predicts direction, not guaranteed persuasion.</p></div>
          </div>
        `;
      }

      function renderFeedResults(feeds) {
        return `
          <div class="metric-grid">
            <div class="metric"><span class="mini-label">Posts</span><strong>${feeds.items.length}</strong></div>
            <div class="metric"><span class="mini-label">High risk</span><strong>${feeds.items.filter((item) => item.risk === "high").length}</strong></div>
            <div class="metric"><span class="mini-label">Counters</span><strong>${feeds.counters.length}</strong></div>
          </div>
          <div class="insight-list">
            ${feeds.items.map((item) => `<div class="feed-item"><strong>${escapeHtml(item.platform)} / ${escapeHtml(item.risk)} risk</strong><p>${escapeHtml(item.text)}</p><div class="pill-row">${item.signals.map((signal) => `<span class="pill">${escapeHtml(signal)}</span>`).join("")}</div></div>`).join("")}
          </div>
          <h3 style="margin-top: 14px;">Counter-feed concepts</h3>
          ${feeds.counters.map(renderCounterCard).join("")}
        `;
      }

      function renderResultNote(kind) {
        const notes = {
          compartmental: state.comp ? `Result implication: the ${state.comp.assumptions?.model_type || "NDIM compartment"} curve reaches ${fmtPct(state.comp.trajectory.at(-1).adoption)} by the horizon with ${finalUncertaintySummary()}. Treat this as the population-level signal, then test whether local agent dynamics support or weaken it.` : "Result implication: run the population model to see whether narrative and intervention inputs produce meaningful adoption growth.",
          agents: state.agents ? `Result implication: the ABM reaches ${fmtPct(state.agents.trajectory.at(-1).adoption)}. ${compareModels()} means the local network assumptions are ${compareModels() === "ABM lower" ? "more cautious than the ODE and may require targeted peer work" : "supportive of diffusion and may justify demonstration-led scaling"}.` : "Result implication: run the agent model to test household-level friction and peer spread.",
          digital: state.digital ? `Result implication: the feedback-adjusted twin reaches ${fmtPct(state.digital.trajectory.at(-1).adoption)}. If this diverges from baseline, the field observation materially changed the model.` : "Result implication: use observed adoption and field notes to correct the next simulation.",
          bayes: state.bayes ? `Result implication: posterior trust is ${fmtPct(state.bayes.trustMean)} and posterior barrier is ${fmtPct(state.bayes.barrierMean)}. ${state.bayes.fallback ? "The backend used a labelled fallback posterior approximation." : "Advanced posterior analytics were used when available."}` : "Result implication: Bayesian updating shows how evidence moves assumptions instead of hiding them.",
          rl: state.rl ? `Result implication: the best learned intervention is "${state.rl.bestAction}" with Q reward ${Number(state.rl.bestReward || 0).toFixed(3)}. ${state.rl.fallback ? "This is a labelled fallback optimizer result." : "This optimizer result came from the analytics endpoint."} Use it as a candidate, not an automatic decision.` : "Result implication: run the optimizer to stress-test intervention packages before drafting policy."
        };
        return `<div class="result-note"><p>${escapeHtml(notes[kind] || "")}</p></div>`;
      }

      function renderRLBars() {
        const history = state.rl?.history || [];
        if (!history.length) return "<p>Run RL to show reward samples.</p>";
        const max = Math.max(...history.map((item) => item.reward), 0.01);
        return history.slice(-8).map((item) => `
          <div class="bar-row">
            <span>ep ${item.episode}</span>
            <div class="bar-track"><div class="bar-fill" style="width:${Math.max(2, (item.reward / max) * 100)}%; background: var(--violet);"></div></div>
            <span>${item.reward.toFixed(2)}</span>
          </div>
        `).join("");
      }

      function compareModels() {
        const c = state.comp?.trajectory?.at(-1)?.adoption;
        const a = state.agents?.trajectory?.at(-1)?.adoption;
        if (typeof c !== "number" || typeof a !== "number") return "-";
        return a >= c ? "ABM higher" : "ABM lower";
      }

      function policyNarrative() {
        if (!state.policy) return "Run the full policy pipeline to produce a recommendation draft.";
        const summary = state.policy.summary || {};
        const adoption = fmtPct(summary.final_adoption);
        const trust = fmtPct(summary.average_trust);
        const barrier = fmtPct(summary.average_barrier);
        const rl = state.rl?.bestAction ? ` The RL loop prefers ${state.rl.bestAction}.` : "";
        const feedback = state.digital ? " Digital twin feedback and posterior values were included in the interpretation." : "";
        const regional = state.regional?.rows?.length ? ` Regional analysis produced ${state.regional.rows.length} intervention unit(s).` : "";
        const inoculation = state.inoculation?.items?.length ? ` The inoculation lab generated ${state.inoculation.items.length} counter-narrative drafts for review.` : "";
        return `Preliminary signal: prioritize trust-led clean-cooking outreach in ${state.meta.district || state.meta.country}. The current run projects ${adoption} final adoption, with average trust at ${trust} and average barrier at ${barrier}.${rl}${feedback}${regional}${inoculation} Human review is required before export.`;
      }

      function governanceJson() {
        return {
          schema: "ndim-governance-ledger-v1",
          project: {
            evidence_mode: state.template.evidenceMode,
            evidence_mode_label: currentEvidenceMode().title,
            country: state.meta.country,
            admin_unit: adminUnitLabel(),
            source_type: state.meta.sourceType,
            source_name: state.meta.sourceName,
            period: state.meta.period,
            language: state.meta.language
          },
          settings: {
            reviewer: state.governance.reviewer,
            reviewer_role: state.governance.reviewerRole,
            visibility: state.governance.visibility,
            consent: state.governance.consent,
            repository_mode: state.governance.repositoryMode,
            review_threshold: state.governance.injectionThreshold
          },
          batch_digest: state.governance.lastDigest,
          master_repository: {
            status: state.masterRepository.status,
            sync_status: state.masterRepository.syncStatus,
            target: state.masterRepository.target,
            backend: state.masterRepository.backend,
            reviewer: state.masterRepository.reviewer,
            reviewer_role: state.masterRepository.role,
            note: state.masterRepository.note,
            last_prepared_at: state.masterRepository.lastPreparedAt,
            last_decision_at: state.masterRepository.lastDecisionAt,
            anchor_hash: state.masterRepository.anchorHash,
            previous_hash: state.masterRepository.previousHash,
            event_hash: state.masterRepository.eventHash,
            decision_hash: state.masterRepository.decisionHash,
            blockchain_status: state.masterRepository.blockchainStatus,
            package_schema: state.masterRepository.package?.schema || null
          },
          records: state.records.map((record) => ({
            narrative_id: record.narrative_id,
            text: record.text,
            source_name: record.metadata?.source_name,
            country: record.metadata?.country,
            admin_unit: record.metadata?.admin_unit,
            evidence_mode: record.metadata?.provenance?.evidence_mode,
            evidence_mode_label: record.metadata?.provenance?.evidence_mode_label,
            question_id: record.metadata?.provenance?.question_id,
            knowledge_type: record.metadata?.provenance?.knowledge_type,
            knowledge_holder: record.metadata?.provenance?.knowledge_holder,
            sensitivity: record.metadata?.provenance?.sensitivity,
            community_validation: record.metadata?.provenance?.community_validation,
            attribution: record.metadata?.provenance?.attribution,
            location_precision: record.metadata?.provenance?.location_precision,
            contributor_type: record.metadata?.provenance?.contributor_type,
            feed_sources: record.metadata?.provenance?.feed_sources,
            citizen_confidence: record.metadata?.provenance?.citizen_confidence,
            validation_status: record.metadata?.provenance?.validation_status,
            evidence_hash: record.governance?.evidence_hash,
            content_hash: record.governance?.content_hash,
            status: record.governance?.status,
            reviewer: record.governance?.reviewer,
            reviewed_at: record.governance?.reviewed_at,
            reviewer_signature: record.governance?.reviewer_signature,
            review_reason: record.governance?.review_reason,
            repository_bucket: record.governance?.repository_bucket,
            committed_at: record.governance?.committed_at,
            commit_signature: record.governance?.commit_signature,
            uncommitted_at: record.governance?.uncommitted_at,
            master_repository_status: record.governance?.master_repository_status,
            master_anchor_hash: record.governance?.master_anchor_hash,
            master_event_hash: record.governance?.master_event_hash,
            master_decision_hash: record.governance?.master_decision_hash,
            master_reviewer: record.governance?.master_reviewer,
            master_reviewed_at: record.governance?.master_reviewed_at,
            master_blockchain_status: record.governance?.master_blockchain_status,
            visibility: record.governance?.visibility,
            consent: record.governance?.consent,
            repository_mode: record.governance?.repository_mode,
            scan: record.governance?.scan
          })),
          ledger: state.governance.ledger
        };
      }

      function policyJson() {
        if (!state.policy) return { status: "not_run" };
        return {
          schema: "ndim-policy-output-v1",
          generated_formats: ["html_policy_brief", "pdf_print_view", "markdown_policy_brief", "json_audit_payload"],
          decision_brief: policyDecisionBrief(),
          metadata: state.meta,
          governance: governanceJson(),
          narrative_commons_intake: {
            evidence_mode: state.template.evidenceMode,
            evidence_mode_label: currentEvidenceMode().title,
            knowledge_type: state.template.knowledgeType,
            knowledge_holder: state.template.knowledgeHolder,
            sensitivity: state.template.sensitivity,
            community_validation: state.template.communityValidation,
            attribution: state.template.attribution,
            location_precision: state.template.locationPrecision,
            contributor_type: state.template.contributorType,
            feed_sources: state.template.feedSources,
            validation_status: state.template.validationStatus
          },
          encoding_mode: state.encodingMode,
          llm_provider: state.llmProvider,
          llm_provider_config: publicLlmConfig(),
          manual_scorecards: state.manualScorecards,
          narratives: state.records.length,
          encoded: state.encoded,
          feedback_chain: {
            evidence_to_encoding: state.encoded.length > 0,
            ode_and_agent_models: Boolean(state.comp || state.agents),
            digital_twin_to_policy: Boolean(state.digital),
            bayesian_posterior_to_policy: Boolean(state.bayes),
            rl_policy_to_recommendation: Boolean(state.rl),
            regional_graph_inoculation_to_brief: Boolean(state.regional || state.graph || state.inoculation),
            inoculation_vaccine_to_digital_twin: Boolean(state.inoculationApplied)
          },
          compartmental_summary: state.comp?.trajectory?.at(-1) || null,
          compartmental_assumptions: state.comp?.assumptions || null,
          agent_summary: state.agents?.trajectory?.at(-1) || null,
          agent_assumptions: state.agents?.assumptions || null,
          digital_twin_summary: state.digital?.trajectory?.at(-1) || null,
          digital_twin_assumptions: state.digital?.assumptions || null,
          bayesian_posterior: state.bayes,
          rl_policy: state.rl,
          regional_analysis: state.regional,
          knowledge_graph: state.graph,
          inoculation_narratives: state.inoculation,
          inoculation_vaccine_applied: state.inoculationApplied,
          pipeline_summary: state.policy.summary,
          recommendation: policyNarrative()
        };
      }

      function policyMarkdown() {
        const pkg = policyJson();
        if (pkg.status === "not_run") return "# NDIM Policy Brief\n\nRun the policy stage before exporting.";
        const brief = pkg.decision_brief || policyDecisionBrief();
        return `# NDIM Policy Brief

## Recommendation

${policyNarrative()}

## Confidence And Review

- Confidence level: ${brief.confidence_level}
- Evidence grade: ${brief.evidence_grade}
- Policy warning: ${brief.policy_use_warning}
- Model used: ${brief.model_type_used}
- Uncertainty: ${brief.uncertainty_summary}
- Validation: ${brief.validation_summary}
- Human review required: yes

## Evidence Base

- Country: ${state.meta.country}
- Administrative unit: ${adminUnitLabel() || "not set"}
- Approved narratives: ${approvedRecords().length}
- Evidence route: ${currentEvidenceMode().title}
- Encoding mode: ${state.encodingMode}
- LLM provider path: ${state.llmProvider}

## Model Feedback Chain

- Digital twin used in policy: ${state.digital ? "yes" : "not yet"}
- Bayesian posterior used in policy: ${state.bayes ? "yes" : "not yet"}
- RL optimizer used in policy: ${state.rl ? `yes, best action: ${state.rl.bestAction}` : "not yet"}
- Regional analysis included: ${state.regional ? "yes" : "not yet"}
- Knowledge graph included: ${state.graph ? "yes" : "not yet"}
- Inoculation drafts included: ${state.inoculation ? "yes" : "not yet"}
- Inoculation vaccine applied to twin: ${state.inoculationApplied ? `yes, strength ${fmtPct(state.inoculation?.interventionStrength)}` : "not yet"}

## Output Package

This brief is generated from the JSON audit payload \`ndim-policy-output-v1\`. The JSON contains governance hashes, encoded narratives, model summaries, digital twin output, Bayesian posterior, RL policy, regional analysis, knowledge graph, inoculation drafts, narrative vaccine status, and the recommendation text.
`;
      }

      function policyHtmlDocument(autoPrint = false) {
        const pkg = policyJson();
        const summary = pkg.pipeline_summary || {};
        const brief = pkg.decision_brief || policyDecisionBrief();
        const rows = [
          ["Country", state.meta.country],
          ["Administrative unit", adminUnitLabel() || "not set"],
          ["Accepted evidence records", String(approvedRecords().length)],
          ["Evidence grade", brief.evidence_grade],
          ["Confidence level", brief.confidence_level],
          ["Policy warning", brief.policy_use_warning],
          ["Encoding mode", state.encodingMode],
          ["LLM provider path", state.llmProvider],
          ["Model used", brief.model_type_used],
          ["Uncertainty", brief.uncertainty_summary],
          ["Validation", brief.validation_summary],
          ["Final adoption", fmtPct(summary.final_adoption)],
          ["Average trust", fmtPct(summary.average_trust)],
          ["Average barrier", fmtPct(summary.average_barrier)],
          ["Digital twin used", state.digital ? "yes" : "not yet"],
          ["Bayesian posterior used", state.bayes ? "yes" : "not yet"],
          ["RL action", state.rl?.bestAction || "not yet"],
          ["Inoculation vaccine applied", state.inoculationApplied ? "yes" : "not yet"]
        ];
        const evidenceRows = approvedRecords().map((record) => `
          <tr>
            <td>${escapeHtml(record.narrative_id)}</td>
            <td>${escapeHtml(record.metadata?.provenance?.evidence_mode_label || currentEvidenceMode().title)}</td>
            <td>${escapeHtml(record.metadata?.admin_unit || record.metadata?.country || "-")}</td>
            <td>${escapeHtml(recordStatusLabel(record))}</td>
          </tr>
        `).join("");
        return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>NDIM Policy Brief</title>
  <style>
    body { margin: 0; color: #111827; background: #f7f4ee; font-family: "Myriad Pro", "Segoe UI", Arial, sans-serif; line-height: 1.55; }
    main { max-width: 980px; margin: 0 auto; padding: 36px 24px 64px; }
    h1 { margin: 0 0 8px; font-size: 42px; line-height: 1.05; }
    h2 { margin-top: 28px; border-top: 1px solid #d7cbb8; padding-top: 20px; }
    p { color: #4b5563; font-size: 16px; }
    table { width: 100%; border-collapse: collapse; margin-top: 12px; background: #fffdf8; }
    th, td { border: 1px solid #d7cbb8; padding: 10px; text-align: left; vertical-align: top; }
    th { background: #efe8dc; font-size: 12px; text-transform: uppercase; letter-spacing: .08em; }
    .brief { border: 1px solid #d7cbb8; border-radius: 16px; background: #fffdf8; padding: 18px; }
    .meta { color: #806c53; font-size: 13px; text-transform: uppercase; letter-spacing: .08em; }
    @media print { body { background: white; } main { max-width: none; padding: 18mm; } button { display: none; } }
  </style>
</head>
<body>
  <main>
    <p class="meta">NDIM Engine policy output</p>
    <h1>Policy-ready clean-cooking intervention brief</h1>
    <p>This is the human-readable decision output. The JSON audit payload is separate and should be used for technical verification, hashes, and reproducibility.</p>
    <section class="brief">
      <h2>Recommendation</h2>
      <p>${escapeHtml(policyNarrative())}</p>
    </section>
    <section class="brief">
      <h2>Confidence, assumptions, and required review</h2>
      <p><strong>Confidence:</strong> ${escapeHtml(brief.confidence_level)}. <strong>Evidence grade:</strong> ${escapeHtml(brief.evidence_grade)}.</p>
      <p>${escapeHtml(brief.policy_use_warning)}</p>
      <p><strong>Uncertainty:</strong> ${escapeHtml(brief.uncertainty_summary)}. <strong>Validation:</strong> ${escapeHtml(brief.validation_summary)}</p>
    </section>
    <h2>Evidence and model chain</h2>
    <table><tbody>${rows.map(([label, value]) => `<tr><th>${escapeHtml(label)}</th><td>${escapeHtml(value)}</td></tr>`).join("")}</tbody></table>
    <h2>Accepted evidence ledger</h2>
    <table>
      <thead><tr><th>Narrative ID</th><th>Route</th><th>Place</th><th>Status</th></tr></thead>
      <tbody>${evidenceRows || '<tr><td colspan="4">No accepted records were committed.</td></tr>'}</tbody>
    </table>
    <h2>Interpretation</h2>
    <p>The policy recommendation should be reviewed against local feasibility, consent restrictions, uncertainty, and whether accepted evidence is representative of the target communities.</p>
  </main>
  ${autoPrint ? "<script>window.addEventListener('load', function () { setTimeout(function () { window.print(); }, 250); });<\\/script>" : ""}
</body>
</html>`;
      }

      function openPrintablePolicy() {
        const blob = new Blob([policyHtmlDocument(true)], { type: "text/html" });
        const url = URL.createObjectURL(blob);
        const opened = window.open(url, "_blank", "noopener,noreferrer");
        if (opened) {
          trace("policy", "PDF-ready policy view opened", "Opened a print-ready HTML brief. Use the browser print dialog to save it as PDF.");
          toast("PDF view opened");
          window.setTimeout(() => URL.revokeObjectURL(url), 60000);
        } else {
          downloadText(`ndim-policy-brief-${Date.now()}.html`, policyHtmlDocument(false), "text/html");
          trace("policy", "PDF view blocked", "The browser blocked the new tab, so the HTML brief was downloaded instead.");
          toast("HTML brief downloaded");
        }
      }

      function fieldTemplateMarkdown() {
        const schema = countrySchema();
        return `# NDIM Narrative Commons Collection Template

## Metadata (Enumerator fills)

- Evidence mode: ${currentEvidenceMode().title}
- Interview ID:
- Country: ${state.meta.country}
${schema.levels.map((level) => `- ${level.label}:`).join("\n")}
- Respondent profile (age range, gender, occupation):
- Primary cooking decision-maker (Yes/No/Shared):
- Current cooking method(s):
- Source name:
- Period:
- Language:
- Knowledge/evidence type:
- Knowledge holder / contributor:
- Cultural sensitivity:
- Community validation:
- Attribution preference:
- Location precision:
- Observation date:
- Contributor type:
- Social feed sources:
- Contributor confidence:
- Validation status:
- Translation / interpretation notes:
- Benefit sharing / community return note:

## Core Narrative Elicitation Questions

${narrativeQuestions.map((question) => `### ${question.title}

${question.prompt}
`).join("\n")}
## Optional Probes

- Can you give an example?
- What happened next?
- How did that make you feel?
- What did others do in that situation?

## Narrative Coding Fields (Post-Interview)

- Tone/Archetype (regret, triumph, denial, pragmatic, anxious):
- Adoption stance (For / Against / Mixed):
- Key barrier (cost, safety, habit, knowledge, access):
- Key motivator (time, fuel savings, status, convenience, health):
- Social influence (high / medium / low):

## Open Narrative / Indigenous Knowledge / Citizen Science Story

Paste or transcribe the full story in the contributor's own words. Keep local concepts and translation notes attached. Separate multiple stories with blank lines when batching.
`;
      }

      function fieldTemplateCsv() {
        const schema = countrySchema();
        const headers = [
          "evidence_mode",
          "interview_id",
          "country",
          ...schema.levels.map((level) => level.label.toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_|_$/g, "")),
          "respondent_profile",
          "primary_decision_maker",
          "current_cooking_methods",
          "knowledge_type",
          "knowledge_holder",
          "sensitivity",
          "community_validation",
          "attribution",
          "location_precision",
          "observation_date",
          "contributor_type",
          "feed_sources",
          "citizen_confidence",
          "validation_status",
          "translation_notes",
          "benefit_sharing",
          "source_name",
          "period",
          "language",
          "narrative",
          ...narrativeQuestions.map((question) => question.id),
          "tone_archetype",
          "adoption_stance",
          "key_barrier",
          "key_motivator",
          "social_influence"
        ];
        const sample = [
          state.template.evidenceMode,
          state.template.interviewId || "RW-NYA-001",
          state.meta.country,
          ...schema.levels.map((level) => state.meta[level.key] || ""),
          state.template.respondentProfile || "35-44, female, farmer",
          state.template.decisionMaker || "yes",
          state.template.cookingMethods || "firewood; charcoal",
          state.template.knowledgeType,
          state.template.knowledgeHolder,
          state.template.sensitivity,
          state.template.communityValidation,
          state.template.attribution,
          state.template.locationPrecision,
          state.template.observationDate,
          state.template.contributorType,
          Array.isArray(state.template.feedSources) ? state.template.feedSources.join(";") : "",
          state.template.citizenConfidence,
          state.template.validationStatus,
          state.template.translationNotes,
          state.template.benefitSharing,
          state.meta.sourceName,
          state.meta.period,
          state.meta.language,
          state.text,
          ...narrativeQuestions.map((question) => state.template[question.id] || ""),
          state.template.tone,
          state.template.stance,
          state.template.barrier,
          state.template.motivator,
          state.template.socialInfluence
        ];
        const csvEscape = (value) => `"${String(value ?? "").replace(/"/g, '""')}"`;
        return `${headers.map(csvEscape).join(",")}\n${sample.map(csvEscape).join(",")}\n`;
      }

      function downloadText(filename, text, type = "text/plain") {
        const blob = new Blob([text], { type });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        link.remove();
        URL.revokeObjectURL(url);
      }

      async function copyText(text, fallbackFilename = "ndim-copy.txt", type = "text/plain") {
        try {
          if (navigator.clipboard?.writeText) {
            await navigator.clipboard.writeText(text);
            return true;
          }
        } catch (error) {
          // Some embedded browsers deny clipboard permissions. Fall back to
          // the older selection path and keep a local copy for inspection.
        }
        const area = document.createElement("textarea");
        area.value = text;
        area.setAttribute("readonly", "");
        area.style.position = "fixed";
        area.style.left = "-9999px";
        document.body.appendChild(area);
        area.focus();
        area.select();
        let copied = false;
        try {
          copied = document.execCommand("copy");
        } catch (error) {
          copied = false;
        }
        area.remove();
        if (!copied) {
          window.__ndimLastCopy = text;
          downloadText(fallbackFilename, text, type);
        }
        return copied;
      }

      async function copyFieldTemplate() {
        const copied = await copyText(fieldTemplateMarkdown(), `ndim-field-template-${state.meta.country.toLowerCase()}.md`, "text/markdown");
        toast(copied ? "Field template copied" : "Copy blocked; template downloaded");
        trace("template", "Field template copied", `Generated a ${state.meta.country} collection template with ${countrySchema().levels.map((level) => level.label).join(" > ")} administrative levels.`);
      }

      function resetIntakeState() {
        state.text = "";
        state.records = [];
        state.importedRecords = [];
        state.encoded = [];
        state.encodingRuns = {};
        state.manualScorecards = {};
        state.manualIndex = 0;
        state.governance.ledger = [];
        state.governance.lastDigest = "";
        state.governance.lastAnchoredAt = "";
        Object.keys(state.template).forEach((key) => { state.template[key] = ""; });
        state.template.evidenceMode = "structured_interview";
        state.template.sensitivity = "ordinary";
        state.template.communityValidation = "pending";
        state.template.attribution = "anonymous";
        state.template.locationPrecision = "approximate";
        state.template.citizenConfidence = "medium";
        state.template.validationStatus = "pending";
        state.template.feedSources = [];
        state.completed.delete("intake");
        state.completed.delete("gate");
        trace("reset", "Intake reset", "Narrative text and staged observations were cleared.");
        toast("Intake reset");
        render();
      }

      function openSupportPage(path, label) {
        const opened = window.open(path, "_blank", "noopener,noreferrer");
        if (opened) {
          toast(`${label} opened`);
          trace("support", `${label} opened`, `Opened ${path} from the Intake Option menu.`);
        } else {
          window.location.href = path;
        }
      }

      async function runIntakeOption() {
        const option = state.intakeOption || $("intakeOptionSelect")?.value || "manual";
        if (option === "manual") {
          openSupportPage("/manual", "Manual");
          return;
        }
        if (option === "corpus") {
          openSupportPage("/stress-test-corpus", "Stress-test corpus");
          return;
        }
        if (option === "copy") {
          await copyFieldTemplate();
          return;
        }
        if (option === "download") {
          downloadText(`ndim-field-template-${state.meta.country.toLowerCase()}.csv`, fieldTemplateCsv(), "text/csv");
          trace("template", "CSV field template downloaded", "The CSV includes country-specific administrative columns and Q1-Q5 narrative columns.");
          toast("CSV template downloaded");
          return;
        }
        if (option === "reset") resetIntakeState();
      }

      function bindStage(id) {
        if (id === "intake") {
          $("country").value = state.meta.country;
          $("language").value = state.meta.language;
          $("sourceType").value = state.meta.sourceType;
          $("evidenceModeSelect").addEventListener("change", (event) => {
            saveIntakeFromDom();
            state.template.evidenceMode = event.target.value;
            state.meta.sourceType = sourceTypeForMode(state.template.evidenceMode);
            trace("intake", "Evidence route selected", `${currentEvidenceMode().title} will use ${state.meta.sourceType} as the default source type.`);
            render();
          });
          $("country").addEventListener("change", (event) => {
            saveIntakeFromDom();
            state.meta.country = event.target.value;
            const schema = countrySchema();
            state.meta.language = schema.language;
            state.meta.province = "";
            state.meta.district = "";
            state.meta.sector = "";
            trace("metadata", "Country schema changed", `${state.meta.country} uses ${schema.levels.map((level) => level.label).join(" > ")}.`);
            render();
          });
          ["province", "district", "sector"].forEach((key) => {
            const el = $(key);
            if (!el) return;
            el.addEventListener("change", (event) => {
              state.meta[key] = event.target.value;
              if (key === "province") {
                state.meta.district = "";
                state.meta.sector = "";
              }
              if (key === "district") {
                state.meta.sector = "";
              }
              trace("metadata", "Administrative unit selected", `${key}: ${event.target.value || "cleared"}.`);
              render();
            });
          });
          document.querySelectorAll("[data-feed-source]").forEach((input) => {
            input.addEventListener("change", () => {
              saveIntakeFromDom();
              trace("intake", "Social feed source updated", `${state.template.feedSources.length || 0} feed source(s) selected for governance review.`);
            });
          });
          $("intakeOptionSelect").addEventListener("change", (event) => {
            state.intakeOption = event.target.value;
            trace("intake", "Intake helper selected", `${intakeOptionActionLabel()} is ready from the Intake Option menu.`);
            render();
          });
          $("runIntakeOption").addEventListener("click", runIntakeOption);
          $("stageEvidence").addEventListener("click", async () => {
            if (await validateIntake()) goStep(1);
          });
          
          $("loadSample").addEventListener("click", () => {
            state.template.evidenceMode = "structured_interview";
            state.meta.country = "Rwanda";
            state.meta.province = "Southern Province";
            state.meta.district = "Nyamagabe";
            state.meta.sector = "Kamegeri sector / village";
            state.meta.language = "rw";
            state.meta.sourceType = "interview";
            state.template.interviewId = "RW-NYA-001";
            state.template.respondentProfile = "35-44, female, farmer";
            state.template.decisionMaker = "yes";
            state.template.cookingMethods = "firewood; charcoal";
            state.template.knowledgeType = "cooking_practice";
            state.template.knowledgeHolder = "household";
            state.template.sensitivity = "ordinary";
            state.template.communityValidation = "pending";
            state.template.attribution = "anonymous";
            state.template.locationPrecision = "approximate";
            state.template.observationDate = "";
            state.template.contributorType = "enumerator";
            state.template.citizenConfidence = "medium";
            state.template.validationStatus = "pending";
            state.template.feedSources = [];
            state.template.benefitSharing = "Return summary findings through community consultation.";
            state.template.q1 = "I cooked beans and vegetables using firewood. The kitchen filled with smoke and I had to keep checking the pot while also doing other work.";
            state.template.q2 = "I first heard about pressure cookers from a neighbour. I thought it sounded faster, but I worried it might be expensive or unsafe.";
            state.template.q3 = "Some women say pressure cookers save time, but others say they do not know where to repair them if something breaks.";
            state.template.q4 = "The difficult part is the first purchase cost and whether my family will trust food cooked in a different way.";
            state.template.q5 = "If it worked well, I would spend less time collecting firewood and the kitchen would have less smoke.";
            state.template.tone = "pragmatic";
            state.template.stance = "mixed";
            state.template.barrier = "cost";
            state.template.motivator = "time";
            state.template.socialInfluence = "high";
            state.text = "";
            state.importedRecords = [];
            trace("sample", "One sample story loaded", "A single built-in Rwanda pressure-cooker interview example was loaded into Q1-Q5 and coding fields for manual intake practice.");
            toast("One sample story loaded");
            render();
          });
          $("fileInput").addEventListener("change", async (event) => {
            const file = event.target.files && event.target.files[0];
            if (!file) return;
            const text = await file.text();
            if (file.name.toLowerCase().endsWith(".csv")) {
              const rows = parseCsv(text);
              applyImportedCsvMetadata(rows[0] || {}, file.name);
              state.importedRecords = recordsFromCsv(text, file.name);
              state.records = state.importedRecords;
              state.text = state.records.map((record) => record.text).join("\n\n");
              state.encoded = [];
              state.encodingRuns = {};
              state.manualScorecards = {};
              state.manualIndex = 0;
              $("narrativeText").value = state.text;
              $("sourceType").value = state.meta.sourceType;
              $("sourceName").value = file.name;
              trace("csv", "CSV file imported", `${state.records.length} narrative observation(s) imported from ${file.name}. Detected route: ${currentEvidenceMode().title}. You can still edit text before staging.`);
            } else {
              state.importedRecords = [];
              state.text = text;
              state.meta.sourceName = file.name;
              $("narrativeText").value = text;
              trace("file", "File loaded", `${file.name} loaded into the intake form.`);
            }
            render();
            toast("File loaded");
          });
        }
        if (id === "gate") {
          $("copyGateTemplate").addEventListener("click", copyFieldTemplate);
          $("downloadGateCsv").addEventListener("click", () => {
            downloadText(`ndim-field-template-${state.meta.country.toLowerCase()}.csv`, fieldTemplateCsv(), "text/csv");
            trace("template", "CSV field template downloaded from gate", "The SDMX gate exported a field-ready template with Q1-Q5 narrative columns.");
            toast("CSV template downloaded");
          });
          ["reviewerName", "reviewerRole", "visibility", "consentTier", "repositoryMode", "injectionThreshold"].forEach((id) => {
            const el = $(id);
            if (el) el.addEventListener("change", () => {
              saveGovernanceFromDom();
              trace("governance", "Governance settings updated", `Visibility ${state.governance.visibility}; consent ${state.governance.consent}; repository ${state.governance.repositoryMode}.`);
              render();
            });
          });
          $("sealEvidence").addEventListener("click", async () => {
            saveGovernanceFromDom();
            await sealRecords("manual governance seal");
            await syncLedgerToBackend("manual governance seal");
            trace("governance", "Evidence re-sealed", `Batch digest ${shortHash(state.governance.lastDigest)} is ready for repository anchoring.`);
            toast("Evidence sealed");
            render();
          });
          $("approveEligible").addEventListener("click", async () => {
            saveGovernanceFromDom();
            if (!state.records.length && !await validateIntake()) return;
            if (!state.governance.lastDigest) await sealRecords("approval seal");
            let approved = 0;
            for (const record of activeReviewRecords()) {
              const risk = record.governance?.scan?.risk || 0;
              if (risk < state.governance.injectionThreshold && record.governance?.status !== "approved_pending_commit") {
                await setRecordApproval(record, "approved", "eligible after automated scan and reviewer gate");
                approved += 1;
              }
            }
            if (approved) {
              await syncLedgerToBackend("eligible records approved");
              trace("approval", "Eligible narratives marked approved", `${approved} observation(s) are approved and waiting for commit into the accepted repository.`);
              toast("Records pending commit");
            } else {
              trace("approval", "No eligible records approved", "All records were either already approved or require manual review.");
              toast("Nothing approved");
            }
            render();
          });
          $("rejectFlagged").addEventListener("click", async () => {
            saveGovernanceFromDom();
            let rejected = 0;
            for (const record of activeReviewRecords()) {
              const risk = record.governance?.scan?.risk || 0;
              if (risk >= state.governance.injectionThreshold && record.governance?.status !== "rejected_pending_commit") {
                await setRecordApproval(record, "rejected", "flagged by prompt-injection/PII/data-quality scan");
                rejected += 1;
              }
            }
            if (rejected) await syncLedgerToBackend("flagged records rejected");
            trace("approval", "Flagged review complete", `${rejected} high-risk observation(s) are rejected and waiting for commit into the rejected repository.`);
            toast(rejected ? "Rejected records pending commit" : "No flagged records");
            render();
          });
          $("commitReviewed").addEventListener("click", async () => {
            saveGovernanceFromDom();
            const result = await commitReviewedRecords();
            if (result.accepted || result.rejected) {
              await syncLedgerToBackend("reviewed records committed");
              trace("repository", "Reviewed records committed", `${result.accepted} accepted and ${result.rejected} rejected record(s) moved out of the active approval queue.`);
              toast("Reviewed records committed");
            } else {
              trace("repository", "No reviewed records to commit", "Approve or reject at least one active record before committing.");
              toast("Nothing to commit");
            }
            render();
          });
          $("copyLedger").addEventListener("click", async () => {
            const copied = await copyText(JSON.stringify(governanceJson(), null, 2), `ndim-governance-ledger-${Date.now()}.json`, "application/json");
            toast(copied ? "Governance ledger copied" : "Copy blocked; ledger downloaded");
            trace("governance", "Ledger copied", "The tamper-evident governance package was copied as JSON.");
          });
          $("downloadLedger").addEventListener("click", () => {
            downloadText(`ndim-governance-ledger-${Date.now()}.json`, JSON.stringify(governanceJson(), null, 2), "application/json");
            trace("governance", "Ledger downloaded", "Downloaded hashes, scan results, approval decisions, and chained ledger events.");
            toast("Ledger downloaded");
          });
          document.querySelectorAll("[data-approve-record]").forEach((button) => {
            button.addEventListener("click", async () => {
              saveGovernanceFromDom();
              const record = state.records[Number(button.dataset.approveRecord)];
              if (!record) return;
              await setRecordApproval(record, "approved", "manual reviewer approval");
              await syncLedgerToBackend("single record approved");
              trace("approval", "Narrative marked approved", `${record.narrative_id} is waiting for Commit reviewed records before it enters the accepted repository.`);
              toast("Approval pending commit");
              render();
            });
          });
          document.querySelectorAll("[data-reject-record]").forEach((button) => {
            button.addEventListener("click", async () => {
              saveGovernanceFromDom();
              const record = state.records[Number(button.dataset.rejectRecord)];
              if (!record) return;
              await setRecordApproval(record, "rejected", "manual reviewer rejection");
              await syncLedgerToBackend("single record rejected");
              trace("approval", "Narrative marked rejected", `${record.narrative_id} is waiting for Commit reviewed records before it enters the rejected repository.`);
              toast("Rejection pending commit");
              render();
            });
          });
        }
        if (id === "encoding") {
          $("llmProvider").value = state.llmProvider;
          ["llmModel", "llmBaseUrl", "llmApiKey"].forEach((fieldId) => {
            const el = $(fieldId);
            if (!el) return;
            el.addEventListener("change", () => {
              state.llmConfig.model = $("llmModel")?.value || "";
              state.llmConfig.baseUrl = $("llmBaseUrl")?.value || "";
              state.llmConfig.apiKey = $("llmApiKey")?.value || "";
              state.llmConfig.status = llmStatusLabel();
              trace("choice", "LLM settings updated", `${state.llmProvider} configured as ${llmStatusLabel()}. API key is session-only and not logged.`);
              render();
            });
          });
          $("encoderName").value = state.encoderName;
          $("encoderName").addEventListener("change", (event) => {
            state.encoderName = event.target.value || "research-encoder";
            const record = currentReviewRecord();
            const card = ensureManualScorecard(record);
            if (card) card.encoder = state.encoderName;
            trace("choice", "Manual encoder set", `Manual scorecards will be signed as ${state.encoderName}.`);
          });
          $("llmProvider").addEventListener("change", (event) => {
            state.llmProvider = event.target.value;
            state.llmConfig.model = "";
            state.llmConfig.baseUrl = "";
            state.llmConfig.status = llmStatusLabel();
            trace("choice", "LLM provider selected", `Selected ${state.llmProvider}. Credentials are supplied per user/session or by local/environment fallback.`);
            render();
          });
          document.querySelectorAll("[data-mode]").forEach((button) => {
            button.addEventListener("click", () => {
              state.encodingMode = button.dataset.mode;
              trace("choice", "Encoding mode selected", `Selected ${state.encodingMode}.`);
              render();
            });
          });
          document.querySelectorAll("[data-score]").forEach((input) => {
            input.addEventListener("change", () => {
              const record = currentReviewRecord();
              const card = ensureManualScorecard(record);
              const key = input.dataset.score;
              const value = clamp01(input.value, manualEncodingVariables.find((variable) => variable.key === key)?.defaultValue ?? 0.5);
              if (card) card.scores[key] = value;
              state.manualScores[key] = value;
              if (card) card.status = "draft";
              trace("manual", "Manual score updated", `${key} set to ${value.toFixed(2)} for ${record?.narrative_id || "current story"}.`);
              render();
            });
          });
          document.querySelectorAll("[data-score-note]").forEach((input) => {
            input.addEventListener("change", () => {
              const record = currentReviewRecord();
              const card = ensureManualScorecard(record);
              if (!card) return;
              card.notes[input.dataset.scoreNote] = input.value;
              card.status = "draft";
              trace("manual", "Score justification updated", `${input.dataset.scoreNote} note saved for ${record.narrative_id}.`);
              render();
            });
          });
          document.querySelectorAll("[data-select-story]").forEach((button) => {
            button.addEventListener("click", () => {
              state.manualIndex = Number(button.dataset.selectStory);
              trace("manual", "Story selected for encoding", `Opened story ${state.manualIndex + 1} in the batch queue.`);
              render();
            });
          });
          const prev = $("prevStory");
          const next = $("nextStory");
          if (prev) prev.addEventListener("click", () => { state.manualIndex = Math.max(0, state.manualIndex - 1); render(); });
          if (next) next.addEventListener("click", () => {
            const reviewableCount = reviewableRecords().length;
            state.manualIndex = Math.min(Math.max(0, reviewableCount - 1), state.manualIndex + 1);
            render();
          });
          $("runEncoding").addEventListener("click", runEncoding);
          $("runCurrentEncoding").addEventListener("click", runCurrentEncoding);
          $("runAllEncodingModes").addEventListener("click", runAllEncodingModes);
          $("resetEncoding").addEventListener("click", () => {
            state.encoded = [];
            state.encodingRuns = {};
            state.manualScorecards = {};
            state.manualIndex = 0;
            state.completed.delete("encoding");
            trace("reset", "Encoding reset", "Manual scorecards, AI runs, hybrid runs, and final encoded outputs were cleared.");
            toast("Encoding reset");
            render();
          });
        }
        if (id === "compartmental") $("runCompartmental").addEventListener("click", runCompartmental);
        if (id === "agents") $("runAgents").addEventListener("click", runAgents);
        if (id === "digital") $("runDigital").addEventListener("click", runDigital);
        if (id === "bayes") $("runBayes").addEventListener("click", runBayes);
        if (id === "rl") $("runRL").addEventListener("click", runRL);
        if (id === "regional") $("runRegional").addEventListener("click", runRegional);
        if (id === "graph") $("buildGraph").addEventListener("click", runKnowledgeGraph);
        if (id === "inoculation") {
          $("runInoculation").addEventListener("click", runInoculationLab);
          const applyButton = $("applyInoculationVaccine");
          if (applyButton) applyButton.addEventListener("click", applyInoculationVaccine);
        }
        if (id === "policy") {
          $("runPolicy").addEventListener("click", runPolicy);
          $("downloadPolicyHtml").addEventListener("click", () => {
            downloadText(`ndim-policy-brief-${Date.now()}.html`, policyHtmlDocument(false), "text/html");
            trace("policy", "Policy HTML downloaded", "Downloaded a human-readable policy brief. JSON remains available for audit only.");
            toast("HTML brief downloaded");
          });
          $("printPolicyPdf").addEventListener("click", openPrintablePolicy);
          $("copyPolicy").addEventListener("click", async () => {
            const copied = await copyText(JSON.stringify(policyJson(), null, 2), `ndim-policy-output-${Date.now()}.json`, "application/json");
            toast(copied ? "Policy JSON copied" : "Copy blocked; policy JSON downloaded");
          });
          $("downloadPolicyJson").addEventListener("click", () => {
            downloadText(`ndim-policy-output-${Date.now()}.json`, JSON.stringify(policyJson(), null, 2), "application/json");
            trace("policy", "Policy JSON downloaded", "Downloaded the ndim-policy-output-v1 audit payload.");
            toast("Policy JSON downloaded");
          });
          $("copyPolicyBrief").addEventListener("click", async () => {
            const copied = await copyText(policyMarkdown(), `ndim-policy-brief-${Date.now()}.md`, "text/markdown");
            toast(copied ? "Policy brief copied" : "Copy blocked; policy brief downloaded");
          });
        }
      }

      function modelParams(extra = {}) {
        const trustBase = avg(state.encoded.map((item) => item.trust_score), 0.6);
        const barrierBase = avg(state.encoded.map((item) => item.adoption_barrier_score), 0.35);
        const vaccineStrength = state.inoculationApplied ? (state.inoculation?.interventionStrength || 0) : 0;
        const trust = clamp01((state.bayes?.trustMean ?? (trustBase + (state.digital ? state.feedback.trustDelta : 0))) + vaccineStrength * 0.08, 0.6);
        const barrier = clamp01((state.bayes?.barrierMean ?? (barrierBase + (state.digital ? state.feedback.barrierDelta : 0))) - vaccineStrength * 0.07, 0.35);
        const confidence = avg(state.encoded.map((item) => item.confidence), 0.5);
        const rlBonus = state.rl?.interventionBonus || 0;
        return {
          trust_score: trust,
          barrier_score: barrier,
          narrative_influence: Math.min(0.9, 0.2 + 0.35 * confidence + vaccineStrength * 0.12),
          intervention_strength: Math.min(0.9, 0.1 + 0.2 * trust + rlBonus + vaccineStrength * 0.28),
          inoculation_strength: vaccineStrength,
          ...extra
        };
      }

      async function requireApprovedRecords() {
        if (!state.records.length && !await validateIntake()) return [];
        const approved = approvedRecords();
        if (!approved.length) {
          setStatus("error");
          toast("Commit accepted evidence first");
          trace("blocked", "Encoding blocked by governance gate", "No narrative will be sent to an encoder until the SDMX gate has at least one approved record committed into the accepted repository.");
          goStep(1);
          return [];
        }
        return approved;
      }

      async function runEncoding() {
        const approved = await requireApprovedRecords();
        if (!approved.length) return;
        if (state.encodingMode === "manual") {
          state.encoded = approved.map((record) => saveManualScorecard(record, true));
          state.encodingRuns.manual = state.encoded;
          state.completed.add("encoding");
          setStatus("complete");
          trace("manual", "Manual batch encoding complete", `${state.encoded.length} narrative scorecard(s) saved story by story. Each score keeps encoder, timestamp, Phi, and justifications.`);
          await evaluateEncodingCalibration();
          toast("Manual encoding complete");
          render();
          return;
        }
        setStatus("running");
        trace("api", "Calling encoder", `POST /encode?mode=${state.encodingMode}&provider=${state.llmProvider} with ${approved.length} approved record(s).`);
        try {
          const response = await fetch(`/encode?mode=${encodeURIComponent(state.encodingMode)}&provider=${encodeURIComponent(state.llmProvider)}`, {
            method: "POST",
            headers: llmRequestHeaders(),
            body: JSON.stringify(approved)
          });
          if (!response.ok) throw new Error(`Backend returned ${response.status}`);
          state.encoded = await response.json();
          state.encodingRuns[state.encodingMode] = state.encoded;
          state.completed.add("encoding");
          setStatus("complete");
          trace("result", "Encoding complete", `Returned ${state.encoded.length} encoded narrative(s).`);
          await evaluateEncodingCalibration();
          toast("Encoding complete");
          render();
        } catch (error) {
          setStatus("error");
          trace("error", "Encoding failed", error.message || "Unknown error");
        }
      }

      async function runCurrentEncoding() {
        const approved = await requireApprovedRecords();
        if (!approved.length) return;
        const record = approved[Math.min(state.manualIndex, approved.length - 1)];
        if (!record) return;
        if (state.encodingMode === "manual") {
          const encoded = saveManualScorecard(record, true);
          state.completed.add("encoding");
          state.manualIndex = nextUnencodedIndex(approved, state.manualIndex + 1);
          setStatus("complete");
          trace("manual", "Manual story encoded", `${encoded.narrative_id} saved with Phi ${encoded.manual_scorecard.phi.toFixed(4)}. Moved to the next unreviewed story.`);
          await evaluateEncodingCalibration();
          toast("Manual score saved");
          render();
          return;
        }
        setStatus("running");
        trace("api", "Encoding one story", `Encoding approved story ${Math.min(state.manualIndex + 1, approved.length)} of ${approved.length} with ${state.encodingMode}.`);
        try {
          const response = await fetch(`/encode?mode=${encodeURIComponent(state.encodingMode)}&provider=${encodeURIComponent(state.llmProvider)}`, {
            method: "POST",
            headers: llmRequestHeaders(),
            body: JSON.stringify([record])
          });
          if (!response.ok) throw new Error(`Backend returned ${response.status}`);
          const [encoded] = await response.json();
          upsertEncoded(state.encodingMode, encoded);
          state.completed.add("encoding");
          state.manualIndex = nextUnencodedIndex(approved, state.manualIndex + 1);
          setStatus("complete");
          trace("result", "Story encoded", `${encoded.narrative_id} encoded. Moved to next story for manual review.`);
          await evaluateEncodingCalibration();
          toast("Story encoded");
          render();
        } catch (error) {
          setStatus("error");
          trace("error", "Story encoding failed", error.message || "Unknown error");
        }
      }

      async function runAllEncodingModes() {
        const approved = await requireApprovedRecords();
        if (!approved.length) return;
        const originalMode = state.encodingMode;
        for (const mode of ["manual", "ai", "hybrid"]) {
          state.encodingMode = mode;
          if (mode === "manual") {
            state.encodingRuns.manual = approved.map((record) => saveManualScorecard(record, true));
            trace("manual", "Comparing manual scorecards", `Prepared ${state.encodingRuns.manual.length} researcher scorecard(s) for comparison.`);
            continue;
          }
          setStatus("running");
          trace("api", "Comparing encoder", `Running ${mode} encoder for ${approved.length} approved narrative(s).`);
          const response = await fetch(`/encode?mode=${encodeURIComponent(mode)}&provider=${encodeURIComponent(state.llmProvider)}`, {
            method: "POST",
            headers: llmRequestHeaders(),
            body: JSON.stringify(approved)
          });
          if (!response.ok) {
            setStatus("error");
            trace("error", "Encoder comparison failed", `${mode} returned ${response.status}.`);
            state.encodingMode = originalMode;
            render();
            return;
          }
          state.encodingRuns[mode] = await response.json();
        }
        state.encodingMode = originalMode;
        state.encoded = state.encodingRuns[originalMode] || state.encodingRuns.hybrid || [];
        state.completed.add("encoding");
        setStatus("complete");
        trace("result", "Encoding comparison complete", "Manual, AI, and hybrid runs are now visible as comparison blocks.");
        await evaluateEncodingCalibration();
        toast("All modes compared");
        render();
      }

      async function runCompartmental() {
        if (!state.encoded.length) {
          toast("Run encoding first");
          trace("blocked", "Encoding required", "Compartmental model needs trust, barrier, confidence, and narrative influence inputs.");
          return;
        }
        setStatus("running");
        trace("api", "Calling compartmental model", "POST /simulate with model_mode=compartmental.");
        try {
          const response = await fetch("/simulate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ model_mode: "compartmental", country: state.meta.country, admin_unit: state.meta.district, horizon_days: 180, parameters: modelParams() })
          });
          if (!response.ok) throw new Error(`Backend returned ${response.status}`);
          state.comp = await response.json();
          state.completed.add("compartmental");
          setStatus("complete");
          trace("model", "Compartmental model complete", `Final adoption ${fmtPct(state.comp.trajectory.at(-1).adoption)}.`);
          toast("Compartmental model complete");
          render();
        } catch (error) {
          setStatus("error");
          trace("error", "Compartmental model failed", error.message || "Unknown error");
        }
      }

      async function runAgents() {
        if (!state.encoded.length) {
          toast("Run encoding first");
          trace("blocked", "Encoding required", "Agent model needs encoded trust and barrier inputs.");
          return;
        }
        const peer = Number($("peerEffect")?.value || 0.08);
        const media = Number($("mediaEffect")?.value || 0.05);
        setStatus("running");
        trace("api", "Calling agent model", `POST /simulate with model_mode=agent_based, peer=${peer}, media=${media}.`);
        try {
          const response = await fetch("/simulate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ model_mode: "agent_based", country: state.meta.country, admin_unit: state.meta.district, horizon_days: 180, parameters: modelParams({ peer_effect: peer, media_effect: media }) })
          });
          if (!response.ok) throw new Error(`Backend returned ${response.status}`);
          state.agents = await response.json();
          state.completed.add("agents");
          setStatus("complete");
          trace("model", "Agent model complete", `Final adoption ${fmtPct(state.agents.trajectory.at(-1).adoption)}.`);
          toast("Agent model complete");
          render();
        } catch (error) {
          setStatus("error");
          trace("error", "Agent model failed", error.message || "Unknown error");
        }
      }

      async function runDigital() {
        state.feedback.observedAdoption = Number($("observedAdoption")?.value || state.feedback.observedAdoption);
        state.feedback.trustDelta = Number($("trustDelta")?.value || 0);
        state.feedback.barrierDelta = Number($("barrierDelta")?.value || 0);
        state.feedback.note = $("feedbackNote")?.value || "";
        setStatus("running");
        trace("feedback", "Applying digital twin feedback", `Observed adoption ${fmtPct(state.feedback.observedAdoption)}, trust shift ${state.feedback.trustDelta}, barrier shift ${state.feedback.barrierDelta}.`);
        try {
          const response = await fetch("/simulate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ model_mode: "hybrid", country: state.meta.country, admin_unit: state.meta.district, horizon_days: 180, parameters: modelParams({ initial_adoption: state.feedback.observedAdoption }) })
          });
          if (!response.ok) throw new Error(`Backend returned ${response.status}`);
          state.digital = await response.json();
          state.completed.add("digital");
          setStatus("complete");
          trace("model", "Digital twin updated", "Feedback-adjusted hybrid simulation is now available and will inform Bayesian/RL stages.");
          toast("Digital twin updated");
          render();
        } catch (error) {
          setStatus("error");
          trace("error", "Digital twin failed", error.message || "Unknown error");
        }
      }

      async function runBayes() {
        ["trustA", "trustB", "barrierA", "barrierB"].forEach((key) => {
          state.priors[key] = Number($(key)?.value || state.priors[key]);
        });
        setStatus("running");
        const trials = Math.max(10, state.records.length * 12);
        const trustObserved = Math.max(0, Math.min(1, avg(state.encoded.map((item) => item.trust_score), 0.6) + (state.feedback.trustDelta || 0)));
        const barrierObserved = Math.max(0, Math.min(1, avg(state.encoded.map((item) => item.adoption_barrier_score), 0.35) + (state.feedback.barrierDelta || 0)));
        const trustSuccess = Math.round(trustObserved * trials);
        const barrierSuccess = Math.round(barrierObserved * trials);
        const trustAlpha = state.priors.trustA + trustSuccess;
        const trustBeta = state.priors.trustB + trials - trustSuccess;
        const barrierAlpha = state.priors.barrierA + barrierSuccess;
        const barrierBeta = state.priors.barrierB + trials - barrierSuccess;
        state.bayes = {
          trials,
          trustAlpha,
          trustBeta,
          barrierAlpha,
          barrierBeta,
          trustMean: trustAlpha / (trustAlpha + trustBeta),
          barrierMean: barrierAlpha / (barrierAlpha + barrierBeta)
        };
        try {
          await refreshAnalyticsStatus();
          const source = (state.digital || state.comp || state.agents)?.trajectory || [];
          const stride = Math.max(1, Math.floor(source.length / 30));
          const observed = source.length
            ? source.filter((_, index) => index % stride === 0 || index === source.length - 1).map((point) => Number(point.adoption || 0))
            : [0.10, trustObserved * 0.35, Math.max(0.12, trustObserved - barrierObserved * 0.25)];
          const backend = await apiJson("/analytics/bayesian", {
            method: "POST",
            body: JSON.stringify(observed)
          });
          const mean = backend?.trajectory?.mean || [];
          const lower = backend?.trajectory?.lower_90 || [];
          const upper = backend?.trajectory?.upper_90 || [];
          state.bayes.backend = backend;
          state.bayes.backendAvailable = Boolean(state.analyticsStatus?.available);
          state.bayes.fallback = Boolean(backend?.diagnostics?.fallback);
          state.bayes.backendWarning = backend?.diagnostics?.warning || "";
          state.bayes.adoptionInterval = {
            mean: mean.length ? mean.at(-1) : null,
            lower: lower.length ? lower.at(-1) : null,
            upper: upper.length ? upper.at(-1) : null
          };
          state.bayes.ndimParameters = backend?.parameters || null;
        } catch (error) {
          state.bayes.backendAvailable = false;
          state.bayes.fallback = true;
          state.bayes.backendWarning = error.message || "Backend Bayesian update unavailable; local Beta update only.";
        }
        state.completed.add("bayes");
        setStatus("complete");
        trace("bayes", "Posterior updated", `Trust posterior ${fmtPct(state.bayes.trustMean)}, barrier posterior ${fmtPct(state.bayes.barrierMean)}. ${state.bayes.backendWarning || finalUncertaintySummary()}`);
        toast("Posterior updated");
        render();
      }

      async function runRL() {
        const episodes = Number($("episodes")?.value || 120);
        const alpha = Number($("learningRate")?.value || 0.18);
        const gamma = Number($("discount")?.value || 0.88);
        const epsilon = Number($("epsilon")?.value || 0.16);
        const actions = [
          { name: "health-worker outreach", lift: 0.12, cost: 0.04, barrier: -0.04 },
          { name: "peer demonstration", lift: 0.10, cost: 0.03, barrier: -0.02 },
          { name: "radio correction", lift: 0.06, cost: 0.02, barrier: -0.01 },
          { name: "subsidy plus trust", lift: 0.15, cost: 0.08, barrier: -0.07 }
        ];
        const trust = state.bayes?.trustMean ?? avg(state.encoded.map((item) => item.trust_score), 0.6);
        const barrier = state.bayes?.barrierMean ?? avg(state.encoded.map((item) => item.adoption_barrier_score), 0.35);
        const runLocalRl = (note = "Local browser Q-learning fallback used.") => {
          const expected = Object.fromEntries(actions.map((action) => [
            action.name,
            action.lift + trust * 0.35 - Math.max(0, barrier + action.barrier) * 0.22 - action.cost
          ]));
          const q = Object.fromEntries(actions.map((action) => [action.name, expected[action.name] * 0.25]));
          const history = [];
          for (let episode = 1; episode <= episodes; episode += 1) {
            const explore = Math.random() < epsilon;
            const action = explore
              ? actions[Math.floor(Math.random() * actions.length)]
              : actions.slice().sort((a, b) => q[b.name] - q[a.name])[0];
            const reward = expected[action.name];
            const nextBest = Math.max(...Object.values(q));
            q[action.name] = q[action.name] + alpha * (reward + gamma * nextBest - q[action.name]);
            if (episode % Math.max(1, Math.floor(episodes / 24)) === 0 || episode === episodes) {
              history.push({ episode, action: action.name, reward });
            }
          }
          Object.keys(q).forEach((key) => { q[key] = (q[key] + expected[key]) / 2; });
          const bestAction = Object.entries(expected).sort((a, b) => b[1] - a[1])[0];
          const bestSpec = actions.find((action) => action.name === bestAction[0]);
          return {
            episodes,
            bestAction: bestAction[0],
            bestReward: bestAction[1],
            q,
            history,
            interventionBonus: Math.max(0, bestSpec?.lift || 0) * 0.35,
            fallback: true,
            note
          };
        };
        setStatus("running");
        try {
          await refreshAnalyticsStatus();
          const backend = await apiJson("/analytics/rl", {
            method: "POST",
            body: JSON.stringify({
              episodes,
              alpha,
              gamma,
              epsilon,
              trust_score: trust,
              barrier_score: barrier,
              confidence: avg(state.encoded.map((item) => item.confidence), 0.5),
              ...modelParams()
            })
          });
          const q = backend?.policy?.q_values || backend?.q || {};
          const bestEntry = Object.entries(q).sort((a, b) => Number(b[1]) - Number(a[1]))[0] || [backend?.policy?.best_action || "not selected", 0];
          const bestAction = backend?.policy?.best_action || bestEntry[0];
          state.rl = {
            episodes,
            bestAction,
            bestReward: Number(q[bestAction] ?? bestEntry[1] ?? 0),
            q,
            history: backend?.history || [],
            interventionBonus: Math.max(0, Number(q[bestAction] ?? 0)) * 0.025,
            backend,
            fallback: Boolean(backend?.fallback),
            note: backend?.note || (state.analyticsStatus?.available ? "Advanced analytics optimizer returned a policy." : "Deterministic fallback optimizer returned a policy.")
          };
        } catch (error) {
          state.rl = runLocalRl(error.message || "Backend RL unavailable; local browser fallback used.");
        }
        state.completed.add("rl");
        setStatus("complete");
        trace("rl", "RL loop complete", `${episodes} episodes selected "${state.rl.bestAction}" as the best intervention.`);
        toast("RL loop complete");
        render();
      }

      function runRegional() {
        if (!state.encoded.length) {
          toast("Run encoding first");
          trace("blocked", "Encoding required", "Regional analysis needs encoded trust, barrier, confidence, and themes.");
          return;
        }
        const mode = $("regionalMode")?.value || "isolated";
        const target = $("regionalTarget")?.value || "barrier";
        const rows = computeRegionalRows();
        const grouped = {
          region: "Grouped evidence",
          count: rows.reduce((sum, row) => sum + row.count, 0),
          trust: avg(rows.map((row) => row.trust), 0.6),
          barrier: avg(rows.map((row) => row.barrier), 0.35),
          confidence: avg(rows.map((row) => row.confidence), 0.5),
          themes: topItems(rows.flatMap((row) => row.themes), 5),
          stories: rows.flatMap((row) => row.stories)
        };
        state.regional = { mode, target, rows: mode === "grouped" ? [grouped] : rows };
        state.completed.add("regional");
        trace("analysis", "Regional analysis complete", `${state.regional.rows.length} analysis unit(s) prepared using ${mode} mode.`);
        toast("Regional analysis complete");
        render();
      }

      function runKnowledgeGraph() {
        if (!state.encoded.length) {
          toast("Run encoding first");
          trace("blocked", "Encoding required", "The graph needs encoded themes and story metadata.");
          return;
        }
        state.graph = buildKnowledgeGraph();
        state.completed.add("graph");
        trace("graph", "Knowledge graph built", `${state.graph.nodes.length} nodes and ${state.graph.edges.length} edges connect locations, themes, trust, and barriers.`);
        toast("Knowledge graph built");
        render();
      }

      function runInoculationLab() {
        if (!state.encoded.length) {
          toast("Run encoding first");
          trace("blocked", "Encoding required", "Inoculation narratives need themes, trust, and barrier signals from encoding.");
          return;
        }
        const audience = $("inoculationAudience")?.value || "households";
        const tone = $("inoculationTone")?.value || "clear";
        const signal = dominantBarrier();
        const region = signal.region.split(" / ").slice(-1)[0];
        const themes = signal.themes.length ? signal.themes.join(", ") : "cost, trust, fuel access";
        const messenger = audience === "health_workers" ? "a local health worker" : audience === "community_leaders" ? "a community leader" : audience === "policy_makers" ? "a district policy team" : "a neighbour who has already tried the stove";
        const interventionStrength = estimateInoculationStrength();
        state.inoculation = {
          audience,
          tone,
          provider: state.llmProvider,
          interventionStrength,
          items: [
            {
              type: "pre-bunk",
              audience,
              title: `Before the rumour spreads in ${region}`,
              text: `Some messages will claim clean cooking is only for wealthy families or that fuel cannot be found. Before accepting that claim, ask who benefits from the doubt and compare it with local households already cooking with less smoke. ${messenger} can show the real costs, fuel options, and health evidence.`,
              components: ["warning", "weakened claim", "trusted messenger", themes]
            },
            {
              type: "refutation",
              audience,
              title: "Cost concern with practical correction",
              text: `It is reasonable to worry about first purchase cost. The misleading version says cost makes adoption impossible. The evidence-based correction is to pair demonstrations with financing, maintenance guidance, and peer comparison of charcoal, fuel, and time costs.`,
              components: ["refutation", "efficacy", "barrier reduction", `provider: ${state.llmProvider}`]
            },
            {
              type: "counter-feed",
              audience,
              title: "Short social counter-message",
              text: `Do not decide from a rumour alone. Visit a local demonstration, ask about fuel and repair support, and compare smoke exposure in a real kitchen. Clean cooking is a health and household-budget decision, not a status symbol.`,
              components: ["short feed", "call to action", "social proof", tone]
            }
          ],
          vaccine: buildInoculationVaccine(interventionStrength)
        };
        state.inoculationApplied = false;
        state.completed.add("inoculation");
        trace("inoculation", "Counter-narratives generated", `Generated ${state.inoculation.items.length} inoculation drafts using ${state.llmProvider} as the selected provider path. Estimated narrative vaccine strength ${fmtPct(interventionStrength)}.`);
        toast("Inoculation narratives ready");
        render();
      }

      function applyInoculationVaccine() {
        if (!state.inoculation?.items?.length) {
          toast("Generate inoculation narratives first");
          trace("blocked", "No inoculation vaccine available", "Run the inoculation lab before applying the narrative vaccine to the digital twin.");
          return;
        }
        const strength = state.inoculation.interventionStrength || estimateInoculationStrength();
        const vaccine = buildInoculationVaccine(strength);
        if (!vaccine.compartmental && !vaccine.agent_based) {
          toast("Run ODE or agent model first");
          trace("blocked", "Baseline model required", "Run the compartmental and agent-based models before applying the narrative vaccine.");
          return;
        }
        state.inoculation.vaccine = vaccine;
        state.inoculationApplied = true;
        state.feedback.trustDelta = Math.min(1, (state.feedback.trustDelta || 0) + strength * 0.08);
        state.feedback.barrierDelta = Math.max(-1, (state.feedback.barrierDelta || 0) - strength * 0.07);
        const digitalTrajectory = vaccine.compartmental?.after || vaccine.agent_based?.after;
        if (digitalTrajectory?.length) {
          state.digital = {
            model_mode: "hybrid_inoculation_vaccine",
            country: state.meta.country,
            admin_unit: state.meta.district,
            parameters: modelParams({ inoculation_strength: strength }),
            trajectory: digitalTrajectory
          };
          state.completed.add("digital");
        }
        trace("inoculation", "Narrative vaccine applied", `Digital twin now includes inoculation strength ${fmtPct(strength)}. Trust shift and barrier shift were updated for downstream Bayesian/RL/policy stages.`);
        toast("Narrative vaccine applied");
        render();
      }

      async function runPolicy() {
        const approved = await requireApprovedRecords();
        if (!approved.length) return;
        if (!state.encoded.length) await runEncoding();
        setStatus("running");
        trace("api", "Calling full policy pipeline", `POST /pipeline/run?mode=${state.encodingMode}.`);
        try {
          const response = await fetch(`/pipeline/run?mode=${encodeURIComponent(state.encodingMode)}&provider=${encodeURIComponent(state.llmProvider)}`, {
            method: "POST",
            headers: llmRequestHeaders(),
            body: JSON.stringify(approved)
          });
          if (!response.ok) throw new Error(`Backend returned ${response.status}`);
          state.policy = await response.json();
          const refined = modelParams();
          state.policy.summary.average_trust = refined.trust_score;
          state.policy.summary.average_barrier = refined.barrier_score;
          if (state.digital?.trajectory?.length) {
            state.policy.summary.final_adoption = state.digital.trajectory.at(-1).adoption;
          }
          state.encoded = state.policy.encoded || state.encoded;
          state.completed.add("policy");
          await appendLedger("policy_output", "Policy JSON generated from approved evidence and current model outputs", state.governance.lastDigest);
          await syncLedgerToBackend("policy output generated");
          setStatus("complete");
          trace("policy", "Policy output prepared", "Recommendation draft, model summary, and evidence trail are ready for human review.");
          toast("Policy output ready");
          render();
        } catch (error) {
          setStatus("error");
          trace("error", "Policy pipeline failed", error.message || "Unknown error");
        }
      }

      async function runCurrentStageShortcut() {
        const id = currentStep().id;
        trace("action", "Run current stage requested", `User triggered the primary action for ${currentStep().title}.`);
        if (id === "intake" || id === "gate") {
          if (await validateIntake()) {
            trace("gate", "Evidence contract refreshed", "Narrative observations and metadata were rebuilt from the current form state.");
            render();
          }
          return;
        }
        const runners = {
          encoding: runEncoding,
          compartmental: runCompartmental,
          agents: runAgents,
          digital: runDigital,
          bayes: runBayes,
          rl: runRL,
          regional: runRegional,
          graph: runKnowledgeGraph,
          inoculation: runInoculationLab,
          policy: runPolicy
        };
        const runner = runners[id];
        if (!runner) return;
        await runner();
      }

      $("backButton").addEventListener("click", () => goStep(state.step - 1));
      $("nextButton").addEventListener("click", nextStep);
      $("resetStageButton").addEventListener("click", resetCurrentStage);
      if ($("quickRunButton")) $("quickRunButton").addEventListener("click", runCurrentStageShortcut);
      if ($("toggleTraceButton")) $("toggleTraceButton").addEventListener("click", () => {
        document.querySelector(".reasoning").classList.toggle("open");
      });
      $("closeTraceButton").addEventListener("click", () => {
        document.querySelector(".reasoning").classList.remove("open");
      });
      $("clearTrace").addEventListener("click", () => {
        state.trace = [["idle", "Log cleared", "The workflow state is unchanged; only the visible reasoning log was cleared."]];
        renderTrace();
      });
      document.querySelectorAll("#themeToggle button").forEach((button) => {
        button.addEventListener("click", () => {
          document.querySelectorAll("#themeToggle button").forEach((item) => item.classList.remove("active"));
          button.classList.add("active");
          document.documentElement.dataset.theme = button.dataset.theme;
        });
      });
      window.addEventListener("resize", syncWorkflowStagesOffset);

      renderTrace();
      render();
      Promise.all([refreshAnalyticsStatus(), refreshValidationStatus()]).then(() => {
        trace("system", "Scientific services checked", `${analyticsSummary()} ${calibrationSummary()}`);
        render();
      });
    </script>
  </body>
</html>
"""

MANUAL_HTML = r"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>NDIM Engine Manual</title>
    <style>
      body { margin: 0; background: #f7f9fc; color: #0f172a; font-family: "Myriad Pro", "Segoe UI", Arial, sans-serif; line-height: 1.65; }
      main { max-width: 960px; margin: 0 auto; padding: 36px 20px 64px; }
      h1 { font-size: 42px; line-height: 1.05; margin: 0 0 10px; }
      h2 { margin-top: 34px; border-top: 1px solid #d8dee9; padding-top: 24px; }
      h3 { margin-bottom: 4px; }
      p, li { font-size: 16px; color: #334155; }
      code, pre { font-family: "Cascadia Mono", Consolas, monospace; }
      pre { background: #0f172a; color: #e2e8f0; padding: 14px; border-radius: 12px; overflow-x: auto; }
      .card { border: 1px solid #d8dee9; border-radius: 14px; background: white; padding: 16px; margin: 12px 0; }
      .grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }
      @media (max-width: 760px) { .grid { grid-template-columns: 1fr; } }
    </style>
  </head>
  <body>
    <main>
      <h1>NDIM Engine Workflow Manual</h1>
      <p><a href="/">Back to tool</a></p>
      <p>This manual explains how to run the Narrative Diffusion and Inoculation Model workflow from evidence ingestion to policy output.</p>

      <h2>1. Narrative intake</h2>
      <p>Select country, province, district, source type, source name, period, and language. Paste narratives or upload TXT/MD/CSV. CSV files should contain a <code>narrative</code>, <code>text</code>, <code>quote</code>, <code>story</code>, or <code>content</code> column.</p>
      <pre>country,district,narrative
Rwanda,Musanze,"Health workers are trusted, but stove cost remains high."</pre>

      <h2>2. SDMX gate</h2>
      <p>The gate checks whether each narrative has enough context to become a traceable observation. The payload is shown in plain language so non-technical users can understand what is being passed to the model.</p>

      <h2>3. Encoding</h2>
      <div class="grid">
        <div class="card"><h3>Manual / rule-based</h3><p>Transparent fallback scoring. Useful for audits and offline review.</p></div>
        <div class="card"><h3>AI encoder</h3><p>Uses the configured LLM provider when keys are available. Otherwise it falls back safely.</p></div>
        <div class="card"><h3>Hybrid review</h3><p>Combines AI/fallback scoring with a human-review flag before modelling.</p></div>
        <div class="card"><h3>Story-by-story</h3><p>Use “Encode current story” to inspect one imported narrative at a time. Use “Compare all modes” to batch-run every encoding mode.</p></div>
      </div>
      <p>Manual Phi is computed as:</p>
      <pre>Phi = 0.30E + 0.30C + 0.20tau + 0.20kappa</pre>

      <h2>4. Compartmental model</h2>
      <p>The population model tracks movement through susceptible, misinformed, truth-aligned, inoculated, and resistant compartments.</p>
      <pre>dS/dt = - beta_m S M - beta_t S T - iota S
dT/dt = beta_t S T + rho M - mu T
dR/dt = gamma I + eta T</pre>

      <h2>5. Agent-based model</h2>
      <p>The agent model tests household heterogeneity: peer effects, media exposure, local trust, and barriers. It helps detect local dynamics hidden by aggregate curves.</p>

      <h2>6. Digital twin feedback</h2>
      <p>Enter observed adoption and field feedback. The digital twin reruns the model with feedback-adjusted parameters.</p>
      <pre>theta_next = theta_model + lambda(field_observed - model_predicted)</pre>

      <h2>7. Bayesian update</h2>
      <p>Priors express what the model believed before feedback. Posterior values update trust and barrier assumptions after observations.</p>
      <pre>prior = Beta(alpha, beta)
posterior = Beta(alpha + successes, beta + failures)</pre>

      <h2>8. RL optimizer</h2>
      <p>The RL loop compares intervention actions and learns which policy package maximizes adoption while penalizing cost and barrier risk.</p>
      <pre>Q(s,a) <- Q(s,a) + alpha [reward + gamma max Q(s',a') - Q(s,a)]</pre>

      <h2>9. Policy output</h2>
      <p>The output is a reviewable recommendation with metadata, encoding mode, model summaries, posterior values, RL policy, and evidence trail. It is not an automatic decision; it should be reviewed by analysts and policy makers.</p>
    </main>
  </body>
</html>
"""

MANUAL_HTML = r"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>NDIM Engine Manual</title>
    <style>
      body { margin: 0; background: #f7f9fc; color: #0f172a; font-family: "Myriad Pro", "Segoe UI", Arial, sans-serif; line-height: 1.65; }
      main { max-width: 1040px; margin: 0 auto; padding: 38px 20px 70px; }
      h1 { font-size: clamp(34px, 5vw, 52px); line-height: 1.04; margin: 0 0 10px; }
      h2 { margin-top: 36px; border-top: 1px solid #d8dee9; padding-top: 24px; }
      h3 { margin: 18px 0 4px; }
      p, li { font-size: 16px; color: #334155; }
      code, pre { font-family: "Cascadia Mono", Consolas, monospace; }
      pre { background: #0f172a; color: #e2e8f0; padding: 14px; border-radius: 12px; overflow-x: auto; }
      table { width: 100%; border-collapse: collapse; margin: 12px 0; background: white; }
      th, td { border: 1px solid #d8dee9; padding: 10px; text-align: left; vertical-align: top; }
      th { background: #eef2f7; color: #0f172a; }
      .card { border: 1px solid #d8dee9; border-radius: 14px; background: white; padding: 16px; margin: 12px 0; }
      .grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }
      .callout { border-left: 4px solid #2459d6; background: white; border-radius: 12px; padding: 14px 16px; margin: 14px 0; }
      .small { color: #64748b; font-size: 14px; }
      @media (max-width: 760px) { .grid { grid-template-columns: 1fr; } }
    </style>
  </head>
  <body>
    <main>
      <h1>NDIM Engine Manual</h1>
      <p><a href="/">Back to tool</a></p>
      <p><strong>NDIM</strong> means <strong>Narrative Diffusion and Inoculation Model</strong>. The engine turns field narratives into traceable model inputs, runs population and household simulations, updates beliefs with evidence, and produces a policy recommendation with an audit trail.</p>
      <div class="callout"><p><strong>Simple reading:</strong> the tool asks, "What are people saying, how should we encode it, how does that narrative change adoption dynamics, what did the field data correct, and which policy action is most robust?"</p></div>

      <h2>Using the Evidence-to-Policy Workbench</h2>
      <p>The opening screen is a workbench, not a separate demo area. Use the compact workflow buttons to move between Evidence, Encode, Model, Learn, Synthesize, and Export. The workbench cards show evidence count, approved records, model signal, current stage, next action, and the narrative repository ledger.</p>
      <table>
        <thead><tr><th>Workbench element</th><th>What it does</th><th>How to use it</th></tr></thead>
        <tbody>
          <tr><td>Narrative repository ledger</td><td>Lists staged narrative records with route, place, status, and evidence seal.</td><td>Click a narrative ID to inspect that record in the governance/encoding flow.</td></tr>
          <tr><td>SDMX readiness panel</td><td>Checks whether route, place, source, period, and evidence body are ready.</td><td>Fix missing items before clicking Stage and validate.</td></tr>
          <tr><td>Activity log</td><td>Shows the reasoning trace and system actions in a drawer.</td><td>Open it only when auditing the workflow; keep it closed while working.</td></tr>
          <tr><td>Run current stage</td><td>Runs the main action for the active stage.</td><td>Use it as a shortcut after the required inputs are present.</td></tr>
        </tbody>
      </table>

      <h2>Workflow overview</h2>
      <table>
        <thead><tr><th>Stage</th><th>Purpose</th><th>Main output</th></tr></thead>
        <tbody>
          <tr><td>01 Narrative intake</td><td>Load text, CSV, notes, or SDMX-like evidence with country and location context.</td><td>Batch of narrative observations.</td></tr>
          <tr><td>02 SDMX gate</td><td>Check whether each observation has source, place, period, language, and measure fields.</td><td>Validated observation payload.</td></tr>
          <tr><td>03 Encoding</td><td>Score narratives using manual, AI, or hybrid review.</td><td>Trust, barrier, confidence, themes, and Phi inputs.</td></tr>
          <tr><td>04 Compartmental model</td><td>Estimate population-level adoption flow.</td><td>Adoption trajectory over time.</td></tr>
          <tr><td>05 Agent-based model</td><td>Test household heterogeneity and peer effects.</td><td>Local adoption trajectory and ODE/ABM contrast.</td></tr>
          <tr><td>06 Digital twin</td><td>Feed field observations back into the model.</td><td>Feedback-adjusted simulation curve.</td></tr>
          <tr><td>07 Bayesian update</td><td>Update trust and barrier assumptions from prior to posterior.</td><td>Posterior trust and barrier distributions.</td></tr>
          <tr><td>08 RL optimizer</td><td>Compare intervention policies by reward.</td><td>Best action, reward curve, and Q values.</td></tr>
          <tr><td>09 Regional analysis</td><td>Analyse regions alone or as grouped evidence.</td><td>Place-based intervention implications.</td></tr>
          <tr><td>10 Knowledge graph</td><td>Connect stories, places, themes, trust, barriers, and interventions.</td><td>Graph of repeated narrative structures.</td></tr>
          <tr><td>11 Inoculation lab</td><td>Generate pre-bunking and refutation narratives from encoded risks.</td><td>Reviewable counter-narrative drafts.</td></tr>
          <tr><td>12 Policy output</td><td>Create a reviewable decision brief.</td><td>Recommendation, JSON audit payload, Markdown brief, and evidence trail.</td></tr>
        </tbody>
      </table>

      <h2>1. Narrative intake</h2>
      <p>NDIM supports a <strong>Narrative Commons</strong> intake model. Structured interviews are one route, but users can also ingest open stories, indigenous knowledge records, citizen-science reports, crowdsourced batches, and experimental social/community feeds.</p>
      <table>
        <thead><tr><th>Route</th><th>Use when</th><th>Extra governance fields</th></tr></thead>
        <tbody>
          <tr><td>Structured interview</td><td>Enumerators collect Q1-Q5 clean-cooking stories.</td><td>Interview ID, respondent profile, decision-maker, current cooking methods.</td></tr>
          <tr><td>Open story</td><td>A community account or oral history does not fit the Q1-Q5 protocol.</td><td>Attribution, interpretation notes, source, location, consent.</td></tr>
          <tr><td>Indigenous knowledge</td><td>Evidence comes from local practice, elder testimony, seasonal memory, or cultural explanation.</td><td>Knowledge type, knowledge holder, sensitivity, community validation, attribution.</td></tr>
          <tr><td>Citizen science</td><td>Community members submit observations for review.</td><td>Contributor type, observation date, contributor confidence, validation status.</td></tr>
          <tr><td>Crowdsourced batch</td><td>Many stories arrive through CSV or shared forms.</td><td>Batch validation, duplicate checks, moderation status, consent tier.</td></tr>
          <tr><td>Social Media Feeds</td><td>X/Twitter, Facebook, LinkedIn, WhatsApp, YouTube, TikTok, Instagram, radio transcripts, community forums, or news comments are being explored.</td><td>Selected with platform checkboxes; treated as experimental evidence until validated and approved.</td></tr>
        </tbody>
      </table>
      <p>Select country, province or region, district, source type, source name, period, language, evidence route, consent, and community validation fields. Paste multi-paragraph narratives or upload TXT, MD, CSV, JSON, XML, or SDMX files. CSV files should contain a <code>narrative</code>, <code>text</code>, <code>quote</code>, <code>story</code>, or <code>content</code> column, and may also include <code>evidence_mode</code>, <code>knowledge_type</code>, <code>community_validation</code>, and <code>sensitivity</code>.</p>
      <pre>evidence_mode,country,district,period,source_name,knowledge_type,community_validation,narrative
indigenous_knowledge,Rwanda,Musanze,2026,community-consultation,cooking_practice,community_validated,"Health workers are trusted, but stove cost remains high."</pre>
      <p>For batch imports, use <strong>Encode current story</strong> to review one narrative at a time, or <strong>Run selected encoder</strong> to encode the entire batch.</p>

      <h2>2. SDMX gate</h2>
      <p>The SDMX gate treats every narrative as an observation with dimensions, attributes, and measures. This keeps qualitative evidence from entering the scientific model without provenance.</p>
      <pre>Observation_i = {
  dimensions: { country, admin_unit, period, language },
  attributes: { source_type, source_name, evidence_mode, consent, sensitivity, provenance },
  measure: { narrative_text },
  tags: [encoding_mode, source_type, evidence_mode, knowledge_type]
}</pre>
      <p>The gate passes when required fields are present. It does not claim the narrative is true; it only confirms that the evidence is traceable.</p>
      <h3>Evidence governance at the gate</h3>
      <p>The current implementation adds a tamper-evident review layer before encoding. Each observation receives a SHA-256 evidence hash, a content hash, an automated risk scan, a visibility tier, a consent tier, and a reviewer decision. Encoding is blocked until at least one record is approved.</p>
      <pre>evidence_hash_i = SHA256(canonical_json(narrative_i, metadata_i, tags_i))
review_signature_i = SHA256(reviewer | role | status | time | evidence_hash_i)
ledger_event_hash_t = SHA256(event_t + previous_event_hash)</pre>
      <p><strong>Interpretation:</strong> hashes and chained ledger events prove whether a record changed after review. They do not prove that the story is factually true. Truth still depends on consent, field validation, duplicate checks, triangulation, and human approval.</p>

      <h3>Narrative repository and evidence ledger</h3>
      <p>The narrative database should be read as one core table plus mode-specific extensions. This is how structured interviews, indigenous knowledge, citizen science, and crowdsourced batches stay coherent without forcing every record into the same form.</p>
      <table>
        <thead><tr><th>Repository layer</th><th>Example fields</th><th>Purpose</th></tr></thead>
        <tbody>
          <tr><td>Core narrative_observations</td><td>narrative_id, evidence_mode, country, admin_unit, period, language, text</td><td>Lets every story be searched, encoded, modelled, and governed together.</td></tr>
          <tr><td>Provenance attributes</td><td>source_type, source_name, contributor_type, consent_tier, visibility, validation_status</td><td>Explains where the evidence came from and who can use it.</td></tr>
          <tr><td>Structured interview extension</td><td>interview_id, respondent_profile, q1-q5, cooking_methods</td><td>Preserves comparable field interviews.</td></tr>
          <tr><td>Indigenous knowledge extension</td><td>knowledge_type, knowledge_holder, sensitivity, community_validation, attribution, translation_notes</td><td>Protects situated knowledge and community governance.</td></tr>
          <tr><td>Citizen science extension</td><td>observation_date, contributor_confidence, location_precision, moderator_status</td><td>Supports public observation and validation workflows.</td></tr>
          <tr><td>Governance ledger</td><td>content_hash, evidence_hash, scan, approval_status, reviewer_signature</td><td>Creates tamper-evident review history.</td></tr>
        </tbody>
      </table>
      <p>SDMX makes this coherent by treating country, location, time, language, and evidence mode as shared <strong>dimensions</strong>; source, consent, validation, and sensitivity as <strong>attributes</strong>; and the story text or encoded score as the <strong>measure</strong>.</p>
      <h3>Federated master repository push</h3>
      <p>The local repository is the first authority. A narrative must be staged, reviewed, and committed locally before it can be prepared for a master repository. The master push tool produces an SDMX-style package rather than silently uploading data.</p>
      <table>
        <thead><tr><th>Step</th><th>What happens</th><th>Why it matters</th></tr></thead>
        <tbody>
          <tr><td>Local commit</td><td>Approved records move into the Accepted repository. Rejected records move into the Rejected repository.</td><td>Only accepted local evidence can influence encoding, modelling, policy output, or master push.</td></tr>
          <tr><td>Prepare SDMX master push</td><td>Accepted records are converted into a package with DSD-like dimensions, codelists, attributes, observations, hashes, and protected-text rules.</td><td>The package can update Google Sheets, Drive, GitHub, Airtable, Supabase, or an institutional database later without losing structure.</td></tr>
          <tr><td>Master approval layer</td><td>A master reviewer approves or rejects the package and signs the decision with a chained hash.</td><td>This prevents every local project from automatically injecting unverified narratives into the shared corpus.</td></tr>
          <tr><td>Blockchain-ready seal</td><td>The package anchor hash and decision hash can be published to a blockchain or timestamp service.</td><td>Later reviewers can verify that the approved package has not been altered without exposing restricted narrative text.</td></tr>
        </tbody>
      </table>
      <p><strong>Important:</strong> the current tool creates the SDMX/DSD package and approval seal locally. It does not push to a live Google Sheet or blockchain by itself until a master repository backend is configured.</p>

      <h2>3. Encoding derivation</h2>
      <div class="grid">
        <div class="card"><h3>Manual scorecard</h3><p>Researchers enter explicit 0-1 numeric scores for each story, plus a short justification for each variable.</p></div>
        <div class="card"><h3>AI encoder</h3><p>Uses the selected LLM provider when configured. If no key is available, the backend falls back safely.</p></div>
        <div class="card"><h3>Hybrid review</h3><p>Combines model scoring with a human-review flag so policy users can inspect sensitive results.</p></div>
        <div class="card"><h3>Batch queue</h3><p>CSV import creates many NarrativeRecords. Each row is reviewed story by story; batch runs only automate the queue.</p></div>
      </div>
      <p>Each narrative <code>i</code> is converted into bounded scores. Manual coding should use only evidence visible in the narrative and metadata. If the coder is unsure, they should choose the middle range and write why.</p>
      <table>
        <thead><tr><th>Symbol</th><th>Meaning</th><th>Low score</th><th>High score</th></tr></thead>
        <tbody>
          <tr><td>E_i</td><td>Exposure and emotional intensity</td><td>Passing mention, weak feeling, little consequence.</td><td>Vivid event, urgent pressure, fear, hope, or repeated lived consequence.</td></tr>
          <tr><td>C_i</td><td>Credibility and cultural resonance</td><td>Abstract claim, weak source, little local grounding.</td><td>Concrete local detail, trusted source, repeated community meaning.</td></tr>
          <tr><td>tau_i</td><td>Trust alignment</td><td>Distrust, rumor, fear, or institutional skepticism dominates.</td><td>Strong trust in technology, messenger, support, or peer example.</td></tr>
          <tr><td>kappa_i</td><td>Inoculation and resistance potential</td><td>No clear misconception or refutation opportunity.</td><td>Clear misleading claim plus evidence that can refute it safely.</td></tr>
          <tr><td>B_i</td><td>Adoption barrier pressure</td><td>Few barriers or barriers already solved.</td><td>Cost, safety, habit, access, repair, fuel, or knowledge barriers likely block adoption.</td></tr>
          <tr><td>S_i</td><td>Social influence strength</td><td>Mostly individual decision.</td><td>Peers, family, leaders, groups, or local networks dominate the decision.</td></tr>
        </tbody>
      </table>
      <pre>Phi_i = 0.30 E_i + 0.30 C_i + 0.20 tau_i + 0.20 kappa_i

trust_score_i   = tau_i
barrier_score_i = B_i
confidence_i    = mean(C_i, kappa_i, S_i)</pre>
      <p><code>Phi</code> is a narrative-strength index. It increases truth diffusion when trust and cultural fit are strong. <code>B</code> is kept separate because a story can be emotionally powerful and culturally credible while still describing barriers that slow adoption.</p>
      <p><strong>Batch import rule:</strong> a CSV file is a container, not a scientific unit. Every row becomes one <code>NarrativeRecord</code> with its own hash, approval status, manual scorecard, LLM pre-code, comparison result, and final encoded output. The UI queue supports "encode current then next" so researchers can review records one by one, while "compare all modes" runs manual, AI, and hybrid over the full approved batch.</p>
      <h3>Bring-your-own LLM configuration</h3>
      <p>NDIM is now designed so a researcher or institution can choose a provider per encoding run. The UI supports OpenAI, Anthropic, Gemini, Azure OpenAI, OpenRouter, Mistral, Ollama, LM Studio, OpenAI-compatible endpoints, and deterministic fallback. API keys entered in the UI are session-only: they are sent to the backend in request headers during encoding and are not written into the policy JSON, reasoning log, or manual scorecard.</p>
      <pre>X-NDIM-LLM-Provider: anthropic | gemini | openai | ollama | ...
X-NDIM-LLM-Key: user session key, optional for local providers
X-NDIM-LLM-Base-URL: optional local or compatible endpoint
X-NDIM-LLM-Model: selected model or deployment</pre>
      <p>For sensitive indigenous knowledge or government evidence, prefer manual scoring or a local provider such as Ollama or LM Studio. Cloud LLMs should only be used when the user has permission to send the narratives to that provider.</p>

      <h2>4. Compartmental model derivation</h2>
      <p>The conceptual NDIM population model has five compartments. They can be normalized so <code>S + M + T + I + R = 1</code>.</p>
      <table>
        <thead><tr><th>Compartment</th><th>Meaning</th></tr></thead>
        <tbody>
          <tr><td>S</td><td>Susceptible households not yet strongly committed to a narrative.</td></tr>
          <tr><td>M</td><td>Misinformed households exposed to barrier or doubt narratives.</td></tr>
          <tr><td>T</td><td>Truth-aligned households influenced by trusted adoption-supporting narratives.</td></tr>
          <tr><td>I</td><td>Inoculated households resilient to misinformation after corrective exposure.</td></tr>
          <tr><td>R</td><td>Resistant or durably adoption-aligned households.</td></tr>
        </tbody>
      </table>
      <pre>dS/dt = - beta_m S M - beta_t S T - iota S
dM/dt =   beta_m S M - rho M - sigma M I
dT/dt =   beta_t S T + rho M - mu T
dI/dt =   iota S + sigma M I - gamma I
dR/dt =   gamma I + eta T</pre>
      <p>Terms are contact or transition rates. For example, <code>beta_m S M</code> is misinformation contact between susceptible and misinformed groups, while <code>beta_t S T</code> is truth-aligned contact. The UI plot shows the backend adoption trajectory, which is the measurable policy-facing outcome of this system.</p>
      <pre>beta_t = beta_t0 * (1 + Phi) * trust_score
beta_m = beta_m0 * barrier_score
iota   = iota0 + intervention_strength</pre>
      <p>Helpful reproduction-style diagnostics are:</p>
      <pre>R_m = beta_m S0 / (rho + sigma I0 + epsilon)
R_t = beta_t S0 / (mu + epsilon)</pre>
      <p>If <code>R_t &gt; R_m</code>, truth-aligned diffusion is stronger than misinformation pressure. If <code>R_m</code> is higher, policy should prioritize trusted correction, inoculation, or barrier reduction before expecting fast adoption.</p>

      <h2>5. Agent-based model derivation</h2>
      <p>The agent model treats each household as a local decision maker. It is useful when one district, village, or social network may behave differently from the national average.</p>
      <pre>peer_i(t)  = mean(adopted neighbors of household i)
media_i(t) = media_exposure_i * trust_i
z_i(t)     = b0 + trust_i + peer_effect * peer_i(t)
           + media_effect * media_i(t) - barrier_i

P(adopt_i at t+1) = 1 / (1 + exp(-z_i(t)))</pre>
      <p>Social network analysis is appropriate here because adoption is partly transmitted by neighbours, trusted messengers, and visible peer examples.</p>
      <pre>A_ij = 1 if household i is socially exposed to household j
degree_i = sum_j A_ij
exposure_i(t) = sum_j A_ij * adopted_j(t) / max(1, degree_i)
bridge_score_i = number of cross-community links from i</pre>
      <p>The ABM curve should be compared with the ODE curve. If the ABM curve is lower, the model is warning that local household friction is important. If the ABM curve is higher, peer diffusion may be stronger than the aggregate model assumes. High-degree or bridge households are good candidates for demonstrations because they move information between clusters.</p>

      <h2>6. Digital twin feedback derivation</h2>
      <p>The digital twin is the feedback mechanism. It takes a field observation and asks how far the model was from reality.</p>
      <pre>error_t = observed_adoption_t - predicted_adoption_t
theta_next = theta_model + lambda * error_t

trust_next   = clamp(trust_model + trust_shift, 0, 1)
barrier_next = clamp(barrier_model + barrier_shift, 0, 1)</pre>
      <p>The updated parameters rerun the simulation. This makes the model a learning system: outputs from the field become inputs for the next model pass.</p>

      <h2>7. Bayesian update derivation</h2>
      <p>Trust and barrier assumptions are bounded probabilities, so the manual uses Beta priors. A Beta prior is written as:</p>
      <pre>p ~ Beta(alpha, beta)
E[p] = alpha / (alpha + beta)</pre>
      <p>After evidence arrives, count successes and failures. For trust, a success means the evidence supports trust. For barrier, a success means the evidence supports the presence of a barrier.</p>
      <pre>likelihood = p^successes * (1 - p)^failures
posterior = Beta(alpha + successes, beta + failures)

trust_posterior_mean =
  (trust_alpha + trust_successes) /
  (trust_alpha + trust_beta + trials)</pre>
      <p>The posterior plot shows how evidence moves the model from prior belief to updated belief. The posterior feeds the model parameters used by RL and the final policy run.</p>

      <h2>8. RL optimizer derivation</h2>
      <p>The RL optimizer is framed as a small policy search problem. States represent model conditions such as trust and barrier levels. Actions represent intervention packages. Rewards combine adoption gain, cost, and risk.</p>
      <pre>reward = adoption_gain - cost_penalty - barrier_penalty

Q(s,a) = Q(s,a) + alpha * [
  reward + gamma * max_a' Q(s',a') - Q(s,a)
]</pre>
      <p>Interpret the reward plot as a learning curve. Stable rewards and a clear best action suggest the policy is robust under the current assumptions. Volatile rewards suggest uncertainty and a need for more evidence, stronger priors, or scenario comparison.</p>

      <h2>9. Regional analysis</h2>
      <p>Regional analysis asks whether the same narrative behaves differently by place. Isolation mode treats each region as its own evidence unit. Grouped mode pools places into a shared campaign view.</p>
      <pre>score_r = mean({Phi_i, trust_i, barrier_i, confidence_i} | location_i = r)

intervention_r =
  if trust_r low: trusted messenger intervention
  if barrier_r high: practical friction reduction
  if trust_r high and barrier_r low: peer diffusion campaign</pre>
      <p><strong>Interpretation:</strong> a region with high trust and high barriers may not need persuasion first; it may need cost, fuel, repair, or access support. A region with low trust needs messenger repair before technical messaging.</p>

      <h2>10. Knowledge graph</h2>
      <p>The knowledge graph is a research lens for studying stories from the same location. Nodes are locations, themes, trust/barrier signals, and intervention concepts. Edges connect a story location to the themes and signals found in that place.</p>
      <pre>G = (V, E)
A_ij = 1 if node i is connected to node j
degree(i) = sum_j A_ij
centrality(theme) = degree(theme) / max_degree</pre>
      <p><strong>Interpretation:</strong> high-degree themes are repeated across locations or stories. They are not automatically causal, but they tell the analyst where narrative meaning clusters. This is useful for comparing districts, identifying repeated rumours, and selecting which narratives need inoculation.</p>

      <h2>11. Inoculation theory and counter-narrative generation</h2>
      <p>Inoculation theory says people can become more resistant to manipulation if they receive a weak preview of a misleading claim plus a clear refutation before the full misinformation appears. The lab turns encoded narrative risks into pre-bunking and counter-feed drafts.</p>
      <pre>inoculation_message =
  warning
  + weakened_misinformation_claim
  + refutation
  + trusted_messenger
  + efficacy_cue

resistance_gain =
  threat_awareness * refutation_quality * source_trust</pre>
      <p>The LLM generation role is to spawn candidate narratives from a structured prompt. A safe prompt should include the target region, audience, barrier theme, trusted messenger, tone, and a requirement that the output does not ridicule the audience.</p>
      <pre>Prompt skeleton:
Generate three inoculation messages for {region}.
Audience: {audience}
Barrier/risk: {theme}
Use: warning, weakened claim, refutation, trusted source, practical action.
Avoid: shame, exaggeration, unsupported claims.</pre>
      <p><strong>Implication:</strong> counter-narratives should be reviewed by humans and ideally tested before use. The output is a policy communication draft, not proof that the message will work.</p>

      <h2>12. Policy output and feedback loop</h2>
      <p>The final output is a reviewable decision brief, not an automatic decision. It includes metadata, encoding mode, LLM provider selection, encoded narratives, compartmental summary, agent summary, digital twin summary, Bayesian posterior, RL policy, regional analysis, knowledge graph, inoculation drafts, and recommendation text.</p>
      <p><strong>Social media feed route:</strong> social feeds now enter through Stage 01 as an evidence route, not as a model stage. The user selects one or more platforms, pastes feed items, and sends them through the same SDMX governance gate before any modelling influence.</p>
      <pre>narratives -> encoding -> model parameters
model parameters -> ODE and ABM trajectories
field feedback -> digital twin rerun
digital twin + encoded evidence -> Bayesian posterior
posterior -> RL policy search
regional analysis -> place-sensitive intervention
knowledge graph -> repeated story structures
inoculation lab -> counter-narrative drafts
all outputs -> policy brief</pre>
      <p><strong>Output formats:</strong> the screen shows an HTML policy brief, the Copy brief button produces Markdown, and the Copy/Download JSON buttons export the <code>ndim-policy-output-v1</code> audit payload with governance hashes, model summaries, posterior values, RL policy, regional analysis, graph, inoculation drafts, and recommendation text.</p>
      <p>For novice users, follow the buttons stage by stage and read the implication notes. For expert users, inspect equations, priors, graph structure, and reward curves. For policy makers, focus on the recommendation, evidence trail, uncertainty, feasibility, and whether the recommended intervention matches the target region.</p>
      <p class="small">Version note: the current backend exposes a labelled NDIM compartment model with S/M/T/I/R compartments, uncertainty bands, persistent evidence ledger sync, validation checks, and deterministic Bayesian/RL fallbacks when advanced Torch/Pyro services are unavailable.</p>
    </main>
  </body>
</html>
"""
