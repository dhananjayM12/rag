import { fetchArticles, type Article } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function CurrentAffairsPage() {
  let articles: Article[] = [];
  let error = false;
  try {
    articles = await fetchArticles(40);
  } catch {
    error = true;
  }

  return (
    <div className="mx-auto max-w-3xl px-4 py-10">
      <h1 className="text-2xl font-bold text-slate-900">Current Affairs</h1>
      <p className="mt-2 text-slate-600">
        Latest updates ingested from official sources (PIB, PRS). These also feed
        the AI Q&amp;A, so you can ask about them and get cited answers.
      </p>

      {error && (
        <div className="mt-6 rounded bg-amber-50 px-4 py-3 text-sm text-amber-800">
          Couldn&apos;t load articles. Run{" "}
          <code>python -m app.rag.ingest_sources</code> on the backend to fetch
          from the configured feeds.
        </div>
      )}

      {!error && articles.length === 0 && (
        <div className="mt-6 rounded border border-dashed border-slate-300 px-4 py-6 text-center text-sm text-slate-500">
          No articles ingested yet. Run{" "}
          <code>python -m app.rag.ingest_sources</code> to populate the feed.
        </div>
      )}

      <ul className="mt-6 space-y-4">
        {articles.map((a) => (
          <li
            key={a.id}
            className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm"
          >
            <div className="mb-1 flex items-center gap-2 text-xs text-slate-500">
              <span className="rounded-full bg-slate-100 px-2 py-0.5 font-medium text-slate-600">
                {a.source}
              </span>
              {a.published_at && <span>{a.published_at}</span>}
            </div>
            <h2 className="font-semibold text-slate-900">
              {a.url ? (
                <a
                  href={a.url}
                  target="_blank"
                  rel="noreferrer"
                  className="hover:text-brand hover:underline"
                >
                  {a.title}
                </a>
              ) : (
                a.title
              )}
            </h2>
            <p className="mt-1 text-sm text-slate-600">{a.summary}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}
