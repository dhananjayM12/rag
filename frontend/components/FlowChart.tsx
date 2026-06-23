"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  Background,
  Controls,
  MiniMap,
  ReactFlow,
  ReactFlowProvider,
  type Edge,
  type Node,
  type NodeMouseHandler,
  type ReactFlowInstance,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";

import { fetchTree, type TreeNode } from "@/lib/api";
import { layoutGraph } from "@/lib/layout";
import SyllabusNode, { type SyllabusNodeData } from "./SyllabusNode";
import ContentDrawer from "./ContentDrawer";

const nodeTypes = { syllabus: SyllabusNode };

interface Flat {
  node: TreeNode;
  parentId: number | null;
  childIds: number[];
}

function flatten(roots: TreeNode[]): Map<number, Flat> {
  const map = new Map<number, Flat>();
  const walk = (n: TreeNode, parentId: number | null) => {
    map.set(n.id, {
      node: n,
      parentId,
      childIds: n.children.map((c) => c.id),
    });
    n.children.forEach((c) => walk(c, n.id));
  };
  roots.forEach((r) => walk(r, null));
  return map;
}

function InnerFlowChart() {
  const [flat, setFlat] = useState<Map<number, Flat>>(new Map());
  const [rootIds, setRootIds] = useState<number[]>([]);
  const [expanded, setExpanded] = useState<Set<number>>(new Set());
  const [selectedSlug, setSelectedSlug] = useState<string | null>(null);
  const [drawerSlug, setDrawerSlug] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [error, setError] = useState<string | null>(null);
  const rfRef = useRef<ReactFlowInstance | null>(null);

  // Load the tree once.
  useEffect(() => {
    fetchTree()
      .then((roots) => {
        const f = flatten(roots);
        setFlat(f);
        setRootIds(roots.map((r) => r.id));
        // Expand stages + papers by default so the structure is visible.
        const initial = new Set<number>();
        f.forEach(({ node }) => {
          if (node.level === "stage" || node.level === "paper") initial.add(node.id);
        });
        setExpanded(initial);
      })
      .catch((e) => setError(String(e)));
  }, []);

  const toggle = useCallback((id: number) => {
    setExpanded((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  }, []);

  // Compute visible nodes/edges from the expansion state, then lay out.
  const { nodes, edges } = useMemo(() => {
    if (flat.size === 0) return { nodes: [] as Node[], edges: [] as Edge[] };

    const visible: number[] = [];
    const seen = new Set<number>();
    const visit = (id: number) => {
      if (seen.has(id)) return;
      seen.add(id);
      visible.push(id);
      const f = flat.get(id);
      if (f && expanded.has(id)) f.childIds.forEach(visit);
    };
    rootIds.forEach(visit);

    const rfNodes: Node[] = visible.map((id) => {
      const f = flat.get(id)!;
      const data: SyllabusNodeData = {
        title: f.node.title,
        level: f.node.level,
        isLeaf: f.node.is_leaf,
        hasContent: f.node.has_content,
        hasChildren: f.childIds.length > 0,
        expanded: expanded.has(id),
        selected: f.node.slug === selectedSlug,
      };
      return { id: String(id), type: "syllabus", position: { x: 0, y: 0 }, data };
    });

    const rfEdges: Edge[] = [];
    visible.forEach((id) => {
      const f = flat.get(id)!;
      if (!expanded.has(id)) return;
      f.childIds.forEach((cid) => {
        if (seen.has(cid)) {
          rfEdges.push({
            id: `${id}-${cid}`,
            source: String(id),
            target: String(cid),
            type: "smoothstep",
          });
        }
      });
    });

    return layoutGraph(rfNodes, rfEdges, "LR");
  }, [flat, rootIds, expanded, selectedSlug]);

  const onNodeClick: NodeMouseHandler = useCallback(
    (_evt, node) => {
      const f = flat.get(Number(node.id));
      if (!f) return;
      setSelectedSlug(f.node.slug);
      if (f.childIds.length > 0) {
        toggle(f.node.id);
      } else {
        setDrawerSlug(f.node.slug);
      }
    },
    [flat, toggle],
  );

  // Search: expand the path to the first matching node and focus it.
  const runSearch = useCallback(() => {
    const q = search.trim().toLowerCase();
    if (!q) return;
    let matchId: number | null = null;
    flat.forEach(({ node }, id) => {
      if (matchId === null && node.title.toLowerCase().includes(q)) matchId = id;
    });
    if (matchId === null) return;

    const toExpand = new Set(expanded);
    let cur: number | null = matchId;
    while (cur !== null) {
      const f = flat.get(cur);
      if (!f) break;
      if (f.childIds.length > 0) toExpand.add(cur);
      cur = f.parentId;
    }
    setExpanded(toExpand);
    const slug = flat.get(matchId)!.node.slug;
    setSelectedSlug(slug);
    setTimeout(() => {
      const n = rfRef.current?.getNode(String(matchId));
      if (n) rfRef.current?.setCenter(n.position.x + 120, n.position.y, { zoom: 1.1, duration: 600 });
    }, 80);
  }, [search, flat, expanded]);

  if (error) {
    return (
      <div className="p-6 text-sm text-red-600">
        Could not load the syllabus. Is the backend running at the configured
        API URL? <br />
        <span className="text-slate-500">{error}</span>
      </div>
    );
  }

  return (
    <div className="relative h-full w-full">
      <div className="absolute left-3 top-3 z-10 flex gap-2">
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && runSearch()}
          placeholder="Search a topic…"
          className="w-56 rounded border border-slate-300 bg-white px-3 py-1.5 text-sm shadow-sm focus:border-brand focus:outline-none"
        />
        <button
          onClick={runSearch}
          className="rounded bg-brand px-3 py-1.5 text-sm font-medium text-white hover:bg-brand-dark"
        >
          Find
        </button>
      </div>

      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        onNodeClick={onNodeClick}
        onInit={(inst) => {
          rfRef.current = inst;
        }}
        fitView
        minZoom={0.15}
        proOptions={{ hideAttribution: true }}
      >
        <Background />
        <Controls />
        <MiniMap pannable zoomable />
      </ReactFlow>

      <ContentDrawer slug={drawerSlug} onClose={() => setDrawerSlug(null)} />
    </div>
  );
}

export default function FlowChart() {
  return (
    <ReactFlowProvider>
      <InnerFlowChart />
    </ReactFlowProvider>
  );
}
