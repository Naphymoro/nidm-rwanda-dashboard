WORKFLOW_UI_HTML = r"""<!doctype html>
<html lang="en" data-theme="light">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>NDIM Engine Stepwise Workflow</title>
    <link rel="icon" href="data:," />
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css" />
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"></script>
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
        position: sticky;
        top: 0;
        height: 100vh;
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
      .assistant-panel {
        position: fixed;
        z-index: 59;
        top: 18px;
        right: 18px;
        bottom: 18px;
        width: min(420px, calc(100vw - 28px));
        border: 1px solid var(--line);
        border-radius: 18px;
        background: var(--panel);
        box-shadow: 0 24px 80px rgba(20, 17, 14, .18);
        display: flex;
        flex-direction: column;
        transform: translateX(calc(100% + 28px));
        transition: transform .2s ease;
        overflow: hidden;
      }
      .assistant-panel.open {
        transform: translateX(0);
      }
      .floating-assistant {
        position: fixed;
        right: 24px;
        bottom: 24px;
        z-index: 74;
        width: 58px;
        height: 58px;
        border: 1px solid var(--line-strong);
        border-radius: 999px;
        background: var(--ink);
        color: #fff;
        display: inline-grid;
        place-items: center;
        box-shadow: 0 18px 48px rgba(20, 17, 14, .24);
        cursor: pointer;
      }
      .floating-assistant:hover,
      .floating-assistant:focus {
        background: var(--ink);
        color: #fff;
        transform: translateY(-1px);
      }
      .floating-assistant .ui-icon {
        width: 25px;
        height: 25px;
      }
      .floating-assistant span {
        position: absolute;
        width: 1px;
        height: 1px;
        overflow: hidden;
        clip: rect(0 0 0 0);
      }
      .assistant-body {
        padding: 16px;
        overflow: auto;
        display: grid;
        gap: 12px;
      }
      .assistant-card {
        border: 1px solid var(--line);
        border-radius: 14px;
        background: var(--card);
        padding: 13px;
      }
      .assistant-card h3 {
        margin: 0 0 6px;
        font-size: 15px;
      }
      .assistant-card p,
      .assistant-card li {
        color: var(--muted);
        font-size: 13.5px;
        line-height: 1.45;
      }
      .assistant-progress {
        display: grid;
        gap: 7px;
      }
      .assistant-progress div {
        display: grid;
        grid-template-columns: minmax(0, 1fr) auto;
        gap: 10px;
        align-items: center;
        border-bottom: 1px solid var(--line);
        padding-bottom: 6px;
      }
      .assistant-progress span {
        color: var(--soft);
        font: 10px var(--font-data);
        letter-spacing: .08em;
        text-transform: uppercase;
      }
      .assistant-progress strong {
        font: 800 12px var(--font-data);
      }
      .workspace-chip {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        border: 1px solid var(--line);
        border-radius: 999px;
        background: var(--panel-2);
        color: var(--text);
        padding: 9px 12px;
        min-height: 38px;
      }
      .workspace-chip span {
        max-width: 210px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
      .workspace-modal {
        position: fixed;
        z-index: 80;
        inset: 0;
        display: none;
        align-items: center;
        justify-content: center;
        padding: 18px;
        background: rgba(20, 17, 14, .42);
      }
      .workspace-modal.open {
        display: flex;
      }
      .workspace-dialog {
        width: min(940px, 100%);
        max-height: calc(100vh - 36px);
        overflow: auto;
        border: 1px solid var(--line);
        border-radius: 22px;
        background: var(--panel);
        color: var(--text);
        box-shadow: 0 28px 90px rgba(0,0,0,.28);
      }
      .workspace-dialog header {
        display: flex;
        justify-content: space-between;
        gap: 14px;
        align-items: flex-start;
        padding: 20px;
        border-bottom: 1px solid var(--line);
      }
      .workspace-dialog-body {
        padding: 20px;
        display: grid;
        gap: 16px;
      }
      .workspace-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
        gap: 12px;
      }
      .workspace-list {
        display: grid;
        gap: 10px;
      }
      .workspace-list-item {
        display: grid;
        grid-template-columns: 46px minmax(0, 1fr) auto;
        gap: 12px;
        align-items: center;
        border: 1px solid var(--line);
        border-radius: 16px;
        background: var(--card);
        padding: 12px;
      }
      .workspace-list-item.active {
        border-color: var(--line-strong);
        box-shadow: inset 3px 0 0 var(--line-strong);
      }
      .workspace-list-item.from-scratch {
        background: color-mix(in srgb, var(--panel-2) 88%, var(--card));
      }
      .workspace-list-icon {
        width: 44px;
        height: 44px;
        display: grid;
        place-items: center;
        border: 1px solid var(--line);
        border-radius: 14px;
        background: var(--panel);
      }
      .workspace-list-item h3,
      .workspace-list-item p {
        margin: 0;
      }
      .workspace-list-item p {
        color: var(--muted);
        line-height: 1.35;
      }
      .workspace-list-actions {
        display: flex;
        gap: 8px;
        align-items: center;
      }
      .workspace-card {
        border: 1px solid var(--line);
        border-radius: 16px;
        background: var(--card);
        padding: 14px;
        display: grid;
        gap: 10px;
      }
      .workspace-card-actions {
        display: grid;
        grid-template-columns: minmax(0, 1fr) auto;
        gap: 8px;
        align-items: stretch;
      }
      .workspace-card.active {
        border-color: var(--line-strong);
        box-shadow: inset 3px 0 0 var(--line-strong);
      }
      .workspace-card h3 {
        margin: 0;
      }
      .icon-only {
        width: 42px;
        min-width: 42px;
        height: 42px;
        padding: 0;
        display: inline-grid;
        place-items: center;
      }
      .icon-only .ui-icon {
        width: 18px;
        height: 18px;
      }
      .workspace-form-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 10px;
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
        flex: 1;
        min-height: 0;
        padding: 14px;
        overflow: auto;
      }
      .stage-scroll-hint {
        margin: -3px 0 10px;
        color: var(--muted);
        font-size: 11.5px;
        line-height: 1.35;
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
      .app.workspace-start-mode .stepper,
      .app.workspace-start-mode #stageJumpSelect,
      .app.workspace-start-mode #quickRunButton,
      .app.workspace-start-mode #toggleTraceButton,
      .app.workspace-start-mode .run-status {
        display: none;
      }
      .app.workspace-start-mode .sidebar-footer {
        margin-top: 0;
      }
      .start-hint {
        border: 1px dashed var(--line);
        border-radius: 14px;
        background: var(--panel-2);
        color: var(--muted);
        padding: 12px;
        font-size: 12px;
        line-height: 1.4;
      }
      .app.workspace-start-mode .stage-nav {
        display: none;
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
      .theme-icon-button {
        width: 38px;
        height: 38px;
        min-width: 38px;
        min-height: 38px;
        display: inline-grid;
        place-items: center;
        border: 1px solid var(--line);
        border-radius: 999px;
        background: var(--card);
        color: var(--text);
        padding: 0;
      }
      .theme-icon-button:hover,
      .theme-icon-button:focus {
        border-color: var(--line-strong);
        color: var(--text);
      }
      .theme-icon-button .ui-icon {
        width: 17px;
        height: 17px;
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
        background:
          linear-gradient(180deg, color-mix(in srgb, var(--panel) 96%, white), var(--panel));
        box-shadow: 0 18px 54px rgba(41, 33, 24, .07);
        padding: 0;
        overflow: visible;
      }
      .command-center + .stage-card {
        margin-top: 14px;
      }
      .command-center.science-os {
        background:
          linear-gradient(180deg, rgba(255,255,255,.82), transparent 360px),
          var(--panel);
      }
      :root[data-theme="dark"] .command-center.science-os {
        background:
          linear-gradient(180deg, rgba(255,255,255,.04), transparent 360px),
          var(--panel);
      }
      .science-os .workspace-launchpad {
        grid-template-columns: minmax(0, 1.35fr) minmax(330px, .72fr);
        gap: 14px;
        padding: 18px;
        border-bottom: 1px solid var(--line);
        background:
          radial-gradient(circle at 10% 12%, rgba(183, 145, 88, .13), transparent 24%),
          radial-gradient(circle at 90% 8%, rgba(20, 17, 14, .05), transparent 28%),
          linear-gradient(135deg, rgba(255,255,255,.72), rgba(245,239,228,.48));
      }
      :root[data-theme="dark"] .science-os .workspace-launchpad {
        background:
          radial-gradient(circle at 10% 12%, rgba(214, 189, 149, .08), transparent 24%),
          linear-gradient(135deg, rgba(255,255,255,.04), transparent 62%);
      }
      .science-os .workspace-prime,
      .science-os .workspace-switcher,
      .science-os .agent-cockpit,
      .os-stage-card,
      .os-repository-card,
      .os-assistant-card,
      .os-metric {
        border: 1px solid var(--line);
        border-radius: 18px;
        background: color-mix(in srgb, var(--card) 92%, var(--panel));
      }
      .science-os .workspace-prime {
        padding: clamp(18px, 2.3vw, 28px);
      }
      .science-os .workspace-title-row h2 {
        max-width: 780px;
        font-size: clamp(38px, 5.5vw, 76px);
        line-height: .94;
        letter-spacing: -.04em;
      }
      .science-os .workspace-title-row p {
        max-width: 780px;
        margin-top: 14px;
        font-size: clamp(15px, 1.35vw, 20px);
        line-height: 1.48;
      }
      .science-os .workspace-badge {
        background: var(--ink);
        color: var(--paper);
        border-color: var(--ink);
      }
      .workspace-context-card {
        margin-top: 16px;
        border: 1px solid var(--line);
        border-radius: 16px;
        background: color-mix(in srgb, var(--card) 88%, var(--panel));
        padding: 13px 14px;
        max-width: 860px;
        box-shadow: inset 3px 0 0 var(--line-strong);
      }
      .workspace-context-card span {
        display: block;
        color: var(--soft);
        font: 850 10px var(--font-data);
        letter-spacing: .12em;
        text-transform: uppercase;
        margin-bottom: 5px;
      }
      .workspace-context-card strong {
        display: block;
        color: var(--text);
        font-size: 18px;
        line-height: 1.15;
      }
      .workspace-context-card p {
        margin: 5px 0 0 !important;
        max-width: 760px !important;
        font-size: 13.5px !important;
        line-height: 1.45 !important;
      }
      .workspace-support-line {
        color: var(--muted) !important;
        font-size: clamp(14px, 1.12vw, 17px) !important;
        line-height: 1.45 !important;
        margin-top: 12px !important;
      }
      .workspace-capability-row {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 10px;
        margin-top: 16px;
      }
      .workspace-capability {
        border: 1px solid var(--line);
        border-radius: 15px;
        background: color-mix(in srgb, var(--panel-2) 88%, var(--card));
        padding: 12px;
        color: var(--muted);
        font-size: 12.5px;
        line-height: 1.42;
      }
      .workspace-capability strong {
        display: block;
        margin-bottom: 5px;
        color: var(--text);
        font-size: 13.5px;
      }
      .workspace-command-row {
        display: grid;
        grid-template-columns: minmax(180px, .65fr) minmax(0, 1fr);
        gap: 10px;
        align-items: stretch;
        margin-top: 16px;
      }
      .workspace-command-row .start-control {
        align-self: stretch;
      }
      .workspace-command-row .start-button {
        min-height: 54px;
      }
      .workspace-quick-actions {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 8px;
      }
      .workspace-quick-actions .button {
        min-height: 54px;
        justify-content: center;
      }
      .workspace-signal-row {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 14px;
      }
      .workspace-signal {
        border: 1px solid var(--line);
        border-radius: 999px;
        background: var(--panel-2);
        color: var(--muted);
        padding: 8px 11px;
        font: 850 10px var(--font-data);
        letter-spacing: .07em;
        text-transform: uppercase;
      }
      .workspace-signal strong {
        color: var(--text);
      }
      .science-os .workspace-side-stack {
        display: grid;
        grid-template-rows: auto 1fr;
        gap: 14px;
      }
      .science-os .workspace-switcher {
        padding: 14px;
      }
      .science-os .agent-cockpit {
        grid-template-columns: 68px minmax(0, 1fr);
        padding: 14px;
        align-content: start;
      }
      .science-os .agent-orb {
        width: 68px;
        height: 68px;
      }
      .os-phase-rail {
        padding: 13px 18px;
        border-bottom: 1px solid var(--line);
        background: color-mix(in srgb, var(--panel) 96%, white);
      }
      .os-phase-rail .flow-lane {
        border: 0;
        background: transparent;
        padding: 0;
      }
      .science-os .flow-card {
        min-height: 54px;
        border-radius: 999px;
        background: var(--card);
      }
      .os-workbench-grid {
        display: grid;
        grid-template-columns: minmax(0, 1.16fr) minmax(320px, .74fr);
        gap: 14px;
        padding: 18px;
        border-bottom: 1px solid var(--line);
      }
      .os-stage-card {
        padding: clamp(18px, 2.2vw, 28px);
      }
      .os-stage-card h2 {
        margin: 8px 0 10px;
        font-size: clamp(32px, 4.2vw, 62px);
        line-height: .98;
        letter-spacing: -.035em;
      }
      .os-stage-card p {
        max-width: 840px;
        color: var(--muted);
        font-size: clamp(15px, 1.2vw, 19px);
        line-height: 1.52;
      }
      .os-action-row {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-top: 18px;
      }
      .os-action-row .button {
        min-height: 48px;
        padding-inline: 18px;
      }
      .os-stage-insight-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 10px;
        margin-top: 20px;
      }
      .os-stage-insight {
        border: 1px solid var(--line);
        border-radius: 14px;
        background: var(--panel-2);
        padding: 12px;
      }
      .os-stage-insight strong {
        display: block;
        margin-bottom: 5px;
        font-size: 13px;
      }
      .os-stage-insight span {
        color: var(--muted);
        font-size: 12.5px;
        line-height: 1.42;
      }
      .os-right-column {
        display: grid;
        gap: 14px;
        align-content: start;
      }
      .os-assistant-card,
      .os-repository-card {
        padding: 14px;
      }
      .os-repository-card {
        grid-column: 1 / -1;
      }
      .os-assistant-card h3,
      .os-repository-card h3 {
        margin: 6px 0 8px;
        font-size: 19px;
        line-height: 1.15;
      }
      .os-assistant-card p,
      .os-repository-card p {
        margin: 0;
        color: var(--muted);
        font-size: 13px;
        line-height: 1.45;
      }
      .os-repository-table {
        display: grid;
        gap: 0;
        margin-top: 12px;
        border: 1px solid var(--line);
        border-radius: 13px;
        overflow: hidden;
      }
      .os-repository-row {
        display: grid;
        grid-template-columns: minmax(0, 1fr) minmax(90px, .55fr) minmax(100px, .7fr);
        gap: 8px;
        padding: 9px 10px;
        border-bottom: 1px solid var(--line);
        background: var(--panel);
        font-size: 12px;
      }
      .os-repository-row:last-child {
        border-bottom: 0;
      }
      .os-repository-row.header {
        background: var(--panel-2);
        color: var(--soft);
        font: 900 9px var(--font-data);
        letter-spacing: .08em;
        text-transform: uppercase;
      }
      .os-repository-row span {
        overflow: hidden;
        white-space: nowrap;
        text-overflow: ellipsis;
      }
      .os-metrics-bar {
        display: grid;
        grid-template-columns: repeat(7, minmax(0, 1fr));
        gap: 8px;
        padding: 16px 18px;
        border-bottom: 1px solid var(--line);
      }
      .os-metric {
        padding: 12px;
      }
      .os-metric span {
        display: block;
        color: var(--soft);
        font: 900 9px var(--font-data);
        letter-spacing: .1em;
        text-transform: uppercase;
      }
      .os-metric strong {
        display: block;
        margin-top: 6px;
        font: 900 24px var(--font-data);
        letter-spacing: .01em;
      }
      .os-system-drawer {
        margin: 0;
        border: 0;
        border-bottom: 1px solid var(--line);
        padding: 0;
      }
      .os-system-drawer summary {
        cursor: pointer;
        padding: 14px 18px;
        color: var(--muted);
        font: 900 11px var(--font-data);
        letter-spacing: .1em;
        text-transform: uppercase;
      }
      .os-system-drawer[open] summary {
        border-bottom: 1px solid var(--line);
      }
      .os-system-drawer-body {
        padding: 16px 18px;
      }
      .workspace-launchpad {
        display: grid;
        grid-template-columns: minmax(0, 1.45fr) minmax(330px, .8fr);
        gap: 12px;
        padding: 16px;
        border-bottom: 1px solid var(--line);
        background:
          radial-gradient(circle at 8% 10%, rgba(183, 145, 88, .10), transparent 28%),
          linear-gradient(135deg, rgba(255,255,255,.68), rgba(245, 239, 228, .52));
      }
      .workspace-prime,
      .workspace-switcher,
      .agent-cockpit {
        min-width: 0;
        border: 1px solid var(--line);
        border-radius: 18px;
        background: var(--card);
        padding: 14px;
      }
      .workspace-side-stack {
        min-width: 0;
        display: grid;
        gap: 12px;
      }
      .workspace-prime {
        display: grid;
        gap: 14px;
        align-content: start;
      }
      .workspace-title-row {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: 12px;
      }
      .workspace-title-row h2 {
        margin: 0;
        font-size: clamp(26px, 3vw, 42px);
        line-height: 1.02;
        letter-spacing: -.02em;
      }
      .workspace-title-row p {
        margin: 8px 0 0;
        color: var(--muted);
        max-width: 760px;
        line-height: 1.45;
      }
      .workspace-badge {
        flex: 0 0 auto;
        border: 1px solid var(--line);
        border-radius: 999px;
        background: var(--panel-2);
        padding: 8px 10px;
        color: var(--soft);
        font: 900 10px var(--font-data);
        letter-spacing: .1em;
        text-transform: uppercase;
      }
      .workspace-route-strip,
      .agent-action-row {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
      }
      .workspace-route-strip {
        align-items: center;
        border: 1px solid var(--line);
        border-radius: 14px;
        background: var(--panel-2);
        padding: 9px;
      }
      .workspace-route-label {
        flex: 0 0 auto;
        color: var(--soft);
        font: 900 9px var(--font-data);
        letter-spacing: .12em;
        text-transform: uppercase;
        padding: 0 3px;
      }
      .workspace-actions-card {
        border: 1px solid var(--line);
        border-radius: 16px;
        background: color-mix(in srgb, var(--card) 74%, var(--panel-2));
        padding: 10px;
      }
      .workspace-actions-card .eyebrow {
        margin-bottom: 8px;
      }
      .workspace-action-grid {
        display: grid;
        grid-template-columns: minmax(180px, .9fr) minmax(0, 1.35fr);
        gap: 10px;
        align-items: stretch;
      }
      .workspace-secondary-actions {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(128px, 1fr));
        gap: 8px;
      }
      .workspace-secondary-actions .button {
        min-height: 46px;
        border-radius: 13px;
        font-size: 13px;
        padding: 0 10px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 7px;
      }
      .start-control {
        position: relative;
        display: inline-grid;
        gap: 10px;
        align-self: start;
      }
      .start-button {
        display: inline-flex;
        align-items: center;
        gap: 7px;
        min-height: 48px;
        width: 100%;
        padding: 10px 16px;
        border-radius: 14px;
        font-size: 14px;
        justify-content: center;
      }
      .start-menu {
        width: min(420px, calc(100vw - 36px));
        border: 1px solid var(--line);
        border-radius: 18px;
        background: var(--panel);
        box-shadow: 0 22px 80px rgba(20, 17, 14, .18);
        padding: 10px;
        display: grid;
        gap: 8px;
      }
      .start-action {
        display: grid;
        grid-template-columns: 34px minmax(0, 1fr);
        gap: 10px;
        align-items: center;
        width: 100%;
        border: 1px solid var(--line);
        border-radius: 14px;
        background: var(--card);
        color: var(--text);
        padding: 10px;
        text-align: left;
      }
      .start-action:hover {
        border-color: var(--line-strong);
      }
      .start-action strong {
        display: block;
        font-size: 13px;
      }
      .start-action span {
        display: block;
        margin-top: 2px;
        color: var(--muted);
        font-size: 11.5px;
        line-height: 1.35;
      }
      .start-existing-list {
        display: grid;
        gap: 7px;
        margin-top: 2px;
        border-top: 1px solid var(--line);
        padding-top: 8px;
      }
      .ui-icon {
        width: 18px;
        height: 18px;
        stroke: currentColor;
        stroke-width: 1.8;
        stroke-linecap: round;
        stroke-linejoin: round;
        fill: none;
        flex: 0 0 auto;
      }
      .icon-cell {
        width: 34px;
        height: 34px;
        border: 1px solid var(--line);
        border-radius: 12px;
        background: var(--panel-2);
        display: grid;
        place-items: center;
        color: var(--ink);
      }
      .workspace-pill {
        border: 1px solid var(--line);
        border-radius: 999px;
        background: var(--panel);
        color: var(--muted);
        padding: 6px 9px;
        font: 850 9px var(--font-data);
        letter-spacing: .05em;
        text-transform: uppercase;
        line-height: 1.15;
        max-width: 190px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }
      .workspace-pill.more {
        color: var(--text);
        background: var(--card);
      }
      .workspace-pill.grade {
        margin-left: auto;
        color: var(--ink);
        background: color-mix(in srgb, var(--amber) 12%, var(--panel));
      }
      .workspace-switcher h3,
      .agent-cockpit h3 {
        margin: 0;
        font-size: 16px;
      }
      .workspace-switcher p,
      .agent-cockpit p {
        margin: 7px 0 0;
        color: var(--muted);
        font-size: 12.5px;
        line-height: 1.45;
      }
      .workspace-mini-list {
        display: grid;
        gap: 8px;
        margin-top: 12px;
      }
      .workspace-mini {
        display: grid;
        grid-template-columns: minmax(0, 1fr) auto;
        gap: 10px;
        align-items: center;
        width: 100%;
        text-align: left;
        border: 1px solid var(--line);
        border-radius: 14px;
        background: var(--panel);
        color: var(--text);
        padding: 10px;
      }
      .workspace-mini.active {
        border-color: var(--ink);
        box-shadow: inset 0 0 0 1px var(--ink);
      }
      .workspace-mini strong {
        display: block;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
      .workspace-mini span {
        display: block;
        margin-top: 3px;
        color: var(--soft);
        font: 800 10px var(--font-data);
        letter-spacing: .06em;
        text-transform: uppercase;
      }
      .workspace-mini b {
        width: 34px;
        height: 34px;
        border-radius: 50%;
        display: grid;
        place-items: center;
        border: 1px solid var(--line);
        background: var(--panel-2);
        font: 900 11px var(--font-data);
      }
      .agent-cockpit {
        display: grid;
        grid-template-columns: 78px minmax(0, 1fr);
        gap: 12px;
        align-items: start;
      }
      .agent-orb {
        width: 78px;
        height: 78px;
        border-radius: 50%;
        display: grid;
        place-items: center;
        background:
          radial-gradient(circle at center, var(--card) 0 58%, transparent 59%),
          conic-gradient(var(--ink) var(--pct), var(--line) 0);
        border: 1px solid var(--line);
      }
      .agent-orb strong {
        display: block;
        font: 900 21px var(--font-data);
        line-height: 1;
      }
      .agent-orb span {
        display: block;
        margin-top: 3px;
        color: var(--soft);
        font: 800 9px var(--font-data);
        letter-spacing: .1em;
        text-transform: uppercase;
        text-align: center;
      }
      .agent-worklist {
        grid-column: 1 / -1;
        display: grid;
        gap: 7px;
        margin-top: 2px;
      }
      .agent-worklist.compact {
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }
      .agent-workitem {
        display: grid;
        grid-template-columns: 18px minmax(0, 1fr) auto;
        gap: 8px;
        align-items: center;
        border: 1px solid var(--line);
        border-radius: 12px;
        background: var(--panel);
        padding: 8px;
      }
      .agent-workitem .agent-dot {
        width: 10px;
        height: 10px;
        border-radius: 99px;
        background: var(--soft);
        margin-left: 4px;
      }
      .agent-workitem.done .agent-dot {
        background: var(--green);
      }
      .agent-workitem strong {
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        font-size: 12px;
      }
      .agent-workitem span:last-child {
        color: var(--soft);
        font: 900 9px var(--font-data);
        letter-spacing: .08em;
        text-transform: uppercase;
      }
      .start-panels {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 12px;
        padding: 0 16px 16px;
      }
      .start-panel {
        border: 1px solid var(--line);
        border-radius: 16px;
        background: var(--card);
        padding: 14px;
      }
      .start-panel h3 {
        display: flex;
        align-items: center;
        gap: 8px;
        margin: 0 0 8px;
        font-size: 16px;
      }
      .start-panel p {
        color: var(--muted);
        margin: 0;
        font-size: 12.8px;
        line-height: 1.5;
      }
      .command-head,
      .workbench-overview {
        display: grid;
        grid-template-columns: minmax(0, .95fr) minmax(360px, .72fr);
        gap: 14px;
        align-items: start;
        padding: 16px;
      }
      .workbench-overview {
        grid-template-columns: minmax(0, 1fr) minmax(320px, .55fr);
        border-bottom: 1px solid var(--line);
        background: color-mix(in srgb, var(--panel) 97%, white);
      }
      .command-head h2,
      .workbench-overview h2 {
        margin: 0;
        max-width: 820px;
        font-size: clamp(24px, 2.15vw, 34px);
        line-height: 1.08;
        letter-spacing: -.015em;
      }
      .command-head p,
      .workbench-overview p {
        margin: 10px 0 0;
        max-width: 820px;
        color: var(--muted);
        font-size: 13px;
        line-height: 1.5;
      }
      .workbench-main,
      .workbench-next {
        min-width: 0;
        border: 1px solid var(--line);
        border-radius: 16px;
        background: var(--card);
        padding: 14px;
      }
      .workbench-next {
        display: grid;
        gap: 10px;
        align-content: start;
      }
      .workbench-next h3 {
        margin: 0;
        font-size: 18px;
      }
      .workbench-tools {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 12px;
      }
      .workbench-tools .button {
        min-height: 36px;
      }
      .next-action-row {
        display: grid;
        grid-template-columns: 1fr;
        gap: 8px;
      }
      .next-action-row .button {
        justify-content: center;
      }
      .workbench-science-grid {
        display: grid;
        grid-template-columns: minmax(0, .95fr) minmax(320px, .55fr);
        gap: 14px;
        padding: 16px;
        border-bottom: 1px solid var(--line);
      }
      .workbench-science-grid > * {
        min-width: 0;
      }
      .current-intel {
        border: 1px solid var(--line);
        border-radius: 14px;
        background: var(--card);
        padding: 12px;
        min-width: 0;
      }
      .current-intel h3 {
        margin: 6px 0 0;
        font-size: 18px;
        line-height: 1.15;
      }
      .hero-side {
        display: grid;
        gap: 10px;
        min-width: 0;
      }
      .system-map-card {
        border: 1px solid var(--line);
        border-radius: 14px;
        background:
          radial-gradient(circle at 16% 12%, rgba(183, 145, 88, .12), transparent 28%),
          var(--card);
        padding: 12px;
        min-width: 0;
      }
      .system-map-head {
        display: flex;
        align-items: start;
        justify-content: space-between;
        gap: 10px;
        margin-bottom: 8px;
      }
      .system-map-head h3 {
        margin: 3px 0 0;
        font-size: 16px;
        line-height: 1.1;
      }
      .system-map-head p {
        margin: 3px 0 0;
        color: var(--muted);
        font-size: 11.5px;
        line-height: 1.35;
      }
      .system-map-scroll {
        overflow-x: auto;
        overflow-y: hidden;
        padding-bottom: 2px;
      }
      .system-map {
        display: block;
        width: 100%;
        min-width: 560px;
        height: auto;
      }
      .map-node {
        cursor: pointer;
        outline: none;
      }
      .map-node rect,
      .map-node path.node-shape {
        fill: var(--panel);
        stroke: var(--line);
        stroke-width: 1.4;
        transition: fill .16s ease, stroke .16s ease, transform .16s ease;
      }
      .map-node:hover rect,
      .map-node:focus rect,
      .map-node:hover path.node-shape,
      .map-node:focus path.node-shape {
        fill: color-mix(in srgb, var(--panel) 82%, white);
        stroke: var(--ink);
      }
      .map-node.active rect,
      .map-node.active path.node-shape {
        stroke: var(--ink);
        stroke-width: 2.2;
      }
      .map-node.ready rect,
      .map-node.ready path.node-shape {
        stroke: rgba(25, 135, 84, .55);
      }
      .map-node.twin rect,
      .map-node.twin path.node-shape {
        fill: color-mix(in srgb, var(--panel) 86%, rgba(25, 135, 84, .18));
        stroke: rgba(25, 135, 84, .72);
        stroke-dasharray: 5 4;
      }
      .map-node.twin.active rect,
      .map-node.twin.active path.node-shape {
        stroke: var(--ink);
        stroke-dasharray: 5 4;
      }
      .map-node.twin .map-chip {
        fill: var(--green);
      }
      .map-node.twin .map-chip-text {
        fill: var(--panel);
      }
      .map-node text {
        fill: var(--text);
        font-family: var(--font-ui);
        font-weight: 900;
        pointer-events: none;
      }
      .map-node text.sub {
        fill: var(--muted);
        font-family: var(--font-data);
        font-size: 10px;
        font-weight: 800;
        letter-spacing: .45px;
      }
      .map-arrow {
        fill: none;
        stroke: var(--soft);
        stroke-width: 1.8;
        stroke-linecap: round;
        stroke-linejoin: round;
        opacity: .82;
      }
      .map-loop {
        fill: none;
        stroke: rgba(88, 110, 92, .75);
        stroke-width: 2;
        stroke-dasharray: 5 5;
      }
      .map-twin-halo {
        fill: none;
        stroke: rgba(25, 135, 84, .24);
        stroke-width: 1.4;
        stroke-dasharray: 2 6;
      }
      .map-label {
        fill: var(--soft);
        font: 800 9px var(--font-data);
        letter-spacing: .75px;
        text-transform: uppercase;
      }
      .map-chip {
        fill: var(--ink);
      }
      .map-chip-text {
        fill: var(--panel);
        font: 900 10px var(--font-data);
        letter-spacing: .8px;
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
        grid-template-columns: repeat(auto-fit, minmax(145px, 1fr));
        gap: 8px;
        padding: 16px;
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
      .flow-lane.workbench-flow {
        background: color-mix(in srgb, var(--panel) 95%, white);
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
      .top-actions .button {
        min-height: 38px;
        padding: 8px 12px;
      }
      .stage-jump {
        width: min(330px, 42vw);
        min-height: 38px;
        border-radius: 999px;
        padding: 0 12px;
        font-weight: 800;
        background: var(--card);
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
      .stage-launcher {
        max-width: none;
        width: 100%;
        margin: 14px 0 0;
        border: 1px solid var(--line);
        border-radius: 18px;
        background:
          linear-gradient(135deg, rgba(255,255,255,.72), transparent 58%),
          var(--panel);
        padding: clamp(16px, 2.4vw, 24px);
        display: grid;
        grid-template-columns: minmax(0, 1.05fr) minmax(320px, .95fr);
        gap: 18px;
        align-items: stretch;
      }
      :root[data-theme="dark"] .stage-launcher {
        background:
          linear-gradient(135deg, rgba(255,255,255,.05), transparent 58%),
          var(--panel);
      }
      .stage-launcher h2 {
        margin: 0 0 8px;
        font-size: clamp(28px, 4vw, 52px);
        line-height: .98;
        letter-spacing: -.02em;
      }
      .stage-launcher p {
        color: var(--muted);
        line-height: 1.55;
      }
      .stage-launcher-actions {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-top: 16px;
      }
      .stage-launcher .button {
        min-height: 44px;
      }
      .stage-launcher-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 10px;
      }
      .stage-launcher-note {
        border: 1px solid var(--line);
        border-radius: 14px;
        background: var(--card);
        padding: 13px;
        min-height: 112px;
      }
      .stage-launcher-note strong {
        display: block;
        margin-bottom: 6px;
      }
      .stage-launcher-note span {
        display: block;
        color: var(--muted);
        font-size: 13px;
        line-height: 1.45;
      }
      .stage-workspace-backdrop {
        position: fixed;
        inset: 0;
        z-index: 88;
        display: none;
        background: rgba(20, 17, 14, .38);
        backdrop-filter: blur(3px);
      }
      .stage-workspace-backdrop.open {
        display: block;
      }
      .stage-workspace {
        position: fixed;
        z-index: 89;
        top: 18px;
        right: 18px;
        bottom: 18px;
        width: min(1180px, calc(100vw - 36px));
        border: 1px solid var(--line);
        border-radius: 22px;
        background: var(--panel);
        color: var(--text);
        box-shadow: 0 34px 120px rgba(20, 17, 14, .34);
        display: flex;
        flex-direction: column;
        overflow: hidden;
        transform: translateX(calc(100% + 42px));
        opacity: .3;
        pointer-events: none;
        transition: transform .24s ease, opacity .24s ease;
      }
      .stage-workspace.open {
        transform: translateX(0);
        opacity: 1;
        pointer-events: auto;
      }
      .stage-workspace-head {
        display: grid;
        grid-template-columns: minmax(0, 1fr) auto;
        gap: 16px;
        align-items: start;
        padding: 18px;
        border-bottom: 1px solid var(--line);
        background:
          linear-gradient(135deg, rgba(255,255,255,.78), transparent 70%),
          var(--panel);
      }
      :root[data-theme="dark"] .stage-workspace-head {
        background:
          linear-gradient(135deg, rgba(255,255,255,.05), transparent 70%),
          var(--panel);
      }
      .stage-workspace-head h2 {
        margin: 0 0 7px;
        font-size: clamp(24px, 3vw, 42px);
        line-height: 1;
      }
      .stage-workspace-head p {
        margin: 0;
        color: var(--muted);
        line-height: 1.45;
      }
      .stage-workspace-actions {
        display: flex;
        flex-wrap: wrap;
        justify-content: flex-end;
        gap: 8px;
      }
      .stage-workspace-body {
        flex: 1;
        min-height: 0;
        overflow: auto;
        padding: 18px;
      }
      .stage-workspace-body > .stage-card {
        border: 0;
        border-radius: 0;
        background: transparent;
        padding: 0;
      }
      .stage-workspace-body > .context-stage-nav {
        position: sticky;
        bottom: 0;
        z-index: 3;
        margin: 18px -18px -18px;
        padding: 12px 18px;
        border-top: 1px solid var(--line);
        background: color-mix(in srgb, var(--panel) 94%, transparent);
        backdrop-filter: blur(12px);
      }
      .stage-workspace-summary {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 10px;
      }
      .stage-workspace-summary span {
        border: 1px solid var(--line);
        border-radius: 999px;
        background: var(--card);
        padding: 7px 10px;
        color: var(--muted);
        font: 800 10px var(--font-data);
        text-transform: uppercase;
        letter-spacing: .07em;
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
        overflow-x: auto;
      }
      .equation.latex-display {
        font-size: 14px;
      }
      .equation .katex-display {
        margin: 0;
        overflow-x: auto;
        overflow-y: hidden;
        padding: 2px 0;
        text-align: left;
      }
      .equation .katex {
        color: var(--text);
        font-size: 1.04em;
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
        height: 240px;
      }
      .plot-grid-line {
        stroke: var(--line);
        stroke-width: 1;
      }
      .plot-axis-label {
        fill: var(--soft);
        font: 10px var(--font-data);
      }
      .plot-axis-title {
        fill: var(--muted);
        font: 11px var(--font-data);
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
        .workspace-launchpad, .workspace-side-stack, .workspace-command-row, .start-panels, .command-head, .workbench-overview, .workbench-science-grid, .os-workbench-grid, .intake-utility-grid, .compact-control-grid, .intake-step-grid, .intake-review-grid { grid-template-columns: 1fr; }
        .science-os .workspace-launchpad,
        .science-os .os-workbench-grid {
          grid-template-columns: 1fr;
        }
        .os-metrics-bar { grid-template-columns: repeat(3, minmax(0, 1fr)); }
        .os-stage-insight-grid { grid-template-columns: 1fr; }
        .flow-lane { grid-template-columns: repeat(3, minmax(0, 1fr)); }
        .chain-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
      }
      @media (max-width: 980px) {
        .app {
          --sidebar-w: 0px;
          grid-template-columns: 1fr;
        }
        .sidebar {
          position: static;
          height: auto;
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
        .app.workspace-start-mode .sidebar {
          display: grid;
          grid-template-columns: minmax(0, 1fr) minmax(260px, auto);
          align-items: center;
          gap: 12px;
          padding: 0 12px;
        }
        .app.workspace-start-mode .brand {
          min-height: 58px;
          height: auto;
          border-bottom: 0;
          padding: 0;
        }
        .app.workspace-start-mode .sidebar-footer {
          grid-template-columns: repeat(4, minmax(0, auto));
          align-items: center;
          border-top: 0;
          padding: 0;
        }
        .app.workspace-start-mode .sidebar-footer .eyebrow {
          margin: 0;
          white-space: nowrap;
        }
        .app.workspace-start-mode .sidebar-footer .button {
          min-height: 38px;
          padding: 8px 10px;
          white-space: nowrap;
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
        .app.workspace-start-mode .sidebar {
          display: block;
          padding: 0;
        }
        .app.workspace-start-mode .sidebar-footer {
          grid-template-columns: 1fr;
          padding: 10px 12px;
          border-top: 1px solid var(--line);
        }
        .topbar { align-items: flex-start; flex-direction: column; padding: 16px; }
        .top-actions, .top-actions .button, .run-status { width: 100%; justify-content: center; }
        .stage-jump { width: 100%; border-radius: 12px; }
        .content { --content-x: 14px; padding: 14px var(--content-x); }
        .stage-card { border-radius: 14px; }
        .command-center { border-radius: 0; }
        .stage-workspace {
          top: 10px;
          right: 10px;
          bottom: 10px;
          width: calc(100vw - 20px);
          border-radius: 18px;
        }
        .stage-workspace-head {
          grid-template-columns: 1fr;
          gap: 12px;
          padding: 14px;
        }
        .stage-workspace-actions {
          justify-content: stretch;
        }
        .stage-workspace-actions .button {
          flex: 1 1 180px;
        }
        .floating-assistant {
          right: 16px;
          bottom: 16px;
          width: 52px;
          height: 52px;
        }
        .stage-workspace-summary span {
          flex: 1 1 150px;
          text-align: center;
          overflow-wrap: anywhere;
        }
        .workspace-launchpad { padding: 12px; }
        .workspace-title-row { flex-direction: column; }
        .workspace-title-row h2 { font-size: clamp(30px, 10vw, 48px); }
        .workspace-badge { align-self: flex-start; }
        .workspace-quick-actions { grid-template-columns: 1fr; }
        .agent-cockpit { grid-template-columns: 1fr; }
        .agent-orb { width: 92px; height: 92px; }
        .agent-worklist.compact {
          grid-template-columns: 1fr;
        }
        .workspace-action-grid {
          grid-template-columns: 1fr;
        }
        .workspace-secondary-actions {
          grid-template-columns: 1fr;
        }
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
        .field-grid, .grid-3, .metric-grid, .command-metrics, .os-metrics-bar, .governance-grid, .compare-grid, .intake-utility-grid, .compact-control-grid, .intake-step-grid, .intake-review-grid, .compact-select-row { grid-template-columns: 1fr; }
        .os-repository-row { grid-template-columns: 1fr; }
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
        .stage-nav {
          position: sticky;
          bottom: 0;
          z-index: 45;
          margin: 14px calc(var(--content-x) * -1) -14px;
          padding: 10px var(--content-x);
          border-top: 1px solid var(--line);
          background: color-mix(in srgb, var(--panel) 94%, transparent);
          backdrop-filter: blur(12px);
        }
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
        .stage-launcher {
          grid-template-columns: 1fr;
          padding: 14px;
        }
        .stage-launcher-grid {
          grid-template-columns: 1fr;
        }
        .stage-workspace {
          inset: 0;
          width: 100vw;
          height: 100vh;
          border-radius: 0;
        }
        .stage-workspace-head {
          grid-template-columns: 1fr;
        }
        .stage-workspace-actions {
          justify-content: stretch;
        }
        .stage-workspace-actions .button {
          flex: 1 1 100%;
        }
      }
    </style>
  </head>
  <body>
    <div class="app" id="appShell">
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
          <p class="stage-scroll-hint">Click a stage to open its focused task workspace, or use Jump to stage in the top bar.</p>
          <div class="step-list" id="stepList"></div>
        </div>
        <div class="sidebar-footer">
          <p class="eyebrow">0.9.0-alpha.8</p>
          <a class="button" href="/academy" target="_blank" rel="noreferrer">NDIM Academy</a>
          <a class="button" href="/publication" target="_blank" rel="noreferrer">Scientific Publication</a>
          <a class="button" href="/manual" target="_blank" rel="noreferrer">Tool manual</a>
          <a class="button" href="/manual#source-access" target="_blank" rel="noreferrer">Source access</a>
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
            <button class="workspace-chip" id="workspaceButton" type="button" title="Open Workspace Manager">Workspace: <span id="workspaceName">loading</span></button>
            <a class="button" href="/manual" target="_blank" rel="noreferrer">Manual</a>
            <a class="button" href="/academy" target="_blank" rel="noreferrer">Academy</a>
            <a class="button" href="/publication" target="_blank" rel="noreferrer">Publication</a>
            <select id="stageJumpSelect" class="stage-jump" aria-label="Jump to workflow stage"></select>
            <button class="button primary" id="quickRunButton" type="button">Run current stage</button>
            <button class="button" id="toggleTraceButton" type="button">Activity log</button>
            <button class="theme-icon-button" id="themeIconToggle" type="button" aria-label="Switch to dark mode" title="Switch to dark mode"></button>
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
            <button class="button icon-only" id="closeTraceButton" type="button" aria-label="Close activity log" title="Close activity log">
              <svg class="ui-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M18 6 6 18"></path><path d="M6 6l12 12"></path></svg>
            </button>
          </div>
        </div>
        <div class="reason-body" id="traceBody"></div>
      </aside>
      <aside class="assistant-panel" id="assistantPanel">
        <div class="reason-head">
          <p class="eyebrow" id="assistantEyebrow">Research Assistant</p>
          <h2>Workflow guide</h2>
          <div class="button-row" style="margin-top: 10px;">
            <button class="button icon-only" id="closeAssistantButton" type="button" aria-label="Close research assistant" title="Close research assistant">
              <svg class="ui-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M18 6 6 18"></path><path d="M6 6l12 12"></path></svg>
            </button>
          </div>
        </div>
        <div class="assistant-body" id="assistantBody"></div>
      </aside>
    </div>
    <div class="toast" id="toast">Ready</div>
    <button class="floating-assistant" id="floatingAssistantButton" type="button" aria-label="Open research assistant" title="Open research assistant">
      <svg class="ui-icon" viewBox="0 0 24 24" aria-hidden="true">
        <path d="M12 3a7 7 0 0 0-7 7v3a4 4 0 0 0 4 4h1l2 3 2-3h1a4 4 0 0 0 4-4v-3a7 7 0 0 0-7-7z"></path>
        <path d="M9 10h.01"></path>
        <path d="M15 10h.01"></path>
        <path d="M9.5 13a4 4 0 0 0 5 0"></path>
      </svg>
      <span>Open research assistant</span>
    </button>
    <div class="workspace-modal" id="workspaceModal" aria-hidden="true">
      <div class="workspace-dialog" role="dialog" aria-modal="true" aria-labelledby="workspaceModalTitle">
        <header>
          <div>
            <p class="eyebrow">Workspace Manager</p>
            <h2 id="workspaceModalTitle">Project workspaces</h2>
            <p class="copy">Load, duplicate, import, export, or create a workspace. Records and templates stay separated by workspace.</p>
          </div>
          <button class="button icon-only" id="closeWorkspaceModal" type="button" aria-label="Close workspace manager" title="Close workspace manager">
            <svg class="ui-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M18 6 6 18"></path><path d="M6 6l12 12"></path></svg>
          </button>
        </header>
        <div class="workspace-dialog-body" id="workspaceModalBody"></div>
      </div>
    </div>
    <div class="stage-workspace-backdrop" id="stageWorkspaceBackdrop" aria-hidden="true"></div>
    <aside class="stage-workspace" id="stageWorkspace" role="dialog" aria-modal="true" aria-labelledby="stageWorkspaceTitle" aria-hidden="true">
      <header class="stage-workspace-head">
        <div>
          <p class="eyebrow" id="stageWorkspaceKicker">Focused stage task</p>
          <h2 id="stageWorkspaceTitle">Current stage</h2>
          <p id="stageWorkspaceCopy">Open the current workflow task.</p>
          <div class="stage-workspace-summary" id="stageWorkspaceSummary"></div>
        </div>
        <div class="stage-workspace-actions">
          <button class="button primary" id="runStagePrimaryAction" type="button">Run primary action</button>
          <button class="button icon-only" id="closeStageWorkspace" type="button" aria-label="Close focused task" title="Close focused task">
            <svg class="ui-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M18 6 6 18"></path><path d="M6 6l12 12"></path></svg>
          </button>
        </div>
      </header>
      <div class="stage-workspace-body" id="stageWorkspaceBody"></div>
    </aside>

    <script>
      const steps = [
        { id: "intake", num: "01", title: "Narrative intake", sub: "country, location, evidence" },
        { id: "gate", num: "02", title: "SDMX gate", sub: "validate input contract" },
        { id: "repository", num: "03", title: "Repository", sub: "review ledger and sync" },
        { id: "encoding", num: "04", title: "Encoding", sub: "manual, AI, hybrid" },
        { id: "compartmental", num: "05", title: "Compartmental model", sub: "S M T I R population flow" },
        { id: "agents", num: "06", title: "Agent-based model", sub: "households and peer effects" },
        { id: "digital", num: "07", title: "Digital twin", sub: "feedback into model" },
        { id: "bayes", num: "08", title: "Bayesian update", sub: "prior to posterior" },
        { id: "rl", num: "09", title: "RL optimizer", sub: "learn intervention policy" },
        { id: "regional", num: "10", title: "Regional analysis", sub: "isolate or group places" },
        { id: "graph", num: "11", title: "Knowledge graph", sub: "stories, themes, places" },
        { id: "inoculation", num: "12", title: "Inoculation lab", sub: "counter-narratives" },
        { id: "policy", num: "13", title: "Policy output", sub: "recommendation and audit" }
      ];

      const workflowPhases = [
        { icon: "EV", label: "Evidence", detail: "Narratives, SDMX gate, repository", step: 0, stages: ["intake", "gate", "repository"] },
        { icon: "EN", label: "Encode", detail: "Manual, AI, hybrid scoring", step: 3, stages: ["encoding"] },
        { icon: "MO", label: "Model", detail: "ODE and agent simulation", step: 4, stages: ["compartmental", "agents"] },
        { icon: "LR", label: "Learn", detail: "Twin, posterior, RL loop", step: 6, stages: ["digital", "bayes", "rl"] },
        { icon: "SY", label: "Synthesize", detail: "Regions, graph, inoculation", step: 9, stages: ["regional", "graph", "inoculation"] },
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

      const evidenceModes = [
        { id: "structured_interview", title: "Structured interview", short: "Q1-Q5 field protocol", detail: "Comparable enumerator-led interview data with respondent profile and post-interview coding." },
        { id: "focus_group", title: "Focus group", short: "Facilitated group discussion", detail: "Group discussion transcript, community dialogue, or FGD notes with facilitator context, speaker roles, consent, and group dynamics." },
        { id: "open_story", title: "Open story", short: "Multi-paragraph narrative", detail: "Community account, oral history, meeting note, or lived-experience story without forcing Q1-Q5." },
        { id: "indigenous_knowledge", title: "Indigenous knowledge", short: "Situated community knowledge", detail: "Local practice, seasonal memory, elder testimony, cultural explanation, or ecological observation." },
        { id: "citizen_science", title: "Citizen science report", short: "Community observation", detail: "Crowdsourced observation with place, time, confidence, validation, consent, and review status." },
        { id: "crowd_batch", title: "Crowdsourced batch", short: "Many stories at once", detail: "CSV or text batch from community submissions that needs moderation, deduplication, and approval." },
        { id: "experimental_feed", title: "Social Media Feeds", short: "Social/community feed evidence", detail: "X/Twitter, Facebook, LinkedIn, WhatsApp, YouTube, TikTok, Instagram, radio, community forums, or news comments. These are evidence inputs that must pass governance before modelling." },
        { id: "custom_evidence", title: "Other / custom evidence", short: "User-defined evidence route", detail: "Use this when a project has narrative, observation, document, media transcript, administrative note, or mixed evidence that does not fit the standard routes." }
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
          customRouteName: "",
          customEvidenceType: "narrative",
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
        intakeOption: "manual_entry",
        intakeImportMode: "manual_entry",
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
        inoculationDiagnoses: [],
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
        googleRepository: null,
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
          target: "Google Drive + Sheets research repository",
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
        workspace: {
          active: null,
          list: [],
          managerOpen: false,
          started: false,
          startOpen: false,
          startMode: "menu",
          assistantOpen: false,
          exportMode: "template_only"
        },
        stageWorkspace: {
          open: false
        },
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

      function workspaceSettings() {
        return state.workspace.active?.settings || {};
      }

      function workspaceName() {
        return state.workspace.active?.name || "NDIM Core";
      }

      function workspaceId() {
        return state.workspace.active?.workspace_id || "ndim-core";
      }

      function activeEvidenceModes() {
        const enabled = workspaceSettings().enabled_evidence_routes;
        if (!Array.isArray(enabled) || !enabled.length) return evidenceModes;
        const filtered = evidenceModes.filter((mode) => enabled.includes(mode.id));
        let modes = filtered.length ? filtered : evidenceModes;
        const focusGroup = evidenceModes.find((mode) => mode.id === "focus_group");
        if (focusGroup && !modes.some((mode) => mode.id === "focus_group")) {
          const structuredIndex = modes.findIndex((mode) => mode.id === "structured_interview");
          modes = structuredIndex >= 0
            ? [...modes.slice(0, structuredIndex + 1), focusGroup, ...modes.slice(structuredIndex + 1)]
            : [focusGroup, ...modes];
        }
        const custom = evidenceModes.find((mode) => mode.id === "custom_evidence");
        return custom && !modes.some((mode) => mode.id === "custom_evidence") ? [...modes, custom] : modes;
      }

      function workspaceStageLabel(step) {
        return workspaceSettings().stage_labels?.[step.id] || step.title;
      }

      function workspaceStageSub(step) {
        if (workspaceId() === "climatetales-rwanda") {
          const custom = {
            intake: "ethnography, digital listening",
            encoding: "risk, trust, messenger fit",
            compartmental: "influence simulation",
            digital: "field feedback loop",
            inoculation: "SBCC and counter-narratives",
            policy: "workshop and project reports"
          };
          return custom[step.id] || step.sub;
        }
        return step.sub;
      }

      function applyWorkspaceDefaults(workspace) {
        if (!workspace) return;
        const settings = workspace.settings || {};
        const countries = Array.isArray(settings.countries) && settings.countries.length ? settings.countries : null;
        if (countries && !countries.includes(state.meta.country)) state.meta.country = countries[0];
        if (settings.default_language) state.meta.language = settings.default_language;
        if (settings.default_source_type) state.meta.sourceType = settings.default_source_type;
        if (settings.default_period) state.meta.period = settings.default_period;
        if (settings.default_evidence_route) state.template.evidenceMode = settings.default_evidence_route;
        const consent = settings.consent_defaults || {};
        if (consent.visibility) state.governance.visibility = consent.visibility;
        if (consent.consent) state.governance.consent = consent.consent;
        if (consent.repository_mode) state.governance.repositoryMode = consent.repository_mode;
        const llm = settings.llm_defaults || {};
        if (llm.provider) state.llmProvider = llm.provider;
        const priors = settings.bayesian_priors || {};
        state.priors = { ...state.priors, ...priors };
        const enabled = activeEvidenceModes();
        if (!enabled.some((mode) => mode.id === state.template.evidenceMode)) {
          state.template.evidenceMode = enabled[0]?.id || "structured_interview";
        }
      }

      async function loadWorkspaceState() {
        try {
          const [active, list] = await Promise.all([
            apiJson("/workspaces/active"),
            apiJson("/workspaces")
          ]);
          state.workspace.active = active;
          state.workspace.list = list.workspaces || [];
          applyWorkspaceDefaults(active);
          trace("workspace", "Workspace loaded", `${workspaceName()} is active. Evidence, templates, model defaults, repository behavior, and assistant guidance now follow this workspace.`);
        } catch (error) {
          state.workspace.active = {
            workspace_id: "ndim-core",
            name: "NDIM Core",
            description: "Fallback local workspace.",
            settings: {}
          };
          trace("workspace", "Workspace service unavailable", error.message || "Using local fallback workspace.");
        }
      }

      async function setActiveWorkspace(workspaceId) {
        const active = await apiJson(`/workspaces/${encodeURIComponent(workspaceId)}/set-active`, { method: "POST" });
        const list = await apiJson("/workspaces");
        state.workspace.active = active;
        state.workspace.list = list.workspaces || [];
        applyWorkspaceDefaults(active);
        trace("workspace", "Workspace switched", `${workspaceName()} is now active. New evidence will use this workspace's defaults.`);
        toast("Workspace switched");
        render();
      }

      async function createWorkspaceFromManager() {
        const name = $("workspaceNewName")?.value?.trim();
        if (!name) {
          toast("Workspace name required");
          return;
        }
        const country = $("workspaceNewCountry")?.value?.trim();
        if (!country) {
          toast("Country required");
          return;
        }
        const payload = {
          name,
          description: $("workspaceNewDescription")?.value || "",
          country,
          domain: $("workspaceNewDomain")?.value?.trim() || "general narrative evidence"
        };
        const workspace = await apiJson("/workspaces", { method: "POST", body: JSON.stringify(payload) });
        await setActiveWorkspace(workspace.workspace_id);
        startWorkspaceSession(`${workspace.name} was created and loaded.`);
        state.workspace.managerOpen = false;
      }

      async function duplicateWorkspaceById(sourceId) {
        const source = (state.workspace.list || []).find((item) => item.workspace_id === sourceId);
        const defaultName = `${source?.name || "Workspace"} Copy`;
        const workspace = await apiJson(`/workspaces/${encodeURIComponent(sourceId)}/duplicate`, {
          method: "POST",
          body: JSON.stringify({ name: defaultName })
        });
        await setActiveWorkspace(workspace.workspace_id);
        startWorkspaceSession(`${workspace.name} was duplicated from ${source?.name || sourceId} and loaded.`);
        trace("workspace", "Workspace duplicated", `${source?.name || sourceId} was copied into ${workspace.name}.`);
      }

      async function exportActiveWorkspace() {
        const mode = $("workspaceExportMode")?.value || state.workspace.exportMode || "template_only";
        if (mode === "full_backup" && !confirm("Full workspace backup may include sensitive records. Continue only if you have permission to export them.")) return;
        window.open(`/workspaces/${encodeURIComponent(workspaceId())}/export?mode=${encodeURIComponent(mode)}`, "_blank", "noopener,noreferrer");
        trace("workspace", "Workspace export requested", `${workspaceName()} export mode: ${mode.replace(/_/g, " ")}.`);
      }

      async function importWorkspaceFromFile(file) {
        if (!file) return;
        const form = new FormData();
        form.append("file", file);
        const response = await fetch("/workspaces/import", { method: "POST", body: form });
        if (!response.ok) throw new Error(`Import failed (${response.status})`);
        const workspace = await response.json();
        await setActiveWorkspace(workspace.workspace_id);
        startWorkspaceSession(`${workspace.name} was imported and loaded.`);
        trace("workspace", "Workspace imported", `${workspace.name} was imported and set active.`);
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

      async function refreshGoogleRepositoryStatus() {
        try {
          state.googleRepository = await apiJson("/repository/google/status");
          state.masterRepository.backend = state.googleRepository.configured ? "google_drive_sheets_phase" : "manual_package_export";
          if (state.googleRepository.configured) {
            state.masterRepository.target = state.googleRepository.root_name || state.masterRepository.target;
            if (state.masterRepository.syncStatus === "local_only") {
              state.masterRepository.syncStatus = "google_repository_configured";
            }
          }
        } catch (error) {
          state.googleRepository = {
            configured: false,
            sync_status: "unavailable",
            user_message: error.message || "Google repository status endpoint is unavailable.",
            storage_model: {
              files: "not checked",
              ledger: "not checked",
              database_warning: "Repository status could not be checked."
            },
            drive_url: "",
            sheet_url: ""
          };
        }
        return state.googleRepository;
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

      function icon(name) {
        const paths = {
          start: '<path d="M5 4l14 8-14 8z"></path>',
          folder: '<path d="M3 7h6l2 2h10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><path d="M3 7V6a2 2 0 0 1 2-2h4l2 3"></path>',
          plus: '<path d="M12 5v14"></path><path d="M5 12h14"></path>',
          copy: '<rect x="8" y="8" width="11" height="11" rx="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v1"></path>',
          import: '<path d="M12 3v12"></path><path d="M7 10l5 5 5-5"></path><path d="M5 21h14"></path>',
          export: '<path d="M12 21V9"></path><path d="M7 14l5-5 5 5"></path><path d="M5 3h14"></path>',
          assistant: '<path d="M12 3a7 7 0 0 0-7 7v3a4 4 0 0 0 4 4h1l2 3 2-3h1a4 4 0 0 0 4-4v-3a7 7 0 0 0-7-7z"></path><path d="M9 10h.01"></path><path d="M15 10h.01"></path><path d="M9.5 13a4 4 0 0 0 5 0"></path>',
          log: '<path d="M8 6h13"></path><path d="M8 12h13"></path><path d="M8 18h13"></path><path d="M3 6h.01"></path><path d="M3 12h.01"></path><path d="M3 18h.01"></path>',
          manual: '<path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H20v16H6.5A2.5 2.5 0 0 0 4 21.5z"></path><path d="M4 5.5v16"></path><path d="M8 7h8"></path><path d="M8 11h7"></path>',
          evidence: '<path d="M4 4h16v16H4z"></path><path d="M8 8h8"></path><path d="M8 12h8"></path><path d="M8 16h5"></path>',
          shield: '<path d="M12 3l7 3v5c0 5-3.5 8-7 10-3.5-2-7-5-7-10V6z"></path><path d="M9 12l2 2 4-5"></path>',
          model: '<path d="M4 17l6-6 4 4 6-8"></path><path d="M4 20h16"></path>',
          policy: '<path d="M6 3h9l3 3v15H6z"></path><path d="M14 3v4h4"></path><path d="M9 13h6"></path><path d="M9 17h6"></path>',
          warning: '<path d="M12 3l10 18H2z"></path><path d="M12 9v5"></path><path d="M12 17h.01"></path>',
          check: '<path d="M20 6L9 17l-5-5"></path>',
          clock: '<circle cx="12" cy="12" r="9"></circle><path d="M12 7v5l3 2"></path>',
          graph: '<circle cx="6" cy="7" r="2"></circle><circle cx="18" cy="7" r="2"></circle><circle cx="12" cy="17" r="2"></circle><path d="M8 8l3 7"></path><path d="M16 8l-3 7"></path><path d="M8 7h8"></path>',
          x: '<path d="M18 6 6 18"></path><path d="M6 6l12 12"></path>',
          sun: '<circle cx="12" cy="12" r="4"></circle><path d="M12 2v2"></path><path d="M12 20v2"></path><path d="M4.93 4.93l1.41 1.41"></path><path d="M17.66 17.66l1.41 1.41"></path><path d="M2 12h2"></path><path d="M20 12h2"></path><path d="M4.93 19.07l1.41-1.41"></path><path d="M17.66 6.34l1.41-1.41"></path>',
          moon: '<path d="M20 14.5A8.5 8.5 0 0 1 9.5 4a7 7 0 1 0 10.5 10.5Z"></path>'
        };
        return `<svg class="ui-icon" viewBox="0 0 24 24" aria-hidden="true">${paths[name] || paths.folder}</svg>`;
      }

      function iconCell(name) {
        return `<span class="icon-cell">${icon(name)}</span>`;
      }

      function setTheme(theme) {
        const nextTheme = theme === "dark" ? "dark" : "light";
        document.documentElement.dataset.theme = nextTheme;
        try {
          window.localStorage?.setItem("ndim_theme", nextTheme);
        } catch (_) {}
        const toggle = $("themeIconToggle");
        if (toggle) {
          const target = nextTheme === "dark" ? "light" : "dark";
          toggle.innerHTML = icon(nextTheme === "dark" ? "sun" : "moon");
          toggle.setAttribute("aria-label", `Switch to ${target} mode`);
          toggle.setAttribute("title", `Switch to ${target} mode`);
        }
        document.querySelectorAll("#themeToggle button").forEach((button) => {
          button.classList.toggle("active", button.dataset.theme === nextTheme);
        });
      }

      function mathBlock(tex, note = "") {
        return `
          <div class="equation latex-display">${escapeHtml(tex)}</div>
          ${note ? `<p class="select-note">${escapeHtml(note)}</p>` : ""}
        `;
      }

      function renderMath() {
        if (!window.katex) return;
        document.querySelectorAll(".latex-display").forEach((node) => {
          if (node.dataset.rendered === "1") return;
          const tex = node.textContent.trim();
          try {
            window.katex.render(tex, node, {
              displayMode: true,
              throwOnError: false,
              strict: "ignore"
            });
            node.dataset.rendered = "1";
          } catch (error) {
            node.dataset.rendered = "0";
          }
        });
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
        const inoculation = aggregateInoculationSignal();
        const diagnosis = dominantInoculationDiagnosis();
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
          regional_analysis_status: state.regional ? "included" : "not_run_pooled_evidence_only",
          uncertainty_summary: finalUncertaintySummary(),
          inoculation_threat_profile: {
            top_threat: inoculation.top_threat,
            misinformation_risk: inoculation.misinformation_risk,
            reactance_penalty: inoculation.reactance_penalty,
            cultural_sensitivity: diagnosis?.cultural_sensitivity_score || 0,
            booster_share: inoculation.booster_share
          },
          recommended_counter_narrative: diagnosis?.counter_narrative || state.inoculation?.items?.[0]?.text || "Run inoculation diagnosis and lab before field communication.",
          trusted_messenger: diagnosis?.trusted_messenger || "local peer demonstrator",
          booster_plan: diagnosis?.booster_strategy || "Repeat through trusted local messengers after field testing.",
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
        return activeEvidenceModes().find((mode) => mode.id === state.template.evidenceMode) || activeEvidenceModes()[0] || evidenceModes[0];
      }

      function collectionTemplateId() {
        const mode = state.template.evidenceMode || "structured_interview";
        if (mode === "structured_interview") return "clean-cooking-pressure-cooker-q1-q5-v1";
        if (mode === "focus_group") return "ndim-focus-group-discussion-v1";
        if (mode === "indigenous_knowledge") return "ndim-indigenous-knowledge-record-v1";
        if (mode === "citizen_science") return "ndim-citizen-science-observation-v1";
        if (mode === "crowd_batch") return "ndim-crowdsourced-batch-v1";
        if (mode === "experimental_feed") return "ndim-social-media-feed-v1";
        if (mode === "custom_evidence") return "ndim-custom-evidence-route-v1";
        return "ndim-open-narrative-v1";
      }

      function narrativeEvidenceTitle() {
        const mode = currentEvidenceMode();
        if (mode.id === "structured_interview") return "Structured interview response";
        if (mode.id === "focus_group") return "Focus group discussion";
        if (mode.id === "indigenous_knowledge") return "Indigenous knowledge record";
        if (mode.id === "citizen_science") return "Citizen science observation";
        if (mode.id === "crowd_batch") return "Crowdsourced narrative";
        if (mode.id === "experimental_feed") return "Social media feed item";
        if (mode.id === "custom_evidence") return state.template.customRouteName || "Custom evidence record";
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
              custom_route_name: state.template.customRouteName,
              custom_evidence_type: state.template.customEvidenceType,
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
        const freeTextBlocks = state.intakeImportMode === "single" && state.text.trim()
          ? [state.text.trim()]
          : splitNarratives(state.text);
        const fromFreeText = freeTextBlocks.map((text, index) =>
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
          state.completed.add("repository");
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
        if (!acceptedRepositoryRecords().length && !rejectedRepositoryRecords().length) state.completed.delete("repository");
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
            evidence_mode_label: (activeEvidenceModes().find((mode) => mode.id === evidenceMode) || evidenceModes.find((mode) => mode.id === evidenceMode))?.title || evidenceMode,
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
                custom_route_name: row.custom_route_name || "",
                custom_evidence_type: row.custom_evidence_type || "",
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
        state.template.customRouteName = row.custom_route_name || state.template.customRouteName;
        state.template.customEvidenceType = row.custom_evidence_type || state.template.customEvidenceType;
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
        if (state.template.evidenceMode === "focus_group") {
          checks.push(
            ["Focus group ID", state.template.interviewId || "recommended", true],
            ["Group profile", state.template.respondentProfile, Boolean(state.template.respondentProfile)],
            ["Community validation", state.template.communityValidation, Boolean(state.template.communityValidation)],
            ["Validation status", state.template.validationStatus, Boolean(state.template.validationStatus)]
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
        if (state.template.evidenceMode === "custom_evidence") {
          checks.push(
            ["Custom route name", state.template.customRouteName, Boolean(state.template.customRouteName)],
            ["Custom evidence type", state.template.customEvidenceType, Boolean(state.template.customEvidenceType)]
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
        state.inoculationDiagnoses = [];
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
        if (state.template.evidenceMode === "focus_group" && !state.template.respondentProfile) {
          setStatus("error");
          trace("blocked", "Missing focus group profile", "Focus group mode needs a short group profile so reviewers know whose voices shaped the discussion.");
          toast("Add focus group profile");
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
        if (state.template.evidenceMode === "custom_evidence" && (!state.template.customRouteName || !state.template.customEvidenceType)) {
          setStatus("error");
          trace("blocked", "Missing custom evidence metadata", "Custom evidence requires a route name and evidence type so the repository and SDMX gate can explain what was ingested.");
          toast("Name the custom evidence route");
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

      function stepIndexById(id) {
        const index = steps.findIndex((step) => step.id === id);
        return index >= 0 ? index : 0;
      }

      function goStep(index) {
        const nextIndex = Math.max(0, Math.min(steps.length - 1, index));
        if (steps[nextIndex]?.id !== "repository") state.repositoryOpen = false;
        state.step = nextIndex;
        render();
        scrollToActiveStage();
      }

      function openStageWorkspace(index = state.step) {
        if (!state.workspace.started) {
          state.workspace.startOpen = true;
          trace("workspace", "Start workspace menu opened", "Choose or create a workspace before opening stage tasks.");
          render();
          return;
        }
        const nextIndex = Math.max(0, Math.min(steps.length - 1, index));
        if (steps[nextIndex]?.id !== "repository") state.repositoryOpen = false;
        state.step = nextIndex;
        state.stageWorkspace.open = true;
        trace("stage", "Focused stage task opened", `${steps[nextIndex].num} ${workspaceStageLabel(steps[nextIndex])} is open as a guided task workspace.`);
        render();
        requestAnimationFrame(() => $("stageWorkspaceBody")?.scrollTo({ top: 0, behavior: "smooth" }));
      }

      function closeStageWorkspace() {
        state.stageWorkspace.open = false;
        trace("stage", "Focused stage task closed", `${currentStep().num} ${workspaceStageLabel(currentStep())} remains selected in the workbench.`);
        render();
      }

      function scrollToActiveStage() {
        requestAnimationFrame(() => {
          const stage = state.stageWorkspace.open
            ? document.querySelector(".stage-workspace.open")
            : document.querySelector(".stage-launcher, .repository-full-view");
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
          state.inoculationDiagnoses = [];
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
          state.completed.delete("repository");
        } else if (id === "repository") {
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
        } else if (id === "encoding") {
          state.encoded = [];
          state.encodingRuns = {};
          state.inoculationDiagnoses = [];
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
            const missing = steps.filter((step) => !["policy", "regional"].includes(step.id) && !state.completed.has(step.id)).map((step) => step.title);
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
        if (id === "repository" && !approvedRecords().length) {
          toast("Commit accepted evidence first");
          trace("blocked", "No accepted repository records", "Approve at least one narrative in the SDMX gate, click Commit reviewed records, then continue to encoding.");
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
          trace("optional", "Regional analysis skipped", "Regional analysis is optional. Policy output will use pooled evidence and state that place-specific analysis was not run.");
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
        if (!state.workspace.started) {
          $("stepList").innerHTML = `
            <div class="start-hint">
              <strong>Start a workspace first.</strong><br>
              The scientific workflow appears after a project workspace is loaded.
            </div>
          `;
          return;
        }
        $("stepList").innerHTML = steps.map((step, index) => `
          <button class="step-button ${index === state.step ? "active" : ""} ${state.completed.has(step.id) ? "done" : ""}" data-step="${index}" type="button">
            <span class="num">${step.num}</span>
            <span><strong>${escapeHtml(workspaceStageLabel(step))}</strong><span>${escapeHtml(workspaceStageSub(step))}</span></span>
          </button>
        `).join("");
        document.querySelectorAll("[data-step]").forEach((button) => {
          button.addEventListener("click", () => openStageWorkspace(Number(button.dataset.step)));
        });
      }

      function renderStageJump() {
        const select = $("stageJumpSelect");
        if (!select) return;
        if (!state.workspace.started) {
          select.innerHTML = '<option>Start workspace first</option>';
          select.disabled = true;
          return;
        }
        select.disabled = false;
        select.innerHTML = steps.map((step, index) => `
          <option value="${index}" ${index === state.step ? "selected" : ""}>${step.num} ${escapeHtml(workspaceStageLabel(step))}</option>
        `).join("");
        select.value = String(state.step);
        select.onchange = () => openStageWorkspace(Number(select.value));
      }

      function workspaceReadinessPercent() {
        const gates = [
          Boolean(state.workspace.active),
          state.records.length > 0,
          approvedRecords().length > 0,
          state.encoded.length > 0,
          Boolean(state.comp || state.agents),
          Boolean(state.digital),
          Boolean(state.bayes || state.rl),
          Boolean(state.policy)
        ];
        return Math.round((gates.filter(Boolean).length / gates.length) * 100);
      }

      function assistantWorkItems() {
        return [
          ["Workspace loaded", Boolean(state.workspace.active)],
          ["Evidence staged", state.records.length > 0],
          ["Governance reviewed", approvedRecords().length > 0],
          ["Narratives encoded", state.encoded.length > 0],
          ["Models executed", Boolean(state.comp || state.agents)],
          ["Twin updated", Boolean(state.digital)],
          ["Policy brief ready", Boolean(state.policy)]
        ];
      }

      function workspaceSummaryText() {
        const settings = workspaceSettings();
        const country = (settings.countries || [state.meta.country || "Rwanda"]).join(", ");
        const routes = activeEvidenceModes().map((mode) => mode.title).slice(0, 4).join(", ");
        const domain = settings.domain || "narrative evidence";
        return `${workspaceName()} is configured for ${domain} in ${country}. Active intake routes include ${routes || "the core NDIM evidence routes"}.`;
      }

      function startWorkspaceSession(detail = "Workspace loaded") {
        state.workspace.started = true;
        state.workspace.startOpen = false;
        state.workspace.startMode = "menu";
        trace("workspace", "Workspace session started", detail);
      }

      function renderStartMenu() {
        if (!state.workspace.startOpen) return "";
        return `
          <div class="start-menu" role="menu" aria-label="Start workspace options">
            <button class="start-action" data-start-action="continue" type="button">
              ${iconCell("start")}<span><strong>Continue last workspace</strong><span>Open ${escapeHtml(workspaceName())} and reveal the guided workflow.</span></span>
            </button>
            <button class="start-action" data-start-action="open" type="button">
              ${iconCell("folder")}<span><strong>Open existing workspace</strong><span>Choose from saved local project workspaces.</span></span>
            </button>
            ${state.workspace.startMode === "open" ? `
              <div class="start-existing-list">
                ${(state.workspace.list || []).map((item) => `
                  <button class="workspace-mini ${item.workspace_id === workspaceId() ? "active" : ""}" data-workspace-open-quick="${escapeHtml(item.workspace_id)}" type="button">
                    <span><strong>${escapeHtml(item.name)}</strong><span>${escapeHtml(item.domain || item.workspace_id)}</span></span>
                    <b>${item.workspace_id === workspaceId() ? "ON" : "GO"}</b>
                  </button>
                `).join("")}
              </div>
            ` : ""}
            <button class="start-action" data-start-action="create" type="button">
              ${iconCell("plus")}<span><strong>Create new workspace</strong><span>Start a new country, district, study, or policy programme.</span></span>
            </button>
            <button class="start-action" data-start-action="import" type="button">
              ${iconCell("import")}<span><strong>Import workspace package</strong><span>Load a workspace shared from another computer.</span></span>
            </button>
          </div>
        `;
      }

      function renderWorkspaceLaunchpad() {
        const settings = workspaceSettings();
        const readiness = workspaceReadinessPercent();
        const allModes = activeEvidenceModes().map((mode) => mode.title);
        const modes = allModes.slice(0, 5);
        const extraModes = Math.max(0, allModes.length - modes.length);
        const activeId = workspaceId();
        const workspaces = (state.workspace.list || []).slice(0, 3);
        const title = "NDIM Engine";
        const summary = "NDIM Engine is a local-first scientific workbench for studying how narratives, misinformation, trust, social influence, and intervention messages shape adoption decisions in communities. It turns field stories into governed evidence, encodes narrative mechanisms, simulates diffusion with compartmental and agent-based models, updates uncertainty through Bayesian learning, tests inoculation strategies in a digital twin, and produces human-reviewed policy briefs.";
        return `
          <div class="workspace-launchpad workspace-os" aria-label="Workspace launchpad">
            <section class="workspace-prime">
              <div class="workspace-title-row">
                <div>
                  <p class="eyebrow">Narrative Diffusion and Inoculation Model</p>
                  <h2>${escapeHtml(title)}</h2>
                  <p>${escapeHtml(summary)}</p>
                  <p class="workspace-support-line">From field narratives to traceable model evidence, intervention testing, and policy-ready decision support.</p>
                </div>
                <span class="workspace-badge">local-first research tool</span>
              </div>
              <div class="workspace-capability-row" aria-label="NDIM scientific capabilities">
                <div class="workspace-capability"><strong>Governed evidence</strong>SDMX metadata, consent, review status, hashes, and an audit trail before evidence can influence models.</div>
                <div class="workspace-capability"><strong>Scientific modelling</strong>Narrative encoding, ODE flow, agent behaviour, Bayesian updating, RL optimisation, and digital-twin feedback.</div>
                <div class="workspace-capability"><strong>Policy safety</strong>Uncertainty, assumptions, limitations, confidence level, and required human review in every policy output.</div>
              </div>
              ${state.workspace.started ? `
                <div class="workspace-context-card" role="status" aria-label="Active workspace context">
                  <span>Project context loaded</span>
                  <strong>${escapeHtml(workspaceName())}</strong>
                  <p>${escapeHtml(workspaceSummaryText())}</p>
                </div>
              ` : ""}
              <div class="workspace-command-row">
                <div class="start-control">
                  <button class="button primary start-button" data-start-toggle type="button">${icon("start")} ${state.workspace.started ? "Switch workspace" : "Start workspace"}</button>
                  ${renderStartMenu()}
                </div>
                <div class="workspace-quick-actions">
                  <button class="button" data-open-workspace-manager type="button">${icon("folder")} Workspace manager</button>
                  <button class="button" data-start-action="create" type="button">${icon("plus")} New workspace</button>
                  <a class="button" href="/manual#workspaces" target="_blank" rel="noreferrer">${icon("manual")} Workspace guide</a>
                </div>
              </div>
              <div class="workspace-signal-row" aria-label="Workspace evidence routes">
                <span class="workspace-signal"><strong>Routes</strong> ${modes.map(escapeHtml).join(" / ")}${extraModes ? ` / +${extraModes}` : ""}</span>
                <span class="workspace-signal"><strong>Grade</strong> ${escapeHtml(evidenceGrade())}</span>
                <span class="workspace-signal"><strong>Offline</strong> ready</span>
                <span class="workspace-signal"><strong>Storage</strong> local</span>
              </div>
            </section>
            <div class="workspace-side-stack">
              <section class="workspace-switcher">
                <p class="eyebrow">${state.workspace.started ? "Open workspaces" : "Project choices"}</p>
                <h3>${state.workspace.started ? "Switch without losing context" : "Load before analysis"}</h3>
                <p>${state.workspace.started ? "Change projects from the list below, or keep this workspace active while you finish the evidence-to-policy chain." : "Start from a saved workspace, duplicate a project, or create a new workspace before importing evidence."}</p>
                <div class="workspace-mini-list">
                  ${state.workspace.started ? workspaces.map((item) => `
                    <button class="workspace-mini ${item.workspace_id === activeId ? "active" : ""}" data-workspace-open-quick="${escapeHtml(item.workspace_id)}" type="button">
                      <span><strong>${escapeHtml(item.name)}</strong><span>${escapeHtml(item.domain || item.workspace_id)}</span></span>
                      <b>${item.workspace_id === activeId ? "ON" : "GO"}</b>
                    </button>
                  `).join("") : `
                    <div class="start-panel">
                      <h3>${icon("folder")} Existing</h3>
                      <p>Open ClimateTales Rwanda, NDIM Core, or another local project.</p>
                    </div>
                    <div class="start-panel">
                      <h3>${icon("plus")} New</h3>
                      <p>Create a project with its own country, route, and export rules.</p>
                    </div>
                    <div class="start-panel">
                      <h3>${icon("copy")} Duplicate</h3>
                      <p>Open Workspace manager, then use the duplicate icon beside the workspace you want to copy.</p>
                    </div>
                  `}
                </div>
              </section>
              <section class="agent-cockpit" aria-label="Research assistant progress">
                <div class="agent-orb" style="--pct:${readiness}%;">
                  <div><strong>${readiness}</strong><span>ready</span></div>
                </div>
                <div>
                  <p class="eyebrow">Research assistant</p>
                  <h3>${state.workspace.started ? "Watching the workflow" : "I will guide the setup"}</h3>
                  <p>${escapeHtml(state.workspace.started ? assistantNextAction() : "Start by choosing a workspace. I will then reveal the workflow, explain each stage, track what is complete, and warn when evidence is not ready for policy use.")}</p>
                </div>
                <div class="agent-worklist compact">
                  ${assistantWorkItems().map(([label, done]) => `
                    <div class="agent-workitem ${done ? "done" : ""}">
                      <span class="agent-dot"></span>
                      <strong>${escapeHtml(label)}</strong>
                      <span>${done ? "done" : "waiting"}</span>
                    </div>
                  `).join("")}
                </div>
              </section>
            </div>
          </div>
        `;
      }

      function scientificCautionText() {
        if (!state.records.length) return "Begin with governed evidence. Models stay advisory until narratives have source, place, consent, visibility, and reviewer context.";
        if (!approvedRecords().length) return "Evidence is staged but not yet accepted. Approve, reject, and commit records before treating them as model-ready observations.";
        if (!state.encoded.length) return "Accepted evidence exists, but encoding has not yet converted stories into model inputs. Use manual, LLM-assisted, or hybrid scoring next.";
        if (!state.digital && !state.comp && !state.agents) return "Encoded narratives are ready. Run the compartmental and agent-based models before interpreting adoption pathways.";
        if (!state.policy) return "Model outputs are available, but the policy brief still needs uncertainty, assumptions, limitations, and human review before use.";
        return "A policy output exists. Treat it as a decision brief for review, not an automatic policy decision.";
      }

      function renderCommandCenter() {
        const step = currentStep();
        const readiness = Math.round((state.completed.size / steps.length) * 100);
        const adoption = bestAdoptionSignal();
        const encodedSummary = state.encoded.length ? `${state.encoded.length}/${state.records.length || state.encoded.length}` : "0";
        const topLocation = [state.meta.country, state.meta.district || state.meta.province].filter(Boolean).join(" / ") || "not set";
        const recordSummary = state.records.length ? `${state.records.length} staged record${state.records.length === 1 ? "" : "s"}` : "No records staged yet";
        const recordExplanation = state.records.length
          ? "Review staged narratives, approvals, repository state, and evidence seal before sending results into the model chain."
          : "Records appear here only after you upload or manually load evidence, then stage and validate it.";
        const repoPreview = state.records.slice(0, 3).map((record, index) => `
          <div class="os-repository-row">
            <span title="${escapeHtml(record.narrative_id || `record-${index + 1}`)}">${escapeHtml(record.narrative_id || `record-${index + 1}`)}</span>
            <span title="${escapeHtml(recordRouteLabel(record))}">${escapeHtml(recordRouteLabel(record))}</span>
            <span title="${escapeHtml(recordStatusLabel(record))}">${escapeHtml(recordStatusLabel(record))}</span>
          </div>
        `).join("");
        return `
          <section class="command-center science-os" aria-label="NDIM scientific workbench">
            ${renderWorkspaceLaunchpad()}
            <div class="os-phase-rail" aria-label="Evidence-to-policy phases">
              <div class="flow-lane workbench-flow">
                ${workflowPhases.map(renderFlowCard).join("")}
              </div>
            </div>
            <div class="os-workbench-grid">
              <section class="os-stage-card">
                <p class="eyebrow">Active scientific task</p>
                <h2>${escapeHtml(step.num)} ${escapeHtml(step.title)}</h2>
                <p>${escapeHtml(assistantNextAction())}</p>
                <div class="os-action-row">
                  <button class="button primary" id="workbenchRunButton" type="button">${icon("start")} Run current stage</button>
                  <button class="button" data-open-stage-workspace type="button">${icon("folder")} Open focused task</button>
                  <button class="button" id="workbenchTraceButton" type="button">${icon("log")} Activity log</button>
                </div>
                <div class="os-stage-insight-grid">
                  <div class="os-stage-insight">
                    <strong>Input</strong>
                    <span>${escapeHtml(stageInputSummary(step.id))}</span>
                  </div>
                  <div class="os-stage-insight">
                    <strong>Scientific check</strong>
                    <span>${escapeHtml(stageAdvice(step.id))}</span>
                  </div>
                  <div class="os-stage-insight">
                    <strong>Status</strong>
                    <span>${escapeHtml(stageCompletionLabel(step.id))}</span>
                  </div>
                </div>
              </section>
              <div class="os-right-column">
                <section class="os-assistant-card">
                  <p class="eyebrow">Research assistant</p>
                  <h3>What to know now</h3>
                  <p>${escapeHtml(scientificCautionText())}</p>
                  <div class="agent-worklist" style="margin-top: 12px;">
                    ${assistantWorkItems().slice(0, 4).map(([label, done]) => `
                      <div class="agent-workitem ${done ? "done" : ""}">
                        <span class="agent-dot"></span>
                        <strong>${escapeHtml(label)}</strong>
                        <span>${done ? "done" : "waiting"}</span>
                      </div>
                    `).join("")}
                  </div>
                </section>
              </div>
              <section class="os-repository-card" id="narrativeRepository">
                <p class="eyebrow">Narrative repository</p>
                <h3>${escapeHtml(recordSummary)}</h3>
                <p>${escapeHtml(recordExplanation)}</p>
                <div class="os-repository-table" aria-label="Repository preview">
                  <div class="os-repository-row header"><span>Narrative</span><span>Route</span><span>Status</span></div>
                  ${repoPreview || `<div class="os-repository-row"><span>Waiting for staged records.</span><span>-</span><span>-</span></div>`}
                </div>
                <div class="workbench-tools" aria-label="Repository actions">
                  <a class="button" href="#narrativeRepository" data-jump-repository>${icon("evidence")} Repository view</a>
                  <button class="button" data-open-full-repository type="button">${icon("folder")} Full repository</button>
                </div>
              </section>
            </div>
            <div class="os-metrics-bar" aria-label="Workspace metrics">
              <div class="os-metric"><span>Observations</span><strong>${escapeHtml(state.records.length || "-")}</strong></div>
              <div class="os-metric"><span>Approved</span><strong>${escapeHtml(approvedRecords().length || "-")}</strong></div>
              <div class="os-metric"><span>Encoded</span><strong>${escapeHtml(encodedSummary)}</strong></div>
              <div class="os-metric"><span>Model signal</span><strong>${escapeHtml(adoption)}</strong></div>
              <div class="os-metric"><span>Location</span><strong title="${escapeHtml(topLocation)}">${escapeHtml(topLocation)}</strong></div>
              <div class="os-metric"><span>Validation</span><strong>${escapeHtml(state.validation?.status || "checking")}</strong></div>
              <div class="os-metric"><span>Seal</span><strong>${escapeHtml(shortHash(state.governance.lastDigest))}</strong></div>
            </div>
            <details class="os-system-drawer">
              <summary>View NDIM system map and feedback chain</summary>
              <div class="os-system-drawer-body">
                <div class="hero-side">
                  ${renderSystemDynamicsMap()}
                </div>
              </div>
            </details>
          </section>
        `;
      }

      function renderStartExperience() {
        return `
          <section class="command-center science-os start-only" aria-label="NDIM start workspace">
            ${renderWorkspaceLaunchpad()}
            <div class="start-panels">
              <div class="start-panel">
                <h3>${icon("evidence")} Evidence to policy</h3>
                <p>NDIM turns governed narrative evidence into encoding, models, uncertainty updates, intervention tests, and policy outputs.</p>
              </div>
              <div class="start-panel">
                <h3>${icon("assistant")} Assistant guided</h3>
                <p>The Research Assistant stays visible, explains what to do next, and keeps scientific caution in plain language.</p>
              </div>
              <div class="start-panel">
                <h3>${icon("shield")} Local first</h3>
                <p>Your workspace, repository, hashes, approvals, and exports stay local unless you deliberately export or sync them.</p>
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

      function recordRouteLabel(record) {
        const modeId = record?.metadata?.provenance?.evidence_mode || record?.metadata?.evidence_mode || state.template.evidenceMode;
        return (activeEvidenceModes().find((mode) => mode.id === modeId) || evidenceModes.find((mode) => mode.id === modeId))?.title || modeId || "Narrative";
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

      function renderSystemDynamicsMap() {
        const step = currentStep();
        const active = (ids) => ids.includes(step.id) ? "active" : "";
        const ready = (value) => value ? "ready" : "";
        const node = ({ x, y, w, h, label, sub, stepIndex, ids, isReady, chip, shape = "rect", variant = "", tip }) => {
          const shapeMarkup = shape === "hex"
            ? `<path class="node-shape" d="M${x + 14} ${y} H${x + w - 14} L${x + w} ${y + h / 2} L${x + w - 14} ${y + h} H${x + 14} L${x} ${y + h / 2} Z"></path>`
            : `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="14"></rect>`;
          return `
            <g class="map-node ${variant} ${active(ids)} ${ready(isReady)}" data-flow-step="${stepIndex}" tabindex="0" role="button" aria-label="${escapeHtml(label)}: ${escapeHtml(tip)}">
              <title>${escapeHtml(tip)}</title>
              ${shapeMarkup}
              <text x="${x + 14}" y="${y + 25}" font-size="14">${escapeHtml(label)}</text>
              <text class="sub" x="${x + 14}" y="${y + 43}">${escapeHtml(sub)}</text>
              <circle class="map-chip" cx="${x + w - 21}" cy="${y + 21}" r="13"></circle>
              <text class="map-chip-text" x="${x + w - 21}" y="${y + 25}" text-anchor="middle">${escapeHtml(chip)}</text>
            </g>
          `;
        };
        return `
          <div class="system-map-card" id="narrativeRepository">
            <div class="system-map-head">
              <div>
                <p class="eyebrow">NDIM system map</p>
                <h3>How evidence becomes policy</h3>
                <p>Click any node to jump to that stage. Hover for the scientific role.</p>
              </div>
              <button class="button" data-open-full-repository type="button">Repository</button>
            </div>
            <div class="system-map-scroll" aria-label="NDIM evidence-to-policy systems dynamics diagram">
              <svg class="system-map" viewBox="0 0 760 342" role="img" aria-label="NDIM workflow system map with feedback loops and digital twin">
                <defs>
                  <marker id="mapArrow" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto">
                    <path d="M0,0 L8,4.5 L0,9 Z" fill="var(--soft)"></path>
                  </marker>
                  <marker id="mapLoopArrow" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto">
                    <path d="M0,0 L8,4.5 L0,9 Z" fill="rgba(88, 110, 92, .82)"></path>
                  </marker>
                </defs>
                <path class="map-arrow" marker-end="url(#mapArrow)" d="M132 75 H158"></path>
                <path class="map-arrow" marker-end="url(#mapArrow)" d="M272 75 H298"></path>
                <path class="map-arrow" marker-end="url(#mapArrow)" d="M412 75 H438"></path>
                <path class="map-arrow" marker-end="url(#mapArrow)" d="M552 75 H578"></path>
                <path class="map-arrow" marker-end="url(#mapArrow)" d="M646 108 V128"></path>
                <path class="map-arrow" marker-end="url(#mapArrow)" d="M552 94 C578 111 594 124 608 138"></path>
                <path class="map-arrow" marker-end="url(#mapArrow)" d="M646 198 V224"></path>
                <path class="map-arrow" marker-end="url(#mapArrow)" d="M580 261 H552"></path>
                <path class="map-arrow" marker-end="url(#mapArrow)" d="M438 261 H412"></path>
                <path class="map-loop" marker-end="url(#mapLoopArrow)" d="M580 158 C532 132 545 91 580 82"></path>
                <text class="map-label" x="505" y="130">model rerun</text>
                <path class="map-loop" marker-end="url(#mapLoopArrow)" d="M500 232 C526 202 552 185 580 170"></path>
                <text class="map-label" x="470" y="212">inoculation feedback</text>
                <path class="map-loop" marker-end="url(#mapLoopArrow)" d="M302 290 C176 321 84 280 80 112"></path>
                <text class="map-label" x="84" y="318">human review and evidence correction</text>
                ${node({
                  x: 20, y: 44, w: 112, h: 64,
                  label: "Intake", sub: "stories + context", stepIndex: 0,
                  ids: ["intake"], isReady: state.records.length > 0,
                  chip: String(state.records.length || "0"),
                  tip: "Structured interviews, focus groups, open stories, indigenous knowledge, citizen science, batches, and social feeds enter with context."
                })}
                ${node({
                  x: 160, y: 44, w: 112, h: 64,
                  label: "SDMX", sub: "governance gate", stepIndex: 1,
                  ids: ["gate"], isReady: state.completed.has("gate"),
                  chip: state.completed.has("gate") ? "OK" : "--",
                  tip: "Checks place, period, source, consent, visibility, route metadata, hashes, and review readiness."
                })}
                ${node({
                  x: 300, y: 44, w: 112, h: 64,
                  label: "Repository", sub: "accepted ledger", stepIndex: 2,
                  ids: ["repository"], isReady: acceptedRepositoryRecords().length > 0,
                  chip: String(acceptedRepositoryRecords().length || "0"),
                  tip: "Accepted, rejected, pending, hash-sealed, and master-sync-ready narrative records live here."
                })}
                ${node({
                  x: 440, y: 44, w: 112, h: 64,
                  label: "Encoding", sub: "manual + LLM", stepIndex: 3,
                  ids: ["encoding"], isReady: state.encoded.length > 0,
                  chip: String(state.encoded.length || "0"),
                  tip: "Manual, LLM, and hybrid scoring turn narratives into trust, barriers, influence, confidence, and Phi inputs."
                })}
                ${node({
                  x: 580, y: 44, w: 132, h: 64,
                  label: "ODE + ABM", sub: "diffusion models", stepIndex: 4,
                  ids: ["compartmental", "agents"], isReady: Boolean(state.comp || state.agents),
                  chip: Boolean(state.comp || state.agents) ? "ON" : "--",
                  shape: "hex",
                  tip: "Compartmental and agent-based models translate encoded evidence into population and household diffusion dynamics."
                })}
                <ellipse class="map-twin-halo" cx="646" cy="168" rx="82" ry="42"></ellipse>
                ${node({
                  x: 580, y: 136, w: 132, h: 62,
                  label: "Digital twin", sub: "field mirror", stepIndex: 6,
                  ids: ["digital"], isReady: Boolean(state.digital),
                  chip: Boolean(state.digital) ? "DT" : "--",
                  shape: "hex",
                  variant: "twin",
                  tip: "The digital twin compares predicted adoption with observed evidence, updates assumptions, and reruns the model."
                })}
                ${node({
                  x: 580, y: 232, w: 132, h: 58,
                  label: "Bayes/RL", sub: "posterior policy", stepIndex: 7,
                  ids: ["bayes", "rl"], isReady: Boolean(state.bayes || state.rl),
                  chip: Boolean(state.bayes || state.rl) ? "LR" : "--",
                  shape: "hex",
                  tip: "Bayesian posterior updates and RL policy search refine uncertainty, reward, and intervention choice."
                })}
                ${node({
                  x: 440, y: 232, w: 112, h: 58,
                  label: "Synthesis", sub: "regions graph lab", stepIndex: 9,
                  ids: ["regional", "graph", "inoculation"], isReady: Boolean(state.regional || state.graph || state.inoculation),
                  chip: Boolean(state.regional || state.graph || state.inoculation) ? "SY" : "--",
                  tip: "Regional analysis, knowledge graphs, and inoculation messages explain where and how interventions should differ."
                })}
                ${node({
                  x: 300, y: 232, w: 112, h: 58,
                  label: "Policy", sub: "brief + review", stepIndex: 12,
                  ids: ["policy"], isReady: Boolean(state.policy),
                  chip: evidenceGrade(),
                  tip: "The final decision brief exports readable policy advice with uncertainty, evidence grade, assumptions, limitations, and human review."
                })}
              </svg>
            </div>
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
            <td>${repositoryEncodingCell(record, "manual")}</td>
            <td>${repositoryEncodingCell(record, "ai")}</td>
            <td>${repositoryEncodingCell(record, "hybrid")}</td>
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
                <thead><tr><th>Narrative ID</th><th>Route</th><th>Place</th><th>Source</th><th>Status</th><th>Manual</th><th>AI</th><th>Hybrid</th><th>Seal</th><th>Decision / reason</th><th>Committed</th><th>Action</th></tr></thead>
                <tbody>
                  ${records.length ? records.map((record) => renderRepositoryRow(record, section)).join("") : `<tr><td colspan="12">No records in this repository section.</td></tr>`}
                </tbody>
              </table>
            </div>
          </div>
        `;
      }

      function jsonForScript(value) {
        return JSON.stringify(value)
          .replace(/</g, "\\u003c")
          .replace(/>/g, "\\u003e")
          .replace(/&/g, "\\u0026");
      }

      function repositoryStandalonePayload() {
        const records = state.records.map((record, index) => {
          const gov = record.governance || {};
          const provenance = record.metadata?.provenance || {};
          const encoded = recordEncoded(record) || {};
          const themes = recordThemes(record);
          return {
            index,
            id: record.narrative_id || `record-${index + 1}`,
            route: recordRouteLabel(record),
            routeRaw: provenance.evidence_mode || state.template.evidenceMode,
            country: record.metadata?.country || "",
            place: recordAdminLabel(record),
            source: recordSourceLabel(record),
            status: recordStatusLabel(record),
            statusGroup: recordStatusGroup(record),
            consent: gov.consent || provenance.consent_tier || "",
            visibility: gov.visibility || provenance.visibility || "",
            reviewer: gov.reviewer || "",
            reviewerRole: gov.reviewer_role || "",
            validation: provenance.validation_status || "",
            master: gov.master_repository_status || "not_prepared",
            seal: shortHash(gov.evidence_hash || gov.content_hash || ""),
            fullHash: gov.evidence_hash || gov.content_hash || "",
            reason: gov.review_reason || gov.scan?.recommendation || "No review note recorded",
            committed: gov.committed_at ? new Date(gov.committed_at).toLocaleString() : "-",
            themes,
            trust: typeof encoded.trust_score === "number" ? encoded.trust_score : null,
            barrier: typeof encoded.adoption_barrier_score === "number" ? encoded.adoption_barrier_score : null,
            confidence: typeof encoded.confidence === "number" ? encoded.confidence : null,
            manual: encodingSummaryForRecord(record, "manual"),
            ai: encodingSummaryForRecord(record, "ai"),
            hybrid: encodingSummaryForRecord(record, "hybrid"),
            text: record.text || ""
          };
        });
        return {
          generatedAt: new Date().toLocaleString(),
          project: "NDIM Engine narrative repository",
          workspace: {
            workspace_id: workspaceId(),
            name: workspaceName()
          },
          batchSeal: shortHash(state.governance.lastDigest),
          records
        };
      }

      function standaloneRepositoryHtml(payload) {
        return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>NDIM Narrative Repository</title>
  <style>
    :root { --ink:#11100e; --body:#5d5141; --muted:#9b8d78; --paper:#fbfaf7; --line:#d8cdbb; --soft:#f1ede5; }
    * { box-sizing: border-box; }
    body { margin:0; background:var(--paper); color:var(--ink); font-family:"Myriad Pro","Segoe UI",Arial,sans-serif; line-height:1.55; }
    main { max-width:1200px; margin:0 auto; padding:28px 18px 64px; }
    header { border-bottom:1px solid var(--line); padding-bottom:16px; margin-bottom:18px; }
    h1 { margin:0 0 8px; font-size:clamp(30px,5vw,52px); line-height:1; }
    h2 { margin-top:30px; padding-top:18px; border-top:1px solid var(--line); }
    p, td { color:var(--body); }
    .meta, label, th { color:var(--muted); font:800 12px "Cascadia Mono",Consolas,monospace; letter-spacing:.08em; text-transform:uppercase; }
    .filters { display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:10px; background:var(--soft); border:1px solid var(--line); border-radius:12px; padding:12px; }
    select, input { width:100%; min-height:38px; border:1px solid var(--line); border-radius:8px; background:white; padding:6px 8px; font:inherit; }
    button { min-height:36px; border:1px solid var(--line); border-radius:999px; background:white; padding:7px 12px; font-weight:800; cursor:pointer; }
    button.primary { background:var(--ink); color:white; border-color:var(--ink); }
    .stats { display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:10px; margin:16px 0; }
    .stat { border:1px solid var(--line); border-radius:12px; background:white; padding:12px; }
    .stat strong { display:block; font-size:24px; }
    table { width:100%; border-collapse:collapse; background:white; margin-top:10px; }
    th, td { border:1px solid var(--line); padding:9px; text-align:left; vertical-align:top; }
    th { background:var(--soft); }
    .summary { max-width:360px; }
    .pill { display:inline-block; border:1px solid var(--line); border-radius:999px; padding:2px 8px; margin:2px 3px 2px 0; font-size:12px; color:var(--body); }
    .empty { border:1px dashed var(--line); border-radius:12px; padding:12px; color:var(--muted); background:white; }
    @media (max-width:760px) {
      table, thead, tbody, th, td, tr { display:block; }
      thead { display:none; }
      tr { border:1px solid var(--line); margin:10px 0; background:white; }
      td { border:0; border-bottom:1px solid var(--line); }
      td::before { content:attr(data-label); display:block; color:var(--muted); font:800 11px "Cascadia Mono",Consolas,monospace; text-transform:uppercase; }
    }
  </style>
</head>
<body>
  <main>
    <header>
      <p class="meta">Standalone repository view</p>
      <h1>NDIM Narrative Repository</h1>
      <p><strong>Workspace:</strong> ${escapeHtml(payload.workspace?.name || "NDIM Core")} (${escapeHtml(payload.workspace?.workspace_id || "ndim-core")}). This tab is generated from the current local workflow ledger. It keeps long repository review outside the main workflow screen. Batch seal: <strong>${escapeHtml(payload.batchSeal || "not sealed")}</strong>. Generated: ${escapeHtml(payload.generatedAt)}.</p>
    </header>
    <section class="filters" aria-label="Repository filters">
      <div><label for="status">Status</label><select id="status"></select></div>
      <div><label for="country">Country</label><select id="country"></select></div>
      <div><label for="place">Admin unit</label><select id="place"></select></div>
      <div><label for="route">Route</label><select id="route"></select></div>
      <div><label for="theme">Theme</label><select id="theme"></select></div>
      <div><label for="consent">Consent</label><select id="consent"></select></div>
      <div><label for="visibility">Visibility</label><select id="visibility"></select></div>
      <div><label for="reviewer">Reviewer</label><select id="reviewer"></select></div>
    </section>
    <div class="stats" id="stats"></div>
    <section id="sections"></section>
  </main>
  <script>
    const payload = ${jsonForScript(payload)};
    const state = { filters: { status:"all", country:"all", place:"all", route:"all", theme:"all", consent:"all", visibility:"all", reviewer:"all" } };
    const esc = (value) => String(value == null ? "" : value).replace(/[&<>"']/g, (char) => ({ "&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#39;" }[char]));
    const label = { active_review:"Active review", pending_commit:"Reviewed, waiting commit", accepted:"Accepted repository", rejected:"Rejected repository" };
    function unique(key) {
      const values = new Set();
      payload.records.forEach((record) => {
        if (key === "theme") (record.themes || []).forEach((theme) => values.add(theme));
        else if (record[key]) values.add(record[key]);
      });
      return Array.from(values).sort((a, b) => String(a).localeCompare(String(b)));
    }
    function fillSelect(id, values, allLabel) {
      const node = document.getElementById(id);
      node.innerHTML = '<option value="all">' + esc(allLabel) + '</option>' + values.map((value) => '<option value="' + esc(value) + '">' + esc(value) + '</option>').join('');
      node.value = state.filters[id] || "all";
      node.onchange = function () { state.filters[id] = node.value; render(); };
    }
    function filtered() {
      return payload.records.filter((record) => {
        const f = state.filters;
        if (f.status !== "all" && record.statusGroup !== f.status) return false;
        if (f.country !== "all" && record.country !== f.country) return false;
        if (f.place !== "all" && record.place !== f.place) return false;
        if (f.route !== "all" && record.route !== f.route) return false;
        if (f.theme !== "all" && !(record.themes || []).includes(f.theme)) return false;
        if (f.consent !== "all" && record.consent !== f.consent) return false;
        if (f.visibility !== "all" && record.visibility !== f.visibility) return false;
        if (f.reviewer !== "all" && record.reviewer !== f.reviewer) return false;
        return true;
      });
    }
    function renderStats(rows) {
      const count = (group) => rows.filter((record) => record.statusGroup === group).length;
      document.getElementById("stats").innerHTML = [
        ["Filtered", rows.length],
        ["Active review", count("active_review")],
        ["Waiting commit", count("pending_commit")],
        ["Accepted", count("accepted")],
        ["Rejected", count("rejected")]
      ].map((item) => '<div class="stat"><span class="meta">' + esc(item[0]) + '</span><strong>' + esc(item[1]) + '</strong></div>').join('');
    }
    function row(record) {
      const canUncommit = record.statusGroup === "accepted" || record.statusGroup === "rejected";
      const themes = (record.themes || []).slice(0, 4).map((theme) => '<span class="pill">' + esc(theme) + '</span>').join('');
      const enc = (summary) => summary ? esc(summary.label) : "-";
      return '<tr>' +
        '<td data-label="Narrative ID"><strong>' + esc(record.id) + '</strong><br><span class="meta">' + esc(record.seal || "no seal") + '</span></td>' +
        '<td data-label="Route">' + esc(record.route) + '</td>' +
        '<td data-label="Place">' + esc(record.place) + '</td>' +
        '<td data-label="Status">' + esc(record.status) + '<br><span class="meta">' + esc(record.master || "") + '</span></td>' +
        '<td data-label="Manual">' + enc(record.manual) + '</td>' +
        '<td data-label="AI">' + enc(record.ai) + '</td>' +
        '<td data-label="Hybrid">' + enc(record.hybrid) + '</td>' +
        '<td data-label="Reviewer">' + esc(record.reviewer || "-") + '<br>' + esc(record.reason || "") + '</td>' +
        '<td data-label="Themes">' + (themes || "-") + '</td>' +
        '<td data-label="Summary" class="summary">' + esc((record.text || "").slice(0, 240)) + ((record.text || "").length > 240 ? "..." : "") + '</td>' +
        '<td data-label="Action">' + (canUncommit ? '<button class="primary" onclick="uncommit(' + record.index + ')">Uncommit</button>' : '-') + '</td>' +
      '</tr>';
    }
    function section(title, group, rows, description) {
      const subset = rows.filter((record) => record.statusGroup === group);
      return '<h2>' + esc(title) + '</h2><p>' + esc(description) + '</p>' +
        (subset.length ? '<table><thead><tr><th>Narrative ID</th><th>Route</th><th>Place</th><th>Status</th><th>Manual</th><th>AI</th><th>Hybrid</th><th>Reviewer</th><th>Themes</th><th>Summary</th><th>Action</th></tr></thead><tbody>' + subset.map(row).join('') + '</tbody></table>' : '<div class="empty">No records in this section.</div>');
    }
    async function uncommit(index) {
      if (!window.opener || !window.opener.ndimRepositoryUncommit) {
        alert("Return to the NDIM workflow tab to uncommit this record.");
        return;
      }
      const ok = await window.opener.ndimRepositoryUncommit(index);
      if (ok) {
        const record = payload.records.find((item) => item.index === index);
        if (record) {
          record.statusGroup = "active_review";
          record.status = "active review";
          record.reason = "Returned to active review from standalone repository tab.";
          record.committed = "-";
        }
        render();
      }
    }
    function render() {
      const rows = filtered();
      renderStats(rows);
      document.getElementById("sections").innerHTML =
        section("Active approval queue", "active_review", rows, "Records waiting for Approve or Reject in the SDMX gate.") +
        section("Reviewed, waiting for commit", "pending_commit", rows, "Records already approved or rejected locally, but not yet committed.") +
        section("Accepted repository", "accepted", rows, "Records accepted for encoding, modelling, synthesis, and policy audit.") +
        section("Rejected repository", "rejected", rows, "Records preserved for audit but excluded from modelling unless uncommitted and reviewed again.");
    }
    fillSelect("status", Object.keys(label).map((key) => key), "All statuses");
    Array.from(document.getElementById("status").options).forEach((option) => { if (label[option.value]) option.textContent = label[option.value]; });
    fillSelect("country", unique("country"), "All countries");
    fillSelect("place", unique("place"), "All places");
    fillSelect("route", unique("route"), "All routes");
    fillSelect("theme", unique("theme"), "All themes");
    fillSelect("consent", unique("consent"), "All consent");
    fillSelect("visibility", unique("visibility"), "All visibility");
    fillSelect("reviewer", unique("reviewer"), "All reviewers");
    render();
  <\/script>
</body>
</html>`;
      }

      function openStandaloneRepository() {
        const payload = repositoryStandalonePayload();
        const opened = window.open("", "_blank");
        if (!opened) {
          state.repositoryOpen = true;
          toast("Repository opened inside tool");
          trace("repository", "Repository tab blocked; opened in workspace", "The browser blocked the standalone repository tab, so NDIM opened the full repository inside the active workflow.");
          render();
          return;
        }
        opened.document.open();
        opened.document.write(standaloneRepositoryHtml(payload));
        opened.document.close();
        toast("Repository opened");
      }

      async function uncommitRecordByIndex(index) {
        const record = state.records[Number(index)];
        if (!record) return false;
        const ok = await uncommitRecord(record);
        if (ok) await syncLedgerToBackend("repository record uncommitted");
        trace("repository", ok ? "Record uncommitted" : "Record not uncommitted", ok ? `${record.narrative_id} moved back into active review.` : `${record.narrative_id} was not in a committed repository.`);
        toast(ok ? "Record back in review" : "Record not committed");
        render();
        return ok;
      }

      window.ndimRepositoryUncommit = uncommitRecordByIndex;

      function renderMasterRepositoryPanel() {
        const eligible = masterEligibleRecords();
        const pkg = state.masterRepository.package;
        const googleRepo = state.googleRepository || {};
        const statusLabel = String(state.masterRepository.status || "not_prepared").replace(/_/g, " ");
        const syncLabel = String(state.masterRepository.syncStatus || "local_only").replace(/_/g, " ");
        const googleLabel = googleRepo.configured ? "configured" : String(googleRepo.sync_status || "not checked").replace(/_/g, " ");
        const driveLink = googleRepo.drive_url ? `<a class="button" href="${escapeHtml(googleRepo.drive_url)}" target="_blank" rel="noreferrer">Open Drive repository</a>` : "";
        const sheetLink = googleRepo.sheet_url ? `<a class="button" href="${escapeHtml(googleRepo.sheet_url)}" target="_blank" rel="noreferrer">Open Sheets ledger</a>` : "";
        return `
          <div class="master-repo-panel">
            <div>
              <p class="eyebrow">Google-backed research repository</p>
              <h3>Prepare accepted evidence for the master research repository</h3>
              <p>For this deployment phase, NDIM can use Google Drive as the file store and Google Sheets as the lightweight evidence ledger. Drive keeps uploads, reports, SDMX exports, and backups. Sheets keeps the structured review ledger. This is a controlled research-phase repository, not a high-scale production database.</p>
              <p>${escapeHtml(googleRepo.user_message || "Repository status has not been checked yet.")}</p>
            </div>
            <div class="metric-grid">
              <div class="metric"><span class="mini-label">Eligible accepted records</span><strong>${eligible.length}</strong></div>
              <div class="metric"><span class="mini-label">Master status</span><strong>${escapeHtml(statusLabel)}</strong></div>
              <div class="metric"><span class="mini-label">Sync state</span><strong>${escapeHtml(syncLabel)}</strong></div>
              <div class="metric"><span class="mini-label">Google repo</span><strong>${escapeHtml(googleLabel)}</strong></div>
              <div class="metric"><span class="mini-label">Anchor hash</span><strong>${escapeHtml(shortHash(state.masterRepository.anchorHash))}</strong></div>
            </div>
            <div class="field-grid" style="margin-top: 12px;">
              <div class="field"><label for="masterRepositoryTarget">Master repository target</label><input id="masterRepositoryTarget" value="${escapeHtml(state.masterRepository.target)}" placeholder="Google Drive folder + Sheets ledger, institutional DB..." /></div>
              <div class="field"><label for="masterReviewer">Master reviewer</label><input id="masterReviewer" value="${escapeHtml(state.masterRepository.reviewer)}" /></div>
              <div class="field"><label for="masterReviewerRole">Reviewer role</label><input id="masterReviewerRole" value="${escapeHtml(state.masterRepository.role)}" /></div>
              <div class="field"><label for="masterApprovalNote">Master approval note</label><input id="masterApprovalNote" value="${escapeHtml(state.masterRepository.note)}" placeholder="Why this package should or should not update the master repository" /></div>
            </div>
            <div class="button-row">
              <button class="button" id="checkGoogleRepository" type="button">Check Google repository</button>
              ${driveLink}
              ${sheetLink}
              <button class="button primary" id="prepareMasterPush" type="button">Prepare SDMX master push</button>
              <button class="button green" id="approveMasterPush" type="button">Approve master push</button>
              <button class="button" id="rejectMasterPush" type="button">Reject master push</button>
              <button class="button" id="copyMasterPushPackage" type="button">Copy SDMX package</button>
              <button class="button" id="exportMasterPushPackage" type="button">Download SDMX JSON</button>
              <button class="button" id="exportMasterCsv" type="button">Download observation CSV</button>
              <button class="button" id="exportMasterDsd" type="button">Download DSD JSON</button>
            </div>
            <p style="margin-top: 10px;"><strong>Safe phase behavior:</strong> if the Google repository is not configured, NDIM still creates downloadable SDMX JSON, observation CSV, and DSD JSON packages. If it is configured, the links open the Drive folder and Sheets ledger for the governed workspace. Sensitive narrative text remains controlled by consent and visibility settings.</p>
            <p><strong>Blockchain-ready seal:</strong> NDIM creates a chained hash for the master push package and the master approval decision. Later, that anchor hash can be published to a blockchain or institutional timestamp service without exposing restricted narrative text.</p>
            ${pkg ? `<p><strong>Last package:</strong> ${escapeHtml(pkg.sdmx?.observations?.length || 0)} observation(s), status ${escapeHtml(pkg.master_review_status || "-")}, generated ${escapeHtml(pkg.generated_at || "-")}.</p>` : ""}
          </div>
        `;
      }

      function renderFullRepositoryView(forceOpen = false) {
        if (!forceOpen && !state.repositoryOpen) return "";
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
                <p class="eyebrow">Stage 3 / Full repository</p>
                <h2>Narrative review, accepted, and rejected repositories</h2>
                <p>Records move from the active approval queue into the accepted or rejected repository only after Commit reviewed records. Accepted local records can then be packaged for a federated master repository with an SDMX structure and tamper-evident approval seal.</p>
              </div>
              ${forceOpen ? `<button class="button" data-flow-step="${stepIndexById("gate")}" type="button">Back to SDMX gate</button>` : `<button class="button icon-only" data-close-full-repository type="button" aria-label="Close repository" title="Close repository">${icon("x")}</button>`}
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

      function renderGoogleRepositoryCheckpoint() {
        const googleRepo = state.googleRepository || {};
        const googleLabel = googleRepo.configured ? "configured" : String(googleRepo.sync_status || "not checked").replace(/_/g, " ");
        const driveLink = googleRepo.drive_url ? `<a class="button" href="${escapeHtml(googleRepo.drive_url)}" target="_blank" rel="noreferrer">Open Drive repository</a>` : "";
        const sheetLink = googleRepo.sheet_url ? `<a class="button" href="${escapeHtml(googleRepo.sheet_url)}" target="_blank" rel="noreferrer">Open Sheets ledger</a>` : "";
        return `
          <div class="panel" style="margin-top: 14px;">
            <h3>Google-backed research repository</h3>
            <p>For this research phase, Drive can store files and Sheets can store the governed evidence ledger. If the Google repository is not configured, NDIM still prepares downloadable SDMX JSON, observation CSV, and DSD JSON packages for manual upload.</p>
            <div class="metric-grid">
              <div class="metric"><span class="mini-label">Google repo</span><strong>${escapeHtml(googleLabel)}</strong></div>
              <div class="metric"><span class="mini-label">Safe default</span><strong>SDMX package</strong></div>
            </div>
            <p>${escapeHtml(googleRepo.user_message || "Repository status has not been checked yet.")}</p>
            <div class="button-row">
              <button class="button" id="checkGoogleRepository" type="button">Check Google repository</button>
              ${driveLink}
              ${sheetLink}
            </div>
          </div>
        `;
      }

      function renderRepositoryStage() {
        const stats = governanceStats();
        return `
          <section class="stage-card">
            <p class="eyebrow">Stage 3</p>
            <h2>Narrative repository</h2>
            <p class="copy">The full repository now opens in its own standalone tab so the workflow stays short and readable. Use this stage as a compact status checkpoint before encoding.</p>
            <div class="metric-grid">
              <div class="metric"><span class="mini-label">Active review</span><strong>${activeReviewRecords().length}</strong></div>
              <div class="metric"><span class="mini-label">Waiting commit</span><strong>${pendingCommitRecords().length}</strong></div>
              <div class="metric"><span class="mini-label">Accepted</span><strong>${acceptedRepositoryRecords().length}</strong></div>
              <div class="metric"><span class="mini-label">Rejected</span><strong>${rejectedRepositoryRecords().length}</strong></div>
              <div class="metric"><span class="mini-label">Flagged</span><strong>${stats.flagged}</strong></div>
              <div class="metric"><span class="mini-label">Batch seal</span><strong>${escapeHtml(shortHash(state.governance.lastDigest))}</strong></div>
            </div>
            <div class="panel" style="margin-top: 14px;">
              <h3>Repository workflow</h3>
              <p>Approve or reject records in the SDMX gate, then click Commit reviewed records. Accepted records become available for encoding and modelling; rejected records stay preserved for audit. Open the full repository tab for filtering, summaries, hashes, reviewer status, and uncommit controls.</p>
              <div class="button-row">
                <button class="button primary" data-open-full-repository type="button">Open full repository</button>
                <button class="button" data-flow-step="${stepIndexById("gate")}" type="button">Back to SDMX gate</button>
              </div>
            </div>
            ${renderGoogleRepositoryCheckpoint()}
            ${renderContextualNext("Open the full repository when you need detailed review; otherwise continue to encoding.")}
          </section>
        `;
      }

      function renderContextualNext(noteText = "") {
        const next = steps[state.step + 1];
        const isLast = state.step === steps.length - 1;
        const label = isLast ? "Finish and return to intake" : `Continue to ${next.num} ${workspaceStageLabel(next)}`;
        const note = noteText || (isLast
          ? "Complete the workflow, then return to the beginning for another route or workspace."
          : `Continue when this stage is ready. The workflow will move to ${workspaceStageLabel(next)}.`);
        return `
          <div class="context-stage-nav" aria-label="Contextual next action">
            <span class="nav-note">${escapeHtml(note)}</span>
            <button class="button primary" data-context-next type="button">${escapeHtml(label)}</button>
          </div>
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

      function stageCompletionLabel(id = currentStep().id) {
        if (state.completed.has(id)) return "complete";
        if (id === "intake" && state.records.length) return "ready for governance";
        if (id === "gate" && activeReviewRecords().length) return "needs review";
        if (id === "repository" && approvedRecords().length) return "accepted evidence ready";
        if (id === "encoding" && approvedRecords().length) return "ready to encode";
        if (id === "regional" && !state.regional) return "optional";
        if (id === "policy" && state.policy) return "brief ready";
        return "waiting";
      }

      function stagePrimaryActionLabel(id = currentStep().id) {
        return {
          intake: state.records.length ? "Refresh SDMX record preview" : "Validate and stage evidence",
          gate: "Refresh SDMX gate",
          repository: "Refresh repository status",
          encoding: "Run encoding",
          compartmental: "Run compartmental model",
          agents: "Run agent-based model",
          digital: "Run digital twin",
          bayes: "Run Bayesian update",
          rl: "Run RL optimizer",
          regional: "Run optional regional analysis",
          graph: "Build knowledge graph",
          inoculation: "Run inoculation lab",
          policy: "Run policy output"
        }[id] || "Run primary action";
      }

      function stageInputSummary(id = currentStep().id) {
        const summaries = {
          intake: state.records.length ? `${state.records.length} staged record(s) available` : "Evidence route, file or text, SDMX dimensions, and narrative body",
          gate: state.records.length ? `${activeReviewRecords().length} active review record(s), ${pendingCommitRecords().length} waiting for commit` : "Staged narrative records",
          repository: `${acceptedRepositoryRecords().length} accepted, ${rejectedRepositoryRecords().length} rejected, ${activeReviewRecords().length} active`,
          encoding: approvedRecords().length ? `${approvedRecords().length} accepted record(s) ready` : "Accepted repository records",
          compartmental: state.encoded.length ? `${state.encoded.length} encoded narrative(s)` : "Encoded trust and barrier inputs",
          agents: state.encoded.length ? `${state.encoded.length} encoded narrative(s)` : "Encoded evidence and peer-effect settings",
          digital: state.comp || state.agents ? "Model outputs plus field feedback" : "Compartmental or agent model output",
          bayes: state.digital ? "Digital twin feedback and priors" : "Model output plus prior assumptions",
          rl: state.bayes ? "Posterior trust/barrier assumptions" : "Bayesian posterior",
          regional: state.encoded.length ? "Encoded records with place metadata" : "Encoded regional evidence",
          graph: approvedRecords().length ? "Accepted stories, themes, and places" : "Accepted repository records",
          inoculation: state.encoded.length ? "Encoded threat and misinformation signals" : "Encoded narratives",
          policy: approvedRecords().length ? "Accepted evidence, model outputs, and audit trail" : "Completed evidence-to-policy chain"
        };
        return summaries[id] || "Current stage inputs";
      }

      function stageAdvice(id) {
        const advice = {
          intake: "Create traceable narrative observations before any model receives evidence.",
          gate: "Hash, scan, review, and approve evidence before encoding.",
          repository: "Search, filter, inspect, export, uncommit, and prepare accepted evidence for master repository sync.",
          encoding: "Compare manual, AI, and hybrid scoring so model inputs are explainable.",
          compartmental: "Run the population ODE view to estimate aggregate diffusion pressure.",
          agents: "Stress-test local household dynamics, peer effects, and network friction.",
          digital: "Feed field observations back into the model before drawing conclusions.",
          bayes: "Turn priors and observations into posterior trust and barrier assumptions.",
          rl: "Let the optimizer test intervention packages while keeping human review in control.",
          regional: "Optional: analyse each region alone or as a grouped evidence set when place-sensitive recommendations are needed.",
          graph: "Connect stories, places, themes, trust, and barriers for qualitative sense-making.",
        inoculation: "Generate pre-bunking and refutation drafts from encoded narrative risk.",
          policy: "Produce the reviewable policy brief, assumptions, and audit payload."
        };
        return advice[id] || "Continue the evidence-to-policy workflow.";
      }

      function renderStageLauncher() {
        const step = currentStep();
        return `
          <section class="stage-launcher" aria-label="Current stage launcher">
            <div>
              <p class="eyebrow">Focused task workspace</p>
              <h2>${escapeHtml(step.num)} ${escapeHtml(workspaceStageLabel(step))}</h2>
              <p>${escapeHtml(stageAdvice(step.id))}</p>
              <div class="stage-workspace-summary">
                <span>${escapeHtml(stageCompletionLabel(step.id))}</span>
                <span>${escapeHtml(workspaceStageSub(step))}</span>
                <span>${escapeHtml(confidenceLevel())} confidence</span>
              </div>
              <div class="stage-launcher-actions">
                <button class="button primary" data-open-stage-workspace type="button">${icon("start")} Open focused task</button>
                <button class="button" data-run-stage-direct type="button">${escapeHtml(stagePrimaryActionLabel(step.id))}</button>
              </div>
            </div>
            <div class="stage-launcher-grid">
              <div class="stage-launcher-note">
                <strong>What NDIM needs</strong>
                <span>${escapeHtml(stageInputSummary(step.id))}</span>
              </div>
              <div class="stage-launcher-note">
                <strong>What NDIM checks</strong>
                <span>${escapeHtml(stageAdvice(step.id))}</span>
              </div>
              <div class="stage-launcher-note">
                <strong>What changed</strong>
                <span>${escapeHtml(stageCompletionLabel(step.id) === "complete" ? "This stage has produced usable output for downstream stages." : "No final output yet. Open the task workspace to complete or review this stage.")}</span>
              </div>
              <div class="stage-launcher-note">
                <strong>Next action</strong>
                <span>${escapeHtml(assistantNextAction())}</span>
              </div>
            </div>
          </section>
        `;
      }

      function bindCommandCenter() {
        const topRunButton = $("quickRunButton");
        if (topRunButton) topRunButton.onclick = () => openStageWorkspace(state.step);
        const topTraceButton = $("toggleTraceButton");
        if (topTraceButton) topTraceButton.onclick = () => {
          document.querySelector(".reasoning").classList.toggle("open");
        };
        const topAssistantButton = $("toggleAssistantButton");
        if (topAssistantButton) topAssistantButton.onclick = () => {
          state.workspace.assistantOpen = !state.workspace.assistantOpen;
          renderAssistant();
        };
        const floatingAssistantButton = $("floatingAssistantButton");
        if (floatingAssistantButton) floatingAssistantButton.onclick = () => {
          state.workspace.assistantOpen = true;
          trace("assistant", "Research assistant opened", "The floating assistant is reading the current stage, workspace, evidence status, and next action.");
          renderAssistant();
        };
        const closeAssistantButton = $("closeAssistantButton");
        if (closeAssistantButton) closeAssistantButton.onclick = () => {
          state.workspace.assistantOpen = false;
          renderAssistant();
        };
        const topWorkspaceButton = $("workspaceButton");
        if (topWorkspaceButton) topWorkspaceButton.onclick = () => {
          state.workspace.managerOpen = true;
          trace("workspace", "Workspace manager opened", "Choose, create, duplicate, import, or export a project workspace.");
          render();
        };
        const closeWorkspaceModal = $("closeWorkspaceModal");
        if (closeWorkspaceModal) closeWorkspaceModal.onclick = () => {
          state.workspace.managerOpen = false;
          renderWorkspaceManager();
        };
        const workspaceModal = $("workspaceModal");
        if (workspaceModal) workspaceModal.onclick = (event) => {
          if (event.target === workspaceModal) {
            state.workspace.managerOpen = false;
            renderWorkspaceManager();
          }
        };
        const backButton = $("backButton");
        if (backButton) backButton.onclick = () => goStep(state.step - 1);
        const nextButton = $("nextButton");
        if (nextButton) nextButton.onclick = () => {
          if (!state.workspace.started) {
            state.workspace.startOpen = true;
            state.workspace.startMode = "menu";
            trace("workspace", "Start workspace menu opened", "Choose an existing workspace, create one, duplicate one, or import a package.");
            render();
            return;
          }
          nextStep();
        };
        const resetStageButton = $("resetStageButton");
        if (resetStageButton) resetStageButton.onclick = resetCurrentStage;
        const closeTraceButton = $("closeTraceButton");
        if (closeTraceButton) closeTraceButton.onclick = () => {
          document.querySelector(".reasoning").classList.remove("open");
        };
        const clearTraceButton = $("clearTrace");
        if (clearTraceButton) clearTraceButton.onclick = () => {
          state.trace = [["idle", "Log cleared", "The workflow state is unchanged; only the visible reasoning log was cleared."]];
          renderTrace();
        };
        const themeIconToggle = $("themeIconToggle");
        if (themeIconToggle) themeIconToggle.onclick = () => {
          setTheme(document.documentElement.dataset.theme === "dark" ? "light" : "dark");
        };
        const runButton = $("workbenchRunButton");
        if (runButton) runButton.addEventListener("click", () => openStageWorkspace(state.step));
        const traceButton = $("workbenchTraceButton");
        if (traceButton) traceButton.addEventListener("click", () => {
          document.querySelector(".reasoning").classList.toggle("open");
        });
        document.querySelectorAll("[data-start-toggle]").forEach((button) => {
          button.addEventListener("click", () => {
            state.workspace.startOpen = !state.workspace.startOpen;
            if (state.workspace.startOpen && !state.workspace.startMode) state.workspace.startMode = "menu";
            trace("workspace", "Start workspace menu toggled", "Choose whether to continue, open, create, or import a workspace. Duplicating is available beside each existing workspace.");
            render();
          });
        });
        document.querySelectorAll("[data-start-action]").forEach((button) => {
          button.addEventListener("click", () => {
            const action = button.dataset.startAction;
            if (action === "continue") {
              startWorkspaceSession(`${workspaceName()} is active. The guided NDIM workflow is now visible.`);
              render();
              return;
            }
            if (action === "open") {
              state.workspace.startOpen = true;
              state.workspace.startMode = state.workspace.startMode === "open" ? "menu" : "open";
              trace("workspace", "Existing workspaces requested", "Select the project workspace NDIM should run.");
              render();
              return;
            }
            if (action === "create" || action === "import") {
              state.workspace.managerOpen = true;
              state.workspace.startOpen = false;
              trace("workspace", `${action} workspace selected`, "The workspace manager is open with existing workspace, blank workspace, duplicate, import, and export controls.");
              render();
            }
          });
        });
        document.querySelectorAll("[data-open-workspace-manager]").forEach((button) => {
          button.addEventListener("click", () => {
            state.workspace.managerOpen = true;
            trace("workspace", "Workspace manager opened", "Choose, create, duplicate, import, or export a project workspace.");
            render();
          });
        });
        document.querySelectorAll("[data-open-assistant-panel]").forEach((button) => {
          button.addEventListener("click", () => {
            state.workspace.assistantOpen = true;
            trace("assistant", "Research assistant opened", "The assistant is reading the active workspace, stage progress, evidence counts, and next action.");
            render();
          });
        });
        document.querySelectorAll("[data-open-stage-workspace]").forEach((button) => {
          button.addEventListener("click", () => openStageWorkspace(state.step));
        });
        document.querySelectorAll("[data-run-stage-direct]").forEach((button) => {
          button.addEventListener("click", runCurrentStageShortcut);
        });
        const closeStageButton = $("closeStageWorkspace");
        if (closeStageButton) closeStageButton.onclick = closeStageWorkspace;
        const stageBackdrop = $("stageWorkspaceBackdrop");
        if (stageBackdrop) stageBackdrop.onclick = closeStageWorkspace;
        const runStagePrimary = $("runStagePrimaryAction");
        if (runStagePrimary) runStagePrimary.onclick = runCurrentStageShortcut;
        document.querySelectorAll("[data-workspace-open-quick]").forEach((button) => {
          button.addEventListener("click", async () => {
            const target = button.dataset.workspaceOpenQuick;
            if (!target) return;
            if (target === workspaceId()) {
              startWorkspaceSession(`${workspaceName()} is active. The guided NDIM workflow is now visible.`);
              render();
              return;
            }
            try {
              await setActiveWorkspace(target);
              startWorkspaceSession(`${workspaceName()} is now the active project workspace.`);
              render();
            } catch (error) {
              toast(error.message || "Workspace not opened");
            }
          });
        });
        document.querySelectorAll("[data-jump-repository]").forEach((button) => {
          button.addEventListener("click", (event) => {
            event.preventDefault();
            trace("repository", "Standalone repository opened", state.records.length ? `${state.records.length} staged record(s) are available for review, commit, and repository inspection.` : "The repository is empty until evidence is staged and validated.");
            openStandaloneRepository();
          });
        });
        document.querySelectorAll("[data-open-full-repository]").forEach((button) => {
          button.addEventListener("click", () => {
            trace("repository", "Standalone repository opened", `${activeReviewRecords().length} active, ${acceptedRepositoryRecords().length} accepted, and ${rejectedRepositoryRecords().length} rejected record(s) are available.`);
            openStandaloneRepository();
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
          ["checkGoogleRepository", async () => {
            await refreshGoogleRepositoryStatus();
            trace("master repository", "Google repository checked", state.googleRepository?.user_message || "Repository status refreshed.");
            toast(state.googleRepository?.configured ? "Google repository configured" : "Google repository not configured");
            render();
          }],
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
            await uncommitRecordByIndex(button.dataset.uncommitRecord);
            requestAnimationFrame(() => $("fullRepositoryView")?.scrollIntoView({ behavior: "smooth", block: "start" }));
          });
        });
        document.querySelectorAll("[data-flow-step]").forEach((button) => {
          button.addEventListener("click", () => openStageWorkspace(Number(button.dataset.flowStep)));
          button.addEventListener("keydown", (event) => {
            if (event.key === "Enter" || event.key === " ") {
              event.preventDefault();
              openStageWorkspace(Number(button.dataset.flowStep));
            }
          });
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
        const stageCard = document.querySelector(".stage-launcher, .repository-full-view");
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

      function assistantStatusValue(value) {
        if (value === true) return "yes";
        if (value === false) return "not yet";
        return String(value ?? "-");
      }

      function assistantNextAction() {
        const id = currentStep().id;
        if (id === "intake") return state.records.length ? "Review SDMX readiness and continue to governance." : "Load or paste evidence, then stage narrative records.";
        if (id === "gate") return pendingCommitRecords().length ? "Commit reviewed records into the accepted or rejected repository." : activeReviewRecords().length ? "Approve or reject each active record." : "Continue to repository review.";
        if (id === "repository") return approvedRecords().length ? "Continue to encoding with accepted evidence." : "Approve and commit at least one record before modelling.";
        if (id === "encoding") return state.encoded.length ? "Review encoding outputs, then run the population model." : "Run manual, AI, or hybrid encoding on accepted records.";
        if (id === "compartmental") return state.comp ? "Compare the ODE result with the agent-based model." : "Run the S/M/T/I/R compartmental model.";
        if (id === "agents") return state.agents ? "Use field feedback to update the digital twin." : "Run the household and peer-effects model.";
        if (id === "digital") return state.digital ? "Update uncertainty with the Bayesian stage." : "Enter field feedback and run the digital twin.";
        if (id === "bayes") return state.bayes ? "Run RL to shortlist intervention packages." : "Run the Bayesian posterior update.";
        if (id === "rl") return state.rl ? "Move to optional regional analysis or continue to synthesis." : "Run the policy optimizer.";
        if (id === "regional") return state.regional ? "Build the knowledge graph." : "Optional stage: run place-based analysis when you need district or region-specific recommendations, or continue with pooled evidence.";
        if (id === "graph") return state.graph ? "Generate inoculation narratives." : "Build the story/theme/place graph.";
        if (id === "inoculation") return state.inoculation ? "Apply or review narrative vaccines, then export policy output." : "Generate counter-narratives for human review.";
        return state.policy ? "Export the HTML/PDF brief and archive the audit payload." : "Run the policy output stage.";
      }

      function assistantInterpretation() {
        const id = currentStep().id;
        const thin = approvedRecords().length < 3;
        const caution = thin ? "Evidence is thin. Treat model output as exploratory until more records are approved and encoded." : "Evidence volume is improving, but human review is still required before policy use.";
        const snippets = {
          intake: "The workspace determines which evidence routes, templates, and project defaults are active. Good modelling starts with clean context.",
          gate: "Governance protects the research chain: consent, visibility, approval, rejection, commit history, and hashes decide what can influence the model.",
          repository: "Only accepted committed records should feed encoding and modelling. Rejected records stay visible for audit but do not influence policy output.",
          encoding: "Encoding converts narrative meaning into trust, barrier, confidence, theme, and inoculation-risk signals.",
          compartmental: "The ODE model estimates aggregate movement through susceptible, misinformed, truth-aligned, inoculated, and resistant states.",
          agents: "The agent model checks whether household heterogeneity and peer effects change the adoption pathway.",
          digital: "The twin is a feedback-adjusted scenario model. It is not a claim of real adoption unless calibrated with repeated field observations.",
          bayes: "Posterior values show how evidence changes prior assumptions. Wide uncertainty should slow policy claims.",
          rl: "The optimizer ranks intervention packages; it does not replace political, ethical, or field judgment.",
          regional: "Regional comparison helps decide whether a national message is appropriate or whether districts need different interventions.",
          graph: "The graph shows repeated story structures by place and theme, useful for seeing where narratives cluster.",
          inoculation: "Inoculation drafts are narrative vaccines: weak-dose claim, refutation, trusted messenger, and booster plan.",
          policy: "The final brief should state confidence, assumptions, limitations, uncertainty, and required human review."
        };
        return `${snippets[id] || ""} ${caution}`;
      }

      function renderAssistant() {
        const panel = $("assistantPanel");
        const body = $("assistantBody");
        if (!panel || !body) return;
        panel.classList.toggle("open", Boolean(state.workspace.assistantOpen));
        const step = currentStep();
        const settings = workspaceSettings();
        const projectGuidance = settings.assistant?.project_guidance || [];
        body.innerHTML = `
          <div class="assistant-card">
            <h3>${escapeHtml(state.workspace.started ? workspaceStageLabel(step) : "Start workspace")}</h3>
            <p><strong>Workspace:</strong> ${escapeHtml(workspaceName())}</p>
            <p>${escapeHtml(state.workspace.started ? assistantInterpretation() : "Choose, create, duplicate, or import a workspace. After that I will reveal the NDIM workflow and guide each scientific stage in plain language.")}</p>
          </div>
          <div class="assistant-card">
            <h3>Progress</h3>
            <div class="assistant-progress">
              <div><span>Evidence collected</span><strong>${assistantStatusValue(state.records.length)}</strong></div>
              <div><span>Pending review</span><strong>${activeReviewRecords().length}</strong></div>
              <div><span>Accepted</span><strong>${approvedRecords().length}</strong></div>
              <div><span>Encoded</span><strong>${state.encoded.length}</strong></div>
              <div><span>Model run</span><strong>${assistantStatusValue(Boolean(state.comp || state.agents))}</strong></div>
              <div><span>Digital twin</span><strong>${assistantStatusValue(Boolean(state.digital))}</strong></div>
              <div><span>Bayesian</span><strong>${assistantStatusValue(Boolean(state.bayes))}</strong></div>
              <div><span>Policy brief</span><strong>${assistantStatusValue(Boolean(state.policy))}</strong></div>
            </div>
          </div>
          <div class="assistant-card">
            <h3>Work plan</h3>
            <div class="agent-worklist">
              ${assistantWorkItems().map(([label, done]) => `
                <div class="agent-workitem ${done ? "done" : ""}">
                  <span class="agent-dot"></span>
                  <strong>${escapeHtml(label)}</strong>
                  <span>${done ? "done" : "waiting"}</span>
                </div>
              `).join("")}
            </div>
          </div>
          <div class="assistant-card">
            <h3>Next best action</h3>
            <p>${escapeHtml(state.workspace.started ? assistantNextAction() : "Click Start workspace, then choose Continue last workspace, Open existing workspace, Create new workspace, Duplicate workspace, or Import workspace package.")}</p>
          </div>
          <div class="assistant-card">
            <h3>Scientific caution</h3>
            <p>${escapeHtml(evidenceGrade() === "do not use for policy" ? "Do not use this run for policy yet. Add evidence, review records, and rerun validation/model stages." : "Use outputs as decision support, not automatic decisions. Check assumptions, evidence grade, and human review status.")}</p>
          </div>
          ${projectGuidance.length ? `<div class="assistant-card"><h3>Workspace guidance</h3><ul>${projectGuidance.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul></div>` : ""}
        `;
      }

      function renderWorkspaceManager() {
        const modal = $("workspaceModal");
        const body = $("workspaceModalBody");
        if (!modal || !body) return;
        modal.classList.toggle("open", Boolean(state.workspace.managerOpen));
        modal.setAttribute("aria-hidden", state.workspace.managerOpen ? "false" : "true");
        const activeId = workspaceId();
        body.innerHTML = `
          <section>
            <h3>Start from</h3>
            <p class="copy">Choose <strong>From scratch</strong> for a new project, or open/duplicate an existing workspace. NDIM Core is only the built-in fallback template; it does not need to be your active project.</p>
            <div class="workspace-list">
              <div class="workspace-list-item from-scratch">
                <div class="workspace-list-icon">${icon("plus")}</div>
                <div>
                  <h3>From scratch</h3>
                  <p>Begin with a blank project container, then define the country, domain, evidence routes, repository rules, and export settings.</p>
                  <p class="mini-label">NEW WORKSPACE / BLANK SETUP</p>
                </div>
                <div class="workspace-list-actions">
                  <button class="button primary" data-workspace-from-scratch type="button">Set up new workspace</button>
                </div>
              </div>
              ${(state.workspace.list || []).map((item) => {
                const isCurrent = state.workspace.started && item.workspace_id === activeId;
                return `
                <div class="workspace-list-item ${isCurrent ? "active" : ""}">
                  <div class="workspace-list-icon">${icon("folder")}</div>
                  <div>
                    <h3>${escapeHtml(item.name)}</h3>
                    <p>${escapeHtml(item.description || item.domain || "NDIM workspace")}</p>
                    <p class="mini-label">${escapeHtml(item.workspace_id)}${item.countries?.length ? ` / ${escapeHtml(item.countries.join(", "))}` : ""}</p>
                  </div>
                  <div class="workspace-list-actions">
                    <button class="button ${isCurrent ? "primary" : ""}" data-workspace-open="${escapeHtml(item.workspace_id)}" type="button">${isCurrent ? "Current" : "Open"}</button>
                    <button class="button icon-only" data-workspace-duplicate="${escapeHtml(item.workspace_id)}" type="button" title="Duplicate ${escapeHtml(item.name)}" aria-label="Duplicate ${escapeHtml(item.name)}">${icon("copy")}</button>
                  </div>
                </div>
              `}).join("")}
            </div>
          </section>
          <section class="panel" id="workspaceCreatePanel">
            <h3>Create blank workspace</h3>
            <p>Use this for a genuinely new study, country, policy programme, or fieldwork stream. It is not prefilled from ClimateTales or the active workspace.</p>
            <div class="workspace-form-grid">
              <div class="field"><label for="workspaceNewName">Workspace name</label><input id="workspaceNewName" placeholder="e.g., Clean Cooking Ghana Pilot" /></div>
              <div class="field"><label for="workspaceNewCountry">Country</label><input id="workspaceNewCountry" placeholder="e.g., Ghana" /></div>
              <div class="field"><label for="workspaceNewDomain">Domain</label><input id="workspaceNewDomain" placeholder="e.g., clean cooking, climate communication" /></div>
              <div class="field"><label for="workspaceNewDescription">Description</label><input id="workspaceNewDescription" placeholder="Short project purpose" /></div>
            </div>
            <div class="button-row"><button class="button primary" id="createWorkspaceButton" type="button">Create workspace</button></div>
          </section>
          <section class="panel">
            <h3>Import and export</h3>
            <p>Export defaults to template-only so sensitive narratives are not shared by accident. Use the duplicate icon in Open workspace when you want to copy a specific existing workspace.</p>
            <div class="workspace-form-grid">
              <div class="field"><label for="workspaceExportMode">Export mode</label><select id="workspaceExportMode">
                <option value="template_only">Template only</option>
                <option value="template_with_stress_test">Template + stress-test data</option>
                <option value="full_backup">Full workspace backup</option>
              </select></div>
              <div class="field"><label for="workspaceImportFile">Import package</label><input id="workspaceImportFile" type="file" accept=".zip,.ndim-workspace" /></div>
            </div>
            <div class="button-row">
              <button class="button" id="exportWorkspaceButton" type="button">Export active workspace</button>
            </div>
          </section>
        `;
        document.querySelectorAll("[data-workspace-open]").forEach((button) => {
          button.addEventListener("click", async () => {
            if (button.dataset.workspaceOpen !== activeId) {
              await setActiveWorkspace(button.dataset.workspaceOpen);
            }
            startWorkspaceSession(`${workspaceName()} is now the active project workspace.`);
            state.workspace.managerOpen = false;
            render();
          });
        });
        document.querySelectorAll("[data-workspace-from-scratch]").forEach((button) => {
          button.addEventListener("click", () => {
            $("workspaceCreatePanel")?.scrollIntoView({ behavior: "smooth", block: "start" });
            setTimeout(() => $("workspaceNewName")?.focus(), 80);
            trace("workspace", "Blank workspace setup selected", "Fill the create form to define a new workspace from scratch.");
          });
        });
        document.querySelectorAll("[data-workspace-duplicate]").forEach((button) => {
          button.addEventListener("click", async () => {
            try {
              await duplicateWorkspaceById(button.dataset.workspaceDuplicate);
              state.workspace.managerOpen = false;
              render();
            } catch (error) {
              toast(error.message || "Workspace not duplicated");
            }
          });
        });
        $("createWorkspaceButton")?.addEventListener("click", async () => {
          try { await createWorkspaceFromManager(); render(); } catch (error) { toast(error.message || "Workspace not created"); }
        });
        $("exportWorkspaceButton")?.addEventListener("click", exportActiveWorkspace);
        $("workspaceImportFile")?.addEventListener("change", async (event) => {
          try {
            await importWorkspaceFromFile(event.target.files && event.target.files[0]);
            state.workspace.managerOpen = false;
            render();
          } catch (error) {
            toast(error.message || "Workspace import failed");
          }
        });
      }

      function renderStageWorkspace() {
        const panel = $("stageWorkspace");
        const backdrop = $("stageWorkspaceBackdrop");
        const body = $("stageWorkspaceBody");
        const title = $("stageWorkspaceTitle");
        const copy = $("stageWorkspaceCopy");
        const kicker = $("stageWorkspaceKicker");
        const summary = $("stageWorkspaceSummary");
        const runButton = $("runStagePrimaryAction");
        if (!panel || !backdrop || !body || !title || !copy || !kicker || !summary) return;
        const open = Boolean(state.workspace.started && state.stageWorkspace.open);
        panel.classList.toggle("open", open);
        backdrop.classList.toggle("open", open);
        panel.setAttribute("aria-hidden", open ? "false" : "true");
        backdrop.setAttribute("aria-hidden", open ? "false" : "true");
        if (!open) {
          body.innerHTML = "";
          return;
        }
        const step = currentStep();
        kicker.textContent = `Stage ${step.num} / focused task`;
        title.textContent = workspaceStageLabel(step);
        copy.textContent = stageAdvice(step.id);
        summary.innerHTML = `
          <span>${escapeHtml(stageCompletionLabel(step.id))}</span>
          <span>${escapeHtml(stageInputSummary(step.id))}</span>
          <span>${escapeHtml(assistantNextAction())}</span>
        `;
        if (runButton) runButton.textContent = stagePrimaryActionLabel(step.id);
        body.innerHTML = renderStage(step.id) + renderContextStageNav();
        bindStage(step.id);
        bindContextStageNav();
        renderMath();
      }

      function render() {
        const step = currentStep();
        $("appShell")?.classList.toggle("workspace-start-mode", !state.workspace.started);
        $("topTitle").textContent = state.workspace.started ? workspaceStageLabel(step) : "Start NDIM workspace";
        $("topCopy").textContent = state.workspace.started ? workspaceStageSub(step) : "Choose or create the project container that NDIM will run.";
        if ($("workspaceName")) $("workspaceName").textContent = workspaceName();
        if ($("assistantEyebrow")) $("assistantEyebrow").textContent = workspaceSettings().assistant?.name || "Research Assistant";
        renderStepList();
        renderStageJump();
        renderAssistant();
        renderWorkspaceManager();
        if (!state.workspace.started) {
          state.stageWorkspace.open = false;
          $("stagePanel").innerHTML = renderStartExperience();
          $("backButton").disabled = true;
          $("nextButton").textContent = "Start";
          bindCommandCenter();
          renderStageWorkspace();
          renderMath();
          syncWorkflowStagesOffset();
          return;
        }
        const floatingRepository = step.id === "repository" ? "" : renderFullRepositoryView();
        $("stagePanel").innerHTML = renderCommandCenter() + renderStageLauncher() + floatingRepository;
        $("backButton").disabled = state.step === 0;
        $("nextButton").textContent = state.step === steps.length - 1 ? "Finish" : "Next";
        bindCommandCenter();
        renderStageWorkspace();
        renderMath();
        syncWorkflowStagesOffset();
      }

      function renderStage(id) {
        if (id === "intake") return renderIntake();
        if (id === "gate") return renderGate();
        if (id === "repository") return renderRepositoryStage();
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
        const nextLabel = isLast ? "Finish and return to intake" : `Continue to ${next.num} ${workspaceStageLabel(next)}`;
        const note = isLast
          ? "At the end, Finish returns to the beginning so another evidence route can be tested."
          : `Next stage: ${workspaceStageLabel(next).toLowerCase()}. The page will jump to the active stage top.`;
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
          focus_group: "focus_group",
          open_story: "field_note",
          indigenous_knowledge: "indigenous_knowledge",
          citizen_science: "citizen_report",
          crowd_batch: "csv",
          experimental_feed: "social_feed",
          custom_evidence: "custom_evidence"
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
          batch: "Open batch file",
          single: "Open single story",
          manual_entry: "Start manual entry",
          guide: "Open intake guide",
          copy: "Copy field template",
          download: "Download template",
          reset: "Reset intake"
        }[option] || "Start manual entry";
      }

      function renderIntakeLoadPanel() {
        return `
          <div class="panel file-control-panel">
            <div>
              <span class="step-kicker">Step 2 / load or paste evidence</span>
              <h3>Choose how to add evidence</h3>
              <p>Select whether you are importing many narratives, opening one story file, or manually adding evidence in the form below. TXT, MD, CSV, JSON, XML, and SDMX files are accepted.</p>
              <div class="compact-select-row" style="margin-top: 12px;">
                <div class="field"><label for="intakeOptionSelect">Evidence input method</label><select id="intakeOptionSelect">
                  <option ${selectedAttr("batch", state.intakeOption)} value="batch">Batch import: CSV or text</option>
                  <option ${selectedAttr("single", state.intakeOption)} value="single">Single story import</option>
                  <option ${selectedAttr("manual_entry", state.intakeOption)} value="manual_entry">Manual entry</option>
                  <option ${selectedAttr("guide", state.intakeOption)} value="guide">Open intake guide</option>
                  <option ${selectedAttr("copy", state.intakeOption)} value="copy">Copy field template</option>
                  <option ${selectedAttr("download", state.intakeOption)} value="download">Download CSV template</option>
                  <option ${selectedAttr("reset", state.intakeOption)} value="reset">Reset intake</option>
                </select></div>
                <button class="button primary" id="runIntakeOption" type="button">${escapeHtml(intakeOptionActionLabel())}</button>
              </div>
              <input id="fileInput" type="file" accept=".txt,.md,.csv,.json,.xml,.sdmx" hidden />
              <p class="select-note">Batch import can load CSV rows or paragraph-separated text. Single story import loads one file into the current route. Manual entry keeps the user in the form.</p>
              <div class="guide-note" style="margin-top: 12px;">
                <strong>Single-story practice</strong>
                <p>To test one story, choose <b>Single story import</b> or <b>Manual entry</b>. The tool no longer loads a hidden built-in sample from this panel, because stress testing should use explicit files from the corpus or text you paste yourself.</p>
              </div>
            </div>
            <div class="intake-option-strip">
              <h3>Input method explained</h3>
              <p class="select-note">${escapeHtml(state.intakeOption === "batch" ? "Use this when testing a corpus or loading many field records at once." : state.intakeOption === "single" ? "Use this when reviewing one story, interview transcript, or field note." : state.intakeOption === "manual_entry" ? "Use this when typing or pasting evidence directly into the route-specific form." : "This option supports the intake workflow without adding evidence.")}</p>
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
        } else if (state.template.evidenceMode === "focus_group") {
          rows.push(
            ["Focus group ID", state.template.interviewId || "recommended", true],
            ["Group profile", state.template.respondentProfile, Boolean(state.template.respondentProfile)],
            ["Common cooking methods", state.template.cookingMethods || "recommended", true],
            ["Contributor type", state.template.contributorType || "recommended", true],
            ["Community validation", state.template.communityValidation, Boolean(state.template.communityValidation)],
            ["Validation status", state.template.validationStatus, Boolean(state.template.validationStatus)]
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
        } else if (state.template.evidenceMode === "custom_evidence") {
          rows.push(
            ["Custom route name", state.template.customRouteName, Boolean(state.template.customRouteName)],
            ["Custom evidence type", state.template.customEvidenceType, Boolean(state.template.customEvidenceType)],
            ["Record or batch ID", state.template.interviewId || "recommended", true],
            ["Attribution", state.template.attribution || "mode-dependent", true],
            ["Validation status", state.template.validationStatus || "mode-dependent", true],
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
            <div class="field"><label for="sourceType">Source type</label><select id="sourceType"><option ${selectedAttr("field_note", state.meta.sourceType)} value="field_note">Field note</option><option ${selectedAttr("interview", state.meta.sourceType)} value="interview">Interview</option><option ${selectedAttr("focus_group", state.meta.sourceType)} value="focus_group">Focus group</option><option ${selectedAttr("oral_history", state.meta.sourceType)} value="oral_history">Oral history</option><option ${selectedAttr("community_meeting", state.meta.sourceType)} value="community_meeting">Community meeting</option><option ${selectedAttr("citizen_report", state.meta.sourceType)} value="citizen_report">Citizen report</option><option ${selectedAttr("indigenous_knowledge", state.meta.sourceType)} value="indigenous_knowledge">Indigenous knowledge</option><option ${selectedAttr("radio", state.meta.sourceType)} value="radio">Radio transcript</option><option ${selectedAttr("social_feed", state.meta.sourceType)} value="social_feed">Social/community feed</option><option ${selectedAttr("custom_evidence", state.meta.sourceType)} value="custom_evidence">Custom evidence</option><option ${selectedAttr("policy_brief", state.meta.sourceType)} value="policy_brief">Policy brief</option><option ${selectedAttr("csv", state.meta.sourceType)} value="csv">CSV extract</option><option ${selectedAttr("sdmx", state.meta.sourceType)} value="sdmx">SDMX exchange</option></select></div>
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
        if (mode === "focus_group") {
          return `
            <div class="panel" style="margin-top: 14px;">
              <h3>Focus group metadata</h3>
              <p>Use this for facilitated group discussions. Capture the group context, moderator, consent level, speaker composition, and any translation notes before modelling.</p>
              <div class="field-grid" style="margin-top: 12px;">
                ${renderRecordIdField("Focus group ID", "e.g., FGD-RW-MUS-001")}
                <div class="field"><label for="respondentProfile">Group profile</label><input id="respondentProfile" value="${escapeHtml(state.template.respondentProfile)}" placeholder="e.g., 8 women farmers, 3 youth, 1 cooperative leader" /></div>
                <div class="field"><label for="cookingMethods">Common cooking method(s)</label><input id="cookingMethods" value="${escapeHtml(state.template.cookingMethods)}" placeholder="firewood, charcoal, LPG, improved cookstove..." /></div>
                ${renderContributorTypeField(false)}
                ${renderAttributionField()}
                ${renderLocationPrecisionField()}
                ${renderCommunityValidationField()}
                ${renderValidationStatusField()}
                ${renderTranslationField()}
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
        if (mode === "custom_evidence") {
          return `
            <div class="panel" style="margin-top: 14px;">
              <h3>Other / custom evidence setup</h3>
              <p>Name the evidence route and classify the evidence type. NDIM will keep it coherent by writing it to the same governed observation table with custom-route provenance.</p>
              <div class="field-grid" style="margin-top: 12px;">
                <div class="field"><label for="customRouteName">Evidence route name</label><input id="customRouteName" value="${escapeHtml(state.template.customRouteName)}" placeholder="e.g., district workshop note, market observation..." /></div>
                <div class="field"><label for="customEvidenceType">Evidence type</label><select id="customEvidenceType">
                  <option ${selectedAttr("narrative", state.template.customEvidenceType)} value="narrative">Narrative</option>
                  <option ${selectedAttr("observation", state.template.customEvidenceType)} value="observation">Observation</option>
                  <option ${selectedAttr("document", state.template.customEvidenceType)} value="document">Document</option>
                  <option ${selectedAttr("media_transcript", state.template.customEvidenceType)} value="media_transcript">Media transcript</option>
                  <option ${selectedAttr("administrative_note", state.template.customEvidenceType)} value="administrative_note">Administrative note</option>
                  <option ${selectedAttr("mixed", state.template.customEvidenceType)} value="mixed">Mixed evidence</option>
                </select></div>
                ${renderRecordIdField("Custom record ID", "e.g., CUSTOM-RW-MUS-001")}
                ${renderContributorTypeField(false)}
                ${renderAttributionField()}
                ${renderLocationPrecisionField()}
                ${renderValidationStatusField()}
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
          focus_group: "Paste the focus group transcript, facilitator notes, speaker excerpts, or thematic summary. Preserve group dynamics, consensus, disagreement, and local terms...",
          open_story: "Paste the full story in the contributor's own words. Keep sequence, emotion, local terms, and context...",
          indigenous_knowledge: "Record the knowledge carefully: local practice, seasonal memory, elder testimony, cultural explanation, or ecological observation...",
          citizen_science: "Paste the observation: what was seen, where, when, by whom, and how confident the contributor is...",
          crowd_batch: "Paste one submitted story per paragraph, or load a CSV with evidence_mode, country, admin fields, and narrative/text/quote columns...",
          experimental_feed: "Paste one social media post, community comment, radio transcript excerpt, WhatsApp summary, or moderated feed item per line. Each line becomes an observation after governance...",
          custom_evidence: "Describe the custom evidence in plain language. Keep enough context for SDMX dimensions, provenance, review, and later interpretation..."
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
        if (mode === "focus_group") {
          return `
            <div class="panel">
              ${summary}
              <h3 style="margin-top: 16px;">Focus group discussion prompts</h3>
              <div class="check-list">
                ${knowledgePrompt("Composition", "Who was in the room, what roles did they represent, and whose voice may be missing?")}
                ${knowledgePrompt("Consensus", "Which views were widely shared, and which were contested or minority views?")}
                ${knowledgePrompt("Influence", "Which trusted messengers, peer groups, leaders, or institutions shaped the discussion?")}
                ${knowledgePrompt("Risk", "What misinformation, fear, identity tension, or adoption barrier appeared in the group?")}
              </div>
              <h3 style="margin-top: 16px;">Optional analytic coding</h3>
              <div style="margin-top: 10px;">${renderCodingFields()}</div>
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
                  ["evidence_mode", "structured_interview, focus_group, open_story, indigenous_knowledge, citizen_science, crowd_batch, experimental_feed, or custom_evidence", "yes"],
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
        if (mode === "custom_evidence") {
          return `
            <div class="panel">
              ${summary}
              <h3 style="margin-top: 16px;">Custom evidence route</h3>
              <p>Use this only when the standard evidence routes do not fit. NDIM will still convert the input into the same SDMX-compatible observation structure and mark it as a custom route in the repository.</p>
              <div class="check-list">
                ${knowledgePrompt("Traceability", "Name what kind of evidence this is so reviewers know why it does not fit a standard route.")}
                ${knowledgePrompt("Governance", "Custom evidence still needs source, consent, visibility, period, location, and review before modelling.")}
                ${knowledgePrompt("Audit trail", "The repository will label this as custom_route and keep the custom name/type in provenance.")}
              </div>
              <h3 style="margin-top: 16px;">Optional analytic coding</h3>
              <div style="margin-top: 10px;">${renderCodingFields()}</div>
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
        const modes = activeEvidenceModes();
        return `
          <div class="field" style="margin-top: 10px;"><label for="evidenceModeSelect">Evidence route</label><select id="evidenceModeSelect">
            ${modes.map((mode) => `<option ${selectedAttr(mode.id, state.template.evidenceMode)} value="${escapeHtml(mode.id)}">${escapeHtml(mode.title)}</option>`).join("")}
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

      function encodingSummaryForRecord(record, mode) {
        const item = encodedFor(mode, record?.narrative_id);
        if (!item) return null;
        const trust = typeof item.trust_score === "number" ? item.trust_score.toFixed(2) : "-";
        const barrier = typeof item.adoption_barrier_score === "number" ? item.adoption_barrier_score.toFixed(2) : "-";
        const confidence = typeof item.confidence === "number" ? item.confidence.toFixed(2) : "-";
        const phi = typeof item.manual_scorecard?.phi === "number" ? item.manual_scorecard.phi.toFixed(3) : null;
        return {
          mode,
          trust,
          barrier,
          confidence,
          phi,
          label: `${mode}: trust ${trust}, barrier ${barrier}, conf ${confidence}${phi ? `, Phi ${phi}` : ""}`,
          themes: (item.themes || []).join(", "),
          notes: item.model_notes || item.reviewer_notes || ""
        };
      }

      function repositoryEncodingCell(record, mode) {
        const summary = encodingSummaryForRecord(record, mode);
        if (!summary) return "-";
        return `<strong>${escapeHtml(summary.mode)}</strong><br/><small>${escapeHtml(`trust ${summary.trust} | barrier ${summary.barrier} | conf ${summary.confidence}${summary.phi ? ` | Phi ${summary.phi}` : ""}`)}</small>`;
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
          evidence_route: activeEvidenceModes().map((mode) => ({ id: mode.id, name: mode.title })),
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
          note: "Research-phase package for updating a governed master narrative repository. Google Drive is the file store and Google Sheets is the lightweight ledger when configured. No upload occurs without a configured backend or user-controlled sync step.",
          generated_at: new Date().toISOString(),
          target: state.masterRepository.target,
          backend: state.masterRepository.backend,
          google_repository: state.googleRepository || null,
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

      function renderEncodingModePanel(record, card, reviewed, records) {
        if (state.encodingMode === "manual") {
          return `
            <div class="grid-2" style="margin-top: 14px;">
              <div class="panel">
                <h3>Manual encoder: current story only</h3>
                <p>Score one narrative at a time. Save the current score, review the comparison block, then continue to the next story. This prevents batch imports from being treated as one merged narrative.</p>
                ${renderStoryNavigator()}
                <div class="field-grid" style="margin-top: 12px;">
                  <div class="field"><label for="encoderName">Encoder name or ID</label><input id="encoderName" value="${escapeHtml(state.encoderName)}" placeholder="e.g., coder-01" /></div>
                  <div class="field"><label>Manual progress</label><input value="${reviewed} of ${records.length} reviewed" disabled /></div>
                </div>
                ${renderManualScorecard(record, card)}
                <div class="button-row">
                  <button class="button primary" id="runCurrentEncoding" type="button">Save current manual score and continue</button>
                  <button class="button" id="resetEncoding" type="button">Reset encoding</button>
                </div>
              </div>
              <div>
                <div class="panel" style="margin-bottom: 14px;">
                  <h3>Encoding queue</h3>
                  <p>Each CSV row or staged story remains separate. Select any story to revise it; saved manual scores appear in the repository as columns.</p>
                  ${renderEncodingQueue()}
                </div>
                ${renderEncodingComparison()}
                ${renderEncodingTable()}
                ${renderInoculationDiagnosisPanel()}
              </div>
            </div>
          `;
        }
        if (state.encodingMode === "ai") {
          return `
            <div class="grid-2" style="margin-top: 14px;">
              <div class="panel">
                <h3>AI encoder: pre-code one story or the accepted queue</h3>
                <p>The AI encoder reads narrative content and returns structured scores. If no real provider key is configured, NDIM labels and uses the deterministic fallback instead of pretending it called an LLM.</p>
                ${renderStoryNavigator()}
                ${renderLLMSettings()}
                <div class="button-row">
                  <button class="button primary" id="runCurrentEncoding" type="button">Encode current story with AI</button>
                  <button class="button" id="runEncoding" type="button">Encode all accepted stories with AI</button>
                  <button class="button" id="resetEncoding" type="button">Reset encoding</button>
                </div>
              </div>
              <div>
                <div class="panel" style="margin-bottom: 14px;">
                  <h3>Story queue and AI progress</h3>
                  <p>AI results are stored separately from manual scores. You can manually encode one narrative first, then run AI to compare the two.</p>
                  ${renderEncodingQueue()}
                </div>
                ${renderEncodingComparison()}
                ${renderEncodingTable()}
                ${renderInoculationDiagnosisPanel()}
              </div>
            </div>
          `;
        }
        return `
          <div class="grid-2" style="margin-top: 14px;">
            <div class="panel">
              <h3>Hybrid encoder: compare human and AI evidence</h3>
              <p>Hybrid mode is for adjudication. It keeps manual and AI scores visible, then creates a reviewed model input that can be used by the ODE, agent model, digital twin, and policy brief.</p>
              ${renderStoryNavigator()}
              ${renderLLMSettings()}
              <div class="button-row">
                <button class="button primary" id="runCurrentEncoding" type="button">Run hybrid for current story</button>
                <button class="button" id="runEncoding" type="button">Run hybrid for all accepted stories</button>
                <button class="button green" id="runAllEncodingModes" type="button">Compare manual, AI, and hybrid</button>
                <button class="button" id="resetEncoding" type="button">Reset encoding</button>
              </div>
            </div>
            <div>
              <div class="panel" style="margin-bottom: 14px;">
                <h3>Comparison queue</h3>
                <p>Use this queue to inspect whether human and AI coding disagree. Disagreement is useful evidence: it should trigger review, not automatic deletion.</p>
                ${renderEncodingQueue()}
              </div>
              ${renderEncodingComparison()}
              ${renderEncodingTable()}
              ${renderInoculationDiagnosisPanel()}
            </div>
          </div>
        `;
      }

      function renderEncoding() {
        const record = currentReviewRecord();
        const card = ensureManualScorecard(record);
        const records = reviewableRecords();
        const reviewed = records.filter((item) => state.manualScorecards[item.narrative_id]?.status === "manual_reviewed").length;
        return `
          <section class="stage-card">
            <p class="eyebrow">Stage 4</p>
            <h2>Story-by-story encoding</h2>
            <p class="copy">Encoding converts each approved narrative into six auditable variables: exposure/emotional intensity, credibility, trust alignment, inoculation potential, barrier pressure, and social influence. These values become model inputs rather than decorative labels.</p>
            <div class="grid-3">
              ${renderEncodingOption("manual", "Manual / rule-based", "One story at a time, with explicit researcher scores and justifications.")}
              ${renderEncodingOption("ai", "AI encoder", "One story or full accepted queue, using BYOK provider or labelled fallback.")}
              ${renderEncodingOption("hybrid", "Hybrid review", "Compare manual and AI results before accepting a model-ready score.")}
            </div>
            ${renderEncodingModePanel(record, card, reviewed, records)}
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
        const metricItems = [
          ["Phi", phi.toFixed(4)],
          ["E exposure", scores.E.toFixed(2)],
          ["C credibility", scores.C.toFixed(2)],
          ["tau trust", scores.tau.toFixed(2)],
          ["kappa inoculation", scores.kappa.toFixed(2)],
          ["B barrier", scores.B.toFixed(2)],
          ["S social", scores.S.toFixed(2)]
        ];
        return `
          <div class="metric-grid" style="margin-top: 12px;">
            ${metricItems.map(([label, value]) => `<div class="metric"><span class="mini-label">${escapeHtml(label)}</span><strong>${escapeHtml(value)}</strong></div>`).join("")}
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

      function renderInoculationDiagnosisPanel() {
        const diagnoses = state.inoculationDiagnoses || [];
        const signal = aggregateInoculationSignal();
        if (!diagnoses.length) {
          return `
            <div class="panel" style="margin-top: 14px;">
              <h3>Inoculation diagnosis</h3>
              <p>After encoding, NDIM will diagnose misinformation threat, weak-dose claim, refutational preemption, trusted messenger fit, reactance risk, and booster need. This makes inoculation theory a real model input rather than only a theme label.</p>
            </div>
          `;
        }
        return `
          <div class="panel" style="margin-top: 14px;">
            <h3>Inoculation diagnosis</h3>
            <p>This layer reads the encoded narratives through inoculation theory. It does not replace adoption encoding; it adds threat diagnosis and intervention parameters that feed the digital twin.</p>
            <div class="metric-grid" style="margin-top: 12px;">
              <div class="metric"><span class="mini-label">Top threat</span><strong>${escapeHtml(signal.top_threat.replace(/_/g, " "))}</strong></div>
              <div class="metric"><span class="mini-label">Misinfo risk</span><strong>${fmtPct(signal.misinformation_risk)}</strong></div>
              <div class="metric"><span class="mini-label">Narrative vaccine</span><strong>${fmtPct(signal.inoculation_strength)}</strong></div>
              <div class="metric"><span class="mini-label">Booster need</span><strong>${fmtPct(signal.booster_share)}</strong></div>
            </div>
            <div class="template-table" style="margin-top: 12px;">
              <div class="template-row head"><span>Story</span><span>Threat</span><span>Messenger</span><span>Counter move</span></div>
              ${diagnoses.slice(0, 6).map((item) => `
                <div class="template-row">
                  <span data-label="Story">${escapeHtml(item.narrative_id)}</span>
                  <span data-label="Threat">${escapeHtml((item.threat_type || "none").replace(/_/g, " "))}<br/><small>risk ${fmtPct(item.misinformation_risk_score)}, reactance ${fmtPct(item.reactance_risk_score)}</small></span>
                  <span data-label="Messenger">${escapeHtml(item.trusted_messenger || "local peer demonstrator")}</span>
                  <span data-label="Counter move">${escapeHtml(item.refutational_preemption || item.counter_narrative || "Human review required.")}</span>
                </div>
              `).join("")}
            </div>
            <div class="guide-note" style="margin-top: 12px;">
              <strong>Scientific interpretation</strong>
              <p>High misinformation risk means the story contains a claim or fear that could slow adoption. High reactance means a correction may backfire if it sounds coercive. A strong trusted-messenger fit means the model should prefer local demonstration or peer correction over generic messaging.</p>
            </div>
          </div>
        `;
      }

      function renderCompartmental() {
        const last = state.comp?.trajectory?.at(-1);
        return `
          <section class="stage-card">
            <p class="eyebrow">Stage 5</p>
            <h2>Compartmental model</h2>
            <p class="copy">Run the population model. It is the high-level S/M/T/I/R view of adoption, misinformation, truth alignment, inoculation, and durable resistance to misinformation.</p>
            <div class="grid-2">
              <div class="panel">
                <h3>S/M/T/I/R meaning</h3>
                ${mathBlock("\\begin{aligned}\\frac{dS}{dt} &= -\\beta_mSM - \\beta_tST - \\iota S \\\\ \\frac{dM}{dt} &= \\beta_mSM - \\rho M - \\sigma MI \\\\ \\frac{dT}{dt} &= \\beta_tST + \\rho M - \\mu T \\\\ \\frac{dI}{dt} &= \\iota S + \\sigma MI - \\gamma I \\\\ \\frac{dR}{dt} &= \\gamma I + \\eta T \\\\ \\Phi_i &= 0.30E_i + 0.30C_i + 0.20\\tau_i + 0.20\\kappa_i \\end{aligned}", "Phi changes beta_t, rho, and iota through narrative strength.")}
                <div class="guide-note"><strong>Guiding note</strong><p>Read this as the executable NDIM compartment model. The backend now carries S, M, T, I, and R compartments plus an adoption signal and uncertainty band. If a future endpoint falls back to a prototype curve, the model type label will say so clearly.</p></div>
                <div class="guide-note"><strong>How Stage 4 feeds this model</strong><p>Each encoded narrative contributes six values. Exposure and credibility raise the narrative force Phi; trust alignment raises the truthful adoption flow; inoculation potential raises the movement into the inoculated compartment; barrier pressure slows adoption; social influence changes how strongly a story diffuses across the population. In plain terms: stories become parameters, and parameters change the curve.</p></div>
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
            <p class="eyebrow">Stage 6</p>
            <h2>Agent-based model</h2>
            <p class="copy">Run the household-level model. It checks how peer effects, trust, and media exposure may differ from the aggregate ODE curve.</p>
            <div class="grid-2">
              <div class="panel">
                <h3>Agent configuration</h3>
                ${mathBlock("\\begin{aligned}P(\\operatorname{adopt}_i) &= \\sigma\\left(b_0 + trust_i + peer\\_effect\\sum_j A_{ij}adopt_j + media_i - barrier_i\\right) \\\\ degree_i &= \\sum_j A_{ij} \\\\ trust_{i,t+1} &= trust_{i,t} + outreach_i + posterior\\_update_i \\end{aligned}")}
                <div class="guide-note"><strong>Guiding note</strong><p>The agent model asks whether local peer dynamics tell a different story from the population curve. If ABM adoption is lower than ODE adoption, district-level friction or network clustering may be hiding in the aggregate model.</p></div>
                <div class="guide-note"><strong>How encoding becomes household behavior</strong><p>Trust increases the probability that a household will try or accept the intervention. Barrier pressure reduces that probability. Social influence controls how much neighbors, savings groups, leaders, and family members affect the decision. Inoculation potential makes misinformation less durable when a trusted correction is present.</p></div>
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

      function baselineTwinTrajectory() {
        const comp = state.comp?.trajectory || [];
        const agents = state.agents?.trajectory || [];
        if (comp.length && agents.length) {
          const length = Math.min(comp.length, agents.length);
          return Array.from({ length }, (_, index) => {
            const c = comp[index];
            const a = agents[index];
            const adoption = 0.55 * Number(c.adoption || 0) + 0.45 * Number(a.adoption || 0);
            return {
              day: c.day ?? a.day ?? index,
              adoption,
              adoption_lower: 0.55 * Number(c.adoption_lower ?? c.adoption ?? adoption) + 0.45 * Number(a.adoption_lower ?? a.adoption ?? adoption),
              adoption_upper: 0.55 * Number(c.adoption_upper ?? c.adoption ?? adoption) + 0.45 * Number(a.adoption_upper ?? a.adoption ?? adoption)
            };
          });
        }
        return comp.length ? comp : agents;
      }

      function digitalTwinErrorSummary() {
        const baseline = baselineTwinTrajectory();
        const predicted = baseline?.at(-1)?.adoption;
        const observed = state.feedback.observedAdoption;
        if (typeof predicted !== "number" || typeof observed !== "number") return "-";
        const error = observed - predicted;
        return `${error >= 0 ? "+" : ""}${(error * 100).toFixed(1)} pp`;
      }

      function digitalTwinScenarioLabel() {
        if (state.inoculationApplied && state.digital?.model_mode === "hybrid_inoculation_vaccine") return "inoculation scenario";
        if (state.digital) return "observed-feedback hybrid rerun";
        return "not run";
      }

      function renderDigitalTwinBenchmark() {
        const rows = [
          ["Observed system state", "partially implemented", "Manual observed adoption, trust shift, barrier shift, and feedback note."],
          ["Virtual representation", "implemented", "Hybrid NDIM run: 55% compartmental S/M/T/I/R model plus 45% agent-based proxy."],
          ["Bidirectional data flow", "partially implemented", "Observations rerun the virtual model; outputs feed Bayesian/RL/policy stages. No automatic live sensor stream yet."],
          ["Calibration", "partially implemented", "Feedback deltas update trust/barrier parameters for the twin rerun; no formal parameter-estimation loop yet."],
          ["Scenario modelling", "partially implemented", "Current scenario is baseline versus feedback-adjusted twin; inoculation lab adds before/during/after narrative-vaccine runs."],
          ["Uncertainty", "partially implemented", "Backend trajectories carry uncertainty bands; this stage still needs richer twin-specific interval plots."],
          ["Provenance", "partially implemented", "Evidence records are hash-sealed; the twin run itself should next receive a downloadable run seal."],
          ["Update loop over time", "prototype", "The loop is on-demand per user run, not continuous streaming or scheduled assimilation."],
          ["Decision support", "implemented", "The policy brief can use the feedback-adjusted twin final adoption and assumptions."]
        ];
        return `
          <div class="panel">
            <h3>Digital twin audit and benchmark</h3>
            <p class="copy">Scientific status: <strong>prototype digital twin feedback loop</strong>. It is credible as a traceable scenario feedback engine, but not yet a full operational digital twin with continuous live data assimilation.</p>
            <div class="template-table">
              <div class="template-row head"><span>Convention</span><span>Status</span><span>Current implementation</span></div>
              ${rows.map(([criterion, status, detail]) => `<div class="template-row"><span data-label="Convention">${escapeHtml(criterion)}</span><span data-label="Status">${escapeHtml(status)}</span><span data-label="Current implementation">${escapeHtml(detail)}</span></div>`).join("")}
            </div>
          </div>
        `;
      }

      function renderDigitalTwinRunReport() {
        if (!state.digital) return "";
        const report = {
          schema: "ndim-digital-twin-run-v1",
          scientific_status: "prototype digital twin feedback loop",
          model_running: state.digital.assumptions?.model_type || state.digital.model_mode || "hybrid NDIM model",
          scenario: digitalTwinScenarioLabel(),
          observed_adoption: state.feedback.observedAdoption,
          predicted_minus_observed_error: digitalTwinErrorSummary(),
          trust_shift: state.feedback.trustDelta,
          barrier_shift: state.feedback.barrierDelta,
          feedback_note: state.feedback.note,
          final_adoption: state.digital.trajectory?.at(-1)?.adoption,
          assumptions: state.digital.assumptions || null,
          provenance: {
            accepted_records: approvedRecords().length,
            encoded_records: state.encoded.length,
            evidence_seal: state.governance.lastDigest || null
          }
        };
        return JSON.stringify(report, null, 2);
      }

      function renderDigital() {
        const last = state.digital?.trajectory?.at(-1);
        const baseline = baselineTwinTrajectory();
        const baselineLast = baseline?.at(-1);
        const modelLabel = state.digital?.assumptions?.model_type || "Hybrid NDIM model";
        return `
          <section class="stage-card">
            <p class="eyebrow">Stage 7</p>
            <h2>Prototype digital twin feedback loop</h2>
            <p class="copy">This stage is currently a traceable scenario feedback engine: it takes observed field feedback, reruns the hybrid NDIM virtual model, compares baseline versus feedback-adjusted adoption, and passes the revised signal into Bayesian, RL, inoculation, and policy stages.</p>
            <div class="grid-2">
              <div class="panel">
                <h3>Feedback input</h3>
                <div class="field-grid">
                  <div class="field"><label for="observedAdoption">Observed adoption</label><input id="observedAdoption" type="number" min="0" max="1" step="0.01" value="${state.feedback.observedAdoption}" /></div>
                  <div class="field"><label for="trustDelta">Trust shift</label><input id="trustDelta" type="number" min="-1" max="1" step="0.01" value="${state.feedback.trustDelta}" /></div>
                  <div class="field"><label for="barrierDelta">Barrier shift</label><input id="barrierDelta" type="number" min="-1" max="1" step="0.01" value="${state.feedback.barrierDelta}" /></div>
                  <div class="field"><label for="feedbackNote">Feedback note</label><input id="feedbackNote" value="${escapeHtml(state.feedback.note)}" placeholder="district feedback, survey note..." /></div>
                </div>
                ${mathBlock("\\begin{aligned}error_t &= observed_t - predicted_t \\\\ \\theta_{t+1} &= \\theta_t + \\lambda error_t \\\\ trust_{t+1} &= clamp(trust_t + trust\\_shift, 0, 1) \\\\ barrier_{t+1} &= clamp(barrier_t + barrier\\_shift, 0, 1) \\end{aligned}")}
                <div class="guide-note"><strong>Guiding note</strong><p>The virtual model running here is the hybrid NDIM model: a weighted blend of the compartmental S/M/T/I/R model and the agent-based proxy. Observed adoption resets the starting state; trust and barrier shifts now directly alter the twin rerun parameters.</p></div>
                <div class="guide-note"><strong>How previous stages feed the twin</strong><p>The twin starts with the ODE and agent model outputs, then checks them against field feedback. If observed adoption is lower than predicted, the twin treats the original model as over-optimistic. If trust rises or barriers fall after an intervention, the twin reruns the forecast with those changes. This is why the digital twin is a feedback loop, not just another chart.</p></div>
                ${renderDigitalFeedbackChain()}
                <div class="button-row"><button class="button primary" id="runDigital" type="button">Apply feedback and rerun twin</button></div>
              </div>
              <div class="panel">
                <h3>Digital twin output</h3>
                <div class="metric-grid">
                  <div class="metric"><span class="mini-label">Twin status</span><strong>${state.digital ? "prototype run" : "not run"}</strong></div>
                  <div class="metric"><span class="mini-label">Model running</span><strong>${escapeHtml(modelLabel)}</strong></div>
                  <div class="metric"><span class="mini-label">Refined adoption</span><strong>${fmtPct(last?.adoption)}</strong></div>
                  <div class="metric"><span class="mini-label">Baseline adoption</span><strong>${fmtPct(baselineLast?.adoption)}</strong></div>
                  <div class="metric"><span class="mini-label">Observed adoption</span><strong>${fmtPct(state.feedback.observedAdoption)}</strong></div>
                  <div class="metric"><span class="mini-label">Observed error</span><strong>${escapeHtml(digitalTwinErrorSummary())}</strong></div>
                  <div class="metric"><span class="mini-label">Scenario</span><strong>${escapeHtml(digitalTwinScenarioLabel())}</strong></div>
                </div>
                <div class="bars" style="margin-top: 14px;">${renderTrajectoryBars(state.digital?.trajectory)}</div>
                ${renderDualLinePlot("Baseline hybrid versus feedback-adjusted twin", baseline, state.digital?.trajectory, "adoption", ["baseline hybrid", "feedback twin"], ["var(--blue)", "var(--amber)"])}
                <div class="button-row"><button class="button" id="downloadTwinReport" type="button" ${state.digital ? "" : "disabled"}>Download twin run report</button></div>
                ${renderResultNote("digital")}
              </div>
            </div>
            ${renderDigitalTwinBenchmark()}
          </section>
        `;
      }

      function renderBayes() {
        const b = state.bayes;
        return `
          <section class="stage-card">
            <p class="eyebrow">Stage 8</p>
            <h2>Bayesian prior to posterior update</h2>
            <p class="copy">Priors hold what the model believed before feedback. Posterior values update those beliefs after observed adoption, narrative encoding, and digital-twin feedback.</p>
            <div class="grid-2">
              <div class="panel">
                <h3>Prior settings</h3>
                <div class="field-grid">
                  <div class="field"><label for="trustA">Trust alpha</label><input id="trustA" type="number" min="1" step="1" value="${state.priors.trustA}" /></div>
                  <div class="field"><label for="trustB">Trust beta</label><input id="trustB" type="number" min="1" step="1" value="${state.priors.trustB}" /></div>
                  <div class="field"><label for="barrierA">Barrier alpha</label><input id="barrierA" type="number" min="1" step="1" value="${state.priors.barrierA}" /></div>
                  <div class="field"><label for="barrierB">Barrier beta</label><input id="barrierB" type="number" min="1" step="1" value="${state.priors.barrierB}" /></div>
                </div>
                ${mathBlock("\\begin{aligned}p &\\sim \\operatorname{Beta}(\\alpha,\\beta) \\\\ posterior &= \\operatorname{Beta}(\\alpha + successes,\\beta + failures) \\\\ \\mathbb{E}[p] &= \\frac{\\alpha}{\\alpha + \\beta} \\end{aligned}")}
                <div class="guide-note"><strong>Guiding note</strong><p>The prior is your starting belief. The posterior is the same belief after evidence is counted. Higher trust posterior raises adoption pressure; higher barrier posterior dampens adoption pressure and makes aggressive policies riskier.</p></div>
                <div class="guide-note"><strong>Plain-language interpretation</strong><p>A prior is the model saying, "before seeing these field stories, this is what I expected." A posterior is the model saying, "after reviewing the accepted evidence and twin feedback, I should adjust my expectation this way." A posterior is not a final truth claim. It is a transparent, uncertainty-aware update that tells policy makers whether the evidence made trust stronger, barriers weaker, or uncertainty too wide for confident action.</p></div>
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
            <p class="eyebrow">Stage 9</p>
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
                ${mathBlock("\\begin{aligned}Q(s,a) &\\leftarrow Q(s,a) + \\alpha\\left[r + \\gamma\\max_{a'}Q(s',a') - Q(s,a)\\right] \\\\ r &= adoption\\_gain - cost\\_penalty - barrier\\_penalty \\end{aligned}")}
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
            <p class="eyebrow">Stage 10</p>
            <h2>Regional analysis <span class="pill">optional</span></h2>
            <p class="copy">Optional but recommended when evidence spans multiple places. If skipped, the policy brief will clearly state that recommendations are based on pooled evidence only.</p>
            <div class="guide-note" style="margin-bottom: 14px;"><strong>Optional stage notice</strong><p>Run this stage when a ministry, district team, or research project needs place-specific interpretation. If the evidence is sparse or the decision is national, you can skip it and continue to synthesis; NDIM will label the final brief as pooled rather than regional.</p></div>
            <div class="grid-2">
              <div class="panel">
                <h3>Analysis setup</h3>
                <div class="field-grid">
                  <div class="field"><label for="regionalMode">Analysis mode</label><select id="regionalMode"><option value="isolated">Isolate each region</option><option value="grouped">Group all regions</option></select></div>
                  <div class="field"><label for="regionalTarget">Target lens</label><select id="regionalTarget"><option value="barrier">Barrier reduction</option><option value="trust">Trust building</option><option value="diffusion">Peer diffusion</option></select></div>
                </div>
                ${mathBlock("\\begin{aligned}score_r &= \\mathbb{E}(\\Phi_i, trust_i, barrier_i, confidence_i \\mid location_i=r) \\\\ intervention_r &= \\arg\\max_a\\; \\mathbb{E}[adoption\\_gain_r(a)] - risk_r(a) \\end{aligned}")}
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
            <p class="eyebrow">Stage 11</p>
            <h2>Knowledge graph</h2>
            <p class="copy">Study stories from the same location by connecting places, narratives, themes, trust, barriers, and candidate interventions.</p>
            <div class="grid-2">
              <div class="panel">
                <h3>Graph theory lens</h3>
                ${mathBlock("\\begin{aligned}G &= (V,E) \\\\ degree(v) &= \\sum_j A_{vj} \\\\ centrality(theme) &= \\frac{degree(theme)}{\\max_v degree(v)} \\end{aligned}")}
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
            <p class="eyebrow">Stage 12</p>
            <h2>Inoculation lab</h2>
            <p class="copy">Show inoculation theory at work. The selected LLM provider is used as the intended generation path; if no model key is configured, the browser produces transparent deterministic drafts from the encoded evidence.</p>
            <div class="grid-2">
              <div class="panel">
                <h3>Inoculation recipe</h3>
                ${mathBlock("\\begin{aligned}message &= warning + weakened\\_claim + refutation + trusted\\_messenger + efficacy\\_cue \\\\ resistance\\_gain &= threat\\_awareness \\times refutation\\_quality \\times source\\_trust \\\\ \\iota' &= \\iota + intervention\\_strength \\end{aligned}")}
                <div class="guide-note"><strong>Guiding note</strong><p>Good inoculation does not simply deny a false claim. It gives people a small preview of the misleading argument, explains the manipulation, then offers a trusted and practical alternative.</p></div>
                <div class="field-grid" style="margin-top: 12px;">
                  <div class="field"><label for="inoculationAudience">Audience</label><select id="inoculationAudience"><option value="households">Households</option><option value="community_leaders">Community leaders</option><option value="health_workers">Health workers</option><option value="policy_makers">Policy makers</option></select></div>
                  <div class="field"><label for="inoculationTone">Tone</label><select id="inoculationTone"><option value="clear">Clear and practical</option><option value="warm">Warm and local</option><option value="technical">Technical evidence</option></select></div>
                </div>
                ${renderInoculationDiagnosisPanel()}
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
          ["Inoculation diagnosis", state.inoculationDiagnoses.length ? `${state.inoculationDiagnoses.length} diagnosed; top threat ${aggregateInoculationSignal().top_threat.replace(/_/g, " ")}` : "waiting"],
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
            <p class="eyebrow">Stage 13</p>
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
            ${state.policy ? `
              <div class="panel" style="margin-bottom: 14px;">
                <h3>Policy brief ready: save the outputs</h3>
                <p class="copy">The human-readable brief is the primary product. Save the HTML brief, use the PDF view to print or save as PDF, and keep the JSON only as an audit payload for reviewers.</p>
                <div class="button-row">
                  <button class="button primary" id="downloadPolicyHtmlPrompt" type="button">Download HTML policy brief</button>
                  <button class="button" id="printPolicyPdfPrompt" type="button">Print or save as PDF</button>
                  <button class="button" id="downloadPolicyJsonPrompt" type="button">Download JSON audit file</button>
                  <button class="button green" id="returnToBeginning" type="button">Return to beginning</button>
                </div>
              </div>
            ` : `
              <div class="guide-note"><strong>Export prompt</strong><p>Run the full policy pipeline first. NDIM will then prompt you to download the HTML brief, open a PDF-ready view, save the JSON audit file, or return to the beginning.</p></div>
            `}
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
                  <div class="template-row"><span data-label="Review item">Inoculation threat</span><span data-label="Status">${escapeHtml((brief.inoculation_threat_profile.top_threat || "not diagnosed").replace(/_/g, " "))}</span><span data-label="Meaning">dominant misinformation or reactance profile</span></div>
                  <div class="template-row"><span data-label="Review item">Trusted messenger</span><span data-label="Status">${escapeHtml(brief.trusted_messenger)}</span><span data-label="Meaning">recommended human channel for correction</span></div>
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
              <div class="panel">
                <h3>Human-readable audit summary</h3>
                <p>This screen avoids raw JSON. The audit file is still available through <b>Download JSON</b>, but reviewers first see the plain-language chain of evidence.</p>
                <div class="template-table" style="margin-top: 12px;">
                  <div class="template-row head"><span>Pipeline input</span><span>Human meaning</span><span>Current status</span></div>
                  <div class="template-row"><span data-label="Pipeline input">Accepted evidence</span><span data-label="Human meaning">Narratives approved for modelling</span><span data-label="Current status">${approvedRecords().length} record(s)</span></div>
                  <div class="template-row"><span data-label="Pipeline input">Encoder results</span><span data-label="Human meaning">Manual, AI, or hybrid scores attached to repository records</span><span data-label="Current status">${state.encoded.length} active encoded story input(s)</span></div>
                  <div class="template-row"><span data-label="Pipeline input">Digital twin</span><span data-label="Human meaning">Feedback-adjusted scenario run</span><span data-label="Current status">${state.digital ? "included" : "not run"}</span></div>
                  <div class="template-row"><span data-label="Pipeline input">Bayesian update</span><span data-label="Human meaning">Prior assumptions revised into posterior assumptions</span><span data-label="Current status">${state.bayes ? "included" : "not run"}</span></div>
                  <div class="template-row"><span data-label="Pipeline input">Regional analysis</span><span data-label="Human meaning">Optional place-specific interpretation</span><span data-label="Current status">${state.regional ? "included" : "optional/not run"}</span></div>
                  <div class="template-row"><span data-label="Pipeline input">Human review</span><span data-label="Human meaning">Required before policy use</span><span data-label="Current status">${brief.required_human_review ? "required" : "recorded"}</span></div>
                </div>
              </div>
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

      function axisLabelForX(key) {
        const labels = {
          day: "Time horizon (days)",
          episode: "Training episode",
          x: "Parameter value"
        };
        return labels[key] || `${key} axis`;
      }

      function axisLabelForY(key) {
        const labels = {
          adoption: "Projected adoption share (0-100%)",
          reward: "Reward score",
          y: "Posterior density",
          trust_score: "Trust score (0-1)",
          adoption_barrier_score: "Barrier score (0-1)",
          confidence: "Evidence confidence (0-1)"
        };
        return labels[key] || `${key} value`;
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

      function renderPlotFrame(title, body, legend = "", topLabel = "", bottomLabel = "", xAxisLabel = "Time horizon (days)", yAxisLabel = "Projected adoption share (0-100%)") {
        return `
          <div class="plot-card">
            <div class="plot-title">${escapeHtml(title)}</div>
            <svg viewBox="0 0 640 240" role="img" aria-label="${escapeHtml(title)}">
              <line class="plot-grid-line" x1="30" x2="610" y1="30" y2="30"></line>
              <line class="plot-grid-line" x1="30" x2="610" y1="110" y2="110"></line>
              <line class="plot-grid-line" x1="30" x2="610" y1="190" y2="190"></line>
              <line class="plot-grid-line" x1="30" x2="30" y1="30" y2="190"></line>
              <text class="plot-axis-label" x="36" y="25">${escapeHtml(topLabel)}</text>
              <text class="plot-axis-label" x="36" y="207">${escapeHtml(bottomLabel)}</text>
              <text class="plot-axis-title" x="320" y="232" text-anchor="middle">${escapeHtml(xAxisLabel)}</text>
              <text class="plot-axis-title" transform="translate(12 112) rotate(-90)" text-anchor="middle">${escapeHtml(yAxisLabel)}</text>
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
        return renderPlotFrame(title, body, legend, plotValueLabel(maxY, yKey), plotValueLabel(minY, yKey), axisLabelForX(xKey), axisLabelForY(yKey));
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
        return renderPlotFrame(title, body, legend, plotValueLabel(maxY, "adoption"), plotValueLabel(minY, "adoption"), "Time horizon (days)", "Projected adoption share with interval (0-100%)");
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
        return renderPlotFrame(title, body, legend, plotValueLabel(maxY, yKey), plotValueLabel(minY, yKey), "Time horizon (days)", axisLabelForY(yKey));
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
        return renderPlotFrame(title, body, legend, plotValueLabel(maxY, yKey), plotValueLabel(minY, yKey), "Time horizon (days)", axisLabelForY(yKey));
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
        return renderPlotFrame(title, body, legend, "density", "0 to 1 probability", "Parameter value (0-1)", "Posterior density");
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
        return `
          <svg class="kg-svg" viewBox="0 0 ${w} ${h}" role="img" aria-label="Knowledge graph">${edgeSvg}${nodeSvg}</svg>
          <div class="plot-legend">
            <span><i class="legend-swatch" style="background:var(--blue)"></i>location nodes</span>
            <span><i class="legend-swatch" style="background:var(--amber)"></i>theme nodes</span>
            <span><i class="legend-swatch" style="background:var(--green)"></i>signal nodes</span>
            <span>Layout is relational, not geographic; node size indicates connection count.</span>
          </div>
        `;
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

      function dominantInoculationDiagnosis() {
        const rows = state.inoculationDiagnoses || [];
        if (!rows.length) return null;
        return rows.slice().sort((a, b) => {
          const ar = Number(a.misinformation_risk_score || 0) + Number(a.reactance_risk_score || 0) + Number(a.threat_recognition_score || 0);
          const br = Number(b.misinformation_risk_score || 0) + Number(b.reactance_risk_score || 0) + Number(b.threat_recognition_score || 0);
          return br - ar;
        })[0];
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
        const diagnosis = aggregateInoculationSignal();
        const barrier = avg(state.encoded.map((item) => item.adoption_barrier_score), 0.35);
        const trust = avg(state.encoded.map((item) => item.trust_score), 0.6);
        const confidence = avg(state.encoded.map((item) => item.confidence), 0.5);
        const inoculationThemes = state.encoded.filter((item) => (item.themes || []).some((theme) => /inoculation|safety|trust|social/i.test(theme))).length;
        const themeDensity = state.encoded.length ? inoculationThemes / state.encoded.length : 0.25;
        return clamp01(0.10 + barrier * 0.14 + trust * 0.12 + confidence * 0.10 + themeDensity * 0.12 + diagnosis.inoculation_strength * 0.38 + diagnosis.misinformation_risk * 0.12, 0.32);
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
            <div class="guide-note"><strong>Interpretation</strong><p>The before curve is the current model projection without the counter-narrative. The during curve applies the message while the intervention is active. The after curve estimates residual protection after the message has circulated. A higher after curve means the model predicts a larger adoption-aligned population share under the assumed intervention strength, not that persuasion is guaranteed in the field. Treat this as a testable hypothesis for piloting, monitoring, and revision.</p></div>
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

      function endpointSummary(trajectory) {
        const points = trajectory || [];
        const last = points.length ? points[points.length - 1] : null;
        return {
          adoption: typeof last?.adoption === "number" ? last.adoption : null,
          day: typeof last?.day === "number" ? Math.round(last.day) : Math.max(0, points.length - 1)
        };
      }

      function adoptionInterpretation(label, trajectory, qualifier = "under the current assumptions") {
        const endpoint = endpointSummary(trajectory);
        if (typeof endpoint.adoption !== "number") return "Run the model first so NDIM can estimate the adoption pathway.";
        return `${label} projects ${fmtPct(endpoint.adoption)} adoption-aligned population share by day ${endpoint.day} ${qualifier}. This percentage is a model endpoint, not an observed survey statistic: it means that, in the simulated population, that share is expected to be in the adoption or adoption-ready state at the end of the run. Use it comparatively across scenarios, and check uncertainty, evidence volume, and human review before treating it as policy-grade evidence.`;
      }

      function renderResultNote(kind) {
        const notes = {
          compartmental: state.comp ? `${adoptionInterpretation(`The ${state.comp.assumptions?.model_type || "NDIM compartment"} model`, state.comp.trajectory, "from the S/M/T/I/R population equations")}. The final interval is ${finalUncertaintySummary()}, so a wide band should trigger more evidence collection or sensitivity analysis before a policy recommendation.` : "Result implication: run the population model to see whether narrative and intervention inputs produce meaningful adoption growth.",
          agents: state.agents ? `${adoptionInterpretation("The agent-based model", state.agents.trajectory, "after simulating household heterogeneity, peer influence, trust, and barriers")}. ${compareModels()} means the local network assumptions are ${compareModels() === "ABM lower" ? "more cautious than the population equation; peer bottlenecks, mistrust, or access frictions may need targeted work" : "at least as supportive as the population equation; demonstration-led diffusion may be plausible if evidence quality is adequate"}.` : "Result implication: run the agent model to test household-level friction and peer spread.",
          digital: state.digital ? `${adoptionInterpretation("The feedback-adjusted digital twin", state.digital.trajectory, "after applying observed field adoption, evidence trust, and barrier feedback")}. If this endpoint differs from the baseline ODE or ABM, the field observation changed the calibrated scenario. That is the purpose of the twin: it is a living analytic copy of the policy system, not a separate truth source.` : "Result implication: use observed adoption and field notes to correct the next simulation.",
          bayes: state.bayes ? `The Bayesian update estimates posterior trust at ${fmtPct(state.bayes.trustMean)} and posterior barrier pressure at ${fmtPct(state.bayes.barrierMean)}. These are probability-like calibrated assumptions, not direct survey prevalence. They show how approved evidence moves the model from prior belief to updated belief; weak evidence, disagreement between coders, or sparse regions should widen caution. ${state.bayes.fallback ? "The backend used a labelled fallback posterior approximation, so treat this as provisional until Torch/Pyro analytics are available." : "Advanced posterior analytics were available for this run."}` : "Result implication: Bayesian updating shows how evidence moves assumptions instead of hiding them.",
          rl: state.rl ? `The optimizer currently ranks "${state.rl.bestAction}" highest, with a Q reward of ${Number(state.rl.bestReward || 0).toFixed(3)}. Reward is an analytic score balancing projected adoption gain, barriers, cost, and risk; it is not a moral or political mandate. Use it to shortlist interventions, then compare feasibility, equity, evidence grade, and human review before implementation. ${state.rl.fallback ? "This is a labelled fallback optimizer result." : "This optimizer result came from the analytics endpoint."}` : "Result implication: run the optimizer to stress-test intervention packages before drafting policy."
        };
        return `<div class="result-note"><p>${escapeHtml(notes[kind] || "")}</p></div>`;
      }

      function renderRLBars() {
        const history = state.rl?.history || [];
        if (!history.length) return "<p>Run RL to show reward samples.</p>";
        const max = Math.max(...history.map((item) => item.reward), 0.01);
        return `
          <div class="plot-legend"><span>x-axis: reward magnitude</span><span>y-axis: recent training episodes</span></div>
          ${history.slice(-8).map((item) => `
          <div class="bar-row">
            <span>ep ${item.episode}</span>
            <div class="bar-track"><div class="bar-fill" style="width:${Math.max(2, (item.reward / max) * 100)}%; background: var(--violet);"></div></div>
            <span>${item.reward.toFixed(2)}</span>
          </div>
        `).join("")}
        `;
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
        const regional = state.regional?.rows?.length
          ? ` Regional analysis produced ${state.regional.rows.length} intervention unit(s).`
          : " Regional analysis was not run; recommendations are based on pooled evidence only.";
        const inoculation = state.inoculation?.items?.length ? ` The inoculation lab generated ${state.inoculation.items.length} counter-narrative drafts for review.` : "";
        const threat = state.inoculationDiagnoses.length ? ` Inoculation diagnosis identifies ${aggregateInoculationSignal().top_threat.replace(/_/g, " ")} as the leading threat profile, with misinformation risk ${fmtPct(aggregateInoculationSignal().misinformation_risk)}.` : "";
        return `Preliminary signal: prioritize trust-led clean-cooking outreach in ${state.meta.district || state.meta.country}. The current run projects a ${adoption} adoption-aligned share by the final simulation horizon. This is a scenario estimate, not an observed programme result. Average encoded trust is ${trust}, and average encoded barrier pressure is ${barrier}.${threat}${rl}${feedback}${regional}${inoculation} Human review is required before export, and the brief should state assumptions, evidence grade, uncertainty, inoculation threat profile, and implementation limits.`;
      }

      function governanceJson() {
        return {
          schema: "ndim-governance-ledger-v1",
          workspace_id: workspaceId(),
          workspace: {
            workspace_id: workspaceId(),
            name: workspaceName(),
            domain: workspaceSettings().domain || ""
          },
          project: {
            workspace_id: workspaceId(),
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
          inoculation_diagnoses: state.inoculationDiagnoses,
          inoculation_summary: aggregateInoculationSignal(),
          narratives: state.records.length,
          encoded: state.encoded,
          feedback_chain: {
            evidence_to_encoding: state.encoded.length > 0,
            encoding_to_inoculation_diagnosis: state.inoculationDiagnoses.length > 0,
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
- Regional analysis: ${state.regional ? "included" : "not run; recommendations use pooled evidence only"}
- Knowledge graph included: ${state.graph ? "yes" : "not yet"}
- Inoculation diagnosis included: ${state.inoculationDiagnoses.length ? `yes, top threat: ${aggregateInoculationSignal().top_threat}` : "not yet"}
- Trusted messenger: ${brief.trusted_messenger}
- Booster plan: ${brief.booster_plan}
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
          ["Inoculation threat profile", `${brief.inoculation_threat_profile.top_threat} / misinformation risk ${fmtPct(brief.inoculation_threat_profile.misinformation_risk)}`],
          ["Trusted messenger", brief.trusted_messenger],
          ["Booster plan", brief.booster_plan],
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
          "custom_route_name",
          "custom_evidence_type",
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
          state.template.customRouteName,
          state.template.customEvidenceType,
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
        state.inoculationDiagnoses = [];
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
        state.template.customRouteName = "";
        state.template.customEvidenceType = "narrative";
        state.intakeOption = "manual_entry";
        state.intakeImportMode = "manual_entry";
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
          trace("support", `${label} opened`, `Opened ${path} from the Evidence input method menu.`);
        } else {
          window.location.href = path;
        }
      }

      async function runIntakeOption() {
        const option = state.intakeOption || $("intakeOptionSelect")?.value || "manual_entry";
        if (option === "batch" || option === "single") {
          state.intakeImportMode = option;
          const input = $("fileInput");
          if (input) {
            input.accept = option === "batch" ? ".csv,.txt,.md,.json,.xml,.sdmx" : ".txt,.md,.json,.xml,.sdmx";
            input.value = "";
            input.click();
          }
          trace("intake", option === "batch" ? "Batch import requested" : "Single story import requested", option === "batch" ? "Choose a CSV or text file. CSV rows become separate observations; text is split by paragraph after staging." : "Choose one story, interview transcript, field note, or document text file.");
          return;
        }
        if (option === "manual_entry") {
          state.intakeImportMode = "manual_entry";
          state.importedRecords = [];
          trace("intake", "Manual entry selected", "Use the route-specific form and narrative body below. Nothing is imported until you stage and validate.");
          toast("Manual entry ready");
          setTimeout(() => ($("narrativeText") || $("q1"))?.focus(), 40);
          return;
        }
        if (option === "guide") {
          openSupportPage("/manual#narrative-intake", "Intake guide");
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
            trace("intake", "Evidence input method selected", `${intakeOptionActionLabel()} is ready from the Evidence input method menu.`);
            render();
          });
          $("runIntakeOption").addEventListener("click", runIntakeOption);
          $("stageEvidence").addEventListener("click", async () => {
            if (await validateIntake()) goStep(1);
          });
          
          const loadSampleButton = $("loadSample");
          if (loadSampleButton) loadSampleButton.addEventListener("click", () => {
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
            const importMode = state.intakeImportMode || state.intakeOption || "batch";
            if (file.name.toLowerCase().endsWith(".csv")) {
              const rows = parseCsv(text);
              applyImportedCsvMetadata(rows[0] || {}, file.name);
              state.importedRecords = recordsFromCsv(text, file.name);
              if (importMode === "single" && state.importedRecords.length > 1) {
                state.importedRecords = state.importedRecords.slice(0, 1);
              }
              state.records = state.importedRecords;
              state.text = state.records.map((record) => record.text).join("\n\n");
              state.encoded = [];
              state.encodingRuns = {};
              state.inoculationDiagnoses = [];
              state.manualScorecards = {};
              state.manualIndex = 0;
              $("narrativeText").value = state.text;
              $("sourceType").value = state.meta.sourceType;
              $("sourceName").value = file.name;
              trace("csv", importMode === "single" ? "Single CSV story imported" : "CSV batch imported", `${state.records.length} narrative observation(s) imported from ${file.name}. Detected route: ${currentEvidenceMode().title}. You can still edit text before staging.`);
            } else {
              state.importedRecords = [];
              state.text = text;
              state.meta.sourceName = file.name;
              $("narrativeText").value = text;
              trace("file", importMode === "single" ? "Single story file loaded" : "Text batch file loaded", `${file.name} loaded into the intake form. ${importMode === "batch" ? "Paragraphs can become separate observations after staging." : "It will be treated as one evidence item unless you split it manually."}`);
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
        if (id === "repository") {
          const check = $("checkGoogleRepository");
          if (check) {
            check.addEventListener("click", async () => {
              await refreshGoogleRepositoryStatus();
              trace("master repository", "Google repository checked", state.googleRepository?.user_message || "Repository status refreshed.");
              toast(state.googleRepository?.configured ? "Google repository configured" : "Google repository not configured");
              render();
            });
          }
        }
        if (id === "encoding") {
          if ($("llmProvider")) $("llmProvider").value = state.llmProvider;
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
          if ($("encoderName")) $("encoderName").value = state.encoderName;
          if ($("encoderName")) $("encoderName").addEventListener("change", (event) => {
            state.encoderName = event.target.value || "research-encoder";
            const record = currentReviewRecord();
            const card = ensureManualScorecard(record);
            if (card) card.encoder = state.encoderName;
            trace("choice", "Manual encoder set", `Manual scorecards will be signed as ${state.encoderName}.`);
          });
          if ($("llmProvider")) $("llmProvider").addEventListener("change", (event) => {
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
          if ($("runEncoding")) $("runEncoding").addEventListener("click", runEncoding);
          if ($("runCurrentEncoding")) $("runCurrentEncoding").addEventListener("click", runCurrentEncoding);
          if ($("runAllEncodingModes")) $("runAllEncodingModes").addEventListener("click", runAllEncodingModes);
          if ($("resetEncoding")) $("resetEncoding").addEventListener("click", () => {
            state.encoded = [];
            state.encodingRuns = {};
            state.inoculationDiagnoses = [];
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
        if (id === "digital") {
          $("runDigital").addEventListener("click", runDigital);
          const reportButton = $("downloadTwinReport");
          if (reportButton) reportButton.addEventListener("click", () => {
            if (!state.digital) {
              toast("Run the twin first");
              return;
            }
            downloadText(`ndim-digital-twin-run-${Date.now()}.json`, renderDigitalTwinRunReport(), "application/json");
            trace("digital", "Twin run report downloaded", "Downloaded a JSON report describing the prototype twin run, feedback inputs, model assumptions, and provenance.");
            toast("Twin report downloaded");
          });
        }
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
          const downloadPolicyHtmlBrief = () => {
            downloadText(`ndim-policy-brief-${Date.now()}.html`, policyHtmlDocument(false), "text/html");
            trace("policy", "Policy HTML downloaded", "Downloaded a human-readable policy brief. JSON remains available for audit only.");
            toast("HTML brief downloaded");
          };
          const downloadPolicyJsonAudit = () => {
            downloadText(`ndim-policy-output-${Date.now()}.json`, JSON.stringify(policyJson(), null, 2), "application/json");
            trace("policy", "Policy JSON downloaded", "Downloaded the ndim-policy-output-v1 audit payload.");
            toast("Policy JSON downloaded");
          };
          $("downloadPolicyHtml").addEventListener("click", downloadPolicyHtmlBrief);
          $("printPolicyPdf").addEventListener("click", openPrintablePolicy);
          $("copyPolicy").addEventListener("click", async () => {
            const copied = await copyText(JSON.stringify(policyJson(), null, 2), `ndim-policy-output-${Date.now()}.json`, "application/json");
            toast(copied ? "Policy JSON copied" : "Copy blocked; policy JSON downloaded");
          });
          $("downloadPolicyJson").addEventListener("click", downloadPolicyJsonAudit);
          $("copyPolicyBrief").addEventListener("click", async () => {
            const copied = await copyText(policyMarkdown(), `ndim-policy-brief-${Date.now()}.md`, "text/markdown");
            toast(copied ? "Policy brief copied" : "Copy blocked; policy brief downloaded");
          });
          const htmlPrompt = $("downloadPolicyHtmlPrompt");
          if (htmlPrompt) htmlPrompt.addEventListener("click", downloadPolicyHtmlBrief);
          const pdfPrompt = $("printPolicyPdfPrompt");
          if (pdfPrompt) pdfPrompt.addEventListener("click", openPrintablePolicy);
          const jsonPrompt = $("downloadPolicyJsonPrompt");
          if (jsonPrompt) jsonPrompt.addEventListener("click", downloadPolicyJsonAudit);
          const returnButton = $("returnToBeginning");
          if (returnButton) returnButton.addEventListener("click", () => {
            trace("finish", "Workflow returned to beginning", "The policy brief was prepared. The user returned to intake to start another evidence route or workspace run.");
            goStep(0);
          });
        }
      }

      function inoculationDiagnosisById() {
        return Object.fromEntries((state.inoculationDiagnoses || []).map((item) => [item.narrative_id, item]));
      }

      function aggregateInoculationSignal() {
        const rows = state.inoculationDiagnoses || [];
        if (!rows.length) {
          return {
            inoculation_strength: 0,
            misinformation_risk: 0,
            reactance_penalty: 0,
            trusted_messenger_fit: 0,
            misinformation_decay: 0,
            resistance_growth: 0,
            trust_shift: 0,
            barrier_shift: 0,
            booster_share: 0,
            top_threat: "not diagnosed"
          };
        }
        const params = (key, fallback = 0) => avg(rows.map((item) => item.intervention_parameters?.[key]), fallback);
        const threats = topItems(rows.map((item) => item.threat_type || "none_detected"), 1);
        return {
          inoculation_strength: params("inoculation_strength"),
          misinformation_risk: params("misinformation_risk"),
          reactance_penalty: params("reactance_penalty"),
          trusted_messenger_fit: params("trusted_messenger_fit"),
          misinformation_decay: params("misinformation_decay"),
          resistance_growth: params("resistance_growth"),
          trust_shift: params("trust_shift"),
          barrier_shift: params("barrier_shift"),
          booster_share: rows.filter((item) => item.booster_needed).length / rows.length,
          threat_recognition: avg(rows.map((item) => item.threat_recognition_score), 0),
          narrative_resilience: avg(rows.map((item) => item.narrative_resilience_score), 0),
          top_threat: threats[0] || "none_detected"
        };
      }

      function modelParams(extra = {}) {
        const trustBase = avg(state.encoded.map((item) => item.trust_score), 0.6);
        const barrierBase = avg(state.encoded.map((item) => item.adoption_barrier_score), 0.35);
        const inoculationSignal = aggregateInoculationSignal();
        const vaccineStrength = state.inoculationApplied ? (state.inoculation?.interventionStrength || 0) : 0;
        const trust = clamp01((state.bayes?.trustMean ?? (trustBase + (state.digital ? state.feedback.trustDelta : 0))) + vaccineStrength * 0.08 + inoculationSignal.trust_shift * 0.25, 0.6);
        const barrier = clamp01((state.bayes?.barrierMean ?? (barrierBase + (state.digital ? state.feedback.barrierDelta : 0))) - vaccineStrength * 0.07 + inoculationSignal.barrier_shift * 0.25, 0.35);
        const confidence = avg(state.encoded.map((item) => item.confidence), 0.5);
        const rlBonus = state.rl?.interventionBonus || 0;
        return {
          trust_score: trust,
          barrier_score: barrier,
          narrative_influence: Math.min(0.9, 0.2 + 0.35 * confidence + vaccineStrength * 0.12),
          intervention_strength: Math.min(0.9, 0.1 + 0.2 * trust + rlBonus + vaccineStrength * 0.28),
          inoculation_strength: vaccineStrength,
          recommended_inoculation_strength: inoculationSignal.inoculation_strength,
          misinformation_risk: inoculationSignal.misinformation_risk,
          misinformation_decay: state.inoculationApplied ? Math.max(inoculationSignal.misinformation_decay, vaccineStrength * 0.60) : inoculationSignal.misinformation_decay * 0.25,
          resistance_growth: state.inoculationApplied ? Math.max(inoculationSignal.resistance_growth, vaccineStrength * 0.55) : inoculationSignal.resistance_growth * 0.20,
          reactance_penalty: inoculationSignal.reactance_penalty,
          trusted_messenger_fit: inoculationSignal.trusted_messenger_fit,
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

      async function runInoculationDiagnosis(records = approvedRecords()) {
        if (!records.length) return [];
        trace("api", "Calling inoculation diagnosis", `POST /inoculate with ${records.length} approved record(s).`);
        try {
          const response = await fetch(`/inoculate?provider=${encodeURIComponent(state.llmProvider)}`, {
            method: "POST",
            headers: llmRequestHeaders(),
            body: JSON.stringify(records)
          });
          if (!response.ok) throw new Error(`Backend returned ${response.status}`);
          state.inoculationDiagnoses = await response.json();
          const signal = aggregateInoculationSignal();
          trace("inoculation", "Inoculation diagnosis complete", `Top threat ${signal.top_threat}; misinformation risk ${fmtPct(signal.misinformation_risk)}; recommended vaccine strength ${fmtPct(signal.inoculation_strength)}.`);
          return state.inoculationDiagnoses;
        } catch (error) {
          trace("error", "Inoculation diagnosis failed", error.message || "Unknown error");
          state.inoculationDiagnoses = records.map((record) => ({
            narrative_id: record.narrative_id,
            diagnosis_mode: "browser_fallback",
            narrative_type: "adoption_context",
            threat_type: "requires_review",
            misinformation_mechanism: "requires_review",
            trusted_messenger: "local peer demonstrator",
            misinformation_risk_score: 0.35,
            reactance_risk_score: 0.25,
            threat_recognition_score: 0.35,
            identity_threat_score: 0.20,
            cultural_sensitivity_score: record.metadata?.provenance?.evidence_mode === "indigenous_knowledge" ? 0.65 : 0.25,
            refutability_score: 0.45,
            trusted_messenger_fit_score: 0.45,
            weak_dose_claim: "A local clean-cooking concern needs review before it becomes a misinformation risk.",
            refutational_preemption: "Ask a trusted local reviewer to compare the claim with demonstration evidence, cost data, and repair support.",
            counter_narrative: "Use local demonstration and respectful correction before repeating uncertain claims.",
            booster_strategy: "Repeat through a local peer, health worker, or community leader after initial exposure.",
            booster_needed: true,
            narrative_resilience_score: 0.40,
            confidence: 0.35,
            evidence_spans: { uncertainty: "Backend inoculation endpoint unavailable; browser fallback used." },
            intervention_parameters: {
              inoculation_strength: 0.32,
              misinformation_decay: 0.18,
              resistance_growth: 0.18,
              trust_shift: 0.05,
              barrier_shift: -0.04,
              reactance_penalty: 0.14,
              trusted_messenger_fit: 0.45,
              misinformation_risk: 0.35
            },
            model_notes: "Browser fallback; use backend or LLM diagnosis before policy use."
          }));
          return state.inoculationDiagnoses;
        }
      }

      async function runEncoding() {
        const approved = await requireApprovedRecords();
        if (!approved.length) return;
        if (state.encodingMode === "manual") {
          trace("manual", "Manual encoder is story-by-story", "The main Run stage action now saves only the current manual story so the researcher can inspect each narrative before continuing.");
          await runCurrentEncoding();
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
          await runInoculationDiagnosis(approved);
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
          await runInoculationDiagnosis(approved);
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
          await runInoculationDiagnosis(approved);
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
        await runInoculationDiagnosis(approved);
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
          const baseParams = modelParams({ initial_adoption: state.feedback.observedAdoption });
          const twinParams = {
            ...baseParams,
            trust_score: clamp01(Number(baseParams.trust_score || 0.6) + state.feedback.trustDelta, Number(baseParams.trust_score || 0.6)),
            barrier_score: clamp01(Number(baseParams.barrier_score || 0.35) + state.feedback.barrierDelta, Number(baseParams.barrier_score || 0.35)),
            observed_adoption: state.feedback.observedAdoption,
            feedback_note: state.feedback.note,
            scenario_type: "observed_feedback_hybrid_rerun"
          };
          const response = await fetch("/simulate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ model_mode: "hybrid", country: state.meta.country, admin_unit: state.meta.district, horizon_days: 180, parameters: twinParams })
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
        const diagnosis = dominantInoculationDiagnosis();
        const region = signal.region.split(" / ").slice(-1)[0];
        const themes = signal.themes.length ? signal.themes.join(", ") : "cost, trust, fuel access";
        const messenger = diagnosis?.trusted_messenger || (audience === "health_workers" ? "a local health worker" : audience === "community_leaders" ? "a community leader" : audience === "policy_makers" ? "a district policy team" : "a neighbour who has already tried the stove");
        const interventionStrength = estimateInoculationStrength();
        const weakDose = diagnosis?.weak_dose_claim || "Some messages will claim clean cooking is only for wealthy families or that fuel cannot be found.";
        const refutation = diagnosis?.refutational_preemption || "Before accepting that claim, compare it with local households already cooking with less smoke, verified costs, and available support.";
        const counterMessage = diagnosis?.counter_narrative || "Do not decide from a rumour alone. Visit a local demonstration, ask about fuel and repair support, and compare smoke exposure in a real kitchen.";
        const booster = diagnosis?.booster_strategy || "Repeat the correction through trusted local messengers after the first demonstration.";
        state.inoculation = {
          audience,
          tone,
          provider: state.llmProvider,
          interventionStrength,
          diagnosis,
          items: [
            {
              type: "pre-bunk",
              audience,
              title: `Before the rumour spreads in ${region}`,
              text: `${weakDose} ${refutation} ${messenger} can show the practical evidence in context.`,
              components: ["warning", "weak-dose claim", "trusted messenger", themes]
            },
            {
              type: "refutation",
              audience,
              title: "Refutational preemption",
              text: `${refutation} The correction should be specific, respectful, and paired with a practical next step rather than a generic denial.`,
              components: ["refutation", "efficacy", diagnosis?.threat_type || "barrier reduction", `provider: ${state.llmProvider}`]
            },
            {
              type: "counter-feed",
              audience,
              title: "Short social counter-message",
              text: `${counterMessage} ${booster}`,
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

      async function applyInoculationVaccine() {
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
        try {
          const response = await fetch("/simulate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              model_mode: "hybrid",
              country: state.meta.country,
              admin_unit: state.meta.district,
              horizon_days: 180,
              parameters: modelParams({
                inoculation_strength: strength,
                scenario_type: "inoculation_vaccine_digital_twin"
              })
            })
          });
          if (!response.ok) throw new Error(`Backend returned ${response.status}`);
          state.digital = await response.json();
          state.digital.model_mode = "hybrid_inoculation_vaccine";
          state.completed.add("digital");
        } catch (error) {
          const digitalTrajectory = vaccine.compartmental?.after || vaccine.agent_based?.after;
          if (digitalTrajectory?.length) {
            state.digital = {
              model_mode: "hybrid_inoculation_vaccine",
              country: state.meta.country,
              admin_unit: state.meta.district,
              assumptions: { model_type: "Local fallback vaccine trajectory", error: error.message || "simulate failed" },
              parameters: modelParams({ inoculation_strength: strength }),
              trajectory: digitalTrajectory
            };
            state.completed.add("digital");
          }
          trace("error", "Backend vaccine simulation fallback", error.message || "Unknown error");
        }
        if (state.digital?.trajectory?.length) {
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
          state.inoculationDiagnoses = state.policy.inoculation_diagnoses || state.inoculationDiagnoses;
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
        if (id === "repository") {
          trace("repository", "Repository refreshed", `${state.records.length} local record(s), ${approvedRecords().length} accepted, ${rejectedRepositoryRecords().length} rejected, and ${pendingCommitRecords().length} waiting for commit.`);
          render();
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

      document.querySelectorAll("#themeToggle button").forEach((button) => {
        button.addEventListener("click", () => {
          setTheme(button.dataset.theme);
        });
      });
      setTheme(window.localStorage?.getItem("ndim_theme") || document.documentElement.dataset.theme || "light");
      window.addEventListener("resize", syncWorkflowStagesOffset);
      window.addEventListener("load", renderMath);
      window.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
          if (state.stageWorkspace.open) {
            state.stageWorkspace.open = false;
            render();
          } else if (state.workspace.managerOpen) {
            state.workspace.managerOpen = false;
            renderWorkspaceManager();
          } else {
            document.querySelector(".reasoning")?.classList.remove("open");
            state.workspace.assistantOpen = false;
            renderAssistant();
          }
        }
      });

      renderTrace();
      loadWorkspaceState().then(() => {
        render();
      }).catch(() => render());
      Promise.all([refreshAnalyticsStatus(), refreshValidationStatus(), refreshGoogleRepositoryStatus()]).then(() => {
        trace("system", "Scientific services checked", `${analyticsSummary()} ${calibrationSummary()} Google repository: ${state.googleRepository?.sync_status || "not checked"}.`);
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
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css" />
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"></script>
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
      .math-display { border: 1px solid #d8dee9; border-radius: 14px; background: white; padding: 14px 16px; margin: 12px 0; overflow-x: auto; }
      .math-display .katex-display { margin: 0; text-align: left; overflow-x: auto; overflow-y: hidden; }
      .small { color: #64748b; font-size: 14px; }
      @media (max-width: 760px) { .grid { grid-template-columns: 1fr; } }
    </style>
  </head>
  <body>
    <main>
      <h1>NDIM Engine Manual</h1>
      <p><a href="/">Back to tool</a> | <a href="/academy">Open NDIM Academy</a> | <a href="/publication">Scientific Publication</a> | <a href="/academy#modules">Academy modules</a> | <a href="/academy#practice">Practice exercises</a></p>
      <p><strong>NDIM</strong> means <strong>Narrative Diffusion and Inoculation Model</strong>. The engine turns field narratives into traceable model inputs, runs population and household simulations, updates beliefs with evidence, and produces a policy recommendation with an audit trail.</p>
      <div class="callout"><p><strong>Simple reading:</strong> the tool asks, "What are people saying, how should we encode it, how does that narrative change adoption dynamics, what did the field data correct, and which policy action is most robust?"</p></div>

      <h2 id="academy-learning-path">Academy learning path</h2>
      <p>The manual is the reference guide. <a href="/academy">NDIM Academy</a> is the guided learning path. Use Academy when a research team needs a full lesson, worked example, and exercise. Use this manual when the user already knows the workflow and needs exact operating instructions.</p>
      <table>
        <thead><tr><th>Need</th><th>Use</th><th>Where to go</th></tr></thead>
        <tbody>
          <tr><td>Learn NDIM from scratch</td><td>Academy story, innovation case, glossary, equations, and learning modules.</td><td><a href="/academy#modules">Academy modules</a></td></tr>
          <tr><td>Frame NDIM for journal publication</td><td>Use the Overleaf-style publication workspace for manuscript editing, live preview, LaTeX/BibTeX export, legal literature search, optional OpenAI writing support, validation roadmap, ethics, and article-type fit.</td><td><a href="/publication">Scientific Publication</a></td></tr>
          <tr><td>Practise with ClimateTales Rwanda</td><td>Academy practice workflow and manual stress-test steps.</td><td><a href="/academy#module-climatetales">ClimateTales module</a></td></tr>
          <tr><td>Run the tool correctly</td><td>Manual stage-by-stage operating guide.</td><td><a href="#stage-tutorial">Workflow tutorial</a></td></tr>
          <tr><td>Explain equations to a non-technical reader</td><td>Academy equation map and plain-language interpretation.</td><td><a href="/academy#equations">Academy equations</a></td></tr>
        </tbody>
      </table>

      <h2>Using the Evidence-to-Policy Workbench</h2>
      <p>The opening screen is workspace-first: choose or create the project workspace, then let the workbench and research assistant guide the evidence-to-policy run. Use the compact workflow buttons and the stage selector to move between Evidence, Encode, Model, Learn, Synthesize, and Export. The hero system map shows how evidence, models, the digital twin, learning loops, synthesis, and policy output connect.</p>
      <table>
        <thead><tr><th>Workbench element</th><th>What it does</th><th>How to use it</th></tr></thead>
        <tbody>
          <tr><td>NDIM system map</td><td>Shows the evidence-to-policy chain, including the dashed Digital Twin feedback engine.</td><td>Click any node to jump to that workflow stage.</td></tr>
          <tr><td>Full repository</td><td>Lists staged narrative records with route, place, review status, evidence seal, acceptance, rejection, uncommit history, and master repository readiness.</td><td>Open the Repository stage or the repository button in the system map.</td></tr>
          <tr><td>SDMX readiness panel</td><td>Checks whether route, place, source, period, and evidence body are ready.</td><td>Fix missing items before clicking Stage and validate.</td></tr>
          <tr><td>Activity log</td><td>Shows the reasoning trace and system actions in a drawer.</td><td>Open it only when auditing the workflow; keep it closed while working.</td></tr>
          <tr><td>Run current stage</td><td>Opens the focused stage task workspace, where the user can review inputs, read the research note, and run the primary action.</td><td>Use it when the landing page is too compact for the full scientific form.</td></tr>
        </tbody>
      </table>

      <h2>Workflow overview</h2>
      <table>
        <thead><tr><th>Stage</th><th>Purpose</th><th>Main output</th></tr></thead>
        <tbody>
          <tr><td>01 Narrative intake</td><td>Load text, CSV, notes, or SDMX-like evidence with country and location context.</td><td>Batch of narrative observations.</td></tr>
          <tr><td>02 SDMX gate</td><td>Check whether each observation has source, place, period, language, and measure fields.</td><td>Validated observation payload.</td></tr>
          <tr><td>03 Repository</td><td>Search, inspect, filter, export, uncommit, and prepare accepted records for master repository review.</td><td>Accepted, rejected, pending, and master-sync-ready evidence ledger.</td></tr>
          <tr><td>04 Encoding</td><td>Score narratives using manual, AI, or hybrid review.</td><td>Trust, barrier, confidence, themes, and Phi inputs.</td></tr>
          <tr><td>05 Compartmental model</td><td>Estimate population-level adoption flow.</td><td>Adoption trajectory over time.</td></tr>
          <tr><td>06 Agent-based model</td><td>Test household heterogeneity and peer effects.</td><td>Local adoption trajectory and ODE/ABM contrast.</td></tr>
          <tr><td>07 Digital twin</td><td>Feed field observations back into the model.</td><td>Feedback-adjusted simulation curve.</td></tr>
          <tr><td>08 Bayesian update</td><td>Update trust and barrier assumptions from prior to posterior.</td><td>Posterior trust and barrier distributions.</td></tr>
          <tr><td>09 RL optimizer</td><td>Compare intervention policies by reward.</td><td>Best action, reward curve, and Q values.</td></tr>
          <tr><td>10 Regional analysis</td><td>Analyse regions alone or as grouped evidence.</td><td>Place-based intervention implications.</td></tr>
          <tr><td>11 Knowledge graph</td><td>Connect stories, places, themes, trust, barriers, and interventions.</td><td>Graph of repeated narrative structures.</td></tr>
          <tr><td>12 Inoculation lab</td><td>Generate pre-bunking and refutation narratives from encoded risks.</td><td>Reviewable counter-narrative drafts.</td></tr>
          <tr><td>13 Policy output</td><td>Create a reviewable decision brief.</td><td>Recommendation, JSON audit payload, Markdown brief, and evidence trail.</td></tr>
        </tbody>
      </table>

      <h2 id="narrative-intake">1. Narrative intake</h2>
      <p>NDIM supports a <strong>Narrative Commons</strong> intake model. Structured interviews are one route, but users can also ingest focus groups, open stories, indigenous knowledge records, citizen-science reports, crowdsourced batches, and experimental social/community feeds.</p>
      <table>
        <thead><tr><th>Route</th><th>Use when</th><th>Extra governance fields</th></tr></thead>
        <tbody>
          <tr><td>Structured interview</td><td>Enumerators collect Q1-Q5 clean-cooking stories.</td><td>Interview ID, respondent profile, decision-maker, current cooking methods.</td></tr>
          <tr><td>Focus group</td><td>A facilitated community discussion captures group consensus, disagreement, and peer influence.</td><td>Focus group ID, group profile, facilitator/source, validation status, attribution, translation notes.</td></tr>
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
      <p>For batch imports, use <strong>Save current manual score and continue</strong> when doing human review, <strong>Encode current story with AI</strong> when testing one AI pre-code, or the mode-specific full-queue button when deliberately encoding all accepted stories with AI or hybrid review.</p>

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
      <div class="math-display">\begin{aligned}
evidence\_hash_i &= \operatorname{SHA256}(canonical\_json(narrative_i, metadata_i, tags_i)) \\
review\_signature_i &= \operatorname{SHA256}(reviewer, role, status, time, evidence\_hash_i) \\
ledger\_event\_hash_t &= \operatorname{SHA256}(event_t + ledger\_event\_hash_{t-1})
\end{aligned}</div>
      <p><strong>Interpretation:</strong> hashes and chained ledger events prove whether a record changed after review. They do not prove that the story is factually true. Truth still depends on consent, field validation, duplicate checks, triangulation, and human approval.</p>

      <h2 id="repository">3. Full repository and evidence ledger</h2>
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

      <h2>4. Encoding derivation</h2>
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
      <div class="math-display">\begin{aligned}
\Phi_i &= 0.30E_i + 0.30C_i + 0.20\tau_i + 0.20\kappa_i \\
trust_i &= \tau_i \\
barrier_i &= B_i \\
confidence_i &= \operatorname{mean}(C_i,\kappa_i,S_i)
\end{aligned}</div>
      <p><code>Phi</code> is a narrative-strength index. It increases truth diffusion when trust and cultural fit are strong. <code>B</code> is kept separate because a story can be emotionally powerful and culturally credible while still describing barriers that slow adoption.</p>
      <p><strong>Batch import rule:</strong> a CSV file is a container, not a scientific unit. Every row becomes one <code>NarrativeRecord</code> with its own hash, approval status, manual scorecard, LLM pre-code, comparison result, and final encoded output. The UI queue supports "encode current then next" so researchers can review records one by one, while "compare all modes" runs manual, AI, and hybrid over the full approved batch.</p>
      <h3>Bring-your-own LLM configuration</h3>
      <p>NDIM is now designed so a researcher or institution can choose a provider per encoding run. The UI supports OpenAI, Anthropic, Gemini, Azure OpenAI, OpenRouter, Mistral, Ollama, LM Studio, OpenAI-compatible endpoints, and deterministic fallback. API keys entered in the UI are session-only: they are sent to the backend in request headers during encoding and are not written into the policy JSON, reasoning log, or manual scorecard.</p>
      <pre>X-NDIM-LLM-Provider: anthropic | gemini | openai | ollama | ...
X-NDIM-LLM-Key: user session key, optional for local providers
X-NDIM-LLM-Base-URL: optional local or compatible endpoint
X-NDIM-LLM-Model: selected model or deployment</pre>
      <p>For sensitive indigenous knowledge or government evidence, prefer manual scoring or a local provider such as Ollama or LM Studio. Cloud LLMs should only be used when the user has permission to send the narratives to that provider.</p>

      <h2>5. Compartmental model derivation</h2>
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
      <div class="math-display">\begin{aligned}
\frac{dS}{dt} &= -\beta_mSM - \beta_tST - \iota S \\
\frac{dM}{dt} &= \beta_mSM - \rho M - \sigma MI \\
\frac{dT}{dt} &= \beta_tST + \rho M - \mu T \\
\frac{dI}{dt} &= \iota S + \sigma MI - \gamma I \\
\frac{dR}{dt} &= \gamma I + \eta T
\end{aligned}</div>
      <p>Terms are contact or transition rates. For example, <code>beta_m S M</code> is misinformation contact between susceptible and misinformed groups, while <code>beta_t S T</code> is truth-aligned contact. The UI plot shows the backend adoption trajectory, which is the measurable policy-facing outcome of this system.</p>
      <div class="math-display">\begin{aligned}
\beta_t &= \beta_{t0}(1+\Phi)\,trust \\
\beta_m &= \beta_{m0}\,barrier \\
\iota &= \iota_0 + intervention\_strength
\end{aligned}</div>
      <p>Helpful reproduction-style diagnostics are:</p>
      <div class="math-display">\begin{aligned}
R_m &= \frac{\beta_m S_0}{\rho + \sigma I_0 + \epsilon} \\
R_t &= \frac{\beta_t S_0}{\mu + \epsilon}
\end{aligned}</div>
      <p>If <code>R_t &gt; R_m</code>, truth-aligned diffusion is stronger than misinformation pressure. If <code>R_m</code> is higher, policy should prioritize trusted correction, inoculation, or barrier reduction before expecting fast adoption.</p>

      <h2>6. Agent-based model derivation</h2>
      <p>The agent model treats each household as a local decision maker. It is useful when one district, village, or social network may behave differently from the national average.</p>
      <div class="math-display">\begin{aligned}
peer_i(t) &= \operatorname{mean}(adopted\ neighbors_i) \\
media_i(t) &= media\_exposure_i \cdot trust_i \\
z_i(t) &= b_0 + trust_i + peer\_effect \cdot peer_i(t) + media\_effect \cdot media_i(t) - barrier_i \\
P(adopt_i,t+1) &= \frac{1}{1+\exp(-z_i(t))}
\end{aligned}</div>
      <p>Social network analysis is appropriate here because adoption is partly transmitted by neighbours, trusted messengers, and visible peer examples.</p>
      <div class="math-display">\begin{aligned}
A_{ij} &= 1\ \text{if household } i \text{ is socially exposed to household } j \\
degree_i &= \sum_j A_{ij} \\
exposure_i(t) &= \frac{\sum_j A_{ij}adopted_j(t)}{\max(1,degree_i)} \\
bridge_i &= \operatorname{count}(cross\_community\_links_i)
\end{aligned}</div>
      <p>The ABM curve should be compared with the ODE curve. If the ABM curve is lower, the model is warning that local household friction is important. If the ABM curve is higher, peer diffusion may be stronger than the aggregate model assumes. High-degree or bridge households are good candidates for demonstrations because they move information between clusters.</p>

      <h2>7. Digital twin feedback derivation</h2>
      <p>The current NDIM implementation should be read as a <strong>prototype digital twin feedback loop</strong>. It is more than a static scenario chart because observed field feedback changes the virtual model run and feeds later Bayesian/RL/policy stages. It is not yet a full operational digital twin because it does not continuously ingest live field streams, automatically estimate all parameters, or maintain scheduled state synchronization.</p>
      <p><strong>Model running inside the twin:</strong> the Digital Twin stage calls the backend <code>/simulate</code> endpoint with <code>model_mode = hybrid</code>. The backend runs a hybrid NDIM model, currently a weighted blend of the documented compartmental S/M/T/I/R model and an agent-based proxy:</p>
      <div class="math-display">\begin{aligned}
A_{hybrid}(t) &= 0.55A_{ODE}(t) + 0.45A_{ABM}(t)
\end{aligned}</div>
      <p><strong>Inputs consumed:</strong> accepted and encoded evidence sets the baseline trust, barrier, confidence, Phi, and intervention parameters. The twin then adds observed adoption, trust shift, barrier shift, and a feedback note supplied by the analyst. These are treated as scenario feedback, not as proof that the field observation is nationally representative.</p>
      <div class="math-display">\begin{aligned}
error_t &= observed\_adoption_t - predicted\_adoption_t \\
\theta_{t+1} &= \theta_t + \lambda error_t \\
trust_{t+1} &= clamp(trust_t + trust\_shift,0,1) \\
barrier_{t+1} &= clamp(barrier_t + barrier\_shift,0,1)
\end{aligned}</div>
      <p><strong>Scenario modelling in the current twin:</strong> the main comparison is baseline hybrid trajectory versus feedback-adjusted hybrid trajectory. The Inoculation Lab adds a second scenario family by injecting a narrative vaccine and showing before/during/after ODE and agent curves. A full scenario library with saved named runs is a recommended next upgrade.</p>
      <table>
        <thead><tr><th>Digital twin convention</th><th>NDIM status</th><th>Interpretation</th></tr></thead>
        <tbody>
          <tr><td>Observed system state</td><td>Partially implemented</td><td>Manual observed adoption and feedback deltas are entered by the user.</td></tr>
          <tr><td>Virtual model representation</td><td>Implemented</td><td>Hybrid NDIM virtual model: ODE compartmental dynamics plus ABM proxy.</td></tr>
          <tr><td>Bidirectional data flow</td><td>Partially implemented</td><td>Observed feedback changes the model; model output feeds Bayesian/RL/policy stages. There is no live automatic data stream yet.</td></tr>
          <tr><td>Calibration</td><td>Partially implemented</td><td>Feedback shifts trust and barriers directly. Formal parameter estimation remains a future upgrade.</td></tr>
          <tr><td>Scenario / what-if testing</td><td>Partially implemented</td><td>Baseline versus feedback-adjusted twin is implemented; inoculation before/during/after testing is implemented separately.</td></tr>
          <tr><td>Uncertainty</td><td>Partially implemented</td><td>Trajectory bands exist in model outputs, but twin-specific uncertainty and sensitivity views should be expanded.</td></tr>
          <tr><td>Traceable provenance</td><td>Partially implemented</td><td>Evidence records are hash-sealed. Twin run reports should be archived with the evidence seal.</td></tr>
          <tr><td>Update loop over time</td><td>Prototype</td><td>The current loop is on-demand, not continuous monitoring.</td></tr>
          <tr><td>Decision support</td><td>Implemented</td><td>Policy output can use the feedback-adjusted twin final adoption and assumptions.</td></tr>
        </tbody>
      </table>
      <p><strong>Policy caution:</strong> if only one observation is entered, the twin output should be interpreted as a scenario feedback test, not a calibrated national twin. A policy-grade twin requires repeated observations, provenance, calibration, uncertainty intervals, and human review.</p>

      <h2>8. Bayesian update derivation</h2>
      <p>Trust and barrier assumptions are bounded probabilities, so the manual uses Beta priors. A Beta prior is written as:</p>
      <div class="math-display">\begin{aligned}
p &\sim \operatorname{Beta}(\alpha,\beta) \\
\mathbb{E}[p] &= \frac{\alpha}{\alpha+\beta}
\end{aligned}</div>
      <p>After evidence arrives, count successes and failures. For trust, a success means the evidence supports trust. For barrier, a success means the evidence supports the presence of a barrier.</p>
      <div class="math-display">\begin{aligned}
\mathcal{L}(p) &= p^{successes}(1-p)^{failures} \\
posterior &= \operatorname{Beta}(\alpha+successes,\beta+failures) \\
\mathbb{E}[trust\mid data] &= \frac{\alpha_{trust}+trust\_successes}{\alpha_{trust}+\beta_{trust}+trials}
\end{aligned}</div>
      <p>The posterior plot shows how evidence moves the model from prior belief to updated belief. The posterior feeds the model parameters used by RL and the final policy run.</p>

      <h2>9. RL optimizer derivation</h2>
      <p>The RL optimizer is framed as a small policy search problem. States represent model conditions such as trust and barrier levels. Actions represent intervention packages. Rewards combine adoption gain, cost, and risk.</p>
      <div class="math-display">\begin{aligned}
r &= adoption\_gain - cost\_penalty - barrier\_penalty \\
Q(s,a) &\leftarrow Q(s,a) + \alpha\left[r + \gamma \max_{a'}Q(s',a') - Q(s,a)\right]
\end{aligned}</div>
      <p>Interpret the reward plot as a learning curve. Stable rewards and a clear best action suggest the policy is robust under the current assumptions. Volatile rewards suggest uncertainty and a need for more evidence, stronger priors, or scenario comparison.</p>

      <h2>10. Regional analysis</h2>
      <p>Regional analysis asks whether the same narrative behaves differently by place. Isolation mode treats each region as its own evidence unit. Grouped mode pools places into a shared campaign view.</p>
      <div class="math-display">\begin{aligned}
score_r &= \mathbb{E}(\Phi_i,trust_i,barrier_i,confidence_i \mid location_i=r) \\
intervention_r &= \arg\max_a\ \mathbb{E}[adoption\_gain_r(a)] - risk_r(a)
\end{aligned}</div>
      <p><strong>Interpretation:</strong> a region with high trust and high barriers may not need persuasion first; it may need cost, fuel, repair, or access support. A region with low trust needs messenger repair before technical messaging.</p>

      <h2>11. Knowledge graph</h2>
      <p>The knowledge graph is a research lens for studying stories from the same location. Nodes are locations, themes, trust/barrier signals, and intervention concepts. Edges connect a story location to the themes and signals found in that place.</p>
      <div class="math-display">\begin{aligned}
G &= (V,E) \\
A_{ij} &= 1\ \text{if node } i \text{ is connected to node } j \\
degree(i) &= \sum_j A_{ij} \\
centrality(theme) &= \frac{degree(theme)}{\max_v degree(v)}
\end{aligned}</div>
      <p><strong>Interpretation:</strong> high-degree themes are repeated across locations or stories. They are not automatically causal, but they tell the analyst where narrative meaning clusters. This is useful for comparing districts, identifying repeated rumours, and selecting which narratives need inoculation.</p>

      <h2>12. Inoculation theory and counter-narrative generation</h2>
      <p>Inoculation theory says people can become more resistant to manipulation if they receive a weak preview of a misleading claim plus a clear refutation before the full misinformation appears. The lab turns encoded narrative risks into pre-bunking and counter-feed drafts.</p>
      <div class="math-display">\begin{aligned}
message &= warning + weakened\_claim + refutation + trusted\_messenger + efficacy\_cue \\
resistance\_gain &= threat\_awareness \times refutation\_quality \times source\_trust \\
\iota' &= \iota + intervention\_strength
\end{aligned}</div>
      <p>The LLM generation role is to spawn candidate narratives from a structured prompt. A safe prompt should include the target region, audience, barrier theme, trusted messenger, tone, and a requirement that the output does not ridicule the audience.</p>
      <pre>Prompt skeleton:
Generate three inoculation messages for {region}.
Audience: {audience}
Barrier/risk: {theme}
Use: warning, weakened claim, refutation, trusted source, practical action.
Avoid: shame, exaggeration, unsupported claims.</pre>
      <p><strong>Implication:</strong> counter-narratives should be reviewed by humans and ideally tested before use. The output is a policy communication draft, not proof that the message will work.</p>

      <h2>13. Policy output and feedback loop</h2>
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
      <p>For guided use, follow the buttons stage by stage and read the implication notes. For advanced users, inspect equations, priors, graph structure, and reward curves. For policy users, focus on the recommendation, evidence trail, uncertainty, feasibility, and whether the recommended intervention matches the target region.</p>
      <p class="small">Version note: the current backend exposes a labelled NDIM compartment model with S/M/T/I/R compartments, uncertainty bands, persistent evidence ledger sync, validation checks, and deterministic Bayesian/RL fallbacks when advanced Torch/Pyro services are unavailable.</p>
    </main>
    <script>
      function renderManualMath() {
        if (!window.katex) return;
        document.querySelectorAll(".math-display").forEach((node) => {
          if (node.dataset.rendered === "1") return;
          const tex = node.textContent.trim();
          try {
            window.katex.render(tex, node, { displayMode: true, throwOnError: false, strict: "ignore" });
            node.dataset.rendered = "1";
          } catch (error) {
            node.dataset.rendered = "0";
          }
        });
      }
      window.addEventListener("load", renderManualMath);
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
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css" />
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"></script>
    <style>
      :root {
        --ink:#11100e;
        --body:#564b3d;
        --muted:#8a7d68;
        --paper:#fbfaf7;
        --line:#d6cbbb;
        --soft:#f3efe7;
      }
      * { box-sizing: border-box; }
      html { scroll-behavior: smooth; }
      body {
        margin: 0;
        background: var(--paper);
        color: var(--ink);
        font-family: "Myriad Pro", "Segoe UI", Arial, sans-serif;
        line-height: 1.65;
      }
      main {
        width: min(980px, calc(100% - 32px));
        margin: 0 auto;
        padding: 34px 0 80px;
      }
      header {
        border-bottom: 1px solid var(--line);
        padding-bottom: 18px;
        margin-bottom: 18px;
      }
      h1 {
        margin: 0 0 10px;
        font-size: clamp(34px, 6vw, 58px);
        line-height: 1.02;
        letter-spacing: -.02em;
      }
      h2, h3 { line-height: 1.22; }
      p, li, td {
        color: var(--body);
        font-size: 16px;
      }
      a {
        color: var(--ink);
        text-decoration-thickness: 1px;
        text-underline-offset: 3px;
      }
      .small-link-row {
        display: flex;
        flex-wrap: wrap;
        gap: 14px;
        margin-top: 14px;
        font-size: 14px;
      }
      details {
        border-top: 1px solid var(--line);
        padding: 0;
      }
      details:last-of-type { border-bottom: 1px solid var(--line); }
      summary {
        cursor: pointer;
        list-style: none;
        padding: 18px 0;
        font-size: 22px;
        font-weight: 800;
      }
      summary::-webkit-details-marker { display: none; }
      summary::before {
        content: "+";
        display: inline-block;
        width: 26px;
        color: var(--muted);
        font-family: Consolas, monospace;
      }
      details[open] summary::before { content: "-"; }
      .section-body {
        padding: 0 0 24px 26px;
      }
      table {
        width: 100%;
        border-collapse: collapse;
        margin: 14px 0 18px;
        background: white;
      }
      th, td {
        border: 1px solid var(--line);
        padding: 9px 10px;
        text-align: left;
        vertical-align: top;
      }
      th {
        background: var(--soft);
        color: var(--ink);
        font-size: 12px;
        letter-spacing: .08em;
        text-transform: uppercase;
      }
      code, pre, .mono {
        font-family: "Cascadia Mono", "JetBrains Mono", Consolas, monospace;
      }
      pre {
        background: #11100e;
        color: #f7efe3;
        border-radius: 8px;
        padding: 12px;
        overflow-x: auto;
        white-space: pre-wrap;
      }
      .note {
        border-left: 3px solid var(--ink);
        background: var(--soft);
        padding: 10px 12px;
        margin: 14px 0;
      }
      .callout {
        border: 1px solid var(--line);
        background: white;
        border-radius: 10px;
        padding: 12px;
        margin: 14px 0;
      }
      .callout strong {
        color: var(--ink);
      }
      .exercise-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 10px;
        margin: 14px 0;
      }
      .exercise-card {
        border: 1px solid var(--line);
        border-radius: 10px;
        background: white;
        padding: 12px;
      }
      .exercise-card h3 {
        margin: 0 0 6px;
        font-size: 16px;
      }
      .exercise-card p {
        margin: 0;
        font-size: 14px;
      }
      .math-display {
        border: 1px solid var(--line);
        background: white;
        border-radius: 8px;
        padding: 12px;
        margin: 12px 0;
        overflow-x: auto;
      }
      .math-display.rendered-fallback {
        font-family: "Cambria Math", "STIX Two Math", Georgia, serif;
        font-size: 20px;
        line-height: 1.9;
      }
      .math-display .katex-display {
        margin: 0;
        text-align: left;
        overflow-x: auto;
        overflow-y: hidden;
      }
      .eq-line {
        display: flex;
        align-items: center;
        gap: .45em;
        white-space: nowrap;
      }
      .eq-var { font-style: italic; }
      .eq-op { color: var(--muted); }
      .frac {
        display: inline-grid;
        grid-template-rows: auto auto;
        text-align: center;
        line-height: 1.1;
        vertical-align: middle;
        margin-right: .1em;
      }
      .frac > span:first-child {
        border-bottom: 1px solid currentColor;
        padding: 0 .2em .08em;
      }
      .frac > span:last-child {
        padding: .08em .2em 0;
      }
      .eq-matrix {
        display: inline-grid;
        gap: .15em;
        padding-left: .45em;
        border-left: 2px solid var(--line);
      }
      #backTop {
        position: fixed;
        right: 18px;
        bottom: 18px;
        border: 1px solid var(--line);
        border-radius: 999px;
        background: white;
        color: var(--ink);
        padding: 9px 12px;
        font-weight: 800;
        text-decoration: none;
        box-shadow: 0 8px 24px rgba(40, 32, 20, .10);
      }
      @media (max-width: 720px) {
        main { width: min(100% - 22px, 980px); padding-top: 18px; }
        summary { font-size: 19px; }
        .section-body { padding-left: 0; }
        table, thead, tbody, th, td, tr { display: block; }
        thead { display: none; }
        tr { border: 1px solid var(--line); margin: 10px 0; background: white; }
        td { border: 0; border-bottom: 1px solid var(--line); }
        .exercise-grid { grid-template-columns: 1fr; }
        td::before {
          content: attr(data-label);
          display: block;
          color: var(--muted);
          font: 800 11px "Cascadia Mono", Consolas, monospace;
          letter-spacing: .07em;
          text-transform: uppercase;
        }
      }
      body {
        background:
          radial-gradient(circle at 8% 4%, rgba(255, 255, 255, .75), transparent 28rem),
          linear-gradient(90deg, transparent 0, transparent calc(100% - 1px), rgba(214, 202, 183, .34) calc(100% - 1px)),
          linear-gradient(135deg, #fbfaf7, #f7f0e7 70%, #fbfaf7);
        background-size: auto, 82px 82px, auto;
      }
      .app-topbar {
        position: sticky;
        top: 0;
        z-index: 30;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 16px;
        padding: 10px clamp(14px, 3vw, 34px);
        border-bottom: 1px solid var(--line);
        background: rgba(251, 250, 247, .94);
        backdrop-filter: blur(16px);
      }
      .brand {
        display: inline-flex;
        align-items: center;
        gap: 10px;
        min-width: 240px;
        color: var(--ink);
        text-decoration: none;
      }
      .brand .mark {
        display: grid;
        place-items: center;
        width: 34px;
        height: 34px;
        border-radius: 999px;
        background: var(--ink);
        color: #fff;
        font: 900 12px "Cascadia Mono", Consolas, monospace;
      }
      .brand strong, .brand span { display: block; line-height: 1.1; }
      .brand span {
        color: var(--muted);
        font: 850 10px "Cascadia Mono", Consolas, monospace;
        letter-spacing: .13em;
        text-transform: uppercase;
      }
      .app-nav {
        display: flex;
        flex-wrap: wrap;
        justify-content: flex-end;
        gap: 8px;
      }
      .app-nav a,
      .small-link-row a,
      #backTop,
      .theme-toggle {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-height: 38px;
        border: 1px solid var(--line);
        border-radius: 999px;
        background: rgba(255, 253, 249, .82);
        color: var(--ink);
        padding: 8px 12px;
        font-weight: 850;
        text-decoration: none;
      }
      .app-nav a:first-child,
      .small-link-row a:first-child {
        background: var(--ink);
        border-color: var(--ink);
        color: #fff;
      }
      .theme-toggle {
        min-width: 62px;
        padding: 0 12px;
        cursor: pointer;
      }
      main {
        width: min(1120px, calc(100% - 32px));
      }
      header {
        border: 1px solid var(--line);
        border-radius: 24px;
        background: rgba(255, 253, 249, .78);
        box-shadow: 0 20px 70px rgba(70, 55, 30, .08);
        padding: clamp(20px, 4vw, 36px);
      }
      header .mono,
      summary,
      th {
        letter-spacing: .13em;
      }
      details {
        border: 1px solid var(--line);
        border-radius: 18px;
        background: rgba(255, 253, 249, .78);
        margin: 12px 0;
        overflow: hidden;
        box-shadow: 0 14px 44px rgba(70, 55, 30, .045);
      }
      details:last-of-type { border-bottom: 1px solid var(--line); }
      summary {
        padding: 16px 18px;
      }
      .section-body {
        border-top: 1px solid var(--line);
        padding: 16px 18px 24px 46px;
      }
      table, .callout, .exercise-card, .math-display {
        background: rgba(255, 253, 249, .9);
        border-radius: 14px;
        overflow: hidden;
      }
      .note {
        border-radius: 14px;
        border-left-width: 4px;
      }
      #backTop {
        background: var(--ink);
        color: #fff;
      }
      body.dark {
        --ink:#f8fafc;
        --body:#d1d5db;
        --muted:#9ca3af;
        --paper:#0b0f17;
        --line:#374151;
        --soft:#1f2937;
        background:
          radial-gradient(circle at 8% 4%, rgba(147, 197, 253, .08), transparent 28rem),
          linear-gradient(90deg, transparent 0, transparent calc(100% - 1px), rgba(55, 65, 81, .38) calc(100% - 1px)),
          linear-gradient(135deg, #0b0f17, #111827 72%, #0b0f17);
        background-size: auto, 82px 82px, auto;
      }
      body.dark .app-topbar,
      body.dark header,
      body.dark details,
      body.dark table,
      body.dark .callout,
      body.dark .exercise-card,
      body.dark .math-display,
      body.dark .app-nav a,
      body.dark .small-link-row a,
      body.dark .theme-toggle {
        background-color: #111827;
        color: var(--ink);
        border-color: var(--line);
      }
      body.dark .brand .mark,
      body.dark .app-nav a:first-child,
      body.dark .small-link-row a:first-child,
      body.dark #backTop {
        background: #030712;
        color: #fff;
        border-color: #e5e7eb;
      }
      body.dark th,
      body.dark .note,
      body.dark pre {
        background: #0f172a;
        color: var(--ink);
      }
      body.dark a { color: #bfdbfe; }
      @media (max-width: 720px) {
        .app-topbar { align-items: flex-start; flex-direction: column; }
        .brand { min-width: 0; }
        .app-nav { width: 100%; justify-content: flex-start; }
        .section-body { padding-left: 18px; }
      }
    </style>
  </head>
  <body id="top">
    <nav class="app-topbar" aria-label="NDIM learning navigation">
      <a class="brand" href="./index.html">
        <span class="mark">ND</span>
        <span>
          <strong>NDIM Engine</strong>
          <span>Narrative Diffusion and Inoculation Model</span>
        </span>
      </a>
      <div class="app-nav">
        <a href="./index.html">Tool</a>
        <a href="./academy.html">Academy</a>
        <a href="./publication.html">Publication</a>
        <a href="https://github.com/Naphymoro/nidm-rwanda-dashboard" target="_blank" rel="noreferrer">GitHub</a>
        <button class="theme-toggle" id="themeToggle" type="button" aria-label="Toggle light or dark mode">Dark</button>
      </div>
    </nav>
    <main>
      <header>
        <p class="mono">NDIM ENGINE MANUAL</p>
        <h1>Narrative Diffusion and Inoculation Model</h1>
        <p>NDIM is a local-first scientific and policy tool for turning governed narrative evidence into model inputs, uncertainty-aware simulations, intervention tests, and a human-reviewed policy brief.</p>
        <p class="small-link-row">
          <a href="./index.html">Back to tool</a>
          <a href="./academy.html">NDIM Academy</a>
          <a href="./publication.html">Scientific Publication</a>
          <a href="./academy.html#modules">Academy modules</a>
          <a href="./academy.html#practice">Academy exercises</a>
          <a href="#installation">Installation</a>
          <a href="#source-access">Source access</a>
          <a href="#workspaces">Workspaces</a>
          <a href="#workflow">Workflow</a>
          <a href="#equations">Equations</a>
          <a href="#repository">Repository</a>
          <a href="#cloud-repository">Google repository</a>
          <a href="#climatetales">ClimateTales tutorial</a>
          <a href="#multimodal">Multimodal roadmap</a>
        </p>
      </header>

      <details id="academy-learning-path" open>
        <summary>Academy learning path</summary>
        <div class="section-body">
          <p>The manual is the operating reference. <a href="./academy.html">NDIM Academy</a> is the guided course. Use Academy when a research team needs plain-language lessons, worked examples, exercises, and interpretation support. Use this manual when a user needs exact operating instructions.</p>
          <table>
            <thead><tr><th>User need</th><th>Best place</th><th>What the user gets</th></tr></thead>
            <tbody>
              <tr><td data-label="User need">Learn NDIM from scratch</td><td data-label="Best place"><a href="./academy.html#modules">Academy modules</a></td><td data-label="What the user gets">Full lessons with objectives, key terms, examples, exercises, observations, interpretations, and common mistakes.</td></tr>
              <tr><td data-label="User need">Practise with ClimateTales Rwanda</td><td data-label="Best place"><a href="./academy.html#module-climatetales">ClimateTales module</a></td><td data-label="What the user gets">A route-by-route synthetic evidence exercise from intake to policy brief.</td></tr>
              <tr><td data-label="User need">Prepare a scientific manuscript</td><td data-label="Best place"><a href="./publication.html">Scientific Publication workspace</a></td><td data-label="What the user gets">An Overleaf-style editor with live preview, LaTeX/BibTeX export, legal literature search, and optional OpenAI writing support.</td></tr>
              <tr><td data-label="User need">Operate the tool quickly</td><td data-label="Best place"><a href="#workflow">Manual workflow section</a></td><td data-label="What the user gets">Concise stage instructions and output expectations.</td></tr>
              <tr><td data-label="User need">Explain equations simply</td><td data-label="Best place"><a href="./academy.html#equations">Academy equations</a></td><td data-label="What the user gets">Plain-language explanation of the compartmental model, agent model, digital twin, Bayesian update, and optimizer.</td></tr>
            </tbody>
          </table>
        </div>
      </details>

      <details id="installation" open>
        <summary>Accessing NDIM Engine: web, local, and advanced use</summary>
        <div class="section-body">
          <p>NDIM can be reached in three complementary ways. The hosted web version is the default route for most research and policy users. Local desktop use remains important for offline work, sensitive evidence, field settings, and institutional testing. Advanced users can inspect, modify, or redeploy the source from GitHub.</p>
          <table>
            <thead><tr><th>Access route</th><th>Best for</th><th>What to expect</th></tr></thead>
            <tbody>
              <tr><td data-label="Access route">Hosted web app</td><td data-label="Best for">Research teams, policy users, field coordinators, and training sessions</td><td data-label="What to expect">Open the Cloudflare Pages link and use the workflow without installing developer tools.</td></tr>
              <tr><td data-label="Access route">Local desktop app</td><td data-label="Best for">Offline work, sensitive data, field locations with unreliable internet, and institutional pilots</td><td data-label="What to expect">Install or open the packaged app. Evidence, hashes, approvals, repositories, backups, and exports remain on the local machine unless deliberately synced or exported.</td></tr>
              <tr><td data-label="Access route">Advanced source setup</td><td data-label="Best for">Technical users, auditors, contributors, and deployment teams</td><td data-label="What to expect">Clone the GitHub repository to inspect code, run tests, adapt deployment settings, or operate a separate instance.</td></tr>
            </tbody>
          </table>
          <p>Internet access is optional for the core workflow. Narrative intake, deterministic encoding fallback, governance, repository review, modelling, backup, restore, and exports can run without external services. Cloud LLMs, Google Drive or Sheets sync, and hosted deployment are optional extensions that require user permission and configuration.</p>
          <p class="note">Local-first means evidence stays under the user or institution's control unless a user deliberately exports, syncs, or shares it. Consent, visibility, reviewer approval, and repository settings should be reviewed before any evidence leaves the workspace.</p>
        </div>
      </details>

      <details id="source-access">
        <summary>Source access and GitHub</summary>
        <div class="section-body">
          <p>The NDIM Engine source is managed on GitHub at <code>https://github.com/Naphymoro/nidm-rwanda-dashboard</code>. GitHub is used for version control, alpha release tracking, deployment updates, issue review, and technical audit history.</p>
          <p>The repository currently contains the NDIM workflow UI, FastAPI backend, Cloudflare Pages deployment files, manual, NDIM Academy, Scientific Publication workspace, stress-test corpus, local and desktop packaging material, backend models, SDMX-style export logic, and deployment documentation.</p>
          <p>The hosted web version is served through Cloudflare Pages. Most users should open the hosted NDIM link. Advanced users can use GitHub when they need to fork, audit, customize, deploy, or contribute to the tool.</p>
          <table>
            <thead><tr><th>User type</th><th>Best access route</th><th>Why</th></tr></thead>
            <tbody>
              <tr><td data-label="User type">General research or policy user</td><td data-label="Best access route">Hosted NDIM web link</td><td data-label="Why">Uses the tool without GitHub, terminals, or code setup.</td></tr>
              <tr><td data-label="User type">Field team or sensitive-data project</td><td data-label="Best access route">Local desktop package or approved institutional deployment</td><td data-label="Why">Keeps evidence local unless the project deliberately exports or syncs it.</td></tr>
              <tr><td data-label="User type">Advanced user, technical reviewer, or contributor</td><td data-label="Best access route">GitHub repository access</td><td data-label="Why">Inspects source files, deployment history, backend code, Cloudflare files, and release changes.</td></tr>
              <tr><td data-label="User type">Project maintainer</td><td data-label="Best access route">GitHub plus Cloudflare dashboard</td><td data-label="Why">Publishes updates, reviews issues, and manages deployment settings.</td></tr>
            </tbody>
          </table>
          <p class="note">If the repository is private, non-collaborators may see a GitHub 404 page even when the link is correct. The maintainer can either add collaborators or provide release files and documentation that do not require source-code access.</p>
        </div>
      </details>

      <details id="workspaces" open>
        <summary>Workspaces and Research Assistant</summary>
        <div class="section-body">
          <p>The opening screen is now workspace-first. A workspace is the project container that tells NDIM which country settings, evidence routes, field templates, encoding rubrics, model defaults, digital-twin assumptions, repository paths, validation files, stress-test corpus, assistant guidance, and export formats to use.</p>
          <p>The Research Assistant behaves like a state-aware progress guide: it reads the active workspace, evidence counts, governance state, model progress, and policy readiness, then explains what is complete, what is waiting, and what the next best action should be.</p>
          <p>The launchpad has three parts: a compact route strip showing which evidence routes are enabled, a <strong>Workspace controls</strong> block with Start, Workspace manager, New workspace, and Guide actions, and the floating Research Assistant button. Duplicate actions live beside each existing workspace inside the manager so users copy the exact project they intend to reuse.</p>
          <table>
            <thead><tr><th>Action</th><th>What it means</th><th>When to use it</th></tr></thead>
            <tbody>
              <tr><td data-label="Action">Start workspace</td><td data-label="What it means">Opens the workspace start menu.</td><td data-label="When to use it">Begin with an existing workspace, create a new one, duplicate a template, or import a package.</td></tr>
              <tr><td data-label="Action">Manager</td><td data-label="What it means">Shows available local workspaces.</td><td data-label="When to use it">Switch between NDIM Core, ClimateTales Rwanda, or another local project.</td></tr>
              <tr><td data-label="Action">Duplicate</td><td data-label="What it means">Copies settings, templates, validation material, and stress-test material into a new workspace.</td><td data-label="When to use it">Adapt ClimateTales Rwanda to another country or clean-tech domain without changing the original.</td></tr>
              <tr><td data-label="Action">Guide</td><td data-label="What it means">Opens this manual at the workspace section.</td><td data-label="When to use it">Train a new researcher or field analyst.</td></tr>
              <tr><td data-label="Action">Floating assistant</td><td data-label="What it means">Opens the agent-like progress guide.</td><td data-label="When to use it">Ask what is complete, what is missing, and what to run next.</td></tr>
            </tbody>
          </table>
          <p>The default presets are <strong>NDIM Core</strong> and <strong>ClimateTales Rwanda</strong>. ClimateTales Rwanda adapts the same workflow toward social insight mining, digital listening, behavioural design labs, story activation pilots, influencer training, gamified influence simulation, and AIMS/Imperial report outputs.</p>
          <p>The <strong>Research Assistant</strong> panel is a collapsible guide. It does not invent science. It reads the current workflow state and tells the user what has been completed, what is missing, what the next action should be, and when policy caution is required.</p>
        </div>
      </details>

      <span id="narrative-intake"></span>
      <details id="workflow" open>
        <summary>Workflow from evidence to policy</summary>
        <div class="section-body">
          <p>The tool is designed as a sequential scientific story:</p>
          <ol>
            <li><strong>Narrative intake:</strong> choose country, administrative unit, evidence route, consent, visibility, and narrative body.</li>
            <li><strong>SDMX gate:</strong> check that the record has enough structure to become a governed observation.</li>
            <li><strong>Repository:</strong> approve or reject records, commit reviewed records, and inspect accepted/rejected evidence in the standalone repository tab.</li>
            <li><strong>Encoding:</strong> score narratives manually, with an LLM, or through hybrid review.</li>
            <li><strong>Compartmental model:</strong> run the population-level S/M/T/I/R diffusion model or labelled fallback curve using encoded evidence.</li>
            <li><strong>Agent-based model:</strong> test household heterogeneity, peer influence, trust, and local barriers.</li>
            <li><strong>Digital twin:</strong> feed observed field information back into the virtual model and rerun scenarios.</li>
            <li><strong>Bayesian update:</strong> move from priors to posteriors for trust and barrier assumptions.</li>
            <li><strong>RL optimizer:</strong> compare candidate intervention packages by reward, cost, and risk.</li>
            <li><strong>Regional analysis:</strong> optionally isolate or group places when policy recommendations need local targeting.</li>
            <li><strong>Knowledge graph:</strong> connect stories, themes, places, messengers, barriers, and intervention concepts.</li>
            <li><strong>Inoculation lab:</strong> diagnose threat type, misinformation mechanism, weak-dose claim, refutational preemption, reactance risk, trusted messenger fit, booster need, and narrative resilience; then test counter-narratives as narrative vaccines.</li>
            <li><strong>Policy output:</strong> export a human-readable brief with assumptions, limitations, uncertainty, required review, and HTML/PDF-friendly outputs.</li>
          </ol>
          <p class="note">Regional analysis is optional. If skipped, the final policy brief should say that recommendations use pooled evidence rather than place-specific analysis.</p>
        </div>
      </details>

      <details id="equations">
        <summary>Core equations</summary>
        <div class="section-body">
          <h3>Encoding</h3>
          <p>Encoding turns a narrative into bounded model variables. Manual encoding should include a short justification for each score.</p>
          <div class="math-display">\Phi_i = 0.30E_i + 0.30C_i + 0.20\tau_i + 0.20\kappa_i</div>
          <table>
            <thead><tr><th>Symbol</th><th>Meaning</th></tr></thead>
            <tbody>
              <tr><td data-label="Symbol">E</td><td data-label="Meaning">Exposure, salience, or emotional intensity.</td></tr>
              <tr><td data-label="Symbol">C</td><td data-label="Meaning">Credibility and local grounding.</td></tr>
              <tr><td data-label="Symbol">tau</td><td data-label="Meaning">Trust alignment.</td></tr>
              <tr><td data-label="Symbol">kappa</td><td data-label="Meaning">Inoculation or resistance opportunity.</td></tr>
            </tbody>
          </table>

          <h3>Compartmental NDIM</h3>
          <p>The documented model uses susceptible, misinformation-exposed, truth-aligned, inoculated, and resistant/adoption-aligned compartments. In the basic teaching setup, these compartments conserve the population: people move between states, but the total population share remains one.</p>
          <div class="math-display">\begin{aligned}
\frac{dS}{dt} &= -\beta_mSM - \beta_tST - \iota S \\
\frac{dM}{dt} &= \beta_mSM - \rho M - \mu M \\
\frac{dT}{dt} &= \beta_tST + \rho M - \eta T \\
\frac{dI}{dt} &= \iota S + \eta T - \gamma I \\
\frac{dR}{dt} &= \gamma I + \mu M
\end{aligned}</div>
          <p>Read each derivative as a rate of change. For example, if misinformation contact is high, the M compartment grows. If trusted correction and inoculation are strong, the model moves people toward T, I, and R.</p>

          <h3>Agent-based model</h3>
          <p>The agent-based model is the household-level companion to the population equation. It represents each household as a decision maker with its own trust, barrier level, peer influence, message exposure, and adoption probability.</p>
          <div class="math-display">P(adopt_i) = logistic(trust_i + peer_i + evidence_i - barrier_i - misinformation_i)</div>
          <p>This helps test whether the smooth population curve hides local friction. If the agent model is lower than the compartmental model, local peer networks, trust gaps, or access barriers may be slowing adoption.</p>

          <h3>Digital twin feedback</h3>
          <div class="math-display">\theta_{t+1} = \theta_t + \lambda(y_{observed} - y_{predicted})</div>
          <p>The current twin is a prototype feedback loop. It receives the compartmental model, the agent-based model, approved evidence, encoded narratives, and field feedback. It then reruns the scenario after trust, barriers, or intervention strength change.</p>
          <p>Example: if the population curve predicts strong adoption but field evidence shows safety fear remains high, the twin adjusts the assumptions and reruns the forecast. The new curve is not a final truth; it is a better scenario because it listened to the field signal.</p>

          <h3>Inoculation diagnosis</h3>
          <p>The upgrade adds a separate diagnosis layer after adoption encoding. The diagnosis estimates misinformation risk, reactance risk, messenger fit, and intervention strength before the inoculation lab drafts any counter-narrative.</p>
          <div class="math-display">V_i = 0.20T_i + 0.20M_i + 0.18R_i + 0.14G_i - 0.08X_i</div>
          <table>
            <thead><tr><th>Symbol</th><th>Meaning</th></tr></thead>
            <tbody>
              <tr><td data-label="Symbol">V_i</td><td data-label="Meaning">Recommended narrative vaccine strength for story i.</td></tr>
              <tr><td data-label="Symbol">T_i</td><td data-label="Meaning">Threat recognition score.</td></tr>
              <tr><td data-label="Symbol">M_i</td><td data-label="Meaning">Misinformation risk score.</td></tr>
              <tr><td data-label="Symbol">R_i</td><td data-label="Meaning">Refutability score.</td></tr>
              <tr><td data-label="Symbol">G_i</td><td data-label="Meaning">Trusted messenger fit score.</td></tr>
              <tr><td data-label="Symbol">X_i</td><td data-label="Meaning">Reactance risk penalty.</td></tr>
            </tbody>
          </table>

          <h3>Bayesian update</h3>
          <div class="math-display">\begin{aligned}
prior &= Beta(\alpha,\beta) \\
posterior &= Beta(\alpha + successes,\beta + failures)
\end{aligned}</div>
          <p>The prior is what the model believed before new evidence. The posterior is what the model believes after approved evidence is added. This matters because a policy recommendation should show uncertainty, not only a single confident-looking number.</p>

          <h3>RL optimizer</h3>
          <div class="math-display">Q(s,a) \leftarrow Q(s,a) + \alpha\left[r + \gamma \max_{a'}Q(s',a') - Q(s,a)\right]</div>
          <p>The optimizer ranks candidate interventions by expected reward. Reward balances adoption gain, cost, risk, and uncertainty. It supports human review; it does not automatically decide policy.</p>
        </div>
      </details>

      <details id="repository">
        <summary>Repository and governance</summary>
        <div class="section-body">
          <p>The repository has an active approval queue, an accepted repository, and a rejected repository. Records should move only after review and commit.</p>
          <table>
            <thead><tr><th>Area</th><th>Purpose</th><th>Main action</th></tr></thead>
            <tbody>
              <tr><td data-label="Area">Active approval queue</td><td data-label="Purpose">Records are staged and governed but not reviewed.</td><td data-label="Main action">Approve or Reject.</td></tr>
              <tr><td data-label="Area">Reviewed, waiting commit</td><td data-label="Purpose">Records have a decision but have not entered a repository.</td><td data-label="Main action">Commit reviewed records.</td></tr>
              <tr><td data-label="Area">Accepted repository</td><td data-label="Purpose">Evidence can be encoded, modelled, and used in policy output.</td><td data-label="Main action">Inspect, export, or Uncommit.</td></tr>
              <tr><td data-label="Area">Rejected repository</td><td data-label="Purpose">Evidence is retained for audit but excluded from modelling.</td><td data-label="Main action">Inspect or Uncommit.</td></tr>
            </tbody>
          </table>
          <p>The full repository opens in a separate HTML tab from the main workflow. This keeps the workflow readable while still allowing detailed filtering by country, administrative unit, route, theme, consent, visibility, status, reviewer, and evidence seal.</p>
        </div>
      </details>

      <details id="cloud-repository">
        <summary>Google Drive and Sheets research repository</summary>
        <div class="section-body">
          <p>For the hosted research phase, NDIM can run as a web app while the shared project repository lives in a Google account. This keeps the user experience simple: researchers open the web app, and the project owner manages the shared Drive folder and Sheets ledger.</p>
          <table>
            <thead><tr><th>Part</th><th>What it stores</th><th>Plain explanation</th></tr></thead>
            <tbody>
              <tr><td data-label="Part">Google Drive</td><td data-label="What it stores">Uploads, SDMX exports, accepted/rejected narrative packages, reports, backups, and policy briefs.</td><td data-label="Plain explanation">Drive is the project filing cabinet.</td></tr>
              <tr><td data-label="Part">Google Sheets</td><td data-label="What it stores">Narrative IDs, routes, places, consent, visibility, reviewer decisions, hashes, encoding scores, model runs, and export links.</td><td data-label="Plain explanation">Sheets is the evidence ledger.</td></tr>
              <tr><td data-label="Part">NDIM Web</td><td data-label="What it stores">The app logic, modelling workflow, manual, Academy, and export tools.</td><td data-label="Plain explanation">The app is the workbench; Drive and Sheets are storage and governance layers.</td></tr>
            </tbody>
          </table>
          <p>The repository stage has a <strong>Check Google repository</strong> button. It asks the backend whether the Drive folder ID and Sheet ID are configured. When they are configured, the app shows buttons to open the Drive repository and Sheets ledger. When they are not configured, the app keeps the safer behavior: prepare downloadable SDMX JSON, observation CSV, and DSD JSON packages for manual upload.</p>
          <p class="note">Drive and Sheets are useful for a controlled research pilot. They are not a full production database. For a large institutional deployment, keep PostgreSQL or another governed database as the system of record and use Drive/Sheets for documents, reports, and controlled repository views.</p>
        </div>
      </details>

      <span id="climatetales"></span>
      <details id="stress-test-corpus" open>
        <summary>ClimateTales stress-test tutorial and exercises</summary>
        <div class="section-body">
          <p>The ClimateTales Rwanda corpus is bundled in <code>stress_test_corpus/</code>. It is synthetic, realistic test data for the Rwanda clean-cooking and climate-technology adoption context. It is not loaded by default. A user must deliberately choose a file during intake.</p>
          <p>The goal is not to prove a policy result. The goal is to stress-test the tool: route-specific intake, SDMX fields, approval and rejection, repository behavior, manual and LLM-style encoding, model response, digital-twin feedback, uncertainty, inoculation messages, and final policy export.</p>
          <div class="exercise-grid">
            <div class="exercise-card"><h3>Minimum test</h3><p>Use one route-specific CSV, approve several records, encode, run models, and export a brief.</p></div>
            <div class="exercise-card"><h3>Full route test</h3><p>Repeat the workflow for each route-specific CSV to check that every evidence path works.</p></div>
            <div class="exercise-card"><h3>Stress test</h3><p>Use the master CSV to test a mixed repository, filtering, batch encoding, and policy synthesis.</p></div>
          </div>
          <table>
            <thead><tr><th>Route</th><th>File</th><th>Use</th></tr></thead>
            <tbody>
              <tr><td data-label="Route">Structured interview</td><td data-label="File"><code>climatetales_structured_interview_synthetic.csv</code></td><td data-label="Use">Tests Q1-Q5 field protocol, respondent profile, cooking role, current stove/fuel, and post-interview coding.</td></tr>
              <tr><td data-label="Route">Open story</td><td data-label="File"><code>climatetales_open_story_synthetic.csv</code></td><td data-label="Use">Tests free multi-paragraph narratives, oral history, meeting notes, and lived-experience stories.</td></tr>
              <tr><td data-label="Route">Indigenous knowledge</td><td data-label="File"><code>climatetales_indigenous_knowledge_synthetic.csv</code></td><td data-label="Use">Tests attribution, cultural sensitivity, community validation, contested meanings, and local ecological knowledge.</td></tr>
              <tr><td data-label="Route">Citizen science report</td><td data-label="File"><code>climatetales_citizen_science_synthetic.csv</code></td><td data-label="Use">Tests community observations, confidence, validation status, location precision, and contributor type.</td></tr>
              <tr><td data-label="Route">Crowdsourced batch</td><td data-label="File"><code>climatetales_crowdsourced_batch_synthetic.csv</code></td><td data-label="Use">Tests moderation, deduplication, approval, rejection, commit, and repository filtering.</td></tr>
              <tr><td data-label="Route">Social media feed</td><td data-label="File"><code>climatetales_social_media_feeds_synthetic.csv</code></td><td data-label="Use">Tests experimental feed handling, platform/source checkboxes, rumor monitoring, and digital listening notes.</td></tr>
              <tr><td data-label="Route">Mixed master corpus</td><td data-label="File"><code>climatetales_ndim_synthetic_narratives_master.csv</code></td><td data-label="Use">Tests all routes together as a larger evidence repository.</td></tr>
              <tr><td data-label="Route">Bonus single story</td><td data-label="File"><code>climatetales_bonus_manual_story.txt</code></td><td data-label="Use">Tests single-story import and manual intake practice.</td></tr>
              <tr><td data-label="Route">Desk review report</td><td data-label="File"><code>climatetales_ndim_desk_review_report.pdf</code> and <code>.docx</code></td><td data-label="Use">Read before interpreting the corpus; it gives the research context and should not be treated as raw narrative evidence unless deliberately imported.</td></tr>
            </tbody>
          </table>
          <h3>Exercise A: prepare the workspace</h3>
          <ol>
            <li>Open NDIM Engine locally.</li>
            <li>In <strong>Workspace controls</strong>, click <strong>Start workspace</strong>.</li>
            <li>Choose <strong>Open existing workspace</strong> and select <strong>ClimateTales Rwanda</strong>. If you want to experiment without changing the original, choose <strong>Duplicate</strong> first and work on the copy.</li>
            <li>Open the floating Research Assistant. It should explain that the workspace is active and that Stage 01 is the next task.</li>
          </ol>
          <div class="callout"><strong>Expected result:</strong> the workbench should show the active ClimateTales workspace, evidence routes, repository status, and current stage. If the workspace cannot be opened, test workspace storage before testing the science workflow.</div>

          <h3>Exercise B: import a route-specific CSV</h3>
          <ol>
            <li>Open Stage 01, <strong>Narrative intake</strong>.</li>
            <li>Under <strong>Evidence input method</strong>, choose <strong>Batch import: CSV or text</strong>.</li>
            <li>Under <strong>Evidence route</strong>, choose the route matching the file, for example <strong>Structured interview</strong> for <code>climatetales_structured_interview_synthetic.csv</code>.</li>
            <li>Click the import button and select the file from <code>stress_test_corpus/</code>.</li>
            <li>Check that country, province, district, sector, language, source type, source name, period, consent, visibility, and route-specific fields are populated or editable.</li>
          </ol>
          <div class="callout"><strong>Expected result:</strong> each CSV row should become a separate candidate narrative record. The app should not collapse the batch into one story. Route-specific fields should make sense for the selected route.</div>

          <h3>Exercise C: test single story and manual entry</h3>
          <ol>
            <li>Choose <strong>Single story import</strong> and load <code>climatetales_bonus_manual_story.txt</code>.</li>
            <li>Confirm that the text appears as one evidence item, not as a paragraph-split batch.</li>
            <li>Choose <strong>Manual entry</strong> and paste or type a short invented field note. This should keep the user in the form and should not open a file picker.</li>
          </ol>
          <div class="callout"><strong>Expected result:</strong> batch import, single import, and manual entry should behave differently. This is important because field teams may use all three modes.</div>

          <h3>Exercise D: SDMX readiness and repository governance</h3>
          <ol>
            <li>Review <strong>SDMX readiness and record preview</strong>. Required fields should be marked ready or missing in plain language.</li>
            <li>Click <strong>Stage and validate</strong>.</li>
            <li>Move to the repository/SDMX gate review. Approve some records and reject at least one record.</li>
            <li>Click <strong>Commit reviewed records</strong>. Approved records should move to the Accepted repository; rejected records should move to the Rejected repository; the active queue should shrink.</li>
            <li>Open the full repository in its separate HTML tab. Filter or inspect accepted and rejected records. Use <strong>Uncommit</strong> on one record to verify that it returns to the active approval queue.</li>
          </ol>
          <div class="callout"><strong>Expected result:</strong> the repository should read like human governance, not code. Accepted evidence is eligible for encoding and modelling; rejected evidence remains visible for audit but should not drive the model.</div>

          <h3>Exercise E: encode story by story</h3>
          <ol>
            <li>Move to <strong>Encoding</strong>.</li>
            <li>Select <strong>Manual / rule-based</strong>. For each story, enter numeric scores for the variables and write short justifications. Use <strong>Encode current story</strong> to move through the queue.</li>
            <li>Run <strong>AI</strong> or <strong>Hybrid</strong> if a user-owned LLM key is available. If no key is available, the deterministic heuristic fallback should be clearly labelled.</li>
            <li>Use comparison blocks to check whether different narratives receive different scores. Stories about cost fear, safety rumors, trusted health workers, peer influence, or time savings should not all score the same.</li>
          </ol>
          <div class="callout"><strong>Expected result:</strong> manual, heuristic, and hybrid outputs should vary by narrative content. A flat score across all stories is a bug or a calibration warning.</div>

          <h3>Exercise F: model, learn, and test inoculation</h3>
          <ol>
            <li>Run <strong>Compartmental model</strong>. Read the S/M/T/I/R curves and axis labels. A final percentage is the simulated adoption-aligned share at the final time horizon, not a measured real-world adoption rate.</li>
            <li>Run <strong>Agent-based model</strong>. Compare whether household-level peer effects change the result relative to the population curve.</li>
            <li>Run <strong>Digital twin</strong>. Enter or inspect feedback values and check whether the feedback-adjusted run differs from baseline.</li>
            <li>Run <strong>Bayesian update</strong>. Check whether posterior intervals widen when evidence is thin and narrow when evidence is stronger.</li>
            <li>Run <strong>RL optimizer</strong>. Treat the reward as a shortlist signal, not an automatic decision.</li>
            <li>Run <strong>Knowledge graph</strong> to inspect repeated places, themes, messenger types, and barrier clusters.</li>
            <li>Run <strong>Inoculation lab</strong>. The lab should generate a weak-dose claim, refutational response, trusted messenger recommendation, booster strategy, and intervention strength. Inject the inoculation narrative into the twin and compare before, during, and after projections.</li>
          </ol>
          <div class="callout"><strong>Expected result:</strong> model stages should explain what changed and why. If an inoculation message changes predictions, the app should show whether it modified trust, resistance, misinformation decay, adoption transition, or agent-level behavior.</div>

          <h3>Exercise G: optional regional analysis</h3>
          <ol>
            <li>Run regional analysis when the test dataset includes enough place variation.</li>
            <li>Compare one district against another, or group districts with similar narrative patterns.</li>
            <li>If skipped, continue to policy output. The policy brief should clearly state that recommendations use pooled evidence only.</li>
          </ol>
          <div class="callout"><strong>Expected result:</strong> regional analysis should help decide whether Rwanda-wide messaging is appropriate or whether districts need different messengers, demonstrations, or financing supports.</div>

          <h3>Exercise H: export and interpret the policy brief</h3>
          <ol>
            <li>Run <strong>Policy output</strong>.</li>
            <li>Download the HTML policy brief, use print-to-PDF for a PDF-friendly copy, and keep JSON only as an audit export.</li>
            <li>Check that the brief includes evidence grade, confidence, assumptions, limitations, uncertainty, human-review requirement, accepted narrative IDs, and whether ClimateTales stress-test data was synthetic.</li>
          </ol>
          <div class="callout"><strong>Expected result:</strong> the policy brief should be readable by a ministry analyst. It should not look like raw JSON, and it should not overclaim synthetic stress-test results as real field evidence.</div>
        </div>
      </details>

      <details id="interpretation">
        <summary>Interpreting results</summary>
        <div class="section-body">
          <p>A model percentage such as <strong>95.3%</strong> means the projected adoption-aligned share of the simulated population at the final time horizon. It does not mean that 95.3% of real households have already adopted.</p>
          <table>
            <thead><tr><th>Output</th><th>Meaning</th><th>Caution</th></tr></thead>
            <tbody>
              <tr><td data-label="Output">ODE curve</td><td data-label="Meaning">Population-level diffusion pathway.</td><td data-label="Caution">Can hide local household variation.</td></tr>
              <tr><td data-label="Output">Agent model</td><td data-label="Meaning">Household and peer-effect pathway.</td><td data-label="Caution">Depends on network assumptions.</td></tr>
              <tr><td data-label="Output">Digital twin</td><td data-label="Meaning">Feedback-adjusted scenario rerun.</td><td data-label="Caution">Only as good as the observed feedback and calibration rule.</td></tr>
              <tr><td data-label="Output">Inoculation diagnosis</td><td data-label="Meaning">Threat profile, weak-dose claim, refutational move, trusted messenger, and booster plan.</td><td data-label="Caution">Must be reviewed for cultural sensitivity and possible reactance before field use.</td></tr>
              <tr><td data-label="Output">Posterior</td><td data-label="Meaning">Updated uncertainty about trust and barriers.</td><td data-label="Caution">Sparse evidence should widen caution.</td></tr>
              <tr><td data-label="Output">RL reward</td><td data-label="Meaning">Relative intervention score.</td><td data-label="Caution">Shortlist for review, not an automatic decision.</td></tr>
            </tbody>
          </table>
        </div>
      </details>

      <details id="exports">
        <summary>Outputs and exports</summary>
        <div class="section-body">
          <p>The main output is a human-readable policy brief. It should state evidence grade, confidence level, assumptions, limitations, uncertainty, required human review, and recommended intervention.</p>
          <p>Use HTML for a readable brief. Use browser print-to-PDF for PDF export when direct PDF generation is unavailable. JSON remains available for audit and reproducibility.</p>
        </div>
      </details>

      <details id="multimodal">
        <summary>Multimodal and translation roadmap</summary>
        <div class="section-body">
          <p>This is a roadmap section, not a claim that all features are implemented today.</p>
          <ul>
            <li><strong>Speech to text:</strong> transcribe field interviews, radio discussions, and community meetings before SDMX validation.</li>
            <li><strong>Text to speech:</strong> read field templates, policy briefs, and inoculation messages aloud for accessibility and training.</li>
            <li><strong>Kinyarwanda-English translation:</strong> support translation both directions with translator notes, contested meanings, and confidence flags.</li>
            <li><strong>Local language partners:</strong> integrate resources such as Digital Umuganda where licensing, quality, and governance allow.</li>
            <li><strong>Multimodal evidence:</strong> eventually ingest audio, images of field forms, transcripts, and social feed summaries, but only after consent and provenance checks.</li>
          </ul>
          <p class="note">Translation and transcription can introduce errors. Store original evidence, translated text, reviewer identity, and confidence so policy users know what is certain and what remains uncertain.</p>
        </div>
      </details>
    </main>
    <a id="backTop" href="#top">Back to top</a>
    <script>
      function fallbackEquation(tex) {
        const compact = tex.replace(/\s+/g, " ");
        const frac = (top, bottom) => `<span class="frac"><span>${top}</span><span>${bottom}</span></span>`;
        const line = (left, right) => `<div class="eq-line"><span>${left}</span><span class="eq-op">=</span><span>${right}</span></div>`;
        if (compact.includes("\\Phi_i")) {
          return `<div class="eq-line"><span class="eq-var">Φ<sub>i</sub></span><span class="eq-op">=</span><span>0.30<span class="eq-var">E<sub>i</sub></span> + 0.30<span class="eq-var">C<sub>i</sub></span> + 0.20<span class="eq-var">τ<sub>i</sub></span> + 0.20<span class="eq-var">κ<sub>i</sub></span></span></div>`;
        }
        if (compact.includes("\\frac{dS}{dt}")) {
          return `<div class="eq-matrix">
            ${line(frac("dS", "dt"), `-β<sub>m</sub>SM - β<sub>t</sub>ST - ιS`)}
            ${line(frac("dM", "dt"), `β<sub>m</sub>SM - ρM - μM`)}
            ${line(frac("dT", "dt"), `β<sub>t</sub>ST + ρM - ηT`)}
            ${line(frac("dI", "dt"), `ιS + ηT - γI`)}
            ${line(frac("dR", "dt"), `γI + μM`)}
          </div>`;
        }
        if (compact.includes("\\theta_{t+1}")) {
          return `<div class="eq-line"><span class="eq-var">θ<sub>t+1</sub></span><span class="eq-op">=</span><span><span class="eq-var">θ<sub>t</sub></span> + λ(<span class="eq-var">y<sub>observed</sub></span> - <span class="eq-var">y<sub>predicted</sub></span>)</span></div>`;
        }
        if (compact.includes("prior") && compact.includes("posterior")) {
          return `<div class="eq-matrix">
            ${line(`<span class="eq-var">prior</span>`, `Beta(α, β)`)}
            ${line(`<span class="eq-var">posterior</span>`, `Beta(α + successes, β + failures)`)}
          </div>`;
        }
        if (compact.includes("Q(s,a)")) {
          return `<div class="eq-line"><span class="eq-var">Q(s,a)</span><span class="eq-op">←</span><span><span class="eq-var">Q(s,a)</span> + α [ r + γ max<sub>a′</sub><span class="eq-var">Q(s′,a′)</span> - <span class="eq-var">Q(s,a)</span> ]</span></div>`;
        }
        return `<div class="eq-line">${tex}</div>`;
      }

      function renderManualMath() {
        document.querySelectorAll(".math-display").forEach((node) => {
          if (node.dataset.rendered === "1") return;
          const tex = node.textContent.trim();
          if (window.katex) {
            try {
              window.katex.render(tex, node, { displayMode: true, throwOnError: false, strict: "ignore" });
              node.dataset.rendered = "1";
              return;
            } catch (error) {
              node.dataset.rendered = "0";
            }
          }
          node.innerHTML = fallbackEquation(tex);
          node.classList.add("rendered-fallback");
          node.dataset.rendered = "1";
        });
      }
      window.addEventListener("load", () => {
        const savedTheme = localStorage.getItem("ndim-doc-theme") || localStorage.getItem("ndim_theme") || "light";
        document.body.classList.toggle("dark", savedTheme === "dark");
        const themeToggle = document.getElementById("themeToggle");
        if (themeToggle) {
          themeToggle.textContent = savedTheme === "dark" ? "Light" : "Dark";
          themeToggle.addEventListener("click", () => {
            const next = document.body.classList.contains("dark") ? "light" : "dark";
            document.body.classList.toggle("dark", next === "dark");
            localStorage.setItem("ndim-doc-theme", next);
            localStorage.setItem("ndim_theme", next);
            themeToggle.textContent = next === "dark" ? "Light" : "Dark";
          });
        }
        renderManualMath();
        if (window.location.hash) {
          const target = document.querySelector(window.location.hash);
          if (target && target.tagName.toLowerCase() === "details") target.open = true;
        }
      });
    </script>
  </body>
</html>
"""

ACADEMY_HTML = r"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>NDIM Academy</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css" />
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"></script>
    <style>
      :root {
        --ink:#11100e;
        --body:#564b3d;
        --muted:#8a7d68;
        --paper:#fbfaf7;
        --line:#d6cbbb;
        --soft:#f3efe7;
        --white:#fffdf9;
      }
      * { box-sizing: border-box; }
      html { scroll-behavior: smooth; }
      body {
        margin: 0;
        background: var(--paper);
        color: var(--ink);
        font-family: "Myriad Pro", "Segoe UI", Arial, sans-serif;
        line-height: 1.68;
      }
      main {
        width: min(1080px, calc(100% - 32px));
        margin: 0 auto;
        padding: 34px 0 82px;
      }
      header {
        border-bottom: 1px solid var(--line);
        padding-bottom: 18px;
        margin-bottom: 18px;
      }
      h1 {
        margin: 0 0 12px;
        max-width: 900px;
        font-size: clamp(36px, 7vw, 72px);
        line-height: .98;
        letter-spacing: -.03em;
      }
      h2, h3 { line-height: 1.22; }
      p, li, td {
        color: var(--body);
        font-size: 16px;
      }
      a {
        color: var(--ink);
        text-decoration-thickness: 1px;
        text-underline-offset: 3px;
      }
      details {
        border-top: 1px solid var(--line);
      }
      details:last-of-type {
        border-bottom: 1px solid var(--line);
      }
      summary {
        cursor: pointer;
        list-style: none;
        padding: 18px 0;
        font-size: 22px;
        font-weight: 850;
      }
      summary::-webkit-details-marker { display: none; }
      summary::before {
        content: "+";
        display: inline-block;
        width: 28px;
        color: var(--muted);
        font-family: "Cascadia Mono", Consolas, monospace;
      }
      details[open] summary::before { content: "-"; }
      .section-body {
        padding: 0 0 26px 28px;
      }
      .small-link-row {
        display: flex;
        flex-wrap: wrap;
        gap: 14px;
        margin-top: 14px;
        font-size: 14px;
      }
      .mono {
        font-family: "Cascadia Mono", "JetBrains Mono", Consolas, monospace;
        letter-spacing: .08em;
        text-transform: uppercase;
      }
      .lede {
        max-width: 900px;
        font-size: clamp(18px, 2.2vw, 24px);
        color: var(--body);
      }
      .note {
        border-left: 3px solid var(--ink);
        background: var(--soft);
        padding: 12px 14px;
        margin: 16px 0;
      }
      .story-panel {
        border: 1px solid var(--line);
        border-radius: 18px;
        background: var(--white);
        padding: clamp(20px, 3vw, 34px);
        margin: 18px 0 22px;
      }
      .story-panel h2 {
        margin: 4px 0 12px;
        font-size: clamp(30px, 4vw, 56px);
        letter-spacing: -.02em;
      }
      .story-panel p:last-child {
        margin-bottom: 0;
      }
      .grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 12px;
        margin: 14px 0;
      }
      .card {
        border: 1px solid var(--line);
        border-radius: 12px;
        background: var(--white);
        padding: 14px;
      }
      .card h3 {
        margin: 0 0 6px;
      }
      .card p {
        margin: 0;
      }
      .card ul {
        margin: 10px 0 0 18px;
        padding: 0;
      }
      details.lesson {
        border: 1px solid var(--line);
        border-radius: 14px;
        background: var(--white);
        margin: 12px 0;
        overflow: hidden;
      }
      details.lesson:last-of-type {
        border-bottom: 1px solid var(--line);
      }
      details.lesson summary {
        padding: 14px 16px;
        font-size: 18px;
      }
      details.lesson .lesson-body {
        border-top: 1px solid var(--line);
        padding: 14px 16px 18px 44px;
      }
      .lesson-grid {
        display: grid;
        grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
        gap: 12px;
        margin: 12px 0;
      }
      .lesson-box {
        border: 1px solid var(--line);
        border-radius: 12px;
        background: var(--soft);
        padding: 12px;
      }
      .lesson-box h4 {
        margin: 0 0 6px;
      }
      .lesson-actions {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-top: 12px;
      }
      .lesson-actions a {
        border: 1px solid var(--line);
        border-radius: 999px;
        background: var(--soft);
        padding: 8px 12px;
        text-decoration: none;
        font-weight: 800;
      }
      table {
        width: 100%;
        border-collapse: collapse;
        margin: 14px 0 18px;
        background: var(--white);
      }
      th, td {
        border: 1px solid var(--line);
        padding: 10px;
        text-align: left;
        vertical-align: top;
      }
      th {
        background: var(--soft);
        color: var(--ink);
        font-size: 12px;
        letter-spacing: .08em;
        text-transform: uppercase;
      }
      .math-display {
        border: 1px solid var(--line);
        background: var(--white);
        border-radius: 10px;
        padding: 12px;
        margin: 12px 0;
        overflow-x: auto;
      }
      .math-display.rendered-fallback {
        font-family: "Cambria Math", "STIX Two Math", Georgia, serif;
        font-size: 20px;
        line-height: 1.9;
      }
      .math-display .katex-display {
        margin: 0;
        text-align: left;
        overflow-x: auto;
        overflow-y: hidden;
      }
      .level-tabs {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 10px;
        margin: 12px 0;
      }
      .system-map {
        display: grid;
        grid-template-columns: repeat(5, minmax(110px, 1fr));
        gap: 10px;
        align-items: center;
        margin: 16px 0;
      }
      .map-node {
        border: 1px solid var(--line);
        border-radius: 14px;
        background: var(--white);
        padding: 12px;
        min-height: 96px;
        position: relative;
      }
      .map-node h3 {
        margin: 0 0 6px;
        font-size: 17px;
      }
      .map-node p {
        margin: 0;
        font-size: 14px;
      }
      .map-node::after {
        content: "->";
        position: absolute;
        right: -20px;
        top: 40%;
        color: var(--muted);
        font: 800 18px "Cascadia Mono", Consolas, monospace;
      }
      .map-node:last-child::after {
        content: "";
      }
      .map-node.truth { border-left: 5px solid #315da8; }
      .map-node.risk { border-left: 5px solid #a04d37; }
      .map-node.inoculation { border-left: 5px solid #708461; }
      .conservation-note {
        border: 1px dashed var(--muted);
        border-radius: 12px;
        padding: 12px;
        background: rgba(255,255,255,.55);
      }
      .back-top {
        position: fixed;
        right: 18px;
        bottom: 18px;
        border: 1px solid var(--line);
        border-radius: 999px;
        background: var(--white);
        padding: 8px 12px;
        font-weight: 800;
        box-shadow: 0 8px 24px rgba(40, 32, 20, .10);
      }
      @media (max-width: 760px) {
        main { width: min(100% - 22px, 1080px); padding-top: 18px; }
        summary { font-size: 19px; }
        .section-body { padding-left: 0; }
        .grid, .level-tabs, .system-map, .lesson-grid { grid-template-columns: 1fr; }
        details.lesson .lesson-body { padding-left: 14px; }
        .map-node::after {
          content: "down";
          right: 14px;
          top: auto;
          bottom: -24px;
          font-size: 12px;
        }
        .map-node:last-child::after { content: ""; }
        table, thead, tbody, th, td, tr { display: block; }
        thead { display: none; }
        tr { border: 1px solid var(--line); margin: 10px 0; background: var(--white); }
        td { border: 0; border-bottom: 1px solid var(--line); }
        td::before {
          content: attr(data-label);
          display: block;
          color: var(--muted);
          font: 800 11px "Cascadia Mono", Consolas, monospace;
          letter-spacing: .07em;
          text-transform: uppercase;
        }
      }
      body {
        background:
          radial-gradient(circle at 8% 4%, rgba(255, 255, 255, .75), transparent 28rem),
          linear-gradient(90deg, transparent 0, transparent calc(100% - 1px), rgba(214, 202, 183, .34) calc(100% - 1px)),
          linear-gradient(135deg, #fbfaf7, #f7f0e7 70%, #fbfaf7);
        background-size: auto, 82px 82px, auto;
      }
      .app-topbar {
        position: sticky;
        top: 0;
        z-index: 30;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 16px;
        padding: 10px clamp(14px, 3vw, 34px);
        border-bottom: 1px solid var(--line);
        background: rgba(251, 250, 247, .94);
        backdrop-filter: blur(16px);
      }
      .brand {
        display: inline-flex;
        align-items: center;
        gap: 10px;
        min-width: 240px;
        color: var(--ink);
        text-decoration: none;
      }
      .brand .mark {
        display: grid;
        place-items: center;
        width: 34px;
        height: 34px;
        border-radius: 999px;
        background: var(--ink);
        color: #fff;
        font: 900 12px "Cascadia Mono", Consolas, monospace;
      }
      .brand strong, .brand span { display: block; line-height: 1.1; }
      .brand span {
        color: var(--muted);
        font: 850 10px "Cascadia Mono", Consolas, monospace;
        letter-spacing: .13em;
        text-transform: uppercase;
      }
      .app-nav {
        display: flex;
        flex-wrap: wrap;
        justify-content: flex-end;
        gap: 8px;
      }
      .app-nav a,
      .small-link-row a,
      .lesson-actions a,
      .back-top,
      .theme-toggle {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-height: 38px;
        border: 1px solid var(--line);
        border-radius: 999px;
        background: rgba(255, 253, 249, .82);
        color: var(--ink);
        padding: 8px 12px;
        font-weight: 850;
        text-decoration: none;
      }
      .app-nav a:first-child,
      .small-link-row a:first-child {
        background: var(--ink);
        border-color: var(--ink);
        color: #fff;
      }
      .theme-toggle {
        min-width: 62px;
        padding: 0 12px;
        cursor: pointer;
      }
      main {
        width: min(1180px, calc(100% - 32px));
      }
      header,
      .story-panel {
        border: 1px solid var(--line);
        border-radius: 24px;
        background: rgba(255, 253, 249, .78);
        box-shadow: 0 20px 70px rgba(70, 55, 30, .08);
        padding: clamp(20px, 4vw, 36px);
      }
      header {
        margin-bottom: 18px;
      }
      header .mono,
      summary,
      th {
        letter-spacing: .13em;
      }
      details:not(.lesson) {
        border: 1px solid var(--line);
        border-radius: 18px;
        background: rgba(255, 253, 249, .78);
        margin: 12px 0;
        overflow: hidden;
        box-shadow: 0 14px 44px rgba(70, 55, 30, .045);
      }
      details:not(.lesson):last-of-type { border-bottom: 1px solid var(--line); }
      details:not(.lesson) > summary {
        padding: 16px 18px;
      }
      details:not(.lesson) > .section-body {
        border-top: 1px solid var(--line);
        padding: 16px 18px 24px 46px;
      }
      details.lesson,
      .card,
      .lesson-box,
      .map-node,
      .math-display,
      table {
        background: rgba(255, 253, 249, .9);
        box-shadow: 0 12px 36px rgba(70, 55, 30, .04);
      }
      .note,
      .conservation-note {
        border-radius: 14px;
        border-left-width: 4px;
      }
      .back-top {
        background: var(--ink);
        color: #fff;
      }
      body.dark {
        --ink:#f8fafc;
        --body:#d1d5db;
        --muted:#9ca3af;
        --paper:#0b0f17;
        --line:#374151;
        --soft:#1f2937;
        --white:#111827;
        background:
          radial-gradient(circle at 8% 4%, rgba(147, 197, 253, .08), transparent 28rem),
          linear-gradient(90deg, transparent 0, transparent calc(100% - 1px), rgba(55, 65, 81, .38) calc(100% - 1px)),
          linear-gradient(135deg, #0b0f17, #111827 72%, #0b0f17);
        background-size: auto, 82px 82px, auto;
      }
      body.dark .app-topbar,
      body.dark header,
      body.dark .story-panel,
      body.dark details,
      body.dark .card,
      body.dark .lesson-box,
      body.dark .map-node,
      body.dark .math-display,
      body.dark table,
      body.dark .app-nav a,
      body.dark .small-link-row a,
      body.dark .lesson-actions a,
      body.dark .theme-toggle {
        background-color: #111827;
        color: var(--ink);
        border-color: var(--line);
      }
      body.dark .brand .mark,
      body.dark .app-nav a:first-child,
      body.dark .small-link-row a:first-child,
      body.dark .back-top {
        background: #030712;
        color: #fff;
        border-color: #e5e7eb;
      }
      body.dark th,
      body.dark .note,
      body.dark .conservation-note {
        background: #0f172a;
        color: var(--ink);
      }
      body.dark a { color: #bfdbfe; }
      @media (max-width: 760px) {
        .app-topbar { align-items: flex-start; flex-direction: column; }
        .brand { min-width: 0; }
        .app-nav { width: 100%; justify-content: flex-start; }
        details:not(.lesson) > .section-body { padding-left: 18px; }
      }
    </style>
  </head>
  <body id="top">
    <nav class="app-topbar" aria-label="NDIM learning navigation">
      <a class="brand" href="./index.html">
        <span class="mark">ND</span>
        <span>
          <strong>NDIM Engine</strong>
          <span>Narrative Diffusion and Inoculation Model</span>
        </span>
      </a>
      <div class="app-nav">
        <a href="./index.html">Tool</a>
        <a href="./manual.html">Manual</a>
        <a href="./publication.html">Publication</a>
        <a href="https://github.com/Naphymoro/nidm-rwanda-dashboard" target="_blank" rel="noreferrer">GitHub</a>
        <button class="theme-toggle" id="themeToggle" type="button" aria-label="Toggle light or dark mode">Dark</button>
      </div>
    </nav>
    <main>
      <header>
        <p class="mono">NDIM ACADEMY</p>
        <h1>Learn the Narrative Diffusion and Inoculation Model.</h1>
        <p class="lede">NDIM is a learning and research space for understanding how stories shape decisions. It helps a researcher move carefully from lived experience to evidence, from evidence to models, and from models to a policy brief that still shows its source trail.</p>
        <p class="small-link-row">
          <a href="./index.html">Back to tool</a>
          <a href="./manual.html">Tool manual</a>
          <a href="./publication.html">Scientific Publication</a>
          <a href="#difference">What makes NDIM different</a>
          <a href="#cloud-repository">Shared Google repository</a>
          <a href="#glossary">Glossary</a>
          <a href="#equations">Equations and model map</a>
          <a href="#modules">Learning modules</a>
          <a href="#practice">Practice with NDIM</a>
          <a href="#references">References</a>
        </p>
        <p class="lede">When a team is ready to turn NDIM work into a paper, the <a href="./publication.html">Scientific Publication workspace</a> provides a split editor and preview, legal literature search, BibTeX export, and optional OpenAI writing support.</p>
      </header>

      <section class="story-panel" aria-label="Opening story">
        <p class="mono">A FIELD STORY</p>
        <h2>One rumour can bend the path of a useful technology.</h2>
        <p>Imagine a field officer in Musanze hearing three stories in the same week. One mother says an electric pressure cooker helps her cook beans quickly before the children return from school. A market vendor says the device is too expensive to risk. A neighbour repeats that pressure cookers explode.</p>
        <p>None of these statements is only a "data point". Each one carries trust, fear, social proof, memory, and a possible intervention. NDIM asks a practical question: which stories are shaping adoption, which stories are creating risk, and what trusted message could help people judge the technology more fairly?</p>
        <p>Now shift the lens to malaria. After the rains, a field officer enters a village where the model is not hidden in equations; it is alive in three conversations. A mother touches the net above her children's bed: she believes it saves lives, but by midnight the room is airless, the youngest cries, and protection is folded back against the wall. A father lowers his voice and says he waited two days before testing his son's fever because the clinic felt far, money was tight, and the first help came from remedies the family already trusts. At the trading centre, an aunt repeats a warning from someone she respects: maybe the vaccine or medicine can harm a child.</p>
        <p>That is NDIM in plain sight. Comfort becomes a barrier. Distance becomes delay. Trust becomes a pathway. Fear becomes misinformation risk. A respected neighbour becomes either a carrier of doubt or the messenger who can help inoculate the community before harm spreads.</p>
      </section>

      <details id="why" open>
        <summary>01. Why NDIM is needed</summary>
        <div class="section-body">
          <p>Clean-cooking adoption is not only a technology problem. A pressure cooker can save time and fuel, but a household may still hesitate.</p>
          <p>The hesitation may come from a rumour about explosions. It may come from repair worries. It may come from cost, fuel supply, gendered decision power, habit, or a bad experience from a neighbour. It may also come from a simple question: "Has someone I trust used this safely?"</p>
          <p>A survey can count how many people agree or disagree. That is useful. But a survey can miss the story that explains the answer. NDIM keeps the story, the place, the source, the evidence quality, the model assumption, and the policy recommendation in one visible chain.</p>
          <p>Inoculation theory is central to that chain. In simple terms, it means helping people prepare before a harmful claim takes hold. A good inoculation message warns people that a misleading claim may appear, shows a weak version of the claim, and gives a respectful correction that people can remember.</p>
          <p>For NDIM, that means the tool is not only asking whether misinformation exists. It is asking what kind of misinformation is present, why it feels persuasive, who is likely to repeat it, who can correct it, and how the correction may change adoption over time.</p>
          <p>That is the central workflow: do not jump from raw stories to policy. First govern the evidence. Then encode it. Then model it. Then update uncertainty. Then test interventions. Then write a decision brief that a human can review.</p>
          <div class="note">
            <strong>Why NDIM is the innovation</strong>
            <p>NDIM matters because it refuses to throw away the story before the science begins. A rumour, a memory, a fear, a trusted demonstration, or an indigenous explanation is not treated as noise. It is treated as evidence that needs context, permission, review, and interpretation.</p>
            <p>Most tools answer one narrow question: What is spreading? NDIM asks the fuller policy question: where did the story come from, who can use it, what does it mean, what behaviour could it change, what intervention could respond, and what uncertainty remains?</p>
            <p>That is the innovation: a governed path from narrative evidence to inoculation-aware encoding, from encoding to population and household simulation, from simulation to digital-twin feedback, from feedback to uncertainty learning, and from learning to a decision brief a human can defend.</p>
            <p>This is why NDIM should be documented carefully. The terms, workflow, equations, validation evidence, and policy interpretation are part of the intellectual contribution. They must be reproducible, attributable, and open to scientific audit.</p>
          </div>
        </div>
      </details>

      <details id="difference" open>
        <summary>02. How NDIM differs from epidemiological misinformation models</summary>
        <div class="section-body">
          <p>Researchers have already used epidemic-style models to study rumours and misinformation. The idea is understandable: a claim can move through a community in a way that looks a little like contagion. One person hears it. Another repeats it. Some people resist it. Some people later accept a correction.</p>
          <p>Those models are useful. They help us think about spread, correction, recovery, and network effects.</p>
          <p><strong>But many of them begin after the evidence has already been simplified into states such as "exposed", "infected", or "recovered".</strong></p>
          <p>NDIM begins earlier. It starts with the actual story someone tells. Who said it? Where was it heard? What was the person worried about? Who repeated it? Who could correct it?</p>
          <p>That matters because the response depends on the story. A cost worry needs one kind of support. A safety rumour needs another. A trust problem may need a different messenger. NDIM is built to keep those differences visible.</p>
          <p>Inoculation theory gives NDIM its intervention logic. The simple idea is this: prepare people before the stronger misleading claim reaches them. A trusted message can warn them, show the weak version of the misleading claim, and explain how to refute it.</p>
          <p>NDIM turns that idea into usable model signals: threat recognition, misinformation risk, refutability, reactance risk, trusted messenger fit, and booster need. These signals help the tool test whether a "narrative vaccine" could shift the adoption pathway.</p>
          <table>
            <thead><tr><th>Dimension</th><th>Typical epidemiological misinformation model</th><th>NDIM Engine</th><th>Why it matters for policy</th></tr></thead>
            <tbody>
              <tr><td data-label="Dimension">Evidence source</td><td data-label="Typical model">Often simulated states, social media traces, or abstract network states.</td><td data-label="NDIM Engine">Begins from field narratives, structured interviews, indigenous knowledge, citizen reports, social feeds, and approved evidence records.</td><td data-label="Policy value">Policy users can see what real people said and where the claim came from.</td></tr>
              <tr><td data-label="Dimension">Evidence governance</td><td data-label="Typical model">Usually models spread after data already exists.</td><td data-label="NDIM Engine">Adds SDMX-style metadata, consent, visibility, approval, rejection, repository state, and audit hashes.</td><td data-label="Policy value">Sensitive or unverified stories are not silently promoted into model evidence.</td></tr>
              <tr><td data-label="Dimension">Encoding</td><td data-label="Typical model">Often assigns infection-like states directly.</td><td data-label="NDIM Engine">Encodes trust, barrier strength, misinformation risk, inoculation opportunity, emotional intensity, credibility, and local grounding.</td><td data-label="Policy value">Decision makers learn what kind of intervention is needed, not only whether a claim spreads.</td></tr>
              <tr><td data-label="Dimension">Inoculation theory</td><td data-label="Typical model">May include correction, forgetting, or recovery.</td><td data-label="NDIM Engine">Models weak-dose claims, threat recognition, refutational preemption, reactance risk, trusted messenger fit, and booster need.</td><td data-label="Policy value">Counter-messaging becomes a testable intervention, not generic myth-busting.</td></tr>
              <tr><td data-label="Dimension">Local context</td><td data-label="Typical model">May treat people as homogeneous compartments or generic network nodes.</td><td data-label="NDIM Engine">Links narratives to country, province, district, sector, source, language, respondent role, and community validation.</td><td data-label="Policy value">Rwanda, Kenya, Ghana, Uganda, and Tanzania can have different administrative and fieldwork structures.</td></tr>
              <tr><td data-label="Dimension">Model coupling</td><td data-label="Typical model">Often uses one mathematical model.</td><td data-label="NDIM Engine">Combines compartmental ODEs, agent-based modelling, digital-twin feedback, Bayesian updating, RL optimization, regional analysis, knowledge graphs, and policy synthesis.</td><td data-label="Policy value">The tool can compare population dynamics, local behaviour, uncertainty, and intervention tradeoffs.</td></tr>
              <tr><td data-label="Dimension">Policy output</td><td data-label="Typical model">May estimate spread or intervention impact.</td><td data-label="NDIM Engine">Produces decision briefs with confidence, evidence grade, assumptions, limitations, and required human review.</td><td data-label="Policy value">The final product is usable by ministries and research teams, not only model specialists.</td></tr>
            </tbody>
          </table>
          <p><strong>Bottom line:</strong> NDIM is not just a model of misinformation spread.</p>
          <p>It is a workbench for moving from stories to decisions without losing the story trail. It begins with community evidence. It records where that evidence came from. It turns the evidence into transparent scores. It tests both population-level and household-level dynamics. It updates uncertainty when new evidence arrives. It tests inoculation messages as interventions. It ends with a policy brief that still shows what the decision is based on.</p>
          <p>That is the difference a policy team should feel: the tool does not only say "a rumour may spread". It helps answer, "What did people say, why does it matter, what should we test, what is uncertain, and what can we responsibly recommend?"</p>
        </div>
      </details>

      <details id="cloud-repository" open>
        <summary>03. How the shared Google repository works</summary>
        <div class="section-body">
          <p>The shared Google repository is optional. It is not the scientific engine, and it is not the default private database. It is a controlled collaboration layer for projects that want a readable shared ledger during an early research phase.</p>
          <p>Start with the local workspace. That is where evidence is ingested, reviewed, accepted, rejected, encoded, and modelled. Only after a record is accepted and committed should it be prepared for any shared repository.</p>
          <p>Think of the full system as five different places, each with a different job:</p>
          <table>
            <thead><tr><th>Place</th><th>Simple meaning</th><th>What it should and should not do</th></tr></thead>
            <tbody>
              <tr><td data-label="Place">Local workspace repository</td><td data-label="Simple meaning">The user's project workspace.</td><td data-label="What it should and should not do">It stores working evidence, review decisions, hashes, encodings, model outputs, and exports. It should remain private unless the user deliberately exports or syncs.</td></tr>
              <tr><td data-label="Place">Accepted and rejected repositories</td><td data-label="Simple meaning">The local governance shelves.</td><td data-label="What it should and should not do">Accepted records may feed encoding and modelling. Rejected records stay available for audit but should not drive model results unless they are uncommitted and reviewed again.</td></tr>
              <tr><td data-label="Place">Google Drive</td><td data-label="Simple meaning">A shared filing cabinet.</td><td data-label="What it should and should not do">It can hold evidence packages, SDMX exports, reports, backups, and policy briefs. It should not bypass consent, visibility, or approval decisions.</td></tr>
              <tr><td data-label="Place">Google Sheets</td><td data-label="Simple meaning">A human-readable shared ledger.</td><td data-label="What it should and should not do">It can track accepted records, reviewer decisions, version notes, and sync status during a pilot. It should not replace a governed database for a large institutional deployment.</td></tr>
              <tr><td data-label="Place">GitHub and Cloudflare</td><td data-label="Simple meaning">Source code and public web hosting.</td><td data-label="What it should and should not do">GitHub stores the code and version history. Cloudflare serves the web app. Neither should be used as the private evidence repository.</td></tr>
            </tbody>
          </table>
          <p>The approval pathway should stay clear: local intake -> local approval or rejection -> commit -> accepted repository -> optional SDMX-style export -> optional shared Google repository review.</p>
          <p>A responsible shared record should carry consent, visibility, reviewer identity, evidence hash, route metadata, administrative location, and version history. That is what lets a project share evidence without pretending that every uploaded story is automatically policy-ready.</p>
          <p>In the repository stage, <strong>Check Google repository</strong> tells the user whether Drive and Sheets are configured. If they are not configured, NDIM still produces downloadable SDMX JSON, observation CSV, and DSD JSON packages for manual review or later upload.</p>
          <p class="note">For a controlled pilot, Google Drive and Sheets are practical. For a national or institutional deployment, use a governed database as the system of record and treat Drive/Sheets as a collaboration view or document store.</p>
        </div>
      </details>

      <details id="levels" open>
        <summary>04. How to read NDIM at three depths</summary>
        <div class="section-body">
          <p>Different users need different levels of detail. A field officer may need the next safe action. A policy analyst may need confidence and limits. A modeller may need equations and assumptions. NDIM Academy keeps those levels separate so the main app does not become crowded.</p>
          <div class="level-tabs">
            <div class="card"><h3>Guided learner</h3><p>Start with the story. What did people say, what are they worried about, who do they trust, and what is the next safe action?</p></div>
            <div class="card"><h3>Policy maker</h3><p>Focus on interpretation: evidence grade, confidence, risks, regional differences, feasibility, and what should be reviewed before action.</p></div>
            <div class="card"><h3>Expert</h3><p>Inspect equations, assumptions, priors, posterior intervals, calibration limits, validation data, and model compatibility checks.</p></div>
          </div>
          <p>The main workflow should stay action-oriented. Long explanations belong here. Small "learn more" links can open the relevant Academy section when a user needs help.</p>
        </div>
      </details>

      <details id="glossary">
        <summary>05. Glossary for everyday use</summary>
        <div class="section-body">
          <table>
            <thead><tr><th>Term</th><th>Plain meaning</th><th>Scientific meaning</th><th>Policy example</th></tr></thead>
            <tbody>
              <tr><td data-label="Term">Narrative</td><td data-label="Plain meaning">A story people use to explain a decision.</td><td data-label="Scientific meaning">A unit of meaning that carries source, context, belief, emotion, and social influence.</td><td data-label="Policy example">A mother says pressure cookers save time but neighbours fear explosions.</td></tr>
              <tr><td data-label="Term">Inoculation</td><td data-label="Plain meaning">Preparing people to resist a misleading claim before it harms decisions.</td><td data-label="Scientific meaning">A weak-dose warning plus refutational preemption that builds resistance to persuasion.</td><td data-label="Policy example">A trusted health worker explains the safety myth before a rumour spreads.</td></tr>
              <tr><td data-label="Term">Prebunking</td><td data-label="Plain meaning">Warning and explaining before misinformation arrives.</td><td data-label="Scientific meaning">Pre-emptive correction that teaches people how to recognize and refute a misleading tactic.</td><td data-label="Policy example">A radio segment explains why pressure-release sounds do not mean the cooker will burst.</td></tr>
              <tr><td data-label="Term">Compartment</td><td data-label="Plain meaning">A group of people in the same narrative state.</td><td data-label="Scientific meaning">A population state such as susceptible, misinformed, truth-aligned, inoculated, or resistant.</td><td data-label="Policy example">A district may have many households in the misinformation-exposed group.</td></tr>
              <tr><td data-label="Term">Agent</td><td data-label="Plain meaning">One simulated household or person.</td><td data-label="Scientific meaning">A local decision unit with trust, barriers, peers, media exposure, and adoption probability.</td><td data-label="Policy example">An agent may adopt after seeing a neighbour demonstrate safe use.</td></tr>
              <tr><td data-label="Term">Digital twin</td><td data-label="Plain meaning">A virtual copy of the adoption system that can be updated with field feedback.</td><td data-label="Scientific meaning">A feedback-calibrated model that reruns scenarios after observations adjust parameters.</td><td data-label="Policy example">Observed resistance in Musanze lowers the simulated adoption curve until trust improves.</td></tr>
              <tr><td data-label="Term">Prior</td><td data-label="Plain meaning">What the model believed before new evidence.</td><td data-label="Scientific meaning">A probability distribution representing starting assumptions.</td><td data-label="Policy example">Before fieldwork, the model assumes medium trust in demonstrations.</td></tr>
              <tr><td data-label="Term">Posterior</td><td data-label="Plain meaning">What the model believes after evidence is added.</td><td data-label="Scientific meaning">An updated distribution combining prior assumptions and observed evidence.</td><td data-label="Policy example">After approved narratives, the model estimates stronger barrier pressure.</td></tr>
              <tr><td data-label="Term">SDMX</td><td data-label="Plain meaning">A shared structure for making evidence comparable.</td><td data-label="Scientific meaning">Statistical metadata dimensions, attributes, and measures adapted for governed narrative records.</td><td data-label="Policy example">Country, district, source, period, consent, and narrative text are stored consistently.</td></tr>
              <tr><td data-label="Term">Evidence grade</td><td data-label="Plain meaning">How much confidence a decision maker should place in the evidence base.</td><td data-label="Scientific meaning">A quality signal based on record count, approval, validation, uncertainty, and review status.</td><td data-label="Policy example">Thin evidence triggers a caution before national recommendation.</td></tr>
              <tr><td data-label="Term">Refutational preemption</td><td data-label="Plain meaning">Showing a weak version of a misleading claim and explaining why it is wrong.</td><td data-label="Scientific meaning">A core mechanism in inoculation theory for building resistance to persuasion.</td><td data-label="Policy example">"Some say pressure cookers always explode; here is the safety valve evidence."</td></tr>
              <tr><td data-label="Term">Booster message</td><td data-label="Plain meaning">A follow-up reminder after the first inoculation message.</td><td data-label="Scientific meaning">A repeated intervention to maintain resistance and support behaviour change.</td><td data-label="Policy example">A later community demo repeats the safety explanation and practical action.</td></tr>
            </tbody>
          </table>
        </div>
      </details>

      <details id="equations" open>
        <summary>06. Equations and systems map</summary>
        <div class="section-body">
          <p>This section is not here to make every user a mathematician. It is here to show what the tool is doing when a story becomes a model input. A user should be able to read a chart and ask a good question: what moved, why did it move, and what evidence supports that movement?</p>
          <div class="system-map" aria-label="NDIM evidence-to-policy systems map">
            <div class="map-node"><h3>Narratives</h3><p>Stories from interviews, open accounts, social feeds, or community observations.</p></div>
            <div class="map-node"><h3>Governance</h3><p>Consent, visibility, place, source, approval, rejection, and hash trail.</p></div>
            <div class="map-node truth"><h3>Encoding</h3><p>Trust, barrier, misinformation risk, credibility, and inoculation opportunity.</p></div>
            <div class="map-node inoculation"><h3>Models</h3><p>Population flow, household behaviour, digital-twin feedback, and uncertainty learning.</p></div>
            <div class="map-node"><h3>Policy brief</h3><p>Recommendation, confidence, limitations, and required human review.</p></div>
          </div>

          <h3>1. Narrative strength</h3>
          <div class="math-display">\Phi_i = 0.30E_i + 0.30C_i + 0.20\tau_i + 0.20\kappa_i</div>
          <p><strong>What the equation is trying to represent:</strong> some stories carry more force than others. A story may be forceful because it is emotional, because it is credible locally, because it touches trust, or because it shows an opening for inoculation.</p>
          <p><strong>Plain-language variables:</strong> E is emotional intensity. C is local credibility. Tau is trust signal. Kappa is inoculation opportunity. Phi is the combined narrative force.</p>
          <p><strong>What increases the score:</strong> a vivid story from a trusted local source, repeated by peers, with a clear fear or hope attached to it.</p>
          <p><strong>What the user should look for:</strong> high Phi stories deserve attention. They may reveal an adoption barrier, a trusted messenger, a harmful rumour, or a useful intervention opportunity.</p>
          <p><strong>Policy meaning:</strong> high Phi does not mean the story is true. It means the story has enough force to shape decisions and should not be ignored.</p>

          <h3>2. Compartmental model: the population-level story</h3>
          <p>The compartmental model asks: if a community is divided into narrative states, how do people move between those states over time?</p>
          <div class="system-map" aria-label="NDIM compartmental systems map">
            <div class="map-node"><h3>S: susceptible</h3><p>People who have not yet been strongly shaped by either the misleading claim or the trusted correction.</p></div>
            <div class="map-node risk"><h3>M: misinformation exposed</h3><p>People influenced by fear, rumour, or a misleading story about the intervention.</p></div>
            <div class="map-node truth"><h3>T: truth aligned</h3><p>People reached by trusted evidence, demonstrations, or credible local explanation.</p></div>
            <div class="map-node inoculation"><h3>I: inoculated</h3><p>People prepared to recognize and resist the misleading claim before it spreads further.</p></div>
            <div class="map-node"><h3>R: resistant or adoption aligned</h3><p>People whose position is now more stable: either resistant to misinformation or aligned with adoption.</p></div>
          </div>
          <div class="conservation-note">
            <strong>Conserved population, in plain language.</strong>
            <p>In a conserved model, the total study population stays the same. People move from one compartment to another, but they do not vanish. If 100 percent of the study population is distributed across S, M, T, I, and R, the total remains 100 percent.</p>
            <p>This assumption is useful when NDIM is modelling a fixed study population, such as a defined district sample or an agreed community cohort.</p>
            <p>A non-conserved model is different. It allows people to enter or leave the system. That may be needed when there is migration, births, survey dropout, new programme participants, seasonal movement, or an expanding social-media audience. When NDIM uses a non-conserved scenario, it should say so clearly because the interpretation changes.</p>
          </div>
          <div class="math-display">\begin{aligned}
\frac{dS}{dt} &= -\beta_mSM - \beta_tST - \iota S \\
\frac{dM}{dt} &= \beta_mSM - \rho M - \sigma MI \\
\frac{dT}{dt} &= \beta_tST + \rho M - \mu T \\
\frac{dI}{dt} &= \iota S + \sigma MI - \gamma I \\
\frac{dR}{dt} &= \gamma I + \eta T
\end{aligned}</div>
          <p><strong>What a derivative means here:</strong> it is simply the speed of change. The line for S asks how quickly the susceptible group is shrinking. The line for M asks whether misinformation exposure is growing or declining. The line for I asks whether inoculation is reaching people fast enough.</p>
          <p><strong>What increases or decreases the flows:</strong> misinformation contact increases movement into M. Trusted evidence increases movement into T. Inoculation messages increase movement into I. Recovery, correction, and stable adoption move people toward R.</p>
          <p><strong>What the user should look for in the chart:</strong> if M rises quickly, harmful stories are winning attention. If T and I rise, trusted evidence and inoculation are working. If R rises, the system is becoming more stable.</p>
          <p><strong>Policy meaning:</strong> if misinformation pressure is high, a programme may need trusted messengers and prebunking before technology distribution can succeed.</p>

          <h3>3. Agent-based model: the household-level story</h3>
          <p>The agent-based model asks: what happens if households are different from each other? One household may trust a community health worker. Another may trust a neighbour. Another may face cost, distance, or habit barriers.</p>
          <div class="math-display">P(adopt_i) = logistic(trust_i + peer_i + evidence_i - barrier_i - misinformation_i)</div>
          <p><strong>Plain meaning:</strong> household i becomes more likely to adopt when trust, peer support, and evidence are strong. It becomes less likely to adopt when barriers and misinformation are strong.</p>
          <p><strong>What the user should look for:</strong> if the agent model is lower than the population curve, local household barriers may be slowing adoption. If it is higher, peer effects or trusted messengers may be doing useful work.</p>
          <p><strong>Policy meaning:</strong> a national message may not be enough if the household-level bottleneck is repair access, social proof, trust, or fear.</p>

          <h3>4. Digital twin feedback: learning from the field</h3>
          <div class="math-display">\theta_{t+1} = \theta_t + \lambda(y_{observed} - y_{predicted})</div>
          <p><strong>Plain meaning:</strong> the digital twin compares what the model predicted with what the field observed. If the two differ, the twin adjusts the assumptions and reruns the scenario.</p>
          <p><strong>How the models feed it:</strong> the compartmental model gives the broad population pathway. The agent-based model gives the household and peer-effect pathway. The twin compares those outputs with field feedback: observed adoption, trust change, barrier change, and inoculation effects.</p>
          <p><strong>Example:</strong> suppose the model predicts fast adoption, but field officers report that many households still fear pressure-cooker safety. The twin treats the earlier prediction as too optimistic. It lowers the trust pathway, raises the barrier pressure, and reruns the forecast.</p>
          <p><strong>Policy meaning:</strong> the twin is useful for scenario learning. It is not a national truth machine unless the observations are repeated, validated, and representative.</p>

          <h3>5. Bayesian update: changing confidence responsibly</h3>
          <div class="math-display">posterior = Beta(\alpha + successes,\beta + failures)</div>
          <p><strong>What a prior is:</strong> it is the model's starting belief before the new evidence is added. A prior is not a guess pulled from nowhere. It should come from earlier studies, expert judgment, pilot data, or an explicit assumption.</p>
          <p><strong>What a posterior is:</strong> it is the updated belief after the evidence is added. The posterior should not only give one number. It should also show how uncertain the model remains.</p>
          <p><strong>Example:</strong> before fieldwork, NDIM may assume medium trust in demonstrations. After twenty approved stories from Musanze, the model may learn that trust is higher among households who saw a neighbour use the cooker, but lower where safety rumours are repeated. The posterior captures that update.</p>
          <p><strong>Policy meaning:</strong> wide uncertainty means more evidence is needed. It should produce caution, not overconfidence.</p>

          <h3>6. Policy optimizer: comparing possible actions</h3>
          <div class="math-display">Q(s,a) \leftarrow Q(s,a) + \alpha\left[r + \gamma \max_{a'}Q(s',a') - Q(s,a)\right]</div>
          <p><strong>Plain meaning:</strong> the optimizer compares possible actions. It asks which action is likely to improve adoption while keeping cost, risk, and uncertainty under control.</p>
          <p><strong>Example actions:</strong> a peer demonstration, a health-worker message, a radio correction, a repair-support package, a subsidy, or an inoculation message that prebunks a safety rumour.</p>
          <p><strong>What reward means:</strong> reward is a score for usefulness. It is not a moral judgment and it is not a final decision. It is a way to rank options for review.</p>
          <p><strong>Policy meaning:</strong> the best reward is a shortlist for human review, not an automatic ministry decision. A low-cost action with strong trust gains may beat a costly action that looks impressive but does not address the local narrative barrier.</p>
        </div>
      </details>

      <details id="modules">
        <summary>07. Learning modules</summary>
        <div class="section-body">
          <p>Use these modules as a self-paced course. Each one explains the idea, gives a small worked example, and asks the learner to do something inside the NDIM tool. The goal is not memorisation. The goal is to help a user explain the final policy brief without saying, "the computer told me."</p>

          <details class="lesson" id="module-narrative" open>
            <summary>Module 1. Why narrative evidence matters</summary>
            <div class="lesson-body">
              <p><strong>Learning objective:</strong> understand why NDIM starts with stories rather than only survey counts or abstract model states.</p>
              <div class="lesson-grid">
                <div class="lesson-box"><h4>Key terms</h4><p>Narrative, source, local proof, social influence, adoption barrier, evidence route.</p></div>
                <div class="lesson-box"><h4>Worked example</h4><p>A woman says the cooker saves time, but her neighbour says it may explode. The useful evidence is not only "for" or "against". The story contains time pressure, safety fear, neighbour influence, and a possible trusted messenger.</p></div>
              </div>
              <p><strong>Exercise:</strong> open NDIM, select Stage 01 Narrative intake, choose Open story, and paste one paragraph from the ClimateTales corpus or a practice story. Before staging it, write down the practical barrier, the trust signal, and the person or group influencing the decision.</p>
              <p><strong>What to observe:</strong> the intake form asks for country, location, language, period, source, and route. These fields prevent the story from becoming anonymous text.</p>
              <p><strong>Interpretation:</strong> a story becomes useful for policy only when the user can explain where it came from, why it matters, and what action it suggests.</p>
              <p><strong>Common mistake:</strong> treating one emotional story as national evidence. NDIM keeps the story valuable, but still asks for governance, approval, and uncertainty.</p>
              <div class="lesson-actions"><a href="./index.html">Open NDIM tool</a><a href="./manual.html#narrative-intake">Read manual intake section</a><a href="#module-inoculation">Next module</a></div>
            </div>
          </details>

          <details class="lesson" id="module-inoculation">
            <summary>Module 2. Inoculation theory and narrative vaccines</summary>
            <div class="lesson-body">
              <p><strong>Learning objective:</strong> understand how NDIM uses inoculation theory to test protective messages before harmful claims spread widely.</p>
              <div class="lesson-grid">
                <div class="lesson-box"><h4>Key terms</h4><p>Weak-dose claim, warning, refutational preemption, reactance risk, trusted messenger, booster.</p></div>
                <div class="lesson-box"><h4>Worked example</h4><p>Weak-dose claim: "Pressure cookers always explode." Refutation: "Modern cookers have pressure-release valves; trained users can release pressure safely." Messenger: a health worker or respected local user who has demonstrated safe use.</p></div>
              </div>
              <p><strong>Exercise:</strong> take one safety-rumour story. Write one warning sentence, one weak-dose claim, one correction, and one trusted messenger. Then run the Inoculation lab after encoding accepted evidence.</p>
              <p><strong>What to observe:</strong> the lab should produce a proposed counter-narrative, a messenger fit, a booster need, and an intervention strength. These outputs should be reviewed before field use.</p>
              <p><strong>Interpretation:</strong> an inoculation message is not generic myth-busting. It should prepare people to recognise the misleading claim and resist it respectfully.</p>
              <p><strong>Common mistake:</strong> using a scolding tone. A message that embarrasses people can increase resistance instead of reducing misinformation.</p>
              <div class="lesson-actions"><a href="./index.html">Open NDIM tool</a><a href="./manual.html#workflow">See workflow tutorial</a><a href="#module-governance">Next module</a></div>
            </div>
          </details>

          <details class="lesson" id="module-governance">
            <summary>Module 3. Evidence governance and SDMX intake</summary>
            <div class="lesson-body">
              <p><strong>Learning objective:</strong> learn why NDIM requires evidence context before a narrative can influence a model.</p>
              <div class="lesson-grid">
                <div class="lesson-box"><h4>Key terms</h4><p>SDMX dimensions, attributes, measures, consent tier, visibility tier, approval queue, evidence hash.</p></div>
                <div class="lesson-box"><h4>Worked example</h4><p>A CSV row with only "people fear explosions" is too weak. The same row becomes usable when it includes route, district, source type, period, language, validation status, and reviewer decision.</p></div>
              </div>
              <p><strong>Exercise:</strong> load a route-specific ClimateTales CSV. Review SDMX readiness. Approve two records, reject one, then click Commit reviewed records.</p>
              <p><strong>What to observe:</strong> approved records move to the Accepted repository. Rejected records move to the Rejected repository. The active queue should shrink.</p>
              <p><strong>Interpretation:</strong> governance is not bureaucracy. It is the difference between evidence that can responsibly influence a model and material that should remain audit-only.</p>
              <p><strong>Common mistake:</strong> approving every record because it imported successfully. Import success is not evidence approval.</p>
              <div class="lesson-actions"><a href="./index.html">Open NDIM tool</a><a href="./manual.html#repository">Read repository section</a><a href="#module-encoding">Next module</a></div>
            </div>
          </details>

          <details class="lesson" id="module-encoding">
            <summary>Module 4. Manual, AI, and hybrid encoding</summary>
            <div class="lesson-body">
              <p><strong>Learning objective:</strong> learn how narrative meaning becomes model inputs without hiding human judgement.</p>
              <div class="lesson-grid">
                <div class="lesson-box"><h4>Key terms</h4><p>Trust, barrier, social influence, credibility, Phi, manual scorecard, AI pre-code, hybrid review.</p></div>
                <div class="lesson-box"><h4>Worked example</h4><p>A story about a trusted neighbour demonstrating safe use should score differently from a story about fear, cost, and no repair support. If both receive the same score, the encoder needs calibration.</p></div>
              </div>
              <p><strong>Exercise:</strong> manually encode one accepted narrative. Then run AI or heuristic encoding on the same story. Compare the two score sets and write one sentence explaining any disagreement.</p>
              <p><strong>What to observe:</strong> manual, AI, and hybrid results should be stored separately and appear in the repository as comparison columns.</p>
              <p><strong>Interpretation:</strong> the model needs numbers, but the researcher needs reasons. A score without a short justification is weak evidence.</p>
              <p><strong>Common mistake:</strong> batch-encoding everything without inspecting outliers. Use story-by-story review for validation.</p>
              <div class="lesson-actions"><a href="./index.html">Open NDIM tool</a><a href="./manual.html#workflow">Read Stage 03 tutorial</a><a href="#module-ode">Next module</a></div>
            </div>
          </details>

          <details class="lesson" id="module-ode">
            <summary>Module 5. Compartmental model</summary>
            <div class="lesson-body">
              <p><strong>Learning objective:</strong> understand how encoded narratives feed the population-level S/M/T/I/R model.</p>
              <div class="lesson-grid">
                <div class="lesson-box"><h4>Key terms</h4><p>Susceptible, misinformation-exposed, truth-aligned, inoculated, resistant/adoption-aligned, derivative, adoption share.</p></div>
                <div class="lesson-box"><h4>Worked example</h4><p>If many accepted stories show strong safety rumours, misinformation pressure rises. If many stories show trusted demonstrations, truth alignment and inoculation pressure rise.</p></div>
              </div>
              <p><strong>Exercise:</strong> after encoding at least three accepted narratives, run the compartmental model. Identify which curve grows, which curve declines, and what narrative evidence may explain it.</p>
              <p><strong>What to observe:</strong> the x-axis should show time. The y-axis should show simulated population share. The result is a scenario, not a measured survey statistic.</p>
              <p><strong>Interpretation:</strong> the model asks how fast population groups may move between narrative states under current assumptions.</p>
              <p><strong>Common mistake:</strong> reading a final percentage as real adoption. It is projected adoption-aligned share under model assumptions.</p>
              <div class="lesson-actions"><a href="./index.html">Open NDIM tool</a><a href="#equations">Review equations</a><a href="#module-abm">Next module</a></div>
            </div>
          </details>

          <details class="lesson" id="module-abm">
            <summary>Module 6. Agent-based model</summary>
            <div class="lesson-body">
              <p><strong>Learning objective:</strong> understand why household-level variation can change the adoption story.</p>
              <div class="lesson-grid">
                <div class="lesson-box"><h4>Key terms</h4><p>Agent, peer effect, household trust, barrier friction, network influence, local heterogeneity.</p></div>
                <div class="lesson-box"><h4>Worked example</h4><p>Two districts may have the same average trust score, but one district has strong neighbour demonstrations while the other has isolated households. The agent model can show different adoption paths.</p></div>
              </div>
              <p><strong>Exercise:</strong> run the agent-based model after the compartmental model. Compare whether the agent curve is above, below, or close to the ODE curve.</p>
              <p><strong>What to observe:</strong> disagreement between ODE and ABM is useful. It may reveal household-level bottlenecks hidden by aggregate averages.</p>
              <p><strong>Interpretation:</strong> if ABM adoption is lower, the policy may need peer demonstrations, repair support, or local champions rather than only broad messaging.</p>
              <p><strong>Common mistake:</strong> treating ODE and ABM disagreement as a bug. It can be a scientific warning.</p>
              <div class="lesson-actions"><a href="./index.html">Open NDIM tool</a><a href="#module-twin">Next module</a></div>
            </div>
          </details>

          <details class="lesson" id="module-twin">
            <summary>Module 7. Digital twin</summary>
            <div class="lesson-body">
              <p><strong>Learning objective:</strong> understand the digital twin as a feedback-calibrated simulation, not just another chart.</p>
              <div class="lesson-grid">
                <div class="lesson-box"><h4>Key terms</h4><p>Baseline, feedback-adjusted run, observed adoption, model prediction, calibration, before/during/after intervention.</p></div>
                <div class="lesson-box"><h4>Worked example</h4><p>The model predicts high adoption, but field feedback shows persistent safety fear. The twin lowers trust, raises barrier pressure, and reruns the scenario.</p></div>
              </div>
              <p><strong>Exercise:</strong> run the digital twin, then apply an inoculation narrative from the Inoculation lab. Compare baseline, during intervention, and after intervention outputs.</p>
              <p><strong>What to observe:</strong> the twin should show which inputs changed: trust, resistance, misinformation decay, adoption transition, or household-level behaviour.</p>
              <p><strong>Interpretation:</strong> a feedback-adjusted twin is a learning device. It helps the user ask whether field evidence materially changes the model.</p>
              <p><strong>Common mistake:</strong> assuming the twin is automatically correct. It is only as strong as the evidence, calibration rule, and validation checks.</p>
              <div class="lesson-actions"><a href="./index.html">Open NDIM tool</a><a href="./manual.html#workflow">Read Digital Twin tutorial</a><a href="#module-bayes">Next module</a></div>
            </div>
          </details>

          <details class="lesson" id="module-bayes">
            <summary>Module 8. Bayesian updating</summary>
            <div class="lesson-body">
              <p><strong>Learning objective:</strong> understand why NDIM updates uncertainty instead of pretending one model run is enough.</p>
              <div class="lesson-grid">
                <div class="lesson-box"><h4>Key terms</h4><p>Prior, posterior, evidence strength, interval, calibration, caution flag.</p></div>
                <div class="lesson-box"><h4>Worked example</h4><p>Before fieldwork, the model assumes medium trust in demonstrations. After approved stories show strong trust in health workers but weak trust in vendors, the posterior changes.</p></div>
              </div>
              <p><strong>Exercise:</strong> run the Bayesian update after encoding. Compare prior and posterior values and note whether uncertainty is still wide.</p>
              <p><strong>What to observe:</strong> thin evidence should produce caution. Stronger evidence should narrow uncertainty only when it is consistent and approved.</p>
              <p><strong>Interpretation:</strong> a posterior is an updated belief with uncertainty. It is not a final truth statement.</p>
              <p><strong>Common mistake:</strong> reporting only the average and ignoring the interval or warning label.</p>
              <div class="lesson-actions"><a href="./index.html">Open NDIM tool</a><a href="#equations">Review Bayesian equation</a><a href="#module-rl">Next module</a></div>
            </div>
          </details>

          <details class="lesson" id="module-rl">
            <summary>Module 9. RL policy optimizer</summary>
            <div class="lesson-body">
              <p><strong>Learning objective:</strong> learn how the optimizer ranks candidate interventions without replacing human decision-making.</p>
              <div class="lesson-grid">
                <div class="lesson-box"><h4>Key terms</h4><p>Action, reward, cost penalty, risk penalty, exploration, policy shortlist.</p></div>
                <div class="lesson-box"><h4>Worked example</h4><p>A peer demonstration may score higher than a broad radio message if the encoded evidence shows that neighbour proof is the strongest trust pathway.</p></div>
              </div>
              <p><strong>Exercise:</strong> run the optimizer and identify the top action. Then ask whether the top action is feasible, affordable, equitable, and supported by evidence.</p>
              <p><strong>What to observe:</strong> reward curves can improve over episodes, but the final policy should still include confidence and limitations.</p>
              <p><strong>Interpretation:</strong> the optimizer creates a shortlist for review. It does not issue a command to government.</p>
              <p><strong>Common mistake:</strong> choosing the highest reward without checking cost, fairness, or evidence grade.</p>
              <div class="lesson-actions"><a href="./index.html">Open NDIM tool</a><a href="#module-regional">Next module</a></div>
            </div>
          </details>

          <details class="lesson" id="module-regional">
            <summary>Module 10. Regional analysis</summary>
            <div class="lesson-body">
              <p><strong>Learning objective:</strong> learn when places should be analysed separately and when they can be grouped.</p>
              <div class="lesson-grid">
                <div class="lesson-box"><h4>Key terms</h4><p>District comparison, grouped evidence, place-specific barrier, pooled model, optional stage.</p></div>
                <div class="lesson-box"><h4>Worked example</h4><p>Musanze may show safety fear and peer influence, while Nyamagabe may show cost and access barriers. One national message may not fit both.</p></div>
              </div>
              <p><strong>Exercise:</strong> if your dataset contains multiple districts, run regional analysis. Compare the top barrier and trust signal for each district. If your dataset is too small, skip this stage and say so in the policy brief.</p>
              <p><strong>What to observe:</strong> regional analysis is optional. It is valuable only when the evidence has enough place variation.</p>
              <p><strong>Interpretation:</strong> place-specific evidence can justify different messengers, demonstrations, or financing approaches.</p>
              <p><strong>Common mistake:</strong> making district-specific claims from one or two stories.</p>
              <div class="lesson-actions"><a href="./index.html">Open NDIM tool</a><a href="#module-graph">Next module</a></div>
            </div>
          </details>

          <details class="lesson" id="module-graph">
            <summary>Module 11. Knowledge graph</summary>
            <div class="lesson-body">
              <p><strong>Learning objective:</strong> understand how repeated stories, places, themes, and messengers connect.</p>
              <div class="lesson-grid">
                <div class="lesson-box"><h4>Key terms</h4><p>Node, edge, theme cluster, repeated claim, messenger cluster, place cluster.</p></div>
                <div class="lesson-box"><h4>Worked example</h4><p>If several stories from the same district connect safety fear, WhatsApp repetition, and neighbour influence, the graph makes that pattern visible.</p></div>
              </div>
              <p><strong>Exercise:</strong> run the Knowledge graph after repository and encoding stages. Identify one highly connected theme and one highly connected place.</p>
              <p><strong>What to observe:</strong> graph size means connection, not truth. A large rumour node may be important because it repeats, not because it is correct.</p>
              <p><strong>Interpretation:</strong> the graph helps discover where interventions should focus and which claims should be validated.</p>
              <p><strong>Common mistake:</strong> reading the graph like a geographic map. It is a relationship map.</p>
              <div class="lesson-actions"><a href="./index.html">Open NDIM tool</a><a href="#module-policy">Next module</a></div>
            </div>
          </details>

          <details class="lesson" id="module-policy">
            <summary>Module 12. Policy brief export</summary>
            <div class="lesson-body">
              <p><strong>Learning objective:</strong> learn how to read and export a decision brief without overclaiming the evidence.</p>
              <div class="lesson-grid">
                <div class="lesson-box"><h4>Key terms</h4><p>Evidence grade, confidence level, assumptions, limitations, human review, HTML brief, JSON audit payload.</p></div>
                <div class="lesson-box"><h4>Worked example</h4><p>A brief may recommend health-worker demonstrations plus an inoculation message, but should also say if evidence was synthetic, thin, district-specific, or not field-validated.</p></div>
              </div>
              <p><strong>Exercise:</strong> run Policy output. Download or print the HTML brief. Check that it includes accepted records, evidence grade, uncertainty, model assumptions, recommendation, limitations, and human-review requirement.</p>
              <p><strong>What to observe:</strong> the main brief should be human-readable. JSON is for audit, hashes, and reproducibility.</p>
              <p><strong>Interpretation:</strong> a good policy brief says what to do, why, how confident the evidence is, and what must be reviewed before action.</p>
              <p><strong>Common mistake:</strong> presenting a stress-test result as real-world evidence.</p>
              <div class="lesson-actions"><a href="./index.html">Open NDIM tool</a><a href="./manual.html#exports">Read export section</a><a href="#module-climatetales">Next module</a></div>
            </div>
          </details>

          <details class="lesson" id="module-climatetales">
            <summary>Module 13. ClimateTales Rwanda practice workflow</summary>
            <div class="lesson-body">
              <p><strong>Learning objective:</strong> complete a realistic end-to-end practice run using synthetic ClimateTales data.</p>
              <div class="lesson-grid">
                <div class="lesson-box"><h4>Key terms</h4><p>Synthetic corpus, route-specific CSV, bonus single story, stress test, practice evidence.</p></div>
                <div class="lesson-box"><h4>Worked example</h4><p>A learner loads the structured interview CSV, approves several records, manually encodes two, compares AI or heuristic scores, runs models, injects an inoculation message, and exports a policy brief.</p></div>
              </div>
              <p><strong>Exercise:</strong> complete the full practice path in the Practice section below. Use one CSV first. Then repeat with another route. Finally test the mixed master corpus.</p>
              <p><strong>What to observe:</strong> route-specific forms should adapt, batch records should stay separate, scores should vary by narrative, and the final brief should label stress-test data as synthetic.</p>
              <p><strong>Interpretation:</strong> the practice run proves the workflow and user experience. It does not prove a Rwanda policy conclusion until real approved evidence is added.</p>
              <p><strong>Common mistake:</strong> using all stress-test files at once before learning the single-route workflow.</p>
              <div class="lesson-actions"><a href="./index.html">Open NDIM tool</a><a href="./manual.html#stress-test-corpus">Read ClimateTales tutorial</a><a href="#practice">Go to practice section</a></div>
            </div>
          </details>

        </div>
      </details>

      <details id="practice" open>
        <summary>08. Practice content that works with NDIM</summary>
        <div class="section-body">
          <p>NDIM is easiest to learn with practice evidence. The practice content should look like real field material, but it should be clearly marked as synthetic unless it comes from an approved study.</p>
          <p>A good practice pack should contain several kinds of stories. Some should be hopeful. Some should be cautious. Some should contain rumours. Some should contain practical barriers. Some should show trust, peer influence, gendered decision-making, repair concerns, fuel access, time savings, health concerns, or cultural meanings.</p>
          <table>
            <thead><tr><th>Practice item</th><th>Why it matters</th><th>What the learner should observe</th></tr></thead>
            <tbody>
              <tr><td data-label="Practice item">Structured interview</td><td data-label="Why it matters">Teaches the Q1-Q5 field protocol.</td><td data-label="Observe">How answers become separate evidence records with respondent context.</td></tr>
              <tr><td data-label="Practice item">Open story</td><td data-label="Why it matters">Teaches how to handle long lived-experience narratives.</td><td data-label="Observe">How the same story can carry trust, fear, barrier, and social influence.</td></tr>
              <tr><td data-label="Practice item">Indigenous knowledge note</td><td data-label="Why it matters">Teaches attribution, cultural sensitivity, and community validation.</td><td data-label="Observe">Why local knowledge should not be stripped from its context.</td></tr>
              <tr><td data-label="Practice item">Citizen science report</td><td data-label="Why it matters">Teaches confidence, location precision, and contributor validation.</td><td data-label="Observe">Why an observation can be useful but still limited.</td></tr>
              <tr><td data-label="Practice item">Crowdsourced batch</td><td data-label="Why it matters">Teaches moderation, deduplication, approval, and rejection.</td><td data-label="Observe">How the repository protects the model from unreviewed evidence.</td></tr>
              <tr><td data-label="Practice item">Social media feed</td><td data-label="Why it matters">Teaches experimental digital listening without treating it as core field evidence too early.</td><td data-label="Observe">How rumour signals can be flagged for validation before policy use.</td></tr>
            </tbody>
          </table>
          <p><strong>Recommended exercise:</strong> load ten synthetic narratives from one route. Approve seven, reject three, commit the reviewed records, then encode the accepted records one by one. Run the compartmental model, agent model, digital twin, Bayesian update, optimizer, inoculation lab, and policy export. Ask at each stage: "What changed, why did it change, and what evidence supports the change?"</p>
          <p><strong>What success looks like:</strong> the learner can explain the final policy brief without saying "the computer told me." They should be able to point to the stories, the governance decision, the encoding scores, the model assumptions, the uncertainty, and the human review requirement.</p>
        </div>
      </details>

      <details id="references">
        <summary>09. Scholarly positioning and references</summary>
        <div class="section-body">
          <p>NDIM is related to epidemic misinformation diffusion models, rumour-spreading models, social-contagion models, information-cascade studies, inoculation-theory studies, agent-based adoption models, and digital-twin policy simulation. Its claimed differentiation should be stated carefully: integration of these pieces into a governed, explainable, evidence-to-policy workflow.</p>
          <ul>
            <li>Kermack and McKendrick, 1927: foundational epidemic modelling logic behind SIR-style population transitions.</li>
            <li>Daley and Kendall, 1965, and Maki and Thompson, 1973: classical rumour-spreading models that connect epidemic logic to information transmission.</li>
            <li>McGuire, 1964: psychological inoculation theory and resistance to persuasion.</li>
            <li>Vosoughi, Roy, and Aral, 2018: empirical work on diffusion of true and false news online.</li>
            <li>Roozenbeek and van der Linden, 2022, and Traberg, Roozenbeek, and van der Linden, 2022: psychological inoculation and prebunking against misinformation.</li>
            <li>Recent network epidemic misinformation studies extend SIR-like models with social bias, emotional reaction, intervention, and network topology.</li>
          </ul>
          <p class="note">This Academy uses these references as scholarly positioning, not as a claim that NDIM is the first model of misinformation spread. The stronger claim is that NDIM integrates governed narrative evidence, inoculation-aware encoding, coupled modelling, uncertainty learning, and decision-brief export in one workflow.</p>
        </div>
      </details>
    </main>
    <a class="back-top" href="#top">Back to top</a>
    <script>
      function fallbackEquation(tex) {
        return tex
          .replace(/\\frac\{([^{}]+)\}\{([^{}]+)\}/g, "($1)/($2)")
          .replace(/\\begin\{aligned\}|\\end\{aligned\}/g, "")
          .replace(/\\\\/g, "<br>")
          .replace(/\\leftarrow/g, "&larr;")
          .replace(/\\rightarrow/g, "&rarr;")
          .replace(/\\beta/g, "beta")
          .replace(/\\gamma/g, "gamma")
          .replace(/\\alpha/g, "alpha")
          .replace(/\\tau/g, "tau")
          .replace(/\\kappa/g, "kappa")
          .replace(/\\Phi/g, "Phi")
          .replace(/\\theta/g, "theta")
          .replace(/\\lambda/g, "lambda")
          .replace(/\\iota/g, "iota")
          .replace(/\\rho/g, "rho")
          .replace(/\\sigma/g, "sigma")
          .replace(/\\eta/g, "eta");
      }
      function renderAcademyMath() {
        document.querySelectorAll(".math-display").forEach((node) => {
          if (node.dataset.rendered === "1") return;
          const tex = node.textContent.trim();
          if (window.katex) {
            try {
              window.katex.render(tex, node, { displayMode: true, throwOnError: false, strict: "ignore" });
              node.dataset.rendered = "1";
              return;
            } catch (error) {
              node.dataset.rendered = "0";
            }
          }
          node.innerHTML = fallbackEquation(tex);
          node.classList.add("rendered-fallback");
          node.dataset.rendered = "1";
        });
      }
      window.addEventListener("load", function () {
        const savedTheme = localStorage.getItem("ndim-doc-theme") || localStorage.getItem("ndim_theme") || "light";
        document.body.classList.toggle("dark", savedTheme === "dark");
        const themeToggle = document.getElementById("themeToggle");
        if (themeToggle) {
          themeToggle.textContent = savedTheme === "dark" ? "Light" : "Dark";
          themeToggle.addEventListener("click", () => {
            const next = document.body.classList.contains("dark") ? "light" : "dark";
            document.body.classList.toggle("dark", next === "dark");
            localStorage.setItem("ndim-doc-theme", next);
            localStorage.setItem("ndim_theme", next);
            themeToggle.textContent = next === "dark" ? "Light" : "Dark";
          });
        }
        renderAcademyMath();
        if (window.location.hash) {
          const target = document.querySelector(window.location.hash);
          if (target) {
            if (target.tagName.toLowerCase() === "details") target.open = true;
            let parent = target.parentElement ? target.parentElement.closest("details") : null;
            while (parent) {
              parent.open = true;
              parent = parent.parentElement ? parent.parentElement.closest("details") : null;
            }
            target.scrollIntoView({ behavior: "smooth", block: "start" });
          }
        }
      });
    </script>
  </body>
</html>
"""

LEGACY_MANUAL_HTML_BUSY = r"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>NDIM Engine Manual</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css" />
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"></script>
    <style>
      :root {
        --ink:#0b0a08; --body:#625746; --muted:#a99b84; --paper:#fbfaf7;
        --panel:#f1ede5; --card:#fffdf9; --line:#d3c7b5; --accent:#11100e;
        --green:#708461; --blue:#315da8; --amber:#b98a3a; --red:#a04d37;
      }
      * { box-sizing: border-box; }
      body {
        margin: 0;
        background: radial-gradient(circle at 12% 0%, rgba(179,144,88,.10), transparent 28%), var(--paper);
        color: var(--ink);
        font-family: "Myriad Pro", "Segoe UI", Arial, sans-serif;
        line-height: 1.62;
      }
      main { max-width: 1120px; margin: 0 auto; padding: 34px 18px 72px; }
      header {
        border: 1px solid var(--line);
        border-radius: 24px;
        background: var(--card);
        padding: clamp(22px, 4vw, 44px);
        box-shadow: 0 20px 60px rgba(64,47,24,.08);
      }
      h1 { margin: 0 0 10px; font-size: clamp(36px, 6vw, 68px); line-height: .98; letter-spacing: -.02em; }
      h2, h3 { line-height: 1.18; }
      p, li, td { color: var(--body); font-size: 16px; }
      a { color: var(--blue); font-weight: 800; }
      code, pre, .mono { font-family: "Cascadia Mono", "JetBrains Mono", Consolas, monospace; }
      .top-links { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 18px; }
      .button {
        display: inline-flex; align-items: center; justify-content: center;
        min-height: 42px; padding: 10px 16px; border: 1px solid var(--line);
        border-radius: 999px; background: var(--panel); color: var(--ink); text-decoration: none;
      }
      .button.primary { background: var(--accent); color: white; border-color: var(--accent); }
      .toc {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
        gap: 10px;
        margin: 18px 0 22px;
      }
      .toc a {
        border: 1px solid var(--line); border-radius: 16px; background: var(--card);
        padding: 12px; color: var(--ink); text-decoration: none;
      }
      details {
        border: 1px solid var(--line);
        border-radius: 20px;
        background: var(--card);
        margin: 14px 0;
        overflow: hidden;
      }
      details[open] { box-shadow: 0 14px 40px rgba(64,47,24,.07); }
      summary {
        cursor: pointer;
        list-style: none;
        padding: 18px 20px;
        display: flex;
        gap: 14px;
        align-items: center;
        font-weight: 900;
        font-size: 21px;
      }
      summary::-webkit-details-marker { display: none; }
      summary .num {
        display: inline-flex; width: 42px; height: 42px; align-items: center; justify-content: center;
        border: 1px solid var(--line); border-radius: 14px; background: var(--panel);
        font: 800 14px "Cascadia Mono", monospace;
      }
      .section-body { border-top: 1px solid var(--line); padding: 18px 20px 22px; }
      .grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }
      .card { border: 1px solid var(--line); border-radius: 16px; background: var(--panel); padding: 14px; }
      .callout { border-left: 4px solid var(--blue); background: var(--panel); border-radius: 14px; padding: 14px 16px; margin: 14px 0; }
      .warning { border-left-color: var(--red); }
      .success { border-left-color: var(--green); }
      table { width: 100%; border-collapse: collapse; margin: 14px 0; background: white; }
      th, td { border: 1px solid var(--line); padding: 10px; text-align: left; vertical-align: top; }
      th { background: var(--panel); color: var(--ink); font-size: 12px; letter-spacing: .08em; text-transform: uppercase; }
      pre {
        background: #11100e; color: #f8efe1; padding: 14px; border-radius: 14px; overflow-x: auto;
        white-space: pre-wrap;
      }
      .math-display {
        border: 1px solid var(--line);
        border-radius: 16px;
        background: white;
        padding: 14px 16px;
        margin: 12px 0;
        overflow-x: auto;
      }
      .math-display .katex-display { margin: 0; text-align: left; overflow-x: auto; overflow-y: hidden; }
      .step-list { counter-reset: item; padding-left: 0; list-style: none; }
      .step-list li { counter-increment: item; border: 1px solid var(--line); border-radius: 14px; background: var(--panel); padding: 12px 14px; margin: 10px 0; }
      .step-list li::before { content: counter(item, decimal-leading-zero) " "; font: 800 12px "Cascadia Mono", monospace; color: var(--muted); margin-right: 8px; }
      .small { color: var(--muted); font-size: 13px; }
      @media (max-width: 760px) {
        main { padding: 14px 10px 42px; }
        header { border-radius: 18px; }
        .grid { grid-template-columns: 1fr; }
        summary { font-size: 18px; padding: 14px; }
        .section-body { padding: 14px; }
        table, thead, tbody, th, td, tr { display: block; }
        th { display: none; }
        td { border-top: 0; }
        td::before { content: attr(data-label); display: block; font: 800 11px "Cascadia Mono", monospace; color: var(--muted); text-transform: uppercase; }
      }
    </style>
  </head>
  <body>
    <main>
      <header>
        <p class="mono small">NDIM ENGINE MANUAL</p>
        <h1>Narrative Diffusion and Inoculation Model</h1>
        <p>NDIM is a local-first research and policy workbench for turning governed narrative evidence into transparent encoding, model simulations, uncertainty updates, intervention tests, and a human-reviewed policy brief.</p>
        <div class="top-links">
          <a class="button primary" href="/">Back to tool</a>
          <a class="button" href="#workspaces">Workspaces</a>
          <a class="button" href="#installation">Installation</a>
          <a class="button" href="#stage-tutorial">Workflow tutorial</a>
          <a class="button" href="#stress-test-corpus">Stress-test corpus</a>
          <a class="button" href="#multimodal-roadmap">Multimodal roadmap</a>
        </div>
      </header>

      <nav class="toc" aria-label="Manual sections">
        <a href="#installation">Install and open the local app</a>
        <a href="#workspaces">Workspaces and assistant</a>
        <a href="#tool-map">What the tool does</a>
        <a href="#equations">Scientific equations</a>
        <a href="#stage-tutorial">Stage-by-stage tutorial</a>
        <a href="#stress-test-corpus">Stress-test exercises</a>
        <a href="#interpretation">How to interpret results</a>
        <a href="#exports">Outputs and exports</a>
        <a href="#multimodal-roadmap">Speech, translation, and multimodal roadmap</a>
      </nav>

      <details id="installation" open>
        <summary><span class="num">01</span>Accessing NDIM Engine</summary>
        <div class="section-body">
          <p>The packaged desktop app is intended to run locally on Windows, Linux, and macOS. The user opens NDIM Engine, the local backend starts on a localhost port, and the browser UI opens without sending private evidence to a public server by default.</p>
          <ol class="step-list">
            <li>Install NDIM Engine using the installer or platform bundle supplied by the project maintainer.</li>
            <li>Open NDIM Engine from the Start menu, application launcher, or desktop shortcut.</li>
            <li>Wait for the local status screen to show the backend URL, usually <code>http://127.0.0.1:8010/</code> or a nearby port.</li>
            <li>Use <strong>Open NDIM Engine</strong> to enter the workflow. Use <strong>Open data folder</strong> only when you need logs, local exports, or support files.</li>
            <li>If the backend fails, use <strong>Export support bundle</strong> and send the ZIP to the maintainer. The bundle should not be published publicly if it contains sensitive evidence.</li>
          </ol>
          <div class="callout warning">
            <strong>Policy caution.</strong>
            <p>Local-first does not mean automatically private. Consent, visibility, reviewer decisions, and repository sync settings still determine whether a record can leave the local machine.</p>
          </div>
        </div>
      </details>

      <details id="workspaces" open>
        <summary><span class="num">02</span>Workspaces and the research assistant</summary>
        <div class="section-body">
          <p>The opening screen is workspace-first. A workspace is the project container that carries the country context, evidence routes, field templates, encoding assumptions, model defaults, repository behavior, stress-test material, and export rules for a study.</p>
          <ol class="step-list">
            <li>Use the workspace launchpad at the top of the tool to see which project is active.</li>
            <li>Choose an existing workspace, create a new one, duplicate a previous project, or import a workspace package from another computer.</li>
            <li>Use template-only export when sharing a project structure without sensitive narratives. Use full backup only when the recipient is authorized to see the evidence.</li>
            <li>Open the Research Assistant when a user needs plain-language guidance. It reads the current workflow state, shows completed and waiting tasks, and recommends the next action.</li>
          </ol>
          <div class="callout">
            <strong>What the assistant is and is not.</strong>
            <p>The assistant is a state-aware workflow guide. It does not replace a scientist, reviewer, or policy decision maker. It explains progress, cautions the user when evidence is thin, and helps non-specialists understand what to do next.</p>
          </div>
        </div>
      </details>

      <details id="tool-map" open>
        <summary><span class="num">03</span>What NDIM does</summary>
        <div class="section-body">
          <div class="grid">
            <div class="card"><h3>For researchers</h3><p>NDIM preserves provenance, supports manual and LLM-assisted encoding, displays equations, tracks uncertainty, and keeps an audit trail from raw narrative to policy brief.</p></div>
            <div class="card"><h3>For policy makers</h3><p>NDIM summarizes evidence quality, risks, intervention options, model confidence, regional differences, and required human review in plain language.</p></div>
            <div class="card"><h3>For guided users</h3><p>Follow the stages from top to bottom. Each stage explains what it needs, what it creates, and why the next stage depends on it.</p></div>
            <div class="card"><h3>For advanced users</h3><p>Inspect SDMX metadata, hashes, encoder agreement, priors and posteriors, scenario bands, RL rewards, and exportable audit payloads.</p></div>
          </div>
          <p>The core story is: collect evidence -> validate evidence -> commit to repository -> encode narratives -> simulate diffusion -> test local agents -> update the digital twin -> update uncertainty -> optimize interventions -> test inoculation narratives -> export a decision brief.</p>
        </div>
      </details>

      <details id="equations">
        <summary><span class="num">04</span>Scientific equations used by the tool</summary>
        <div class="section-body">
          <h3>Encoding score</h3>
          <p>Manual and heuristic encoding convert narrative features into a model-ready signal. In production, LLM-assisted scores should be calibrated against double-coded human validation data.</p>
          <div class="math-display">\Phi_i = 0.30E_i + 0.30C_i + 0.20\tau_i + 0.20\kappa_i</div>
          <p>Here, <code>E</code> is exposure or salience, <code>C</code> is credibility/local grounding, <code>tau</code> is trust signal, and <code>kappa</code> is barrier or friction signal. The UI should explain the scoring rule before a researcher enters manual scores.</p>

          <h3>Population compartments</h3>
          <p>The documented NDIM model uses S/M/T/I/R compartments: susceptible, misinformation-exposed, truth-aligned, inoculated, and resistant/adopted.</p>
          <div class="math-display">\begin{aligned}
\frac{dS}{dt} &= -\beta_mSM - \beta_tST - \iota S \\
\frac{dM}{dt} &= \beta_mSM - \rho M - \mu M \\
\frac{dT}{dt} &= \beta_tST + \rho M - \eta T \\
\frac{dI}{dt} &= \iota S + \eta T - \gamma I \\
\frac{dR}{dt} &= \gamma I + \mu M
\end{aligned}</div>
          <p>If the deployed backend uses a simpler curve for speed or fallback, the UI labels it as a prototype adoption curve rather than pretending it is the full NDIM system.</p>

          <h3>Digital twin feedback</h3>
          <div class="math-display">\theta_{t+1} = \theta_t + \lambda(y_{observed} - y_{predicted})</div>
          <p>The twin is a feedback-calibrated analytic copy of the intervention system. It receives approved evidence, encoded narratives, model outputs, field observations, posterior values, RL recommendations, and inoculation-lab interventions.</p>

          <h3>Bayesian update</h3>
          <div class="math-display">\begin{aligned}
prior &= Beta(\alpha,\beta) \\
posterior &= Beta(\alpha + successes,\beta + failures)
\end{aligned}</div>
          <p>The posterior is not "truth". It is the model's updated uncertainty after evidence and assumptions are made explicit.</p>

          <h3>RL optimizer</h3>
          <div class="math-display">Q(s,a) \leftarrow Q(s,a) + \alpha \left[r + \gamma \max_{a'}Q(s',a') - Q(s,a)\right]</div>
          <p>The RL reward ranks candidate policy packages. It should shortlist options for human review, not automatically decide policy.</p>
        </div>
      </details>

      <details id="stage-tutorial" open>
        <summary><span class="num">04</span>Workflow tutorial from intake to policy output</summary>
        <div class="section-body">
          <h3>Stage 01. Narrative intake</h3>
          <ol class="step-list">
            <li>Select the evidence route: structured interview, open story, indigenous knowledge, citizen science, crowdsourced batch, or social media feed.</li>
            <li>Choose country and administrative units. Rwanda, Kenya, Uganda, Tanzania, and Ghana use different admin labels; the form adapts to the country.</li>
            <li>Use <strong>Open text or CSV file</strong> only after the route and location make sense. For a single story, open the bonus text file or paste a paragraph. For batch testing, use one CSV at a time.</li>
            <li>Review consent, visibility, source, period, language, and route-specific metadata before staging.</li>
            <li>Read <strong>SDMX readiness and record preview</strong> immediately after the narrative body. The stage should show route, place, source, consent, visibility, and whether the record is ready.</li>
          </ol>

          <h3>Stage 02. SDMX gate and approval</h3>
          <ol class="step-list">
            <li>Stage the record only if the readiness panel is complete.</li>
            <li>Review the approval queue. Use <strong>Approve</strong> when the record is suitable for modelling; use <strong>Reject</strong> when consent, quality, duplication, or injection risk is unacceptable.</li>
            <li>Click <strong>Commit reviewed records</strong>. Approved records move to the Accepted repository; rejected records move to the Rejected repository.</li>
            <li>Use <strong>Uncommit</strong> only inside a repository record if it needs to return to review.</li>
          </ol>

          <h3>Stage 03. Encoding</h3>
          <p>Encoding turns narratives into variables used by the model. Use manual scoring for transparent human review, AI encoding when a user-supplied LLM key is configured, or hybrid mode when AI suggestions require human confirmation.</p>
          <table>
            <thead><tr><th>Variable</th><th>Meaning</th><th>How to score</th></tr></thead>
            <tbody>
              <tr><td data-label="Variable">Trust</td><td data-label="Meaning">Confidence in messenger, technology, institution, or local evidence.</td><td data-label="How to score">Higher when the story names trusted people, direct experience, or reliable local proof.</td></tr>
              <tr><td data-label="Variable">Barrier</td><td data-label="Meaning">Cost, access, safety, habit, repair, fuel, or social friction.</td><td data-label="How to score">Higher when the story makes adoption difficult even if the respondent is interested.</td></tr>
              <tr><td data-label="Variable">Social influence</td><td data-label="Meaning">Peer, family, leader, group, or media pressure.</td><td data-label="How to score">Higher when decisions are shaped by neighbours, elders, WhatsApp groups, radio, or officials.</td></tr>
              <tr><td data-label="Variable">Inoculation opportunity</td><td data-label="Meaning">Presence of misinformation, fear, or vulnerable misunderstanding that can be pre-bunked.</td><td data-label="How to score">Higher when a weak claim plus respectful refutation could reduce future harm.</td></tr>
            </tbody>
          </table>

          <h3>Stage 04. Compartmental model</h3>
          <p>Run the population model to see the aggregate adoption pathway. Read the axis labels: the x-axis is time horizon in days; the y-axis is projected adoption-aligned population share. This is a scenario estimate, not observed adoption.</p>

          <h3>Stage 05. Agent-based model</h3>
          <p>The agent model tests household-level variation. It asks whether peer effects, trust, and barriers make the aggregate curve too optimistic or too cautious. A lower ABM curve means local frictions may be slowing diffusion.</p>

          <h3>Stage 06. Digital twin</h3>
          <p>The digital twin applies field feedback to the model and reruns the scenario. A result such as 95.3% means the model projects that 95.3 of every 100 simulated households are adoption-aligned by the final horizon under the current assumptions. It is not a claim that 95.3% of real households have adopted.</p>

          <h3>Stage 07. Bayesian update</h3>
          <p>The Bayesian stage updates trust and barrier assumptions. Wide uncertainty or thin evidence should trigger "do not use for policy without further review" caution.</p>

          <h3>Stage 08. RL optimizer</h3>
          <p>The optimizer tests intervention packages such as trusted messenger, subsidy/friction reduction, peer demonstration, and inoculation messaging. The best reward is a candidate for review, not a command.</p>

          <h3>Stage 09. Regional analysis</h3>
          <p>Compare regions in isolation or as a group. This helps identify whether one policy should be national, province-specific, district-specific, or community-specific.</p>

          <h3>Stage 10. Knowledge graph</h3>
          <p>Use the graph to study repeated stories from the same location. Nodes show locations, themes, and signals; larger nodes have more connections. The layout is relational, not a map.</p>

          <h3>Stage 11. Inoculation lab</h3>
          <p>Generate counter-narratives from approved risks. Apply the narrative vaccine to compare before, during, and after intervention curves in both the ODE and agent-based model.</p>

          <h3>Stage 12. Policy output</h3>
          <p>Export a human-readable policy brief. It should include confidence level, evidence grade, assumptions, limitations, uncertainty, and required human review. JSON audit export remains available for traceability.</p>
        </div>
      </details>

      <details id="stress-test-corpus">
        <summary><span class="num">05</span>Stress-test corpus and exercises</summary>
        <div class="section-body">
          <p>The stress-test corpus is bundled in the repository folder <code>stress_test_corpus/</code>. It contains realistic synthetic Rwanda clean-cooking narratives for testing ingestion, route-specific metadata, approval, encoding, modelling, and policy output. Do not auto-load these records by default; choose one file during the exercise.</p>
          <table>
            <thead><tr><th>Evidence route</th><th>File</th><th>How to use it</th></tr></thead>
            <tbody>
              <tr><td data-label="Evidence route">Structured interview</td><td data-label="File"><code>ndim_stress_structured_interview_rwanda.csv</code></td><td data-label="How to use it">Select Structured interview, load the CSV, inspect Q1-Q5 responses, then stage and approve a few records.</td></tr>
              <tr><td data-label="Evidence route">Open story</td><td data-label="File"><code>ndim_stress_open_story_rwanda.csv</code></td><td data-label="How to use it">Select Open story, load the CSV, verify the narrative body, and compare manual vs AI/hybrid encoding.</td></tr>
              <tr><td data-label="Evidence route">Indigenous knowledge</td><td data-label="File"><code>ndim_stress_indigenous_knowledge_rwanda.csv</code></td><td data-label="How to use it">Check cultural sensitivity, attribution preference, community validation, and whether the story should be used for policy claims.</td></tr>
              <tr><td data-label="Evidence route">Citizen science</td><td data-label="File"><code>ndim_stress_citizen_science_rwanda.csv</code></td><td data-label="How to use it">Review observation confidence, validation status, place, and time before approving.</td></tr>
              <tr><td data-label="Evidence route">Crowdsourced batch</td><td data-label="File"><code>ndim_stress_crowdsourced_batch_rwanda.csv</code></td><td data-label="How to use it">Use this to test queue reduction, approve/reject decisions, commit, and repository filtering.</td></tr>
              <tr><td data-label="Evidence route">Social media feed</td><td data-label="File"><code>ndim_stress_experimental_feed_rwanda.csv</code></td><td data-label="How to use it">Select Social media feeds, tick the platforms represented in the file, and keep it experimental until governance is satisfied.</td></tr>
              <tr><td data-label="Evidence route">Bonus single story</td><td data-label="File"><code>ndim_stress_bonus_open_story_kamegeri.txt</code></td><td data-label="How to use it">Use this to test single-story manual loading and one-record encoding.</td></tr>
            </tbody>
          </table>
          <h3>Full exercise path</h3>
          <ol class="step-list">
            <li>Open the tool, choose one evidence route, and use <strong>Open text or CSV file</strong> to load the matching file from <code>stress_test_corpus/</code>.</li>
            <li>Confirm country, province, district, sector, source, language, period, consent, and visibility.</li>
            <li>Read SDMX readiness. If anything is missing, correct it before staging.</li>
            <li>Stage records, approve or reject them, then commit reviewed records so the queue visibly changes.</li>
            <li>Open the full repository and confirm accepted and rejected records are stored in the correct place.</li>
            <li>Encode at least three records using manual, AI/heuristic, and hybrid modes. Compare whether high-barrier and high-trust stories receive different scores.</li>
            <li>Run compartmental and agent-based models. Read the x-axis and y-axis labels before interpreting the curves.</li>
            <li>Run the digital twin with a field observation. Compare baseline and feedback-adjusted curves.</li>
            <li>Run Bayesian update and check whether uncertainty is still too high for policy use.</li>
            <li>Run RL optimizer and compare the best intervention with regional analysis and knowledge graph themes.</li>
            <li>Generate inoculation messages, apply the narrative vaccine, and compare before, during, and after curves.</li>
            <li>Export the policy brief as HTML or print-friendly PDF and review assumptions, limitations, confidence, and required human review.</li>
          </ol>
        </div>
      </details>

      <details id="interpretation">
        <summary><span class="num">06</span>How to interpret results scientifically</summary>
        <div class="section-body">
          <div class="callout">
            <strong>What percentages mean.</strong>
            <p>A model endpoint such as 95.3% means the projected adoption-aligned share of the simulated population at the final time horizon. It does not mean that 95.3% of real households have adopted. Use it to compare scenarios, not as a direct monitoring statistic.</p>
          </div>
          <table>
            <thead><tr><th>Output</th><th>Interpretation</th><th>Policy caution</th></tr></thead>
            <tbody>
              <tr><td data-label="Output">ODE curve</td><td data-label="Interpretation">Population-level trajectory under the compartment equations.</td><td data-label="Policy caution">May hide local network and household variation.</td></tr>
              <tr><td data-label="Output">Agent curve</td><td data-label="Interpretation">Local heterogeneity and peer diffusion effects.</td><td data-label="Policy caution">Depends strongly on assumptions about trust, peers, and barriers.</td></tr>
              <tr><td data-label="Output">Digital twin</td><td data-label="Interpretation">Feedback-adjusted rerun after observed evidence enters the model.</td><td data-label="Policy caution">Only as good as the observation and calibration rule.</td></tr>
              <tr><td data-label="Output">Posterior</td><td data-label="Interpretation">Updated uncertainty about trust and barriers.</td><td data-label="Policy caution">Sparse evidence should widen caution, not confidence.</td></tr>
              <tr><td data-label="Output">RL reward</td><td data-label="Interpretation">Relative score for candidate interventions.</td><td data-label="Policy caution">Shortlist for review, not automatic decision.</td></tr>
            </tbody>
          </table>
        </div>
      </details>

      <details id="exports">
        <summary><span class="num">07</span>Outputs, repository, and exports</summary>
        <div class="section-body">
          <p>The primary output should be a human-readable decision brief. It should include the evidence route, accepted records, rejected records, hashes, reviewers, consent, visibility, encoding mode, model assumptions, uncertainty, intervention recommendations, limitations, and human-review sign-off.</p>
          <p>Use HTML export for reading in a browser. Use print-to-PDF from the HTML brief when direct browser PDF generation is unavailable. JSON remains an audit export for traceability and federation, not the main policy document.</p>
          <p>For federated repository workflows, local accepted records can be prepared for an SDMX-based push to a master repository such as Google Sheets or another governed store. Before pushing, records should pass approval, consent, visibility, hash sealing, and reviewer validation.</p>
        </div>
      </details>

      <details id="multimodal-roadmap">
        <summary><span class="num">08</span>Multimodal and translation roadmap</summary>
        <div class="section-body">
          <p>This section describes a proposed upgrade path, not a claim that every feature is already implemented.</p>
          <div class="grid">
            <div class="card"><h3>Speech to text</h3><p>Field users could record interviews or community discussions and transcribe them locally before SDMX validation. Transcription should preserve speaker, language, place, date, consent, and confidence.</p></div>
            <div class="card"><h3>Text to speech</h3><p>Policy briefs, field templates, and inoculation messages could be read aloud for accessibility, training, and community review.</p></div>
            <div class="card"><h3>Kinyarwanda-English translation</h3><p>NDIM should support translation in both directions, with translator notes, contested terms, and uncertainty flags. Digital Umuganda or similar language resources could be integrated where licensing and quality allow.</p></div>
            <div class="card"><h3>Multimodal evidence</h3><p>Future evidence routes could include audio, photos of field forms, radio transcripts, WhatsApp summaries, and community meeting recordings, but all should pass consent, provenance, validation, and injection-risk checks before modelling.</p></div>
          </div>
          <div class="callout warning">
            <strong>Governance requirement.</strong>
            <p>Translation and speech models can introduce errors. NDIM should store original text/audio references, translation notes, reviewer identity, and confidence so policy users know what was said, what was translated, and what remains uncertain.</p>
          </div>
        </div>
      </details>
    </main>
    <script>
      function renderManualMath() {
        if (!window.katex) return;
        document.querySelectorAll(".math-display").forEach((node) => {
          if (node.dataset.rendered === "1") return;
          const tex = node.textContent.trim();
          try {
            window.katex.render(tex, node, { displayMode: true, throwOnError: false, strict: "ignore" });
            node.dataset.rendered = "1";
          } catch (error) {
            node.dataset.rendered = "0";
          }
        });
      }
      window.addEventListener("load", renderManualMath);
      if (window.location.hash) {
        window.addEventListener("load", () => {
          const target = document.querySelector(window.location.hash);
          if (target && target.tagName.toLowerCase() === "details") target.open = true;
        });
      }
    </script>
  </body>
</html>
"""
