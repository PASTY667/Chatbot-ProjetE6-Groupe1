import './globals.css'
import './variables.css'
import Link from 'next/link'

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (<html lang="fr">
    <body>
      <div className="app-layout">
        {/* SIDEBAR */}
        <nav className="sidebar">
          <Link href="/">
            Franklin
          </Link>
        </nav>

        {/* MAIN CONTENT */}
        <main className="main">
          <header className="page-header">
            <h1 className="page-title">Franklin</h1>
          </header>
          {children}
        </main>
      </div>
    </body>
  </html>
  );
}
