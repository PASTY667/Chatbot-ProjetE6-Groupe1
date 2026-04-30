import type { Metadata } from "next";
import { ReactNode } from "react";
import "./globals.css";
import Sidebar from "@/components/sidebar/sidebar";
import "./variables.css";

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
        <Sidebar />
        <main className="content">{children}</main>
      </body>
    </html>
  );
}

