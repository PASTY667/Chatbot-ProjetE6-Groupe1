import Link from 'next/link';
import './admin-globals.css';
import './admin-variables.css';

export default function AdminLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <div className="app-layout">
      <nav className="sidebar">
        <Link href="/admin">Franklin</Link>
      </nav>
      <main className="main">
        <header className="page-header">
          <h1 className="page-title">Franklin</h1>
        </header>
        {children}
      </main>
    </div>
  );
}
