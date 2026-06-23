"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { fetchContent, type ContentOut } from "@/lib/api";

export default function ContentDrawer({
  slug,
  onClose,
}: {
  slug: string | null;
  onClose: () => void;
}) {
  const [content, setContent] = useState<ContentOut | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!slug) return;
    setLoading(true);
    setContent(null);
    fetchContent(slug)
      .then(setContent)
      .catch(() => setContent(null))
      .finally(() => setLoading(false));
  }, [slug]);

  if (!slug) return null;

  return (
    <div className="absolute inset-0 z-20 flex justify-end">
      <div className="flex-1 bg-black/20" onClick={onClose} />
      <aside className="flex h-full w-full max-w-xl flex-col bg-white shadow-2xl">
        <div className="flex items-center justify-between border-b border-slate-200 px-5 py-3">
          <h2 className="text-base font-semibold text-slate-800">
            {content?.title ?? "Loading…"}
          </h2>
          <button
            onClick={onClose}
            className="rounded px-2 py-1 text-slate-500 hover:bg-slate-100"
            aria-label="Close"
          >
            ✕
          </button>
        </div>

        <div className="flex-1 overflow-y-auto px-5 py-4">
          {loading && <p className="text-sm text-slate-500">Loading content…</p>}
          {content && (
            <>
              {!content.has_content && (
                <div className="mb-3 rounded bg-amber-50 px-3 py-2 text-xs text-amber-800">
                  This micro-topic is in the syllabus map but its study notes are
                  still being authored.
                </div>
              )}
              {content.summary && (
                <p className="mb-3 text-sm italic text-slate-600">
                  {content.summary}
                </p>
              )}
              <div className="prose-content text-sm text-slate-800">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {content.body_md}
                </ReactMarkdown>
              </div>

              {content.sources.length > 0 && (
                <div className="mt-5 border-t border-slate-200 pt-3">
                  <h3 className="mb-1 text-xs font-semibold uppercase tracking-wide text-slate-500">
                    Sources
                  </h3>
                  <ul className="space-y-1 text-xs">
                    {content.sources.map((s, i) => (
                      <li key={i}>
                        {s.url ? (
                          <a
                            href={s.url}
                            target="_blank"
                            rel="noreferrer"
                            className="text-brand hover:underline"
                          >
                            {s.title}
                          </a>
                        ) : (
                          s.title
                        )}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </>
          )}
        </div>

        <div className="border-t border-slate-200 px-5 py-3">
          <Link
            href={`/topic/${slug}`}
            className="text-sm font-medium text-brand hover:underline"
          >
            Open full page →
          </Link>
        </div>
      </aside>
    </div>
  );
}
