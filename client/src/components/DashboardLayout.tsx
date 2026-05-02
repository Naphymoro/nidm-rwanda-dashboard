import React, { createContext, useContext, useState } from "react";
import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";

// ââ Mode Context âââââââââââââââââââââââââââââââââââââââââââââââââ
export type Mode = "novice" | "policy" | "expert";
const ModeContext = createContext<{ mode: Mode; setMode: (m: Mode) => void }>({
  mode: "novice",
  setMode: () => {},
});
export const useMode = () => useContext(ModeContext);

// ââ Tab interface âââââââââââââââââââââââââââââââââââââââââââââââââ
export interface Tab {
  id: string;
  label: string;
  icon: React.ReactNode;
}

// ââ Page metadata ââââââââââââââââââââââââââââââââââââââââââââââââ
const PAGE_META: Record<string, { title: string; sub: string }> = {
  dashboard:   { title: "Mission Control",      sub: "AR7 Authorship Cycle â Rwanda Clean Cooking Â· NIDM" },
  narratives:  { title: "Narrative Library",    sub: "Encode Â· Score Â· Design narratives for diffusion" },
  ode:         { title: "ODE System",           sub: "Compartmental equations Â· Parameter configuration" },
  simulation:  { title: "Simulation",           sub: "Run the NIDM Â· Visualise population trajectories" },
  scenarios:   { title: "Scenario Competition", sub: "Four strategies competing for population belief" },
  sensitivity: { title: "Sensitivity Analysis", sub: "Parameter space exploration Â· Heatmaps" },
  twin:        { title: "Digital Twin",         sub: "Kalman filter state estimation Â· Forward projection" },
  rl:          { title: "RL Optimizer",         sub: "Q-learning agent discovering optimal narrative strategy" },
  analysis:    { title: "Analysis",             sub: "Scenario & sensitivity deep-dive" },
};

// ââ Nav section config ââââââââââââââââââââââââââââââââââââââââââââ
const NAV_SECTIONS = [
  {
    label: "Core",
    items: [
      {
        id: "dashboard",
        label: "Overview",
        sub: "Model summary",
        accentBg: "rgba(59,91,219,.2)",
        accentStroke: "#748FFC",
        icon: (
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
            <rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/>
            <rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>
          </svg>
        ),
      },
      {
        id: "narratives",
        label: "Narratives",
        sub: "Encode Â· Score Â· Design",
        accentBg: "rgba(245,159,0,.15)",
        accentStroke: "#F59F00",
        badge: "CSV",
        icon: (
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
          </svg>
        ),
      },
      {
        id: "ode",
        label: "ODE System",
        sub: "Compartments Â· Equations",
        accentBg: "rgba(116,192,252,.15)",
        accentStroke: "#74C0FC",
        icon: (
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
            <circle cx="8" cy="12" r="3"/><circle cx="16" cy="6" r="3"/><circle cx="16" cy="18" r="3"/>
            <line x1="11" y1="12" x2="13" y2="7.5"/><line x1="11" y1="12" x2="13" y2="16.5"/>
          </svg>
        ),
      },
      {
        id: "simulation",
        label: "Simulation",
        sub: "Run Â· Visualise",
        accentBg: "rgba(32,201,151,.15)",
        accentStroke: "#20C997",
        icon: (
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
            <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
          </svg>
        ),
      },
    ],
  },
  {
    label: "Analysis",
    items: [
      {
        id: "scenarios",
        label: "Scenarios",
        sub: "Strategy competition",
        accentBg: "rgba(151,117,250,.15)",
        accentStroke: "#9775FA",
        icon: (
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
            <line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/>
          </svg>
        ),
      },
      {
        id: "sensitivity",
        label: "Sensitivity",
        sub: "Parameter space",
        accentBg: "rgba(255,107,53,.12)",
        accentStroke: "#FF6B35",
        icon: (
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
            <path d="M9 18 l3-9 3 4 2-4 3 9"/>
            <line x1="3" y1="12" x2="21" y2="12" strokeDasharray="3 2" opacity=".5"/>
          </svg>
        ),
      },
    ],
  },
  {
    label: "Advanced",
    items: [
      {
        id: "twin",
        label: "Digital Twin",
        sub: "Live state estimation",
        accentBg: "rgba(32,201,151,.12)",
        accentStroke: "#20C997",
        badge: "LIVE",
        icon: (
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
            <path d="M12 2a10 10 0 0 0 0 20"/>
            <path d="M12 2a10 10 0 0 1 0 20" strokeDasharray="3 2"/>
            <circle cx="12" cy="12" r="2" fill="#20C997" stroke="none"/>
          </svg>
        ),
      },
      {
        id: "rl",
        label: "RL Optimizer",
        sub: "Narrative discovery",
        accentBg: "rgba(59,91,219,.15)",
        accentStroke: "#748FFC",
        icon: (
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
            <path d="M12 2l4 8h5l-4 5 2 7-7-4-7 4 2-7-4-5h5z"/>
          </svg>
        ),
      },
    ],
  },
];

// ââ Main Component ââââââââââââââââââââââââââââââââââââââââââââââââ
interface DashboardLayoutProps {
  activeTab: string;
  onTabChange: (id: string) => void;
  tabs: Tab[];
  children: React.ReactNode;
}

export default function DashboardLayout({ activeTab, onTabChange, children }: DashboardLayoutProps) {
  const [mode, setMode] = useState<Mode>("novice");
  const meta = PAGE_META[activeTab] || { title: activeTab, sub: "" };

  const handleRunSimulation = () => {
    window.dispatchEvent(new CustomEvent("nidm:run-simulation"));
  };

  return (
    <ModeContext.Provider value={{ mode, setMode }}>
      <SidebarProvider>
        <div className="flex h-screen overflow-hidden" style={{ background: "var(--void)", color: "var(--t1)", fontFamily: "'Space Grotesk', sans-serif" }}>

          {/* ââ DOT GRID BACKGROUND ââ */}
          <div
            className="fixed inset-0 pointer-events-none"
            style={{
              backgroundImage: `
                radial-gradient(ellipse 80% 60% at 20% -10%, rgba(59,91,219,.18) 0%, transparent 60%),
                radial-gradient(ellipse 50% 40% at 80% 110%, rgba(32,201,151,.10) 0%, transparent 55%),
                url("data:image/svg+xml,%3Csvg width='60' height='60' xmlns='http://www.w3.org/2000/svg'%3E%3Cdefs%3E%3Cpattern id='g' width='60' height='60' patternUnits='userSpaceOnUse'%3E%3Ccircle cx='1' cy='1' r='.5' fill='%233B5BDB' opacity='.07'/%3E%3C/pattern%3E%3C/defs%3E%3Crect width='60' height='60' fill='url(%23g)'/%3E%3C/svg%3E")
              `,
              zIndex: 0,
            }}
          />

          {/* ââ SIDEBAR ââ */}
          <aside
            className="relative flex-shrink-0 flex flex-col overflow-hidden"
            style={{
              width: 220,
              minWidth: 220,
              background: "rgba(11,18,48,.95)",
              borderRight: "1px solid var(--bdr)",
              backdropFilter: "blur(20px)",
              zIndex: 10,
            }}
          >
            {/* Brand */}
            <div style={{ padding: "20px 16px 14px", borderBottom: "1px solid var(--bdr)" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 6 }}>
                <div style={{
                  width: 34, height: 34,
                  background: "linear-gradient(135deg, #3B5BDB, #0C8C68)",
                  borderRadius: 9, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0,
                }}>
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                    <circle cx="12" cy="6" r="2" fill="rgba(255,255,255,.9)"/>
                    <circle cx="5" cy="18" r="2" fill="rgba(116,192,252,.8)"/>
                    <circle cx="19" cy="18" r="2" fill="rgba(32,201,151,.8)"/>
                    <line x1="12" y1="8" x2="5" y2="16" stroke="rgba(255,255,255,.4)" strokeWidth="1.2"/>
                    <line x1="12" y1="8" x2="19" y2="16" stroke="rgba(255,255,255,.4)" strokeWidth="1.2"/>
                    <line x1="5" y1="18" x2="19" y2="18" stroke="rgba(255,255,255,.3)" strokeWidth="1" strokeDasharray="2 2"/>
                  </svg>
                </div>
                <span style={{ fontFamily: "'Syne', sans-serif", fontSize: 18, fontWeight: 800, color: "var(--t1)", letterSpacing: "-.3px" }}>
                  NIDM
                </span>
              </div>
              <div style={{ fontSize: 9.5, color: "var(--t3)", fontFamily: "'JetBrains Mono', monospace", letterSpacing: ".8px", textTransform: "uppercase", marginBottom: 10 }}>
                Narrative Inoculation Diffusion
              </div>
              <div style={{ padding: "8px 10px", background: "rgba(59,91,219,.1)", border: "1px solid var(--bdr)", borderRadius: 8, fontSize: 10.5, color: "#748FFC", fontFamily: "'JetBrains Mono', monospace", lineHeight: 1.6 }}>
                Context: <span style={{ color: "#20C997" }}>Rwanda Clean Cooking</span><br/>
                Pop: <span style={{ color: "#20C997" }}>1.2M households</span><br/>
                Horizon: <span style={{ color: "#20C997" }}>52 weeks</span>
              </div>
            </div>

            {/* Nav */}
            <nav style={{ flex: 1, overflowY: "auto", padding: "10px 8px" }}>
              {NAV_SECTIONS.map((section) => (
                <div key={section.label}>
                  <div style={{ fontSize: 9, letterSpacing: "1.5px", textTransform: "uppercase", color: "var(--t4)", fontFamily: "'JetBrains Mono', monospace", padding: "10px 8px 4px" }}>
                    {section.label}
                  </div>
                  {section.items.map((item) => {
                    const isActive = activeTab === item.id;
                    return (
                      <div
                        key={item.id}
                        onClick={() => onTabChange(item.id)}
                        style={{
                          display: "flex", alignItems: "center", gap: 9, padding: "8px 10px",
                          borderRadius: 8, cursor: "pointer", marginBottom: 2,
                          border: `1px solid ${isActive ? "rgba(59,91,219,.35)" : "transparent"}`,
                          background: isActive ? "rgba(59,91,219,.18)" : "transparent",
                          position: "relative", transition: "all .18s",
                        }}
                        onMouseEnter={(e) => { if (!isActive) { (e.currentTarget as HTMLDivElement).style.background = "rgba(59,91,219,.12)"; (e.currentTarget as HTMLDivElement).style.borderColor = "rgba(59,91,219,.18)"; }}}
                        onMouseLeave={(e) => { if (!isActive) { (e.currentTarget as HTMLDivElement).style.background = "transparent"; (e.currentTarget as HTMLDivElement).style.borderColor = "transparent"; }}}
                      >
                        {isActive && (
                          <div style={{ position: "absolute", left: 0, top: "50%", transform: "translateY(-50%)", width: 2, height: 16, background: "#748FFC", borderRadius: "0 2px 2px 0" }}/>
                        )}
                        <div style={{ width: 30, height: 30, borderRadius: 7, background: item.accentBg, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0, color: item.accentStroke, transition: "all .18s", ...(isActive ? { boxShadow: `0 0 12px ${item.accentBg}` } : {}) }}>
                          {item.icon}
                        </div>
                        <div style={{ flex: 1, minWidth: 0 }}>
                          <div style={{ fontSize: 12.5, fontWeight: 500, color: isActive ? "#748FFC" : "rgba(232,236,247,.65)", lineHeight: 1.3 }}>
                            {item.label}
                          </div>
                          <div style={{ fontSize: 10, color: "var(--t4)", fontFamily: "'JetBrains Mono', monospace", marginTop: 1 }}>
                            {item.sub}
                          </div>
                        </div>
                        {"badge" in item && item.badge && (
                          <div style={{ fontSize: 9.5, padding: "1px 7px", borderRadius: 8, background: "rgba(245,159,0,.2)", color: "#FFD43B", border: "1px solid rgba(245,159,0,.3)", fontFamily: "'JetBrains Mono', monospace", fontWeight: 600, flexShrink: 0 }}>
                            {item.badge}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              ))}
            </nav>

            {/* Mode toggle + footer */}
            <div style={{ padding: "12px 10px", borderTop: "1px solid var(--bdr)" }}>
              <div style={{ background: "var(--well)", border: "1px solid var(--bdr)", borderRadius: 9, display: "flex", padding: 3, marginBottom: 10 }}>
                {(["novice", "policy", "expert"] as Mode[]).map((m) => (
                  <div
                    key={m}
                    onClick={() => setMode(m)}
                    style={{
                      flex: 1, padding: "5px 4px", borderRadius: 6, fontSize: 10.5, textAlign: "center",
                      cursor: "pointer", fontFamily: "'JetBrains Mono', monospace",
                      color: mode === m ? "#748FFC" : "var(--t3)",
                      background: mode === m ? "var(--card)" : "transparent",
                      fontWeight: mode === m ? 600 : 400,
                      transition: "all .15s",
                    }}
                  >
                    {m.charAt(0).toUpperCase() + m.slice(1)}
                  </div>
                ))}
              </div>
              <a
                href="https://nidm-rwanda-dashboard-one.vercel.app"
                target="_blank"
                rel="noopener noreferrer"
                style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 10.5, color: "var(--t4)", fontFamily: "'JetBrains Mono', monospace", textDecoration: "none", padding: "4px 8px" }}
              >
                <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><circle cx="12" cy="12" r="9"/><path d="M2 12h20"/><path d="M12 2a15 15 0 0 1 0 20M12 2a15 15 0 0 0 0 20"/></svg>
                <span style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>Live deployment â</span>
              </a>
            </div>
          </aside>

          {/* ââ MAIN AREA ââ */}
          <div className="flex flex-col flex-1 overflow-hidden" style={{ position: "relative", zIndex: 1 }}>

            {/* Topbar */}
            <header style={{
              height: 52, minHeight: 52,
              background: "rgba(7,12,31,.92)", backdropFilter: "blur(20px)",
              borderBottom: "1px solid var(--bdr)",
              display: "flex", alignItems: "center", padding: "0 22px", gap: 14,
            }}>
              <SidebarTrigger style={{ color: "var(--t3)", marginRight: 4 }} />
              <div style={{ flex: 1 }}>
                <span style={{ fontFamily: "'Syne', sans-serif", fontSize: 15, fontWeight: 700, color: "var(--t1)" }}>
                  {meta.title}
                </span>
                <span style={{ fontSize: 11, color: "var(--t3)", fontFamily: "'Space Grotesk', sans-serif", marginLeft: 12 }}>
                  {meta.sub}
                </span>
              </div>
              <div style={{ display: "flex", gap: 6 }}>
                <button
                  onClick={handleRunSimulation}
                  style={{
                    display: "inline-flex", alignItems: "center", gap: 6, padding: "6px 14px",
                    borderRadius: 9, fontSize: 13, fontWeight: 600, fontFamily: "'Space Grotesk', sans-serif",
                    cursor: "pointer", border: "none", background: "#3B5BDB", color: "#fff",
                    transition: "all .18s",
                  }}
                  onMouseEnter={(e) => { (e.currentTarget as HTMLButtonElement).style.background = "#748FFC"; (e.currentTarget as HTMLButtonElement).style.transform = "translateY(-1px)"; }}
                  onMouseLeave={(e) => { (e.currentTarget as HTMLButtonElement).style.background = "#3B5BDB"; (e.currentTarget as HTMLButtonElement).style.transform = "none"; }}
                >
                  <svg width="11" height="11" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"/></svg>
                  Run
                </button>
              </div>
            </header>

            {/* Content */}
            <div id="content-area" className="flex-1 overflow-y-auto" style={{ padding: "20px 22px" }}>
              {children}
            </div>
          </div>
        </div>
      </SidebarProvider>
    </ModeContext.Provider>
  );
}
