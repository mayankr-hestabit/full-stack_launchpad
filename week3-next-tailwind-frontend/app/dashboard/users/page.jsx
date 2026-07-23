"use client";

import { useState, useMemo } from "react";
import { ArrowDown, Search, ChevronRight, UserCog } from "lucide-react";
import Card from "@/components/ui/Card";
import Input from "@/components/ui/Input";

// Mocked data — no backend, matches the reference table's shape
// (Name, Email, Role, Created at, Updated at + an action icon column).
const allUsers = [
  { name: "User", email: "user@example.com", role: "User", createdAt: "18/10/2024 05:27", updatedAt: "18/10/2024 05:27" },
  { name: "Dr. Ray Stoltenberg", email: "rosalinda42@example.com", role: "User", createdAt: "18/10/2024 05:27", updatedAt: "18/10/2024 05:27" },
  { name: "Mrs. Mertie Murray MD", email: "ernser.susanna@example.net", role: "User", createdAt: "18/10/2024 05:27", updatedAt: "18/10/2024 05:27" },
  { name: "Gilbert Rice", email: "willard.walter@example.org", role: "User", createdAt: "18/10/2024 05:27", updatedAt: "18/10/2024 05:27" },
  { name: "Sydnie Rau", email: "doug.padberg@example.org", role: "User", createdAt: "18/10/2024 05:27", updatedAt: "18/10/2024 05:27" },
  { name: "Mr. Arvid Veum DDS", email: "schinner.meaghan@example.org", role: "User", createdAt: "18/10/2024 05:27", updatedAt: "18/10/2024 05:27" },
  { name: "Jayme Beier DDS", email: "orn.ahmed@example.com", role: "User", createdAt: "18/10/2024 05:27", updatedAt: "18/10/2024 05:27" },
  { name: "Uriah Swaniawski", email: "wilburn.champlin@example.org", role: "User", createdAt: "18/10/2024 05:27", updatedAt: "18/10/2024 05:27" },
  { name: "Rosanna Heaney", email: "boconner@example.com", role: "User", createdAt: "18/10/2024 05:27", updatedAt: "18/10/2024 05:27" },
  { name: "Adan Reichel", email: "mya.labadie@example.com", role: "User", createdAt: "18/10/2024 05:27", updatedAt: "18/10/2024 05:27" },
  { name: "Elta Kohler", email: "elta.kohler@example.com", role: "Admin", createdAt: "18/10/2024 05:27", updatedAt: "18/10/2024 05:27" },
  { name: "Brycen Hane", email: "brycen.hane@example.org", role: "Editor", createdAt: "18/10/2024 05:27", updatedAt: "18/10/2024 05:27" },
];

const PER_PAGE = 10;

function SortableHeader({ children }) {
  return (
    <th className="px-4 py-3 font-medium text-slate-700">
      <span className="flex items-center gap-1 cursor-pointer select-none">
        {children}
        <ArrowDown size={12} className="text-slate-400" />
      </span>
    </th>
  );
}

export default function UsersPage() {
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);

  const filtered = useMemo(
    () =>
      allUsers.filter(
        (u) =>
          u.name.toLowerCase().includes(search.toLowerCase()) ||
          u.email.toLowerCase().includes(search.toLowerCase())
      ),
    [search]
  );

  const totalPages = Math.max(1, Math.ceil(filtered.length / PER_PAGE));
  const pageItems = filtered.slice((page - 1) * PER_PAGE, page * PER_PAGE);

  return (
    <div>
      {/* breadcrumb */}
      <p className="flex items-center gap-1 text-sm text-slate-400">
        Users <ChevronRight size={14} /> List
      </p>
      <h1 className="mt-1 text-2xl font-bold text-slate-800">Users</h1>

      <Card className="mt-6" bodyClassName="p-0">
        <div className="flex justify-end p-4">
          <Input
            icon={Search}
            placeholder="Search"
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(1);
            }}
            className="w-full sm:w-64"
          />
        </div>

        <div className="overflow-x-auto">
          <table className="w-full min-w-[700px] text-left text-sm">
            <thead className="border-y border-slate-100 text-xs uppercase text-slate-500">
              <tr>
                <SortableHeader>Name</SortableHeader>
                <SortableHeader>Email</SortableHeader>
                <th className="px-4 py-3 font-medium text-slate-700">Role</th>
                <th className="px-4 py-3 font-medium text-slate-700">Created at</th>
                <th className="px-4 py-3 font-medium text-slate-700">Updated at</th>
                <th className="px-4 py-3"></th>
              </tr>
            </thead>
            <tbody>
              {pageItems.map((user) => (
                <tr key={user.email} className="border-b border-slate-50 last:border-0 hover:bg-slate-50">
                  <td className="px-4 py-3 font-medium text-slate-800">{user.name}</td>
                  <td className="px-4 py-3 text-slate-500">{user.email}</td>
                  <td className="px-4 py-3 text-slate-500">{user.role}</td>
                  <td className="px-4 py-3 text-slate-500">{user.createdAt}</td>
                  <td className="px-4 py-3 text-slate-500">{user.updatedAt}</td>
                  <td className="px-4 py-3">
                    <button className="text-indigo-400 hover:text-indigo-600">
                      <UserCog size={18} />
                    </button>
                  </td>
                </tr>
              ))}
              {pageItems.length === 0 && (
                <tr>
                  <td colSpan={6} className="px-4 py-8 text-center text-slate-400">
                    No users match your search.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* pagination footer */}
        <div className="flex flex-col items-center justify-between gap-3 border-t border-slate-100 p-4 text-sm text-slate-500 sm:flex-row">
          <span>
            Showing {filtered.length === 0 ? 0 : (page - 1) * PER_PAGE + 1} to{" "}
            {Math.min(page * PER_PAGE, filtered.length)} of {filtered.length} results
          </span>
          <div className="flex items-center gap-2">
            {Array.from({ length: totalPages }, (_, i) => i + 1).map((p) => (
              <button
                key={p}
                onClick={() => setPage(p)}
                className={`h-7 w-7 rounded-md text-xs font-medium ${
                  p === page ? "bg-blue-600 text-white" : "border border-slate-200 hover:bg-slate-50"
                }`}
              >
                {p}
              </button>
            ))}
          </div>
        </div>
      </Card>
    </div>
  );
}
