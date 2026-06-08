import Link from 'next/link';

interface AppCardProps {
  title: string;
  desc: string;
  href: string;
}

export default function AppCard({ title, desc, href }: AppCardProps) {
  return (
    <Link href={href} className="app-card">
      <p className="app-title">{title}</p>
      <p className="app-desc">{desc}</p>
    </Link>
  );
}
