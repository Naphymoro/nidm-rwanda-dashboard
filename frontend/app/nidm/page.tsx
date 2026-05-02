"use client";

import { useMemo, useState } from "react";

const sections = [
  { id: "overview", label: "Overview", sub: "Model summary" },
  { id: "narratives", label: "Narratives", sub: "Encode · Score · Design" },
  { id: "model", label: "ODE System", sub: "Compartments · Equations" },
  { id: "simulation", label: "Simulation", sub: "Run · Visualise" },
  { id: "scenarios", label: "Scenarios", sub: "Strategy competition" },
  { id: "sensitivity", label: "Sensitivity", sub: "Parameter space" },
  { id: "twin", label: "Digital Twin", sub: "Live state estimation" },
  { id: "rl", label: "RL Optimizer", sub: "Narrative discovery" },
] as const;

type Section = (typeof sections)[number]["id"];

type State = { S: number; M: number; T: number; I: number; R: number };

const narratives = [
  { type: "truth", title: "The Smoke That Took My Mother", quote: "Every morning my mother stood over that three-stone fire. By the time I was twelve, she coughed more than she spoke.", E: .95, C: .78, tau: .82, kappa: .88 },
  { type: "inoculation", title: "We Tried It First", quote: "Our cooperative in Musanze switched first. Neighbours laughed until they saw our energy bills.", E: .72, C: .91, tau: .88, kappa: .75 },
  { type: "misinfo", title: "What If the Gas Explodes?", quote: "My cousin's friend had a cylinder burst. These companies just want your money.", E: .88, C: .65, tau: .45, kappa: .71 },
  { type: "truth", title: "Clean Air, Healthy Children", quote: "After switching, my youngest stopped getting chest infections. The district nurse confirmed the link.", E: .81, C: .84, tau: .79, kappa: .76 },
];

function clamp(value: number) { return Math.max(0, Math.min(1, value)); }
function pct(value: number) { return `${(value * 100).toFixed(1)}%`; }
function phi(n: { E: number; C: number; tau: number; kappa: number }) { return .3 * n.E + .3 * n.C + .2 * n.tau + .2 * n.kappa; }

function simulate(betaTruth: number, betaMisinfo: number, inoculation: number, weeks = 52) {
  let S = .65, M = .15, T = .12, I = .05, R = .03;
  const rows: State[] = [];
  for (let week = 0; week <= weeks; week++) {
    rows.push({ S, M, T, I, R });
    const dS = .01 * (1 - S) - betaMisinfo * 1.35 * S * M - betaTruth * 1.74 * S * T;
    const dM = betaMisinfo * 1.35 * S * M - (inoculation + .05 + .01) * M;
    const dT = betaTruth * 1.74 * S * T - (inoculation + .04 + .01) * T;
    const dI = inoculation * (M + T) - (.12 + .01) * I;
    const dR = .12 * I - .01 * R;
    S = clamp(S + dS);
    M = clamp(M + dM);
    T = clamp(T + dT);
    I = clamp(I + dI);
    R = clamp(R + dR);
    const total = S + M + T + I + R;
    S /= total; M /= total; T /= total; I /= total; R /= total;
  }
  return rows;
}

function linePath(rows: State[], key: keyof State) {
  const w = 760;
  const h = 260;
  return rows.map((row, index) => {
    const x = (index / Math.max(1, rows.length - 1)) * w;
    const y = h - row[key] * h;
    return `${index === 0 ? "M" : "L"}${x.toFixed(1)},${y.toFixed(1)}`;
  }).join(" ");
}

export default function NIDMPage() {
  const [section, setSection] = useState<Section>("overview");
  const [mode, setMode] = useState("Novice");
  const [betaTruth, setBetaTruth] = useState(.22);
  const [betaMisinfo, setBetaMisinfo] = useState(.18);
  const [inoculation, setInoculation] = useState(.08);
  const [selectedNarrative, setSelectedNarrative] = useState(0);

  const rows = useMemo(() => simulate(betaTruth, betaMisinfo, inoculation), [betaTruth, betaMisinfo, inoculation]);
  const last = rows.at(-1)!;
  const selected = narratives[selectedNarrative];
  const selectedPhi = phi(selected);
  const rt = betaTruth * 1.74 / (inoculation + .04 + .01);
  const rm = betaMisinfo * 1.35 / (inoculation + .05 + .01);

  return (
    <main className="nidm-shell">
      <aside className="sb">
        <div className="brand">
          <div className="logo">N</div>
          <div>
            <strong>NIDM</strong>
            <span>Narrative Inoculation Diffusion Model</span>
          </div>
        </div>
        <div className="context">
          Context: <b>Rwanda Clean Cooking</b><br />
          Population: <b>1.2M households</b><br />
          Horizon: <b>52 weeks</b>
        </div>
        <nav>
          <p>Core</p>
          {sections.slice(0, 4).map((item) => <NavItem key={item.id} item={item} active={section === item.id} onClick={() => setSection(item.id)} />)}
          <p>Analysis</p>
          {sections.slice(4, 6).map((item) => <NavItem key={item.id} item={item} active={section === item.id} onClick={() => setSection(item.id)} />)}
          <p>Advanced</p>
          {sections.slice(6).map((item) => <NavItem key={item.id} item={item} active={section === item.id} onClick={() => setSection(item.id)} />)}
        </nav>
        <div className="mode">
          {["Novice", "Policy", "Expert"].map((m) => <button key={m} className={mode === m ? "on" : ""} onClick={() => setMode(m)}>{m}</button>)}
        </div>
      </aside>

      <section className="main">
        <header className="topbar">
          <div>
            <strong>{titleFor(section)}</strong>
            <span> Rwanda Clean Cooking · Scientific Mission Control</span>
          </div>
          <div className="pills"><button>Run</button><button className="on">Weekly</button><button>Export</button></div>
        </header>

        <section className="content">
          {section === "overview" && <Overview rows={rows} last={last} rt={rt} rm={rm} selectedPhi={selectedPhi} mode={mode} />}
          {section === "narratives" && <Narratives selected={selectedNarrative} setSelected={setSelectedNarrative} />}
          {section === "model" && <Model betaTruth={betaTruth} setBetaTruth={setBetaTruth} betaMisinfo={betaMisinfo} setBetaMisinfo={setBetaMisinfo} inoculation={inoculation} setInoculation={setInoculation} />}
          {section === "simulation" && <Simulation rows={rows} betaTruth={betaTruth} betaMisinfo={betaMisinfo} inoculation={inoculation} />}
          {section === "scenarios" && <Scenarios />}
          {section === "sensitivity" && <Sensitivity />}
          {section === "twin" && <Twin last={last} />}
          {section === "rl" && <RL />}
        </section>
      </section>

      <style jsx>{`
        .nidm-shell{--void:#04060F;--deep:#070C1F;--well:#0B1230;--card:#0F1840;--rim:#162052;--indigo:#3B5BDB;--indigoL:#748FFC;--verdant:#20C997;--flame:#FF6B35;--gold:#F59F00;--violet:#9775FA;--sky:#74C0FC;--t1:#E8ECF7;--t2:rgba(232,236,247,.65);--t3:rgba(232,236,247,.38);--bdr:rgba(59,91,219,.18);display:flex;height:100vh;overflow:hidden;background:radial-gradient(ellipse 80% 60% at 20% -10%,rgba(59,91,219,.18),transparent 60%),radial-gradient(ellipse 50% 40% at 80% 110%,rgba(32,201,151,.10),transparent 55%),var(--void);color:var(--t1);font-family:"Space Grotesk",Inter,system-ui,sans-serif}
        .sb{width:245px;min-width:245px;background:rgba(11,18,48,.94);border-right:1px solid var(--bdr);display:flex;flex-direction:column;overflow:hidden;backdrop-filter:blur(20px)}
        .brand{display:flex;gap:10px;align-items:center;padding:20px 16px 10px}.logo{width:36px;height:36px;border-radius:10px;background:linear-gradient(135deg,var(--indigo),#0C8C68);display:grid;place-items:center;font-weight:900}.brand strong{display:block;font-family:Syne,Inter,sans-serif;font-size:20px}.brand span{display:block;color:var(--t3);font:9px monospace;text-transform:uppercase;letter-spacing:.8px}.context{margin:0 14px 10px;padding:9px 10px;border:1px solid var(--bdr);border-radius:9px;background:rgba(59,91,219,.1);color:var(--indigoL);font:11px monospace;line-height:1.7}.context b{color:var(--verdant);font-weight:500}
        nav{padding:8px;overflow:auto;flex:1}nav p{font:9px monospace;color:var(--t3);letter-spacing:1.5px;text-transform:uppercase;margin:12px 8px 6px}.navItem{width:100%;display:flex;gap:10px;align-items:center;text-align:left;padding:9px 10px;border:1px solid transparent;border-radius:9px;background:transparent;color:var(--t2);cursor:pointer;transition:.18s}.navItem:hover,.navItem.active{background:rgba(59,91,219,.16);border-color:rgba(59,91,219,.35)}.navIcon{width:28px;height:28px;border-radius:7px;background:rgba(59,91,219,.18);display:grid;place-items:center;color:var(--indigoL);font-weight:900}.navItem b{display:block;font-size:13px}.navItem span{font:10px monospace;color:var(--t3)}.mode{display:flex;gap:3px;padding:12px;border-top:1px solid var(--bdr)}.mode button{flex:1;padding:6px;border-radius:7px;border:1px solid var(--bdr);background:var(--well);color:var(--t3);font:10px monospace}.mode button.on{background:var(--card);color:var(--indigoL)}
        .main{flex:1;min-width:0;display:flex;flex-direction:column}.topbar{height:54px;display:flex;align-items:center;justify-content:space-between;padding:0 24px;border-bottom:1px solid var(--bdr);background:rgba(7,12,31,.92);backdrop-filter:blur(20px)}.topbar strong{font-family:Syne,Inter,sans-serif}.topbar span{color:var(--t3);font-size:12px;margin-left:10px}.pills{display:flex;gap:7px}.pills button,.btn{border:1px solid var(--bdr);border-radius:999px;background:transparent;color:var(--t2);padding:6px 12px;font:12px monospace;cursor:pointer}.pills .on,.btn.primary{background:rgba(59,91,219,.2);border-color:var(--indigoL);color:var(--indigoL)}.content{flex:1;overflow:auto;padding:20px 24px}.grid4{display:grid;grid-template-columns:repeat(4,1fr);gap:13px}.grid2{display:grid;grid-template-columns:2fr 1fr;gap:16px}.grid3{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}.card,.stat{background:var(--card);border:1px solid var(--bdr);border-radius:16px;padding:18px 20px;position:relative;overflow:hidden}.card:before,.stat:before{content:"";position:absolute;left:0;right:0;top:0;height:1px;background:linear-gradient(90deg,transparent,rgba(59,91,219,.48),transparent)}.stat{transition:.2s}.stat:hover{transform:translateY(-2px);border-color:rgba(59,91,219,.42)}.stat small,.cardSub{color:var(--t3);font:11px monospace;text-transform:uppercase;letter-spacing:.8px}.stat strong{display:block;margin:6px 0;font:800 30px Syne,Inter,sans-serif}.green{color:var(--verdant)}.red{color:var(--flame)}.gold{color:var(--gold)}.sky{color:var(--sky)}.violet{color:var(--violet)}h2{margin:0 0 4px;font:800 18px Syne,Inter,sans-serif}.mb{margin-bottom:16px}.chartSvg{width:100%;height:300px;background:var(--deep);border:1px solid var(--bdr);border-radius:12px;padding:16px;overflow:visible}.gridline{stroke:rgba(232,236,247,.08);stroke-width:1}.legend{display:flex;gap:12px;flex-wrap:wrap;margin-top:12px;color:var(--t2);font-size:12px}.dot{width:10px;height:10px;border-radius:50%;display:inline-block;margin-right:5px}.explainer{border-left:3px solid var(--indigoL);background:rgba(59,91,219,.08);padding:12px 14px;border-radius:0 9px 9px 0;color:var(--t2);font-size:13px;line-height:1.55}.narrCard{background:var(--well);border:1px solid var(--bdr);border-radius:12px;padding:14px;margin-bottom:10px;cursor:pointer}.narrCard.active{border-color:var(--indigoL);background:rgba(59,91,219,.14)}.tag{display:inline-block;padding:3px 8px;border-radius:999px;font:10px monospace;text-transform:uppercase;margin-bottom:7px}.truth{background:rgba(32,201,151,.14);color:var(--verdant)}.misinfo{background:rgba(255,107,53,.14);color:var(--flame)}.inoculation{background:rgba(245,159,0,.14);color:var(--gold)}.bar{height:5px;background:var(--rim);border-radius:4px;overflow:hidden}.fill{height:100%;border-radius:4px}label{display:block;color:var(--t2);font-weight:700;font-size:13px;margin-bottom:12px}input[type=range]{width:100%;accent-color:var(--indigoL);margin-top:6px}.scenario{background:var(--well);border:1px solid var(--bdr);border-radius:13px;padding:15px}.scenario.active{border-color:var(--indigoL);background:rgba(59,91,219,.12)}.eq{background:var(--deep);border:1px solid var(--bdr);border-radius:10px;padding:14px 16px;font:13px monospace;line-height:2;color:var(--t2);white-space:pre-wrap}.flow{width:100%;height:230px;background:var(--deep);border:1px solid var(--bdr);border-radius:12px}.comp{fill:rgba(59,91,219,.08);stroke-width:2}.compText{font:700 12px monospace;text-anchor:middle}.compVal{font:800 13px Syne;text-anchor:middle}.heat{display:grid;grid-template-columns:repeat(7,1fr);gap:3px}.cell{height:32px;display:grid;place-items:center;border-radius:5px;font:10px monospace;color:white}.rlRow{display:flex;align-items:center;gap:10px;margin-bottom:8px;background:var(--deep);border-radius:8px;padding:9px}.rlBar{flex:1;height:6px;background:var(--rim);border-radius:4px;overflow:hidden}@media(max-width:980px){.nidm-shell{display:block;overflow:auto}.sb{width:100%;height:auto}.main{height:auto}.grid4,.grid2,.grid3{grid-template-columns:1fr}.content{overflow:visible}.topbar{height:auto;padding:14px;display:block}}
      `}</style>
    </main>
  );
}

function NavItem({ item, active, onClick }: { item: { id: Section; label: string; sub: string }; active: boolean; onClick: () => void }) {
  return <button className={`navItem ${active ? "active" : ""}`} onClick={onClick}><span className="navIcon">{item.label[0]}</span><span><b>{item.label}</b><span>{item.sub}</span></span></button>;
}

function titleFor(section: Section) {
  return sections.find((s) => s.id === section)?.label || "NIDM";
}

function Overview({ rows, last, rt, rm, selectedPhi, mode }: { rows: State[]; last: State; rt: number; rm: number; selectedPhi: number; mode: string }) {
  return <>
    <div className="grid4 mb">
      <Stat label="Simulation weeks" value="52" sub="1-year horizon" color="sky" />
      <Stat label="Rm — Misinformation" value={rm.toFixed(2)} sub={rm > 1 ? "Spreading" : "Contained"} color="red" />
      <Stat label="Rt — Truth" value={rt.toFixed(2)} sub={rt > rm ? "Truth wins" : "Needs intervention"} color="green" />
      <Stat label="Φ max narrative" value={selectedPhi.toFixed(2)} sub="Best narrative" color="gold" />
    </div>
    <div className="grid2 mb">
      <div className="card"><h2>Population Compartment Flow</h2><p className="cardSub">SMTIR diffusion system</p><Flow last={last} /><div className="explainer">{mode === "Expert" ? "ODE equilibrium depends on the ratio Φt·βt / Φm·βm and initial conditions." : "The population moves between belief states. Narratives act as transmission vectors and Φ multiplies their spread."}</div></div>
      <div className="card"><h2>Narrative Strength Φ</h2><p className="cardSub">Weighted composite</p><Radar /><div className="explainer">When Rt exceeds Rm, truth narratives outcompete misinformation.</div></div>
    </div>
    <Trajectory rows={rows} title="Population Trajectory — 52-Week Simulation" />
  </>;
}

function Stat({ label, value, sub, color }: { label: string; value: string; sub: string; color: string }) { return <article className="stat"><small>{label}</small><strong className={color}>{value}</strong><span className={color}>{sub}</span></article>; }

function Flow({ last }: { last: State }) {
  return <svg className="flow" viewBox="0 0 540 230">
    <defs><marker id="arr" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto"><path d="M0,0 L8,3 L0,6" fill="#748FFC" /></marker></defs>
    <path d="M130,90 Q175,55 220,90" stroke="#FF6B35" strokeWidth="2" fill="none" markerEnd="url(#arr)" /><path d="M130,140 Q175,170 220,140" stroke="#20C997" strokeWidth="2" fill="none" markerEnd="url(#arr)" /><path d="M260,115 L350,115" stroke="#F59F00" strokeWidth="2" fill="none" markerEnd="url(#arr)" /><path d="M400,115 L465,115" stroke="#9775FA" strokeWidth="2" fill="none" markerEnd="url(#arr)" />
    <Node x={90} y={115} label="S" name="Susceptible" value={pct(last.S)} color="#74C0FC" /><Node x={240} y={90} label="M" name="Misinformed" value={pct(last.M)} color="#FF6B35" /><Node x={240} y={150} label="T" name="Truth" value={pct(last.T)} color="#20C997" /><Node x={380} y={115} label="I" name="Inoculated" value={pct(last.I)} color="#F59F00" /><Node x={500} y={115} label="R" name="Resistant" value={pct(last.R)} color="#9775FA" />
  </svg>;
}
function Node({ x, y, label, name, value, color }: any) { return <g><circle cx={x} cy={y} r="34" fill="rgba(255,255,255,.02)" stroke={color} strokeWidth="2" /><text x={x} y={y - 8} fill={color} className="compText">{label}</text><text x={x} y={y + 6} fill="rgba(232,236,247,.55)" fontSize="9" textAnchor="middle">{name}</text><text x={x} y={y + 21} fill={color} className="compVal">{value}</text></g>; }

function Trajectory({ rows, title }: { rows: State[]; title: string }) {
  const colors: Record<keyof State, string> = { S: "#74C0FC", M: "#FF6B35", T: "#20C997", I: "#F59F00", R: "#9775FA" };
  return <div className="card mb"><h2>{title}</h2><p className="cardSub">Hover-ready scientific trajectory view</p><svg className="chartSvg" viewBox="0 0 760 260" preserveAspectRatio="none">{[0,1,2,3,4].map((i)=><line key={i} x1="0" x2="760" y1={i*65} y2={i*65} className="gridline" />)}{(Object.keys(colors) as (keyof State)[]).map((k)=><path key={k} d={linePath(rows,k)} fill="none" stroke={colors[k]} strokeWidth="3" />)}</svg><div className="legend">{(Object.keys(colors) as (keyof State)[]).map((k)=><span key={k}><i className="dot" style={{background:colors[k]}} />{k}</span>)}</div></div>;
}

function Radar() { return <svg viewBox="-110 -110 220 220" style={{width:"100%",height:210}}><polygon points="0,-85 74,-42 74,42 0,85 -74,42 -74,-42" fill="none" stroke="rgba(232,236,247,.12)"/><polygon points="0,-60 52,-30 52,30 0,60 -52,30 -52,-30" fill="none" stroke="rgba(232,236,247,.09)"/><polygon points="0,-76 65,-35 60,34 0,68 -48,30" fill="rgba(59,91,219,.23)" stroke="#748FFC" strokeWidth="2"/></svg>; }

function Narratives({ selected, setSelected }: { selected: number; setSelected: (n: number) => void }) {
  const n = narratives[selected];
  return <div className="grid2"><div>{narratives.map((item, index)=><article key={item.title} className={`narrCard ${index===selected?"active":""}`} onClick={()=>setSelected(index)}><span className={`tag ${item.type}`}>{item.type}</span><h2>{item.title}</h2><p style={{color:"var(--t2)",fontStyle:"italic"}}>{item.quote}</p><Score label="Φ" value={phi(item)} color="var(--gold)" /></article>)}</div><div className="card"><h2>{n.title}</h2><span className={`tag ${n.type}`}>{n.type}</span><p style={{color:"var(--t2)",lineHeight:1.7,fontStyle:"italic"}}>"{n.quote}"</p><Score label="Emotional" value={n.E} color="var(--flame)"/><Score label="Cultural" value={n.C} color="var(--verdant)"/><Score label="Trust" value={n.tau} color="var(--sky)"/><Score label="Arc" value={n.kappa} color="var(--violet)"/><Score label="Narrative Strength Φ" value={phi(n)} color="var(--gold)"/></div></div>;
}
function Score({ label, value, color }: { label: string; value: number; color: string }) { return <div style={{margin:"10px 0"}}><div style={{display:"flex",justifyContent:"space-between",fontSize:12,color:"var(--t2)"}}><span>{label}</span><b>{value.toFixed(2)}</b></div><div className="bar"><div className="fill" style={{width:`${value*100}%`,background:color}} /></div></div>; }

function Model(props: any) { return <div className="grid2"><div className="card"><h2>NIDM Differential Equations</h2><div className="eq">dS/dt = μ(1-S) - βmΦmSM - βtΦtST{"\n"}dM/dt = βmΦmSM - (ι+γm+μ)M{"\n"}dT/dt = βtΦtST - (ι+γt+μ)T{"\n"}dI/dt = ι(M+T) - (ρ+μ)I{"\n"}dR/dt = ρI - μR{"\n\n"}Φ = wE·E + wC·C + wτ·τ + wκ·κ</div></div><div className="card"><h2>Parameter Configuration</h2><Slider label="βt Truth transmission" value={props.betaTruth} setValue={props.setBetaTruth}/><Slider label="βm Misinfo transmission" value={props.betaMisinfo} setValue={props.setBetaMisinfo}/><Slider label="ι Inoculation" value={props.inoculation} setValue={props.setInoculation}/><div className="explainer">Policy insight: shrink M by deploying high-Φ truth narratives early. Inoculation acts as a firewall.</div></div></div>; }
function Slider({ label, value, setValue }: { label: string; value: number; setValue: (n: number) => void }) { return <label>{label} <b>{value.toFixed(2)}</b><input type="range" min="0.01" max="0.6" step="0.01" value={value} onChange={(e)=>setValue(Number(e.target.value))}/></label>; }
function Simulation({ rows }: any) { return <Trajectory rows={rows} title="Simulation Output" />; }
function Scenarios() { return <><div className="grid4 mb">{[["A","Baseline",.18,.42],["B","Emotional",.34,.28],["C","Inoculation",.29,.18],["D","RL-Optimised",.41,.12]].map((s,i)=><div key={String(s[0])} className={`scenario ${i===3?"active":""}`}><small>Scenario {s[0]}</small><h2>{s[1]}</h2><Score label="Truth" value={Number(s[2])} color="var(--verdant)"/><Score label="Misinfo" value={Number(s[3])} color="var(--flame)"/></div>)}</div><div className="explainer">Policy recommendation: the RL-optimised strategy achieves highest truth adoption and lowest misinformation persistence.</div></>; }
function Sensitivity() { const cells=Array.from({length:49},(_,i)=>.18+(i%7)*.07+Math.floor(i/7)*.03); return <div className="card"><h2>Sensitivity Heatmap — Truth Adoption</h2><p className="cardSub">Final T fraction across parameter space</p><div className="heat">{cells.map((v,i)=><div key={i} className="cell" style={{background:`rgba(${20+i*2},${80+i*3},${130+i},.9)`}}>{Math.min(91,Math.round(v*100))}%</div>)}</div></div>; }
function Twin({ last }: { last: State }) { return <div className="grid2"><div className="card"><h2>Digital Twin — State Estimation</h2><p className="green">● Digital twin active · estimating week 26</p><Score label="Susceptible" value={last.S} color="var(--sky)"/><Score label="Misinformed" value={last.M} color="var(--flame)"/><Score label="Truth" value={last.T} color="var(--verdant)"/><Score label="Inoculated" value={last.I} color="var(--gold)"/></div><div className="card"><h2>6-Week Forward Projection</h2>{[1,2,3,4,5,6].map((w)=><div className="rlRow" key={w}><span>Week {26+w}</span><span className="green">T→{(.22+w*.012).toFixed(3)}</span><span className="red">M→{(.31-w*.009).toFixed(3)}</span></div>)}</div></div>; }
function RL() { return <div className="grid2"><div className="card"><h2>Reinforcement Learning — Narrative Optimizer</h2><p className="cardSub">Q-learning agent discovering optimal narrative strategy</p>{[.12,.19,.23,.31,.37,.44].map((v,i)=><div className="rlRow" key={i}><span>Ep {i*25+25}</span><div className="rlBar"><div className="fill" style={{width:`${v*100}%`,background:"var(--verdant)"}} /></div><b>{v.toFixed(3)}</b></div>)}</div><div className="card"><h2>Optimal Narrative Policy</h2><div className="explainer">Best strategy discovered: deploy high-emotional-salience truth narratives in weeks 1–26, then switch to inoculation narratives in weeks 27–52.</div></div></div>; }
