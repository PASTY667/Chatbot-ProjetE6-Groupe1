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
            {children}
          </main>
        </div>
      </body>
    </html>
    );
}
