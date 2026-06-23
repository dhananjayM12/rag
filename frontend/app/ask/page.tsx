"use client";

import { useState } from "react";
import Link from "next/link";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { postAsk, type AskResponse } from "@/lib/api";

const examples = [
  "What are the classical dances of India?",
  "Explain the fundamental rights in the Constitution",
  "How does the Indian monsoon work?",
];

export default function AskPage() {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState<AskResponse | null>(null);
  const [loading, setLoading] = useState(false);

  const ask = async (q: string) => {
    if (!q.trim()) return;
    setQuestion(q);
    setLoading(true);
    try {
      setResult(await postAsk(q));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-2xl px-4 py-12">
      <h1 className="text-2xl font-bold text-slate-900">Ask AI</h1>
      <p className="mt-2 text-slate-600">
        Answers are retrieved from the indexed official-source notes and shown
        with citations. Runs fully locally — no external API.
      </p>

      <div className="mt-6 flex gap-2">
        <input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && ask(question)}
          placeholder="e.g. What is the significance of the Preamble?"
          className="flex-1 rounded-lg border border-slate-300 px-4 py-2 focus:border-brand focus:outline-none"
        />
        <button
          onClick={() => ask(question)}
          disabled={loading}
          className="rounded-lg bg-brand px-5 py-2 font-semibold text-white hover:bg-brand-dark disabled:opacity-60"
        >
          {loading ? "…" : "Ask"}
        </button>
      </div>

      <div className="mt-3 flex flex-wrap gap-2">
        {examples.map((ex) => (
          <button
            key={ex}
            onClick={() => ask(ex)}
            className="rounded-full border border-slate-200 bg-white px-3 py-1 text-xs text-slate-600 hover:border-brand hover:text-brand"
          >
            {ex}
          </button>
        ))}
      </div>

      {result && (
        <div className="mt-6 space-y-4">
          <div className="rounded-lg border border-slate-200 bg-white p-5">
            <div className="prose-content text-sm text-slate-800">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {result.answer}
              </ReactMarkdown>
            </div>
          </div>

          {result.related.length > 0 && (
            <div>
              <h2 className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">
                Related topics
              </h2>
              <div className="flex flex-wrap gap-2">
                {result.related.map((r) => (
                  <Link
                    key={r.slug}
                    href={`/topic/${r.slug}`}
                    className="rounded-full bg-blue-50 px-3 py-1 text-xs font-medium text-brand hover:bg-blue-100"
                  >
                    {r.title}
                  </Link>
                ))}
              </div>
            </div>
          )}

          {result.citations.length > 0 && (
            <div>
              <h2 className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">
                Sources
              </h2>
              <ul className="space-y-1 text-xs">
                {result.citations.map((s, i) => (
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
        </div>
      )}
    </div>
  );
}
