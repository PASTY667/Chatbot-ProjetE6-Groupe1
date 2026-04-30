import Link from 'next/link';

export default function AdminLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <div className="app-layout">
      <nav className="sidebar">
        <Link href="/">Franklin</Link>
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
