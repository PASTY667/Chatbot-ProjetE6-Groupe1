import type { Metadata } from "next";
import { ReactNode } from "react";
import "./globals.css";
import Sidebar from "@/pages/sidebar/sidebar";

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
        <Sidebar />
      </head>
      <body className="layout">
        <main className="content">{children}</main>
      </body>
    </html>
  );
}
