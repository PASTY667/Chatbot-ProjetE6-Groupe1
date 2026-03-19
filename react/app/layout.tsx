import type { Metadata } from "next";
import { ReactNode } from "react";
import "./globals.css";
import Sidebar from "@/components/sidebar";
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
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <link rel="stylesheet" href="./variables.css" />
        <link rel="stylesheet" href="css/style.css" />
        <title>Franklin</title>
      </head>
      <body className="layout">
        <Sidebar />
        <main className="content">{children}</main>
      </body>
    </html>
  );
}
