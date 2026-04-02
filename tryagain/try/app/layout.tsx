import type { Metadata } from "next";
import "./globals.css";
import "./variables.css";


export const metadata: Metadata = {
  title: "Franklin | Connexion",
  description: "Page de connexion",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
    >
      <body>{children}</body>
    </html>
  );
}
