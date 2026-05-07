WORKFLOW_UI_HTML = r"""<!doctype html>
<html lang="en" data-theme="light">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>NDIM Engine Stepwise Workflow</title>
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
      * { box-sizing: border-box; }
      body {
        margin: 0;
        min-height: 100vh;
        background:
          linear-gradient(180deg, rgba(255, 255, 255, .55), transparent 220px),
          var(--bg);
        color: var(--text);
        font-family: var(--font-ui);
      }
      button, input, textarea, select { font: inherit; }
      button { cursor: pointer; }
      .app {
        display: grid;
        grid-template-columns: 260px minmax(0, 1fr) 380px;
        min-height: 100vh;
      }
      .sidebar, .reasoning {
        background: var(--panel);
        min-width: 0;
      }
      .sidebar {
        border-right: 1px solid var(--line);
        display: flex;
        flex-direction: column;
      }
      .reasoning {
        border-left: 1px solid var(--line);
        display: flex;
        flex-direction: column;
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
      }
      .step-button span span {
        display: block;
        margin-top: 3px;
        color: var(--soft);
        font: 10px var(--font-data);
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
      }
      .topbar {
        min-height: 88px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 16px;
        padding: 18px 24px;
        border-bottom: 1px solid var(--line);
        background: var(--panel);
      }
      h1, h2, h3, p { margin-top: 0; }
      h1 {
        margin: 0;
        font-size: 30px;
        line-height: 1.05;
      }
      .topbar p {
        margin: 7px 0 0;
        max-width: 820px;
        color: var(--muted);
        font-size: 13.5px;
        line-height: 1.5;
      }
      .ndim-background {
        max-width: 920px;
        color: var(--text);
        font-size: 14px;
        line-height: 1.55;
      }
      .run-status {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        border: 1px solid var(--line);
        border-radius: 999px;
        background: var(--card);
        color: var(--muted);
        padding: 8px 12px;
        font: 800 10px var(--font-data);
        text-transform: uppercase;
        white-space: nowrap;
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
        overflow: auto;
        padding: 22px;
      }
      .command-center {
        max-width: 1120px;
        margin: 0 auto 14px;
        border: 1px solid var(--line);
        border-radius: 18px;
        background: var(--panel);
        box-shadow: 0 28px 80px rgba(41, 33, 24, .08);
        padding: 0;
        overflow: hidden;
      }
      .command-head {
        display: grid;
        grid-template-columns: minmax(0, 1fr) minmax(220px, .36fr);
        gap: 14px;
        align-items: stretch;
        padding: 18px 18px 16px;
      }
      .command-head h2 {
        margin: 0;
        max-width: 820px;
        font-size: clamp(30px, 4.4vw, 52px);
        line-height: 1;
        letter-spacing: -.015em;
      }
      .command-head p {
        margin: 10px 0 0;
        max-width: 820px;
        color: var(--muted);
        font-size: 14px;
        line-height: 1.55;
      }
      .current-intel {
        border: 1px solid var(--line);
        border-radius: 14px;
        background: var(--card);
        padding: 12px;
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
      .status-chip-row {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 14px;
      }
      .status-chip {
        display: inline-flex;
        align-items: center;
        gap: 7px;
        border: 1px solid var(--line);
        border-radius: 999px;
        background: var(--card);
        color: var(--muted);
        padding: 7px 10px;
        font: 800 10px var(--font-data);
        letter-spacing: .7px;
        text-transform: uppercase;
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
        grid-template-columns: repeat(4, minmax(0, 1fr));
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
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        font: 800 20px var(--font-data);
      }
      .flow-lane {
        display: flex;
        align-items: center;
        gap: 0;
        border-bottom: 1px solid var(--line);
        background: color-mix(in srgb, var(--panel) 92%, white);
        padding: 20px 18px;
        overflow-x: auto;
      }
      .flow-card {
        position: relative;
        flex: 1 0 164px;
        min-height: 58px;
        display: grid;
        grid-template-columns: 46px minmax(0, 1fr);
        gap: 12px;
        align-items: center;
        border: 0;
        border-radius: 0;
        background: transparent;
        color: var(--muted);
        padding: 0 36px 0 0;
        text-align: left;
        transition: color .16s ease, transform .16s ease;
      }
      .flow-card:not(:last-child)::after {
        content: "";
        position: absolute;
        top: 22px;
        right: 14px;
        width: 42px;
        height: 2px;
        background: var(--line);
      }
      .flow-card:hover {
        transform: translateY(-1px);
      }
      .flow-card.active {
        color: var(--text);
      }
      .flow-card.done { color: var(--text); }
      .flow-card b {
        display: inline-grid;
        place-items: center;
        width: 44px;
        height: 44px;
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
        font-size: 17px;
        line-height: 1.2;
      }
      .flow-card small {
        display: block;
        margin-top: 4px;
        color: var(--soft);
        font: 10px var(--font-data);
        line-height: 1.4;
      }
      .evidence-preview {
        display: grid;
        grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
        gap: 10px;
        padding: 0 18px 18px;
      }
      .preview-panel {
        border: 1px solid var(--line);
        border-radius: 13px;
        background: var(--card);
        padding: 12px;
        min-width: 0;
      }
      .preview-panel h3 {
        margin: 0 0 6px;
        font-size: 15px;
      }
      .preview-panel p {
        margin: 0;
        color: var(--muted);
        font-size: 12.5px;
        line-height: 1.55;
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
      }
      .stage-card {
        max-width: 1120px;
        margin: 0 auto;
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
      .button:hover { border-color: var(--line-strong); color: var(--text); }
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
      }
      .option span {
        display: block;
        color: var(--soft);
        font-size: 12.5px;
        line-height: 1.45;
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
      }
      .panel p {
        margin: 0;
        color: var(--muted);
        font-size: 13px;
        line-height: 1.55;
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
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 10px;
      }
      .metric {
        border: 1px solid var(--line);
        border-radius: 12px;
        background: var(--panel-2);
        padding: 12px;
      }
      .metric strong {
        display: block;
        margin-top: 5px;
        font: 800 22px var(--font-data);
      }
      .bars {
        display: grid;
        gap: 10px;
      }
      .bar-row {
        display: grid;
        grid-template-columns: 120px minmax(0, 1fr) 60px;
        gap: 10px;
        align-items: center;
        color: var(--muted);
        font-size: 12px;
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
      }
      .kg-svg {
        width: 100%;
        min-height: 340px;
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
      }
      .stage-nav {
        max-width: 1120px;
        margin: 12px auto 0;
        display: flex;
        justify-content: space-between;
        gap: 10px;
      }
      .reason-head {
        height: 66px;
        border-bottom: 1px solid var(--line);
        padding: 16px;
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
        gap: 10px;
        margin-bottom: 6px;
      }
      .trace strong {
        color: var(--text);
        font-size: 13px;
      }
      .trace small {
        color: var(--blue);
        font: 800 10px var(--font-data);
        text-transform: uppercase;
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
        .app { grid-template-columns: 230px minmax(0, 1fr); }
        .reasoning { grid-column: 1 / -1; border-left: 0; border-top: 1px solid var(--line); }
        .grid-2 { grid-template-columns: 1fr; }
        .command-head, .evidence-preview { grid-template-columns: 1fr; }
        .flow-lane { grid-template-columns: repeat(3, minmax(0, 1fr)); }
      }
      @media (max-width: 760px) {
        .app { grid-template-columns: 1fr; }
        .topbar { align-items: flex-start; flex-direction: column; }
        .field-grid, .grid-3, .metric-grid, .command-metrics, .flow-lane { grid-template-columns: 1fr; }
        .row { min-width: 760px; }
        .table { overflow-x: auto; }
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
            <p class="ndim-background">NDIM Engine expands the Narrative Diffusion and Inoculation Model into a reviewable scientific workflow: ingest field stories, encode meaning, simulate diffusion, update beliefs, test interventions, and produce a policy brief with an evidence trail.</p>
            <p id="topCopy">Start by defining the evidence context, country, location, source, and narrative text.</p>
          </div>
          <div class="top-actions">
            <div class="run-status" id="runStatus"><span class="dot"></span><span>idle</span></div>
            <button class="button primary" id="quickRunButton" type="button">Run current stage</button>
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
          <p class="eyebrow">Reasoning trace</p>
          <h2>What the system is doing</h2>
          <div class="button-row" style="margin-top: 10px;"><button class="button" id="clearTrace" type="button">Clear log</button></div>
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
        { id: "feeds", num: "12", title: "Experimental feeds", sub: "social listening sandbox" },
        { id: "policy", num: "13", title: "Policy output", sub: "recommendation and audit" }
      ];

      const workflowPhases = [
        { icon: "EV", label: "Evidence", detail: "Narratives, context, SDMX gate", step: 0, stages: ["intake", "gate"] },
        { icon: "EN", label: "Encode", detail: "Manual, AI, hybrid scoring", step: 2, stages: ["encoding"] },
        { icon: "MO", label: "Model", detail: "ODE and agent simulation", step: 3, stages: ["compartmental", "agents"] },
        { icon: "LR", label: "Learn", detail: "Twin, posterior, RL loop", step: 5, stages: ["digital", "bayes", "rl"] },
        { icon: "SY", label: "Synthesize", detail: "Regions, graph, inoculation", step: 8, stages: ["regional", "graph", "inoculation", "feeds"] },
        { icon: "EX", label: "Export", detail: "Policy output and audit", step: 12, stages: ["policy"] }
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
          interviewId: "",
          respondentProfile: "",
          decisionMaker: "",
          cookingMethods: "",
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
        records: [],
        importedRecords: [],
        encodingMode: "hybrid",
        llmProvider: "openai",
        manualIndex: 0,
        encodingRuns: {},
        manualScores: { E: 0.55, C: 0.58, tau: 0.62, kappa: 0.52 },
        encoded: [],
        comp: null,
        agents: null,
        digital: null,
        feedback: { observedAdoption: 0.48, trustDelta: 0.05, barrierDelta: -0.04, note: "" },
        bayes: null,
        priors: { trustA: 6, trustB: 4, barrierA: 4, barrierB: 6 },
        rl: null,
        regional: null,
        graph: null,
        inoculation: null,
        feeds: null,
        policy: null,
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

      function narrativeRecord(text, index, extra = {}) {
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
              collection_template: "clean-cooking-pressure-cooker-v1",
              question_id: extra.questionId || null,
              question_title: extra.questionTitle || null,
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
          tags: [state.encodingMode, state.meta.sourceType, extra.questionId || "", state.template.stance || ""].filter(Boolean)
        };
      }

      function buildRecords() {
        const fromQuestions = questionBlocks().map((question, index) =>
          narrativeRecord(`${question.title}: ${question.answer}`, index, {
            narrative_id: `${state.template.interviewId || "field"}-${question.id}-${Date.now()}`,
            questionId: question.id,
            questionTitle: question.title
          })
        );
        const fromFreeText = splitNarratives(state.text).map((text, index) =>
          narrativeRecord(text, fromQuestions.length + index, { questionId: "free_text", questionTitle: "Additional narrative" })
        );
        const importedText = state.importedRecords.map((record) => record.text).join("\n\n").trim();
        if (!fromQuestions.length && state.importedRecords.length && state.text.trim() === importedText) {
          state.records = state.importedRecords;
          return;
        }
        state.records = [...fromQuestions, ...fromFreeText];
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

      function recordsFromCsv(text, filename) {
        const rows = parseCsv(text);
        return rows.flatMap((row, index) => {
          const country = row.country || state.meta.country;
          const schema = countrySchema(country);
          const adminValues = schema.levels.map((level) => {
            const key = level.label.toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_|_$/g, "");
            return row[level.key] || row[key] || row.admin_unit || "";
          }).filter(Boolean);
          const baseMetadata = {
            source_type: "csv",
            source_name: filename || row.source_name || state.meta.sourceName,
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
          const makeCsvRecord = (narrative, questionId = row.question_id || row.question || "", questionTitle = "") => ({
            narrative_id: row.narrative_id || row.id || `csv-${Date.now()}-${index + 1}-${questionId || "narrative"}`,
            text: narrative,
            metadata: {
              ...baseMetadata,
              provenance: {
                period: row.period || state.meta.period,
                csv_row: index + 1,
                question_id: questionId,
                question_title: questionTitle,
                ui: "csv-import",
                collection_template: "clean-cooking-pressure-cooker-v1"
              }
            },
            tags: [state.encodingMode, "csv", row.type || "", questionId].filter(Boolean)
          });
          const questionRecords = narrativeQuestions
            .filter((question) => row[question.id])
            .map((question) => makeCsvRecord(`${question.title}: ${row[question.id]}`, question.id, question.title));
          if (questionRecords.length) return questionRecords;
          const narrative = row.narrative || row.text || row.quote || row.story || row.content || Object.values(row).find((value) => value && value.length > 24) || "";
          return narrative ? [makeCsvRecord(narrative)] : [];
        }).filter((record) => record.text);
      }

      function computePhi() {
        const s = state.manualScores;
        return Number((0.3 * s.E + 0.3 * s.C + 0.2 * s.tau + 0.2 * s.kappa).toFixed(4));
      }

      function gateChecks() {
        const qCount = questionBlocks().length;
        const adminParts = adminUnitParts();
        return [
          ["Country", state.meta.country, Boolean(state.meta.country)],
          ["Administrative schema", countrySchema().levels.map((level) => level.label).join(" > "), Boolean(state.meta.country)],
          ["Administrative unit", adminUnitLabel(), adminParts.length >= 2],
          ["Interview ID", state.template.interviewId, Boolean(state.template.interviewId)],
          ["Respondent profile", state.template.respondentProfile, Boolean(state.template.respondentProfile)],
          ["Decision-maker", state.template.decisionMaker, Boolean(state.template.decisionMaker)],
          ["Current cooking method(s)", state.template.cookingMethods, Boolean(state.template.cookingMethods)],
          ["Source", `${state.meta.sourceType} / ${state.meta.sourceName}`, Boolean(state.meta.sourceType && state.meta.sourceName)],
          ["Period", state.meta.period, Boolean(state.meta.period)],
          ["Language", state.meta.language, Boolean(state.meta.language)],
          ["Core narrative questions", `${qCount} of ${narrativeQuestions.length} answered`, qCount > 0],
          ["Narrative observations", `${state.records.length} parsed`, state.records.length > 0]
        ];
      }

      function saveIntakeFromDom() {
        ["country", "province", "district", "sector", "language", "sourceType", "sourceName", "period"].forEach((key) => {
          const el = $(key);
          if (el) state.meta[key] = el.value;
        });
        Object.keys(state.template).forEach((key) => {
          const el = $(key);
          if (el) state.template[key] = el.value;
        });
        const textEl = $("narrativeText");
        if (textEl) state.text = textEl.value;
      }

      function validateIntake() {
        saveIntakeFromDom();
        buildRecords();
        if (!state.text.trim() && !questionBlocks().length) {
          setStatus("error");
          trace("blocked", "No narrative text", "Answer at least one Q1-Q5 narrative question or paste at least one narrative paragraph before moving to the SDMX gate.");
          toast("Add narrative evidence first");
          return false;
        }
        if (!state.meta.country || !state.meta.sourceName || !state.meta.period || !state.template.interviewId) {
          setStatus("error");
          trace("blocked", "Missing metadata", "Country, source name, period, and interview ID are required for the SDMX input contract.");
          toast("Complete required metadata");
          return false;
        }
        state.completed.add("intake");
        state.completed.add("gate");
        setStatus("complete");
        trace("intake", "Evidence staged", `${state.records.length} narrative observation(s) prepared for ${state.meta.country}.`);
        trace("gate", "SDMX gate prepared", "The records now carry source, location, language, period, provenance, text, and tags.");
        return true;
      }

      function currentStep() {
        return steps[state.step];
      }

      function goStep(index) {
        state.step = Math.max(0, Math.min(steps.length - 1, index));
        render();
      }

      function resetCurrentStage() {
        const id = currentStep().id;
        if (id === "intake") {
          state.text = "";
          state.records = [];
          state.importedRecords = [];
          state.completed.delete("intake");
          state.completed.delete("gate");
        } else if (id === "gate") {
          state.completed.delete("gate");
        } else if (id === "encoding") {
          state.encoded = [];
          state.encodingRuns = {};
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
          state.completed.delete("inoculation");
        } else if (id === "feeds") {
          state.feeds = null;
          state.completed.delete("feeds");
        } else if (id === "policy") {
          state.policy = null;
          state.completed.delete("policy");
        }
        trace("reset", `${currentStep().title} reset`, "This stage output was cleared without deleting unrelated stages.");
        setStatus("idle");
        render();
      }

      function nextStep() {
        const id = currentStep().id;
        if (id === "intake" && !validateIntake()) return;
        if (id === "gate" && !state.completed.has("gate")) {
          if (!validateIntake()) return;
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
                <p class="eyebrow">Narrative intelligence command center</p>
                <h2>From field stories to policy-ready inoculation strategy</h2>
                <p>NDIM keeps the full chain visible: source evidence, SDMX validation, LLM-assisted encoding, population and agent simulation, posterior learning, optimization, regional interpretation, inoculation drafting, and human review.</p>
                <div class="status-chip-row">
                  ${statusChip("Evidence staged", state.records.length > 0)}
                  ${statusChip("Encoding ready", state.encoded.length > 0)}
                  ${statusChip("Model feedback loop", Boolean(state.digital || state.bayes || state.rl))}
                  ${statusChip("Policy audit", Boolean(state.policy))}
                </div>
              </div>
              <div class="current-intel">
                <span class="mini-label">Now running</span>
                <strong>${escapeHtml(step.num)} ${escapeHtml(step.title)}</strong>
                <p>${escapeHtml(stageAdvice(step.id))}</p>
              </div>
            </div>
            <div class="command-metrics">
              ${commandMetric("Observations", state.records.length || "-")}
              ${commandMetric("Encoded stories", encodedSummary)}
              ${commandMetric("Best adoption signal", adoption)}
              ${commandMetric("Workflow readiness", `${readiness}%`)}
            </div>
            <div class="evidence-preview">
              <div class="preview-panel">
                <p class="eyebrow">Evidence ledger</p>
                <h3>${escapeHtml(topLocation)}</h3>
                <p>${escapeHtml(evidenceLedgerText())}</p>
              </div>
              <div class="preview-panel">
                <p class="eyebrow">Recent reasoning</p>
                <div class="mini-trace">
                  ${state.trace.slice(0, 3).map(([kind, title, detail]) => `
                    <div><h3>${escapeHtml(title)}</h3><p>${escapeHtml(detail)}</p></div>
                  `).join("")}
                </div>
              </div>
            </div>
          </section>
        `;
      }

      function renderFlowCard(phase) {
        const active = phase.stages.includes(currentStep().id);
        const done = phase.stages.every((id) => state.completed.has(id));
        const someDone = phase.stages.some((id) => state.completed.has(id));
        const status = done ? "complete" : someDone ? "in progress" : "pending";
        return `
          <button class="flow-card ${active ? "active" : ""} ${done ? "done" : ""}" data-flow-step="${phase.step}" type="button">
            <b>${escapeHtml(phase.icon)}</b>
            <span>
              <strong>${escapeHtml(phase.label)}</strong>
              <small>${escapeHtml(phase.detail)} / ${escapeHtml(status)}</small>
            </span>
          </button>
        `;
      }

      function commandMetric(label, value) {
        return `<div class="command-metric"><span>${escapeHtml(label)}</span><strong>${escapeHtml(String(value))}</strong></div>`;
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
        return `${state.records.length} observation(s) staged from ${sourceTypes}. Active place lens: ${places || state.meta.country}.`;
      }

      function stageAdvice(id) {
        const advice = {
          intake: "Create traceable narrative observations before any model receives evidence.",
          gate: "Confirm the source, place, period, language, and narrative fields are complete.",
          encoding: "Compare manual, AI, and hybrid scoring so model inputs are explainable.",
          compartmental: "Run the population ODE view to estimate aggregate diffusion pressure.",
          agents: "Stress-test local household dynamics, peer effects, and network friction.",
          digital: "Feed field observations back into the model before drawing conclusions.",
          bayes: "Turn priors and observations into posterior trust and barrier assumptions.",
          rl: "Let the optimizer test intervention packages while keeping human review in control.",
          regional: "Analyse each region alone or as a grouped evidence set before intervention design.",
          graph: "Connect stories, places, themes, trust, and barriers for qualitative sense-making.",
          inoculation: "Generate pre-bunking and refutation drafts from encoded narrative risk.",
          feeds: "Use social-listening prototypes as experimental inputs, not official evidence.",
          policy: "Produce the reviewable policy brief, assumptions, and audit payload."
        };
        return advice[id] || "Continue the evidence-to-policy workflow.";
      }

      function bindCommandCenter() {
        document.querySelectorAll("[data-flow-step]").forEach((button) => {
          button.addEventListener("click", () => goStep(Number(button.dataset.flowStep)));
        });
      }

      function render() {
        const step = currentStep();
        $("topTitle").textContent = step.title;
        $("topCopy").textContent = step.sub;
        renderStepList();
        $("stagePanel").innerHTML = renderCommandCenter() + renderStage(step.id);
        $("backButton").disabled = state.step === 0;
        $("nextButton").textContent = state.step === steps.length - 1 ? "Finish" : "Next";
        bindCommandCenter();
        bindStage(step.id);
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
        if (id === "feeds") return renderExperimentalFeeds();
        return renderPolicy();
      }

      function selectedAttr(value, current) {
        return value === current ? "selected" : "";
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
        const answered = questionBlocks().length;
        return `
          <section class="stage-card">
            <p class="eyebrow">Stage 1</p>
            <h2>Ingest narratives with context</h2>
            <p class="copy">Use this as the field collection sheet. Choose a country so NDIM loads the right administrative unit labels, then capture Q1-Q5 narratives for downstream encoding and modelling.</p>
            <div class="button-row" style="margin-top: 0; margin-bottom: 14px;">
              <a class="manual-link" href="/manual" target="_blank" rel="noreferrer">Open tutorial manual</a>
              <button class="button" id="copyTemplate" type="button">Copy field template</button>
              <button class="button" id="downloadCsvTemplate" type="button">Download CSV template</button>
              <button class="button" id="resetIntake" type="button">Reset intake</button>
            </div>
            <div class="grid-2">
              <div>
                <div class="field-grid">
                  <div class="field"><label for="country">Country</label><select id="country">${countries.map((country) => `<option ${selectedAttr(country, state.meta.country)}>${country}</option>`).join("")}</select></div>
                  ${renderAdminFields()}
                  <div class="field"><label for="language">Language</label><select id="language"><option ${selectedAttr("en", state.meta.language)} value="en">English</option><option ${selectedAttr("rw", state.meta.language)} value="rw">Kinyarwanda</option><option ${selectedAttr("fr", state.meta.language)} value="fr">French</option><option ${selectedAttr("sw", state.meta.language)} value="sw">Swahili</option></select></div>
                  <div class="field"><label for="sourceType">Source type</label><select id="sourceType"><option value="field_note">Field note</option><option value="interview">Interview</option><option value="focus_group">Focus group</option><option value="radio">Radio transcript</option><option value="policy_brief">Policy brief</option><option value="csv">CSV extract</option><option value="sdmx">SDMX exchange</option></select></div>
                  <div class="field"><label for="sourceName">Source name</label><input id="sourceName" value="${escapeHtml(state.meta.sourceName)}" /></div>
                  <div class="field"><label for="period">Period</label><input id="period" value="${escapeHtml(state.meta.period)}" /></div>
                  <div class="field"><label for="interviewId">Interview ID</label><input id="interviewId" value="${escapeHtml(state.template.interviewId)}" placeholder="e.g., RW-NYA-001" /></div>
                  <div class="field"><label for="respondentProfile">Respondent profile</label><input id="respondentProfile" value="${escapeHtml(state.template.respondentProfile)}" placeholder="age range, gender, occupation" /></div>
                  <div class="field"><label for="decisionMaker">Primary cooking decision-maker</label><select id="decisionMaker"><option value="">Select</option><option ${selectedAttr("yes", state.template.decisionMaker)} value="yes">Yes</option><option ${selectedAttr("no", state.template.decisionMaker)} value="no">No</option><option ${selectedAttr("shared", state.template.decisionMaker)} value="shared">Shared decision</option></select></div>
                  <div class="field"><label for="cookingMethods">Current cooking method(s)</label><input id="cookingMethods" value="${escapeHtml(state.template.cookingMethods)}" placeholder="charcoal, firewood, LPG..." /></div>
                </div>
                <textarea id="narrativeText" placeholder="Optional: paste extra narrative paragraphs here, or load CSV with interview_id, country, administrative fields, question_id, and narrative/text/quote columns..." style="margin-top: 14px;">${escapeHtml(state.text)}</textarea>
                <div class="button-row">
                  <button class="button green" id="loadSample" type="button">Load Rwanda sample</button>
                  <label class="button" for="fileInput">Open text or CSV file</label>
                  <input id="fileInput" type="file" accept=".txt,.md,.csv,.json,.xml,.sdmx" hidden />
                  <button class="button primary" id="stageEvidence" type="button">Stage and validate</button>
                </div>
              </div>
              <div class="panel">
                <h3>What this stage creates</h3>
                <p>Each answered Q1-Q5 prompt or pasted paragraph becomes a NarrativeRecord with country, administrative units, interview metadata, language, period, source, and post-interview coding fields.</p>
                <div class="metric-grid" style="margin-top: 12px;">
                  <div class="metric"><span class="mini-label">Q answered</span><strong>${answered}/${narrativeQuestions.length}</strong></div>
                  <div class="metric"><span class="mini-label">Admin path</span><strong>${adminUnitParts().length || "-"}</strong></div>
                  <div class="metric"><span class="mini-label">Records</span><strong>${state.records.length || "-"}</strong></div>
                </div>
                <h3 style="margin-top: 16px;">Core Q1-Q5 worksheet</h3>
                <p>Use these as compact field prompts. Open only the question you are recording.</p>
                <div class="question-stack" style="margin-top: 10px;">${renderQuestionCards()}</div>
                <h3 style="margin-top: 16px;">Post-interview coding fields</h3>
                <p>Complete these after the interview; they travel with the records for encoding comparison and policy audit.</p>
                <div style="margin-top: 10px;">${renderCodingFields()}</div>
                <div class="guide-note">
                  <strong>Optional probes for enumerators</strong>
                  <p>Can you give an example? What happened next? How did that make you feel? What did others do in that situation?</p>
                </div>
              </div>
            </div>
          </section>
        `;
      }

      function renderTemplateContract() {
        const rows = [
          ["Interview ID", state.template.interviewId, Boolean(state.template.interviewId)],
          ...countrySchema().levels.map((level) => [level.label, state.meta[level.key], Boolean(state.meta[level.key])]),
          ["Respondent profile", state.template.respondentProfile, Boolean(state.template.respondentProfile)],
          ["Primary decision-maker", state.template.decisionMaker, Boolean(state.template.decisionMaker)],
          ["Current cooking methods", state.template.cookingMethods, Boolean(state.template.cookingMethods)],
          ...narrativeQuestions.map((question) => [question.title, state.template[question.id], Boolean(state.template[question.id])]),
          ["Tone / archetype", state.template.tone || "post-interview", true],
          ["Adoption stance", state.template.stance || "post-interview", true],
          ["Key barrier", state.template.barrier || "post-interview", true],
          ["Key motivator", state.template.motivator || "post-interview", true],
          ["Social influence", state.template.socialInfluence || "post-interview", true]
        ];
        return `
          <div class="template-table">
            <div class="template-row head"><span>Template field</span><span>Current value</span><span>Status</span></div>
            ${rows.map(([field, value, pass]) => `
              <div class="template-row">
                <span>${escapeHtml(field)}</span>
                <span>${escapeHtml(value || "missing")}</span>
                <span>${pass ? "ready" : "needed"}</span>
              </div>
            `).join("")}
          </div>
        `;
      }

      function renderGate() {
        const checks = gateChecks();
        return `
          <section class="stage-card">
            <p class="eyebrow">Stage 2</p>
            <h2>SDMX gate</h2>
            <p class="copy">The gate converts the field template into a traceable SDMX-style observation contract: country-specific administrative units, enumerator metadata, Q1-Q5 narrative text, and post-interview coding fields.</p>
            <div class="button-row" style="margin-top: 0; margin-bottom: 14px;">
              <button class="button" id="copyGateTemplate" type="button">Copy field template</button>
              <button class="button" id="downloadGateCsv" type="button">Download CSV template</button>
            </div>
            <div class="grid-2">
              <div class="check-list">
                ${checks.map(([label, value, pass]) => `
                  <div class="check ${pass ? "pass" : ""}"><i>${pass ? "OK" : "!"}</i><div><strong>${escapeHtml(label)}</strong><span>${escapeHtml(value || "missing")}</span></div></div>
                `).join("")}
                <div class="panel">
                  <h3>Collection template contract</h3>
                  <p>This is the table the field team can use before export. The Q1-Q5 answers become the narratives for the next stages.</p>
                  ${renderTemplateContract()}
                </div>
              </div>
              <div class="panel">
                <h3>Observation payload explained</h3>
                <div class="payload-body">${renderPayloadBody()}</div>
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
            <p><b>Question:</b> ${escapeHtml(record.metadata.provenance?.question_title || "Narrative")}. <b>Interview:</b> ${escapeHtml(record.metadata.interview_id || "not set")}. <b>Source:</b> ${escapeHtml(record.metadata.source_type)} from ${escapeHtml(record.metadata.source_name)}. <b>Language:</b> ${escapeHtml(record.metadata.language)}. <b>Text:</b> ${escapeHtml(record.text.slice(0, 220))}${record.text.length > 220 ? "..." : ""}</p>
          </div>
        `).join("") + (state.records.length > 6 ? `<div class="payload-item"><strong>${state.records.length - 6} more observations</strong><p>They are included in batch encoding and modelling.</p></div>` : "");
      }

      function renderEncoding() {
        return `
          <section class="stage-card">
            <p class="eyebrow">Stage 3</p>
            <h2>Encoding options</h2>
            <p class="copy">This is the scientific scoring stage. Choose one of the three paths, then inspect returned themes, trust, barrier, and confidence.</p>
            <div class="field" style="max-width: 360px; margin-bottom: 12px;">
              <label for="llmProvider">LLM provider for AI encoding</label>
              <select id="llmProvider">
                <option value="openai">OpenAI</option>
                <option value="azure-openai">Azure OpenAI</option>
                <option value="anthropic">Anthropic</option>
                <option value="local">Local model</option>
                <option value="deterministic">Deterministic fallback</option>
              </select>
            </div>
            <div class="grid-3">
              ${renderEncodingOption("manual", "Manual / rule-based", "Transparent local scoring. Good for demos, audits, and when no model key is configured.")}
              ${renderEncodingOption("ai", "AI encoder", "Uses the backend OpenAI path when OPENAI_API_KEY is configured; otherwise falls back safely.")}
              ${renderEncodingOption("hybrid", "Hybrid review", "AI/fallback score plus a human-review flag before the model uses it.")}
            </div>
            <div class="grid-2" style="margin-top: 14px;">
              <div class="panel">
                <h3>Manual Phi controls</h3>
                ${renderStoryNavigator()}
                ${renderSlider("E", "Emotional salience")}
                ${renderSlider("C", "Cultural resonance")}
                ${renderSlider("tau", "Trust alignment")}
                ${renderSlider("kappa", "Narrative arc")}
                <p style="margin-top: 10px;">Phi = <strong>${computePhi().toFixed(4)}</strong></p>
              </div>
              <div>
                <div class="button-row" style="margin-top: 0;">
                  <button class="button primary" id="runEncoding" type="button">Run selected encoder</button>
                  <button class="button" id="runCurrentEncoding" type="button">Encode current story</button>
                  <button class="button" id="runAllEncodingModes" type="button">Compare all modes</button>
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

      function renderSlider(key, label) {
        const value = state.manualScores[key];
        return `
          <div class="field" style="margin-top: 9px;">
            <label>${label} (${key})</label>
            <input type="range" min="0" max="1" step="0.01" value="${value}" data-score="${key}" />
            <span class="mini-label">${value.toFixed(2)}</span>
          </div>
        `;
      }

      function renderStoryNavigator() {
        const record = state.records[state.manualIndex];
        if (!record) return '<div class="story-card"><strong>No current story</strong><blockquote>Stage evidence first, then use Encode current story for manual review.</blockquote></div>';
        return `
          <div class="story-card">
            <span class="mini-label">Story ${state.manualIndex + 1} of ${state.records.length}</span>
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
          return `<div class="table">${head}<div class="row"><span>No encoding yet</span><span>-</span><span>-</span><span>-</span><span>-</span><span>-</span></div></div>`;
        }
        return `<div class="table">${head}${state.encoded.map((item) => `
          <div class="row">
            <span>${escapeHtml(item.narrative_id)}</span>
            <span>${escapeHtml(item.encoding_mode)}</span>
            <span>${escapeHtml((item.themes || ["general"]).join(", "))}</span>
            <span>${typeof item.trust_score === "number" ? item.trust_score.toFixed(2) : "-"}</span>
            <span>${typeof item.adoption_barrier_score === "number" ? item.adoption_barrier_score.toFixed(2) : "-"}</span>
            <span>${typeof item.confidence === "number" ? item.confidence.toFixed(2) : "-"}</span>
          </div>
        `).join("")}</div>`;
      }

      function renderEncodingComparison() {
        const modes = Object.keys(state.encodingRuns);
        if (modes.length < 2) return "";
        return `
          <div class="compare-grid">
            ${modes.map((mode) => {
              const rows = state.encodingRuns[mode] || [];
              const trust = avg(rows.map((item) => item.trust_score), 0);
              const barrier = avg(rows.map((item) => item.adoption_barrier_score), 0);
              const conf = avg(rows.map((item) => item.confidence), 0);
              const themes = [...new Set(rows.flatMap((item) => item.themes || []))].slice(0, 5).join(", ") || "general";
              return `<div class="compare-card ${state.encodingMode === mode ? "active" : ""}"><h3>${escapeHtml(mode)}</h3><p>Trust ${trust.toFixed(2)} / Barrier ${barrier.toFixed(2)} / Confidence ${conf.toFixed(2)}</p><p>Themes: ${escapeHtml(themes)}</p></div>`;
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
                <div class="guide-note"><strong>Guiding note</strong><p>Read this plot as the population-level adoption signal. The current backend returns the measurable adoption trajectory; the S/M/T/I/R equations show the scientific structure that explains why trust, misinformation, and inoculation change the curve.</p></div>
                <div class="check-list">
                  ${["S Susceptible households", "M Misinformed households", "T Truth-aligned households", "I Inoculated households", "R Resistant or durable adoption belief"].map((item) => `<div class="check pass"><i>--</i><div><strong>${item}</strong><span>Tracked by the scientific model layer.</span></div></div>`).join("")}
                </div>
                <div class="button-row"><button class="button primary" id="runCompartmental" type="button">Run compartmental model</button></div>
              </div>
              <div class="panel">
                <h3>Population output</h3>
                <div class="metric-grid">
                  <div class="metric"><span class="mini-label">Final adoption</span><strong>${fmtPct(last?.adoption)}</strong></div>
                  <div class="metric"><span class="mini-label">Model mode</span><strong>ODE</strong></div>
                  <div class="metric"><span class="mini-label">Horizon</span><strong>180d</strong></div>
                </div>
                <div class="bars" style="margin-top: 14px;">${renderTrajectoryBars(state.comp?.trajectory)}</div>
                ${renderLinePlot("Population adoption trajectory", state.comp?.trajectory, "adoption", "var(--blue)", "day")}
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
                </div>
                <p class="copy" style="margin-top: 12px;">Posterior values feed the RL optimizer and final policy run as refined trust and barrier parameters.</p>
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
                </div>
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
          </section>
        `;
      }

      function renderExperimentalFeeds() {
        const feeds = state.feeds;
        return `
          <section class="stage-card">
            <p class="eyebrow">Stage 12 experimental</p>
            <h2>Social feed sandbox</h2>
            <p class="copy">This is deliberately outside the core scientific workflow. It lets researchers prototype Twitter/X, Facebook, LinkedIn, WhatsApp-summary, or radio transcript ingestion before adding real platform connectors and consent controls.</p>
            <div class="grid-2">
              <div class="panel">
                <h3>Experimental feed input</h3>
                <div class="field-grid">
                  <div class="field"><label for="feedPlatform">Platform</label><select id="feedPlatform"><option value="twitter">Twitter/X</option><option value="facebook">Facebook</option><option value="linkedin">LinkedIn</option><option value="whatsapp_summary">WhatsApp summary</option><option value="radio">Radio call-in</option></select></div>
                  <div class="field"><label for="feedRegion">Region lens</label><input id="feedRegion" value="${escapeHtml(state.meta.district || state.meta.country)}" /></div>
                </div>
                <textarea id="socialFeedInput" placeholder="Paste one post per line. This sandbox classifies narrative risk and drafts counter-feeds; it does not connect to live social APIs yet.">${escapeHtml(feeds?.raw || "")}</textarea>
                <div class="button-row">
                  <button class="button" id="loadFeedSample" type="button">Load sample feed</button>
                  <button class="button primary" id="runFeeds" type="button">Analyse feed and generate counters</button>
                </div>
              </div>
              <div class="panel">
                <h3>Experimental output</h3>
                ${feeds ? renderFeedResults(feeds) : '<p>No feed analysed yet. Use this area for sandbox social listening, not official policy evidence.</p>'}
              </div>
            </div>
          </section>
        `;
      }

      function renderPolicy() {
        const summary = state.policy?.summary || {};
        return `
          <section class="stage-card">
            <p class="eyebrow">Stage 13</p>
            <h2>Policy output and audit</h2>
            <p class="copy">This stage creates a reviewable decision output rather than a black-box answer. It shows recommendation, evidence trail, and model assumptions.</p>
            <div class="button-row" style="margin-top: 0; margin-bottom: 14px;">
              <button class="button green" id="runPolicy" type="button">Run full policy pipeline</button>
              <button class="button" id="copyPolicy" type="button">Copy JSON</button>
            </div>
            <div class="metric-grid">
              <div class="metric"><span class="mini-label">Final adoption</span><strong>${fmtPct(summary.final_adoption)}</strong></div>
              <div class="metric"><span class="mini-label">Average trust</span><strong>${fmtPct(summary.average_trust)}</strong></div>
              <div class="metric"><span class="mini-label">Average barrier</span><strong>${fmtPct(summary.average_barrier)}</strong></div>
            </div>
            <div class="grid-2" style="margin-top: 14px;">
              <div class="panel">
                <h3>Recommendation draft</h3>
                <p>${policyNarrative()}</p>
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
          compartmental: state.comp ? `Result implication: the ODE curve reaches ${fmtPct(state.comp.trajectory.at(-1).adoption)} by the horizon. Treat this as the population-level ceiling, then test whether local agent dynamics support or weaken it.` : "Result implication: run the population model to see whether narrative and intervention inputs produce meaningful adoption growth.",
          agents: state.agents ? `Result implication: the ABM reaches ${fmtPct(state.agents.trajectory.at(-1).adoption)}. ${compareModels()} means the local network assumptions are ${compareModels() === "ABM lower" ? "more cautious than the ODE and may require targeted peer work" : "supportive of diffusion and may justify demonstration-led scaling"}.` : "Result implication: run the agent model to test household-level friction and peer spread.",
          digital: state.digital ? `Result implication: the feedback-adjusted twin reaches ${fmtPct(state.digital.trajectory.at(-1).adoption)}. If this diverges from baseline, the field observation materially changed the model.` : "Result implication: use observed adoption and field notes to correct the next simulation.",
          bayes: state.bayes ? `Result implication: posterior trust is ${fmtPct(state.bayes.trustMean)} and posterior barrier is ${fmtPct(state.bayes.barrierMean)}. These values now become refined priors for optimization and policy interpretation.` : "Result implication: Bayesian updating shows how evidence moves assumptions instead of hiding them.",
          rl: state.rl ? `Result implication: the best learned intervention is "${state.rl.bestAction}" with Q reward ${state.rl.bestReward.toFixed(3)}. Use it as a candidate, not an automatic decision.` : "Result implication: run the optimizer to stress-test intervention packages before drafting policy."
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

      function policyJson() {
        if (!state.policy) return { status: "not_run" };
        return {
          metadata: state.meta,
          encoding_mode: state.encodingMode,
          llm_provider: state.llmProvider,
          narratives: state.records.length,
          encoded: state.encoded,
          compartmental_summary: state.comp?.trajectory?.at(-1) || null,
          agent_summary: state.agents?.trajectory?.at(-1) || null,
          digital_twin_summary: state.digital?.trajectory?.at(-1) || null,
          bayesian_posterior: state.bayes,
          rl_policy: state.rl,
          regional_analysis: state.regional,
          knowledge_graph: state.graph,
          inoculation_narratives: state.inoculation,
          experimental_feeds: state.feeds,
          pipeline_summary: state.policy.summary,
          recommendation: policyNarrative()
        };
      }

      function fieldTemplateMarkdown() {
        const schema = countrySchema();
        return `# Narrative Collection Template: Clean Cooking (Pressure Cooker Adoption)

## Metadata (Enumerator fills)

- Interview ID:
- Country: ${state.meta.country}
${schema.levels.map((level) => `- ${level.label}:`).join("\n")}
- Respondent profile (age range, gender, occupation):
- Primary cooking decision-maker (Yes/No/Shared):
- Current cooking method(s):
- Source name:
- Period:
- Language:

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
`;
      }

      function fieldTemplateCsv() {
        const schema = countrySchema();
        const headers = [
          "interview_id",
          "country",
          ...schema.levels.map((level) => level.label.toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_|_$/g, "")),
          "respondent_profile",
          "primary_decision_maker",
          "current_cooking_methods",
          "source_name",
          "period",
          "language",
          ...narrativeQuestions.map((question) => question.id),
          "tone_archetype",
          "adoption_stance",
          "key_barrier",
          "key_motivator",
          "social_influence"
        ];
        const sample = [
          state.template.interviewId || "RW-NYA-001",
          state.meta.country,
          ...schema.levels.map((level) => state.meta[level.key] || ""),
          state.template.respondentProfile || "35-44, female, farmer",
          state.template.decisionMaker || "yes",
          state.template.cookingMethods || "firewood; charcoal",
          state.meta.sourceName,
          state.meta.period,
          state.meta.language,
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

      async function copyFieldTemplate() {
        await navigator.clipboard.writeText(fieldTemplateMarkdown());
        toast("Field template copied");
        trace("template", "Field template copied", `Generated a ${state.meta.country} collection template with ${countrySchema().levels.map((level) => level.label).join(" > ")} administrative levels.`);
      }

      function bindStage(id) {
        if (id === "intake") {
          $("country").value = state.meta.country;
          $("language").value = state.meta.language;
          $("sourceType").value = state.meta.sourceType;
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
          $("copyTemplate").addEventListener("click", copyFieldTemplate);
          $("downloadCsvTemplate").addEventListener("click", () => {
            downloadText(`ndim-field-template-${state.meta.country.toLowerCase()}.csv`, fieldTemplateCsv(), "text/csv");
            trace("template", "CSV field template downloaded", "The CSV includes country-specific administrative columns and Q1-Q5 narrative columns.");
          });
          $("stageEvidence").addEventListener("click", () => {
            if (validateIntake()) goStep(1);
          });
          $("resetIntake").addEventListener("click", () => {
            state.text = "";
            state.records = [];
            state.importedRecords = [];
            Object.keys(state.template).forEach((key) => { state.template[key] = ""; });
            state.completed.delete("intake");
            state.completed.delete("gate");
            trace("reset", "Intake reset", "Narrative text and staged observations were cleared.");
            render();
          });
          $("loadSample").addEventListener("click", () => {
            state.meta.country = "Rwanda";
            state.meta.province = "Southern Province";
            state.meta.district = "Nyamagabe";
            state.meta.sector = "Kamegeri sector / village";
            state.meta.language = "rw";
            state.template.interviewId = "RW-NYA-001";
            state.template.respondentProfile = "35-44, female, farmer";
            state.template.decisionMaker = "yes";
            state.template.cookingMethods = "firewood; charcoal";
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
            trace("sample", "Template sample loaded", "A Rwanda pressure-cooker interview sample was loaded into Q1-Q5 and coding fields.");
            toast("Sample loaded");
            render();
          });
          $("fileInput").addEventListener("change", async (event) => {
            const file = event.target.files && event.target.files[0];
            if (!file) return;
            const text = await file.text();
            if (file.name.toLowerCase().endsWith(".csv")) {
              state.meta.sourceType = "csv";
              state.meta.sourceName = file.name;
              state.importedRecords = recordsFromCsv(text, file.name);
              state.records = state.importedRecords;
              state.text = state.records.map((record) => record.text).join("\n\n");
              $("narrativeText").value = state.text;
              $("sourceType").value = "csv";
              $("sourceName").value = file.name;
              trace("csv", "CSV batch imported", `${state.records.length} narrative row(s) imported from ${file.name}. You can still edit text before staging.`);
            } else {
              state.importedRecords = [];
              $("narrativeText").value = text;
              trace("file", "File loaded", `${file.name} loaded into the intake form.`);
            }
            toast("File loaded");
          });
        }
        if (id === "gate") {
          $("copyGateTemplate").addEventListener("click", copyFieldTemplate);
          $("downloadGateCsv").addEventListener("click", () => {
            downloadText(`ndim-field-template-${state.meta.country.toLowerCase()}.csv`, fieldTemplateCsv(), "text/csv");
            trace("template", "CSV field template downloaded from gate", "The SDMX gate exported a field-ready template with Q1-Q5 narrative columns.");
          });
        }
        if (id === "encoding") {
          $("llmProvider").value = state.llmProvider;
          $("llmProvider").addEventListener("change", (event) => {
            state.llmProvider = event.target.value;
            trace("choice", "LLM provider selected", `Selected ${state.llmProvider}. Backend currently supports OpenAI when configured and deterministic fallback otherwise.`);
          });
          document.querySelectorAll("[data-mode]").forEach((button) => {
            button.addEventListener("click", () => {
              state.encodingMode = button.dataset.mode;
              trace("choice", "Encoding mode selected", `Selected ${state.encodingMode}.`);
              render();
            });
          });
          document.querySelectorAll("[data-score]").forEach((input) => {
            input.addEventListener("input", () => {
              state.manualScores[input.dataset.score] = Number(input.value);
              render();
            });
          });
          const prev = $("prevStory");
          const next = $("nextStory");
          if (prev) prev.addEventListener("click", () => { state.manualIndex = Math.max(0, state.manualIndex - 1); render(); });
          if (next) next.addEventListener("click", () => { state.manualIndex = Math.min(Math.max(0, state.records.length - 1), state.manualIndex + 1); render(); });
          $("runEncoding").addEventListener("click", runEncoding);
          $("runCurrentEncoding").addEventListener("click", runCurrentEncoding);
          $("runAllEncodingModes").addEventListener("click", runAllEncodingModes);
        }
        if (id === "compartmental") $("runCompartmental").addEventListener("click", runCompartmental);
        if (id === "agents") $("runAgents").addEventListener("click", runAgents);
        if (id === "digital") $("runDigital").addEventListener("click", runDigital);
        if (id === "bayes") $("runBayes").addEventListener("click", runBayes);
        if (id === "rl") $("runRL").addEventListener("click", runRL);
        if (id === "regional") $("runRegional").addEventListener("click", runRegional);
        if (id === "graph") $("buildGraph").addEventListener("click", runKnowledgeGraph);
        if (id === "inoculation") $("runInoculation").addEventListener("click", runInoculationLab);
        if (id === "feeds") {
          $("loadFeedSample").addEventListener("click", () => {
            $("socialFeedInput").value = [
              "I heard the new stove needs fuel that is impossible to find in Musanze.",
              "A neighbour says health workers explained the smoke risk and the stove cooked beans faster.",
              "Some sellers claim clean cooking is only for rich households, not ordinary families."
            ].join("\\n");
            trace("sample", "Experimental feed sample loaded", "Three social-listening style posts were inserted into the sandbox.");
          });
          $("runFeeds").addEventListener("click", runExperimentalFeeds);
        }
        if (id === "policy") {
          $("runPolicy").addEventListener("click", runPolicy);
          $("copyPolicy").addEventListener("click", async () => {
            await navigator.clipboard.writeText(JSON.stringify(policyJson(), null, 2));
            toast("Policy JSON copied");
          });
        }
      }

      function modelParams(extra = {}) {
        const trustBase = avg(state.encoded.map((item) => item.trust_score), 0.6);
        const barrierBase = avg(state.encoded.map((item) => item.adoption_barrier_score), 0.35);
        const trust = Math.max(0, Math.min(1, state.bayes?.trustMean ?? (trustBase + (state.digital ? state.feedback.trustDelta : 0))));
        const barrier = Math.max(0, Math.min(1, state.bayes?.barrierMean ?? (barrierBase + (state.digital ? state.feedback.barrierDelta : 0))));
        const confidence = avg(state.encoded.map((item) => item.confidence), 0.5);
        const rlBonus = state.rl?.interventionBonus || 0;
        return {
          trust_score: trust,
          barrier_score: barrier,
          narrative_influence: 0.2 + 0.35 * confidence,
          intervention_strength: Math.min(0.8, 0.1 + 0.2 * trust + rlBonus),
          ...extra
        };
      }

      async function runEncoding() {
        if (!state.records.length && !validateIntake()) return;
        setStatus("running");
        trace("api", "Calling encoder", `POST /encode?mode=${state.encodingMode}&provider=${state.llmProvider} with ${state.records.length} record(s).`);
        try {
          const response = await fetch(`/encode?mode=${encodeURIComponent(state.encodingMode)}&provider=${encodeURIComponent(state.llmProvider)}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(state.records)
          });
          if (!response.ok) throw new Error(`Backend returned ${response.status}`);
          state.encoded = await response.json();
          state.encodingRuns[state.encodingMode] = state.encoded;
          state.completed.add("encoding");
          setStatus("complete");
          trace("result", "Encoding complete", `Returned ${state.encoded.length} encoded narrative(s).`);
          toast("Encoding complete");
          render();
        } catch (error) {
          setStatus("error");
          trace("error", "Encoding failed", error.message || "Unknown error");
        }
      }

      async function runCurrentEncoding() {
        if (!state.records.length && !validateIntake()) return;
        const record = state.records[state.manualIndex];
        if (!record) return;
        setStatus("running");
        trace("api", "Encoding one story", `Encoding story ${state.manualIndex + 1} of ${state.records.length} with ${state.encodingMode}.`);
        try {
          const response = await fetch(`/encode?mode=${encodeURIComponent(state.encodingMode)}&provider=${encodeURIComponent(state.llmProvider)}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify([record])
          });
          if (!response.ok) throw new Error(`Backend returned ${response.status}`);
          const [encoded] = await response.json();
          state.encoded = state.encoded.filter((item) => item.narrative_id !== encoded.narrative_id).concat(encoded);
          state.encodingRuns[state.encodingMode] = state.encoded;
          state.completed.add("encoding");
          state.manualIndex = Math.min(state.records.length - 1, state.manualIndex + 1);
          setStatus("complete");
          trace("result", "Story encoded", `${encoded.narrative_id} encoded. Moved to next story for manual review.`);
          toast("Story encoded");
          render();
        } catch (error) {
          setStatus("error");
          trace("error", "Story encoding failed", error.message || "Unknown error");
        }
      }

      async function runAllEncodingModes() {
        if (!state.records.length && !validateIntake()) return;
        const originalMode = state.encodingMode;
        for (const mode of ["manual", "ai", "hybrid"]) {
          state.encodingMode = mode;
          setStatus("running");
          trace("api", "Comparing encoder", `Running ${mode} encoder for ${state.records.length} narrative(s).`);
          const response = await fetch(`/encode?mode=${encodeURIComponent(mode)}&provider=${encodeURIComponent(state.llmProvider)}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(state.records)
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

      function runBayes() {
        ["trustA", "trustB", "barrierA", "barrierB"].forEach((key) => {
          state.priors[key] = Number($(key)?.value || state.priors[key]);
        });
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
        state.completed.add("bayes");
        trace("bayes", "Posterior updated", `Trust posterior ${fmtPct(state.bayes.trustMean)}, barrier posterior ${fmtPct(state.bayes.barrierMean)}.`);
        toast("Posterior updated");
        render();
      }

      function runRL() {
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
        const q = Object.fromEntries(actions.map((action) => [action.name, 0]));
        const history = [];
        const trust = state.bayes?.trustMean ?? avg(state.encoded.map((item) => item.trust_score), 0.6);
        const barrier = state.bayes?.barrierMean ?? avg(state.encoded.map((item) => item.adoption_barrier_score), 0.35);
        for (let episode = 1; episode <= episodes; episode += 1) {
          const explore = Math.random() < epsilon;
          const action = explore
            ? actions[Math.floor(Math.random() * actions.length)]
            : actions.slice().sort((a, b) => q[b.name] - q[a.name])[0];
          const reward = action.lift + trust * 0.35 - Math.max(0, barrier + action.barrier) * 0.22 - action.cost;
          const nextBest = Math.max(...Object.values(q));
          q[action.name] = q[action.name] + alpha * (reward + gamma * nextBest - q[action.name]);
          if (episode % Math.max(1, Math.floor(episodes / 24)) === 0 || episode === episodes) {
            history.push({ episode, action: action.name, reward });
          }
        }
        const bestAction = Object.entries(q).sort((a, b) => b[1] - a[1])[0];
        const bestSpec = actions.find((action) => action.name === bestAction[0]);
        state.rl = {
          episodes,
          bestAction: bestAction[0],
          bestReward: bestAction[1],
          q,
          history,
          interventionBonus: Math.max(0, bestSpec?.lift || 0) * 0.35
        };
        state.completed.add("rl");
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
        state.inoculation = {
          audience,
          tone,
          provider: state.llmProvider,
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
          ]
        };
        state.completed.add("inoculation");
        trace("inoculation", "Counter-narratives generated", `Generated ${state.inoculation.items.length} inoculation drafts using ${state.llmProvider} as the selected provider path.`);
        toast("Inoculation narratives ready");
        render();
      }

      function runExperimentalFeeds() {
        const raw = $("socialFeedInput")?.value || "";
        const platform = $("feedPlatform")?.value || "twitter";
        const region = $("feedRegion")?.value || state.meta.district || state.meta.country;
        const lines = raw.split(/\n+/).map((line) => line.trim()).filter(Boolean);
        if (!lines.length) {
          toast("Paste or load feed posts first");
          trace("blocked", "No social feed input", "The experimental sandbox needs one post per line.");
          return;
        }
        const riskWords = ["expensive", "impossible", "scam", "rich", "fuel", "fake", "doubt", "not ordinary"];
        const items = lines.map((text) => {
          const signals = riskWords.filter((word) => text.toLowerCase().includes(word));
          return { platform, region, text, signals: signals.length ? signals : ["general sentiment"], risk: signals.length >= 2 ? "high" : signals.length ? "medium" : "low" };
        });
        const high = items.filter((item) => item.risk !== "low");
        const counters = (high.length ? high : items.slice(0, 2)).map((item, index) => ({
          type: "experimental counter-feed",
          audience: region,
          title: `Counter ${index + 1}: ${item.signals[0] || "general"}`,
          text: `A careful response to this ${item.platform} post should acknowledge the concern, show local evidence, name a trusted source, and invite verification through a demonstration or field officer rather than arguing online.`,
          components: ["experimental", "not core evidence", ...item.signals.slice(0, 3)]
        }));
        state.feeds = { raw, platform, region, items, counters };
        state.completed.add("feeds");
        trace("experimental", "Feed sandbox analysed", `${items.length} post(s) classified; ${counters.length} counter-feed concepts generated for research review.`);
        toast("Experimental feed analysed");
        render();
      }

      async function runPolicy() {
        if (!state.records.length && !validateIntake()) return;
        if (!state.encoded.length) await runEncoding();
        setStatus("running");
        trace("api", "Calling full policy pipeline", `POST /pipeline/run?mode=${state.encodingMode}.`);
        try {
          const response = await fetch(`/pipeline/run?mode=${encodeURIComponent(state.encodingMode)}&provider=${encodeURIComponent(state.llmProvider)}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(state.records)
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
          if (validateIntake()) {
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
          feeds: runExperimentalFeeds,
          policy: runPolicy
        };
        const runner = runners[id];
        if (!runner) return;
        await runner();
      }

      $("backButton").addEventListener("click", () => goStep(state.step - 1));
      $("nextButton").addEventListener("click", nextStep);
      $("resetStageButton").addEventListener("click", resetCurrentStage);
      $("quickRunButton").addEventListener("click", runCurrentStageShortcut);
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

      renderTrace();
      render();
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
      <p>This manual explains how to run the Narrative Diffusion and Inoculation Model workflow from evidence ingestion to policy output.</p>

      <h2>1. Narrative intake</h2>
      <p>Select country, province, district, source type, source name, period, and language. Paste narratives or upload TXT/MD/CSV. CSV files should contain a <code>narrative</code>, <code>text</code>, <code>quote</code>, <code>story</code>, or <code>content</code> column.</p>
      <pre>country,district,narrative
Rwanda,Musanze,"Health workers are trusted, but stove cost remains high."</pre>

      <h2>2. SDMX gate</h2>
      <p>The gate checks whether each narrative has enough context to become a traceable observation. The payload is shown in plain language so non-technical users can understand what is being passed to the model.</p>

      <h2>3. Encoding</h2>
      <div class="grid">
        <div class="card"><h3>Manual / rule-based</h3><p>Transparent fallback scoring. Useful for audits and for offline demos.</p></div>
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
      <p><strong>NDIM</strong> means <strong>Narrative Diffusion and Inoculation Model</strong>. The engine turns field narratives into traceable model inputs, runs population and household simulations, updates beliefs with evidence, and produces a policy recommendation with an audit trail.</p>
      <div class="callout"><p><strong>Simple reading:</strong> the tool asks, "What are people saying, how should we encode it, how does that narrative change adoption dynamics, what did the field data correct, and which policy action is most robust?"</p></div>

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
          <tr><td>12 Experimental feeds</td><td>Sandbox social feed ingestion and counter-feed design.</td><td>Research prototype output, not core evidence.</td></tr>
          <tr><td>13 Policy output</td><td>Create a reviewable decision brief.</td><td>Recommendation plus evidence trail.</td></tr>
        </tbody>
      </table>

      <h2>1. Narrative intake</h2>
      <p>Select country, province or region, district, source type, source name, period, and language. Paste multi-paragraph narratives or upload TXT, MD, CSV, JSON, XML, or SDMX files. CSV files should contain a <code>narrative</code>, <code>text</code>, <code>quote</code>, <code>story</code>, or <code>content</code> column.</p>
      <pre>country,district,period,source_name,narrative
Rwanda,Musanze,2026,community-consultation,"Health workers are trusted, but stove cost remains high."</pre>
      <p>For batch imports, use <strong>Encode current story</strong> to review one narrative at a time, or <strong>Run selected encoder</strong> to encode the entire batch.</p>

      <h2>2. SDMX gate</h2>
      <p>The SDMX gate treats every narrative as an observation with dimensions, attributes, and measures. This keeps qualitative evidence from entering the scientific model without provenance.</p>
      <pre>Observation_i = {
  dimensions: { country, admin_unit, period, language },
  attributes: { source_type, source_name, provenance },
  measure: { narrative_text },
  tags: [encoding_mode, source_type]
}</pre>
      <p>The gate passes when required fields are present. It does not claim the narrative is true; it only confirms that the evidence is traceable.</p>

      <h2>3. Encoding derivation</h2>
      <div class="grid">
        <div class="card"><h3>Manual / rule-based</h3><p>Transparent local scoring for audits, offline use, and reproducible demos.</p></div>
        <div class="card"><h3>AI encoder</h3><p>Uses the selected LLM provider when configured. If no key is available, the backend falls back safely.</p></div>
        <div class="card"><h3>Hybrid review</h3><p>Combines model scoring with a human-review flag so policy users can inspect sensitive results.</p></div>
        <div class="card"><h3>Comparison mode</h3><p>Runs manual, AI, and hybrid encoders and displays trust, barrier, confidence, and theme differences.</p></div>
      </div>
      <p>Each narrative <code>i</code> is converted into bounded scores:</p>
      <table>
        <thead><tr><th>Symbol</th><th>Meaning</th><th>Interpretation</th></tr></thead>
        <tbody>
          <tr><td>E_i</td><td>Emotional salience</td><td>How strongly the narrative may move attention or concern.</td></tr>
          <tr><td>C_i</td><td>Cultural resonance</td><td>How well the narrative fits local norms, trusted messengers, and lived experience.</td></tr>
          <tr><td>tau_i</td><td>Trust alignment</td><td>Whether the narrative supports trust in clean-cooking evidence or messengers.</td></tr>
          <tr><td>kappa_i</td><td>Narrative arc</td><td>Whether the story has a coherent problem, cause, and resolution.</td></tr>
        </tbody>
      </table>
      <pre>Phi_i = 0.30 E_i + 0.30 C_i + 0.20 tau_i + 0.20 kappa_i

trust_score = mean(tau_i)
barrier_score = mean(encoded barrier_i)
confidence = mean(encoder confidence_i)</pre>
      <p><code>Phi</code> is a narrative-strength index. It increases truth diffusion when trust and cultural fit are strong, and slows adoption when barrier narratives dominate.</p>

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

      <h2>12. Experimental social feed sandbox</h2>
      <p>The experimental feed section is intentionally not part of the core evidence pipeline. It is a sandbox for future connectors to Twitter/X, Facebook, LinkedIn, WhatsApp summaries, radio call-ins, or community moderation feeds. Live platform ingestion needs consent, privacy controls, rate-limit handling, and provenance rules.</p>
      <pre>feed_post -> narrative risk classifier -> theme/risk labels
theme/risk labels -> counter-feed generator
counter-feed -> human review -> optional field test</pre>
      <p><strong>Counter-feed design:</strong> acknowledge the concern, identify the misleading frame, provide local evidence, name a trusted source, and invite verification. The goal is not to win an argument online; it is to reduce susceptibility to a harmful narrative before it diffuses.</p>

      <h2>13. Policy output and feedback loop</h2>
      <p>The final output is a reviewable decision brief, not an automatic decision. It includes metadata, encoding mode, LLM provider selection, encoded narratives, compartmental summary, agent summary, digital twin summary, Bayesian posterior, RL policy, regional analysis, knowledge graph, inoculation drafts, and recommendation text.</p>
      <pre>narratives -> encoding -> model parameters
model parameters -> ODE and ABM trajectories
field feedback -> digital twin rerun
digital twin + encoded evidence -> Bayesian posterior
posterior -> RL policy search
regional analysis -> place-sensitive intervention
knowledge graph -> repeated story structures
inoculation lab -> counter-narrative drafts
all outputs -> policy brief</pre>
      <p>For novice users, follow the buttons stage by stage and read the implication notes. For expert users, inspect equations, priors, graph structure, and reward curves. For policy makers, focus on the recommendation, evidence trail, uncertainty, feasibility, and whether the recommended intervention matches the target region.</p>
      <p class="small">Version note: the current backend simulates adoption trajectories directly. The UI documents the richer NDIM scientific structure and shows the measurable trajectory available from the running API.</p>
    </main>
  </body>
</html>
"""
