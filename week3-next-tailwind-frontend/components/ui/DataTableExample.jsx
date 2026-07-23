"use client";

import { useState, useMemo } from "react";
import Input from "@/components/ui/Input";
import { Search } from "lucide-react";

const rows = [
  { name: "Tiger Nixon", position: "System Architect", office: "Edinburgh", age: 61 },
  { name: "Garrett Winters", position: "Accountant", office: "Tokyo", age: 63 },
  { name: "Ashton Cox", position: "Junior Technical Author", office: "San Francisco", age: 66 },
  { name: "Cedric Kelly", position: "Senior Javascript Developer", office: "Edinburgh", age: 22 },
  { name: "Airi Satou", position: "Accountant", office: "Tokyo", age: 33 },
  { name: "Brielle Williamson", position: "Integration Specialist", office: "New York", age: 61 },
];

export default function DataTableExample() {
  const [perPage, setPerPage] = useState(10);
  const [search, setSearch] = useState("");

  const filtered = useMemo(
    () => rows.filter((r) => r.name.toLowerCase().includes(search.toLowerCase())),
    [search]
  );

  return (
    <div>
      <div className="flex flex-col gap-3 p-4 sm:flex-row sm:items-center sm:justify-between">
        <label className="flex items-center gap-2 text-sm text-slate-500">
          Show
          <select
            value={perPage}
            onChange={(e) => setPerPage(Number(e.target.value))}
            className="rounded-md border border-slate-200 px-2 py-1 text-sm"
          >
            <option value={10}>10</option>
            <option value={25}>25</option>
            <option value={50}>50</option>
          </select>
          entries
        </label>

        <Input
          icon={Search}
          placeholder="Search:"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full sm:w-56"
        />
      </div>

      <div className="overflow-x-auto">
        <table className="w-full min-w-[500px] text-left text-sm">
          <thead className="border-y border-slate-100 text-xs uppercase text-slate-500">
            <tr>
              <th className="px-4 py-3">Name</th>
              <th className="px-4 py-3">Position</th>
              <th className="px-4 py-3">Office</th>
              <th className="px-4 py-3">Age</th>
            </tr>
          </thead>
          <tbody>
            {filtered.slice(0, perPage).map((r) => (
              <tr key={r.name} className="border-b border-slate-50 last:border-0">
                <td className="px-4 py-3 font-medium text-slate-800">{r.name}</td>
                <td className="px-4 py-3 text-slate-500">{r.position}</td>
                <td className="px-4 py-3 text-slate-500">{r.office}</td>
                <td className="px-4 py-3 text-slate-500">{r.age}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
