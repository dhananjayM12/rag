import Link from "next/link";

const features = [
  {
    title: "Interactive Syllabus Map",
    desc: "Navigate the entire UPSC syllabus as a living flowchart — drill from papers down to micro-topics, each with concise, source-backed notes.",
    href: "/flowchart",
    cta: "Explore the map",
    badge: "Live",
  },
  {
    title: "AI Answer Evaluation",
    desc: "Write a Mains answer and get rubric-based feedback on structure, content, dimensions and word limit — like a personal mentor.",
    href: "/evaluate",
    cta: "Try answer check",
    badge: "Preview",
  },
  {
    title: "Ask AI (RAG)",
    desc: "Ask any question and get answers grounded in official government and UPSC sources, with citations you can verify.",
    href: "/ask",
    cta: "Ask a question",
    badge: "Preview",
  },
];

export default function Home() {
  return (
    <div className="mx-auto max-w-6xl px-4">
      <section className="py-16 text-center">
        <h1 className="text-4xl font-extrabold tracking-tight text-slate-900 sm:text-5xl">
          Crack UPSC with a clear{" "}
          <span className="text-brand">map of the syllabus</span>
        </h1>
        <p className="mx-auto mt-4 max-w-2xl text-lg text-slate-600">
          PrepPath turns the sprawling UPSC syllabus into an interactive
          flowchart — every topic, subtopic and micro-topic in one place, backed
          by official sources and AI study tools.
        </p>
        <div className="mt-8 flex justify-center gap-3">
          <Link
            href="/flowchart"
            className="rounded-lg bg-brand px-6 py-3 font-semibold text-white shadow hover:bg-brand-dark"
          >
            Explore the Syllabus Map
          </Link>
          <Link
            href="/evaluate"
            className="rounded-lg border border-slate-300 bg-white px-6 py-3 font-semibold text-slate-700 hover:bg-slate-50"
          >
            Check an Answer
          </Link>
        </div>
      </section>

      <section className="grid gap-6 pb-20 sm:grid-cols-3">
        {features.map((f) => (
          <div
            key={f.title}
            className="flex flex-col rounded-xl border border-slate-200 bg-white p-6 shadow-sm"
          >
            <div className="mb-2 flex items-center justify-between">
              <h2 className="text-lg font-semibold text-slate-900">{f.title}</h2>
              <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-600">
                {f.badge}
              </span>
            </div>
            <p className="flex-1 text-sm text-slate-600">{f.desc}</p>
            <Link
              href={f.href}
              className="mt-4 text-sm font-semibold text-brand hover:underline"
            >
              {f.cta} →
            </Link>
          </div>
        ))}
      </section>
    </div>
  );
}
