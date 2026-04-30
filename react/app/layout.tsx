import type { Metadata } from "next";
import "./globals.css";
import "./variables.css";
import LayoutShell from "@/components/LayoutShell";

export const metadata: Metadata = {
  title: "Franklin",
  description: "Chatbot souverain",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        <title>Franklin</title>
      </head>
      <body className="layout">
        <LayoutShell>{children}</LayoutShell>
      </body>
    </html>
  );
}
