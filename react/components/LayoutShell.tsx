"use client";

import { usePathname } from "next/navigation";
import Sidebar from "@/components/sidebar/sidebar";

type LayoutShellProps = {
  children: React.ReactNode;
};

export default function LayoutShell({ children }: LayoutShellProps) {
  const pathname = usePathname();
  const isAdminRoute = pathname === "/admin" || pathname.startsWith("/admin/");

  if (isAdminRoute) {
    return <>{children}</>;
  }

  return (
    <>
      <Sidebar />
      <main className="content">{children}</main>
    </>
  );
}
