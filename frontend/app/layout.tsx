import './globals.css';

export const metadata = {
  title: 'NIDM Research Platform',
  description: 'Narrative intelligence and digital twin research platform',
};

const links = [
  ['/', 'Overview'],
  ['/ingest', 'Ingest'],
  ['/encode', 'Encode'],
  ['/simulate', 'Simulate'],
  ['/explorer', 'Explorer'],
  ['/evaluate', 'Evaluate'],
];

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="shell">
          <aside className="sidebar">
            <div className="brand">NIDM</div>
            <nav>
              {links.map(([href, label]) => <a href={href} key={href}>{label}</a>)}
            </nav>
          </aside>
          <main className="content">{children}</main>
        </div>
      </body>
    </html>
  );
}
