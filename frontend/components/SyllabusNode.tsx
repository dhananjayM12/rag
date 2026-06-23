"use client";

import { Handle, Position, type NodeProps } from "@xyflow/react";
import type { Level } from "@/lib/api";

export interface SyllabusNodeData {
  title: string;
  level: Level;
  isLeaf: boolean;
  hasContent: boolean;
  hasChildren: boolean;
  expanded: boolean;
  selected: boolean;
  [key: string]: unknown;
}

const levelStyles: Record<Level, string> = {
  stage: "bg-slate-800 text-white border-slate-800",
  paper: "bg-brand text-white border-brand",
  topic: "bg-blue-50 text-slate-800 border-blue-300",
  subtopic: "bg-emerald-50 text-slate-800 border-emerald-300",
  micro: "bg-white text-slate-800 border-slate-300",
};

export default function SyllabusNode({ data }: NodeProps) {
  const d = data as SyllabusNodeData;
  return (
    <div
      className={`rounded-lg border px-3 py-2 text-xs shadow-sm transition ${
        levelStyles[d.level]
      } ${d.selected ? "ring-2 ring-amber-400" : ""}`}
      style={{ width: 240 }}
    >
      <Handle type="target" position={Position.Left} className="!bg-slate-400" />
      <div className="flex items-center justify-between gap-2">
        <span className="font-medium leading-tight">{d.title}</span>
        <span className="flex shrink-0 items-center gap-1">
          {d.isLeaf && d.hasContent && (
            <span title="Study content available">📄</span>
          )}
          {d.hasChildren && (
            <span className="font-bold opacity-80">{d.expanded ? "−" : "+"}</span>
          )}
        </span>
      </div>
      <Handle type="source" position={Position.Right} className="!bg-slate-400" />
    </div>
  );
}
