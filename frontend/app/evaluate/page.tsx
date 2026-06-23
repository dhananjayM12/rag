"use client";

import { useState } from "react";
import { postEvaluate, type EvaluateResponse } from "@/lib/api";

export default function EvaluatePage() {
  const [question, setQuestion] = useState(
    "Examine the significance of the Directive Principles of State Policy.",
  );
  const [answer, setAnswer] = useState("");
  const [wordLimit, setWordLimit] = useState(250);
  const [result, setResult] = useState<EvaluateResponse | null>(null);
  const [loading, setLoading] = useState(false);

  const wordCount = answer.trim() ? answer.trim().split(/\s+/).length : 0;

  const submit = async () => {
    if (!answer.trim()) return;
    setLoading(true);
    try {
      setResult(await postEvaluate(question, answer, wordLimit));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-3xl px-4 py-12">
      <h1 className="text-2xl font-bold text-slate-900">Answer Evaluation</h1>
      <p className="mt-2 text-slate-600">
        Write a Mains-style answer and get structured, rubric-based feedback.
      </p>
      <div className="mt-2 inline-block rounded-full bg-amber-100 px-3 py-1 text-xs font-medium text-amber-800">
        Preview — AI grading arrives in the next milestone (word-limit check is
        live)
      </div>

      <div className="mt-6 space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-700">
            Question
          </label>
          <input
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 focus:border-brand focus:outline-none"
          />
        </div>

        <div>
          <div className="flex items-center justify-between">
            <label className="block text-sm font-medium text-slate-700">
              Your Answer
            </label>
            <span
              className={`text-xs ${
                wordCount > wordLimit ? "text-red-600" : "text-slate-500"
              }`}
            >
              {wordCount} / {wordLimit} words
            </span>
          </div>
          <textarea
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            rows={10}
            placeholder="Write your answer here…"
            className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 focus:border-brand focus:outline-none"
          />
        </div>

        <div className="flex items-center gap-3">
          <label className="text-sm text-slate-700">Word limit</label>
          <input
            type="number"
            value={wordLimit}
            onChange={(e) => setWordLimit(Number(e.target.value) || 0)}
            className="w-24 rounded-lg border border-slate-300 px-3 py-1.5"
          />
          <button
            onClick={submit}
            disabled={loading}
            className="ml-auto rounded-lg bg-brand px-5 py-2 font-semibold text-white hover:bg-brand-dark disabled:opacity-60"
          >
            {loading ? "Evaluating…" : "Evaluate"}
          </button>
        </div>
      </div>

      {result && (
        <div className="mt-8 rounded-lg border border-slate-200 bg-white p-5">
          <div className="flex items-baseline justify-between">
            <h2 className="text-lg font-semibold text-slate-900">
              Score: {result.overall_score} / {result.max_score}
            </h2>
            <span className="text-sm text-slate-500">
              {result.word_count} words
            </span>
          </div>

          <table className="mt-4 w-full text-sm">
            <thead>
              <tr className="text-left text-slate-500">
                <th className="py-1">Criterion</th>
                <th className="py-1">Score</th>
                <th className="py-1">Feedback</th>
              </tr>
            </thead>
            <tbody>
              {result.rubric.map((r, i) => (
                <tr key={i} className="border-t border-slate-100">
                  <td className="py-2 pr-2">{r.criterion}</td>
                  <td className="py-2 pr-2 whitespace-nowrap">
                    {r.score} / {r.max_score}
                  </td>
                  <td className="py-2 text-slate-600">{r.feedback}</td>
                </tr>
              ))}
            </tbody>
          </table>

          {result.suggestions.length > 0 && (
            <ul className="mt-4 list-disc space-y-1 pl-5 text-sm text-slate-600">
              {result.suggestions.map((s, i) => (
                <li key={i}>{s}</li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
