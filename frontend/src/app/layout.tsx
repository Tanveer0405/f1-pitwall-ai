import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Veloce — F1 Intelligence",
  description: "Formula 1 AI chatbot. Every driver, race, and championship.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-f1dark min-h-screen antialiased">{children}</body>
    </html>
  );
}