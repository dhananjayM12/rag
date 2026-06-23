"use client";

import { useState } from "react";
import { postAsk } from "@/lib/api";

export default function AskPage() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const submit = async () => {
    if (!question.trim()) return;
    setLoading(true);
    try {
      const res = await postAsk(question);
      setAnswer(res.answer);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-2xl px-4 py-12">
      <h1 className="text-2xl font-bold text-slate-900">Ask AI</h1>
      <p className="mt-2 text-slate-600">
        Ask any UPSC question. Answers will be grounded in official government
        and UPSC sources, with citations.
      </p>
      <div className="mt-2 inline-block rounded-full bg-amber-100 px-3 py-1 text-xs font-medium text-amber-800">
        Preview — retrieval &amp; generation arrive in the next milestone
      </div>

      <div className="mt-6 flex gap-2">
        <input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && submit()}
          placeholder="e.g. What is the significance of the Preamble?"
          className="flex-1 rounded-lg border border-slate-300 px-4 py-2 focus:border-brand focus:outline-none"
        />
        <button
          onClick={submit}
          disabled={loading}
          className="rounded-lg bg-brand px-5 py-2 font-semibold text-white hover:bg-brand-dark disabled:opacity-60"
        >
          {loading ? "…" : "Ask"}
        </button>
      </div>

      {answer && (
        <div className="mt-6 rounded-lg border border-slate-200 bg-white p-5 text-slate-700">
          {answer}
        </div>
      )}
    </div>
  );
}
