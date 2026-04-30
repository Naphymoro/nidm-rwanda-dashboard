import './globals.css';
import { Activity, BrainCircuit, Database, FlaskConical, Globe2, Network, Radar, ShieldCheck, UploadCloud } from 'lucide-react';

export const metadata = {
  title: 'NIDM Command',
  description: 'Narrative intelligence and digital twin research platform',
};

const links = [
  { href: '/', label: 'Command', icon: Radar },
  { href: '/ingest', label: 'Ingest', icon: UploadCloud },
  { href: '/encode', label: 'Encode', icon: BrainCircuit },
  { href: '/simulate', label: 'Simulate', icon: Activity },
  { href: '/explorer', label: 'Explorer', icon: Database },
  { href: '/evaluate', label: 'Evaluate', icon: ShieldCheck },
];

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="app-shell">
          <aside className="side-rail">
            <div className="brand-block">
              <div className="brand-mark"><Network size={20} /></div>
              <div>
                <strong>NIDM</strong>
                <span>Research OS</span>
              </div>
            </div>
            <nav className="nav-stack">
              {links.map(({ href, label, icon: Icon }) => (
                <a href={href} key={href}><Icon size={17} /> {label}</a>
              ))}
            </nav>
            <div className="rail-footer">
              <Globe2 size={16} />
              <span>RW · KE · NG</span>
            </div>
          </aside>
          <section className="app-content">
            <header className="top-bar">
              <div><FlaskConical size={16} /> Narrative Twin Lab</div>
              <span className="status-chip">Live system</span>
            </header>
            {children}
          </section>
        </div>
      </body>
    </html>
  );
}
