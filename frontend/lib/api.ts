// Typed client for the FastAPI backend.

// In the browser we always use the public URL. On the server (SSR inside the
// container) we prefer an internal URL so requests reach the backend service
// directly (e.g. http://backend:8000 under docker-compose).
export function apiBase(): string {
  if (typeof window === "undefined") {
    return (
      process.env.API_URL_INTERNAL ??
      process.env.NEXT_PUBLIC_API_URL ??
      "http://localhost:8000"
    );
  }
  return process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
}

export const API_URL = apiBase();

export type Level = "stage" | "paper" | "topic" | "subtopic" | "micro";

export interface TreeNode {
  id: number;
  slug: string;
  title: string;
  exam: string;
  level: Level;
  is_leaf: boolean;
  position: number;
  has_content: boolean;
  children: TreeNode[];
}

export interface Source {
  title: string;
  url?: string | null;
}

export interface ContentOut {
  node_slug: string;
  title: string;
  summary?: string | null;
  body_md: string;
  sources: Source[];
  updated_at?: string | null;
  has_content: boolean;
}

export interface Crumb {
  slug: string;
  title: string;
  level: Level;
}

async function getJSON<T>(path: string): Promise<T> {
  const res = await fetch(`${apiBase()}${path}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`API ${path} failed: ${res.status}`);
  return res.json() as Promise<T>;
}

export function fetchTree(exam?: string): Promise<TreeNode[]> {
  const q = exam ? `?exam=${encodeURIComponent(exam)}` : "";
  return getJSON<TreeNode[]>(`/api/syllabus/tree${q}`);
}

export function fetchContent(slug: string): Promise<ContentOut> {
  return getJSON<ContentOut>(`/api/content/${encodeURIComponent(slug)}`);
}

export async function postAsk(question: string): Promise<{
  answer: string;
  status: string;
}> {
  const res = await fetch(`${apiBase()}/api/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  return res.json();
}

export interface EvaluateResponse {
  overall_score: number;
  max_score: number;
  word_count: number;
  rubric: { criterion: string; score: number; max_score: number; feedback: string }[];
  suggestions: string[];
  status: string;
}

export async function postEvaluate(
  question: string,
  answer: string,
  word_limit: number,
): Promise<EvaluateResponse> {
  const res = await fetch(`${apiBase()}/api/evaluate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, answer, word_limit }),
  });
  return res.json();
}
