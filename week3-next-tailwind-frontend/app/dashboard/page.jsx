import { ChevronRight, TrendingUp, BarChart3, Table2 } from "lucide-react";
import Card from "@/components/ui/Card";
import AreaChartExample from "@/components/ui/AreaChartExample";
import BarChartExample from "@/components/ui/BarChartExample";
import DataTableExample from "@/components/ui/DataTableExample";

const stats = [
  { label: "Primary Card", color: "primary" },
  { label: "Warning Card", color: "warning" },
  { label: "Success Card", color: "success" },
  { label: "Danger Card", color: "danger" },
];

export default function DashboardPage() {
  return (
    <div>
      <h1 className="text-2xl font-bold text-slate-800">Dashboard</h1>
      <div className="mt-3 rounded-md bg-slate-100 px-4 py-2 text-sm text-slate-500">
        Dashboard
      </div>

      {/* stat cards */}
      <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <Card
            key={stat.label}
            color={stat.color}
            footer={
              <div className="flex w-full items-center justify-between">
                <span>View Details</span>
                <ChevronRight size={14} />
              </div>
            }
          >
            <p className="text-lg font-semibold">{stat.label}</p>
          </Card>
        ))}
      </div>

      {/* charts */}
      <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card bodyClassName="p-0">
          <div className="flex items-center gap-2 border-b border-slate-100 px-4 py-3 text-sm font-medium text-slate-700">
            <TrendingUp size={16} /> Area Chart Example
          </div>
          <div className="p-4">
            <AreaChartExample />
          </div>
        </Card>

        <Card bodyClassName="p-0">
          <div className="flex items-center gap-2 border-b border-slate-100 px-4 py-3 text-sm font-medium text-slate-700">
            <BarChart3 size={16} /> Bar Chart Example
          </div>
          <div className="p-4">
            <BarChartExample />
          </div>
        </Card>
      </div>

      {/* data table */}
      <Card className="mt-6" bodyClassName="p-0">
        <div className="flex items-center gap-2 border-b border-slate-100 px-4 py-3 text-sm font-medium text-slate-700">
          <Table2 size={16} /> DataTable Example
        </div>
        <DataTableExample />
      </Card>
    </div>
  );
}
