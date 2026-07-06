import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "MAMET OS",
  description: "Sistem Operasi Kognitif Tiga Kanal",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="id">
      <body className="h-screen bg-[#0a0a0a] text-[#e0e0e0]">
        {children}
      </body>
    </html>
  );
}