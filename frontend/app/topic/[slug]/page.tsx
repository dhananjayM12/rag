import Link from "next/link";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { fetchContent } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function TopicPage({
  params,
}: {
  params: { slug: string };
}) {
  let content;
  try {
    content = await fetchContent(params.slug);
  } catch {
    content = null;
  }

  if (!content) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-12">
        <p className="text-slate-600">Could not load this topic.</p>
        <Link href="/flowchart" className="text-brand hover:underline">
          ← Back to the syllabus map
        </Link>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-3xl px-4 py-10">
      <Link
        href="/flowchart"
        className="text-sm text-brand hover:underline"
      >
        ← Back to the syllabus map
      </Link>

      <h1 className="mt-3 text-2xl font-bold text-slate-900">{content.title}</h1>
      {content.summary && (
        <p className="mt-1 text-slate-600">{content.summary}</p>
      )}

      {!content.has_content && (
        <div className="mt-4 rounded bg-amber-50 px-4 py-3 text-sm text-amber-800">
          Study notes for this micro-topic are still being authored.
        </div>
      )}

      <article className="prose-content mt-6 text-slate-800">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>
          {content.body_md}
        </ReactMarkdown>
      </article>

      {content.sources.length > 0 && (
        <div className="mt-8 border-t border-slate-200 pt-4">
          <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-slate-500">
            Sources
          </h2>
          <ul className="list-disc space-y-1 pl-5 text-sm">
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

      <div className="mt-8 rounded-lg border border-dashed border-slate-300 p-4 text-sm text-slate-500">
        Coming soon: mark as studied, add to revision, and linked previous-year
        questions for this micro-topic.
      </div>
    </div>
  );
}
