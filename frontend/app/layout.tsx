import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "PrepPath — UPSC Study App",
  description:
    "Master the UPSC syllabus with an interactive flowchart, AI answer evaluation, and a RAG-powered Q&A grounded in official sources.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <header className="border-b border-slate-200 bg-white">
          <nav className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
            <Link href="/" className="text-lg font-bold text-brand">
              PrepPath
            </Link>
            <div className="flex gap-5 text-sm font-medium text-slate-600">
              <Link href="/flowchart" className="hover:text-brand">
                Syllabus Map
              </Link>
              <Link href="/current-affairs" className="hover:text-brand">
                Current Affairs
              </Link>
              <Link href="/ask" className="hover:text-brand">
                Ask AI
              </Link>
              <Link href="/evaluate" className="hover:text-brand">
                Answer Check
              </Link>
            </div>
          </nav>
        </header>
        <main>{children}</main>
      </body>
    </html>
  );
}
