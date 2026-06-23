import FlowChart from "@/components/FlowChart";

export default function FlowChartPage() {
  return (
    <div className="flex flex-col" style={{ height: "calc(100vh - 57px)" }}>
      <div className="border-b border-slate-200 bg-white px-4 py-2">
        <h1 className="text-sm font-semibold text-slate-700">
          UPSC Syllabus Map
        </h1>
        <p className="text-xs text-slate-500">
          Click a topic to expand it. Click a leaf (📄) to read the notes.
        </p>
      </div>
      <div className="flex-1">
        <FlowChart />
      </div>
    </div>
  );
}
