import './globals.css';

export const metadata = {
  title: 'NIDM Rwanda Dashboard',
  description: 'Narrative intelligence and digital twin research platform',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="shell">
          <aside className="sidebar">
            <div className="brand">NIDM</div>
            <nav>
              <a href="/">Dashboard</a>
              <a href="/ingest">Ingest</a>
              <a href="/encode">Encode</a>
              <a href="/simulate">Simulate</a>
              <a href="/explorer">Explorer</a>
              <a href="/evaluate">Evaluate</a>
            </nav>
          </aside>
          <section className="content">{children}</section>
        </div>
      </body>
    </html>
  );
}
