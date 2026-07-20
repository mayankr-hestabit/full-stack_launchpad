"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, Columns, FileText, ChevronDown, BarChart2, Table, User } from "lucide-react";
import { useState } from "react";

function SidebarSectionLabel({ children }) {
  return (
    <p className="px-4 pt-4 pb-2 text-xs font-semibold uppercase tracking-wider text-slate-500">
      {children}
    </p>
  );
}

// Navigable link — uses next/link + usePathname so the active state reflects
// the ACTUAL current route, not a manually-passed prop.
function SidebarNavLink({ icon: Icon, label, href }) {
  const pathname = usePathname();
  const active = pathname === href;

  return (
    <Link
      href={href}
      className={`flex items-center gap-3 px-4 py-2.5 text-sm transition-colors
        ${active ? "bg-slate-800 text-white" : "text-slate-300 hover:bg-slate-800 hover:text-white"}`}
    >
      <Icon size={16} />
      {label}
    </Link>
  );
}

// Non-navigable link with a collapsible dropdown (Layouts, Pages — no real routes yet)
function SidebarDropdown({ icon: Icon, label }) {
  const [open, setOpen] = useState(false);

  return (
    <div>
      <button
        onClick={() => setOpen(!open)}
        className="flex w-full items-center justify-between px-4 py-2.5 text-sm text-slate-300 transition-colors hover:bg-slate-800 hover:text-white"
      >
        <span className="flex items-center gap-3">
          <Icon size={16} />
          {label}
        </span>
        <ChevronDown size={14} className={`transition-transform ${open ? "rotate-180" : ""}`} />
      </button>

      {open && (
        <div className="bg-slate-950/40 pb-2 pl-11 text-sm text-slate-400">
          <a href="#" className="block py-1.5 hover:text-white">Sub Item 1</a>
          <a href="#" className="block py-1.5 hover:text-white">Sub Item 2</a>
        </div>
      )}
    </div>
  );
}

export default function Sidebar({ open }) {
  return (
    <aside
      className={`fixed left-0 top-14 z-40 h-[calc(100vh-3.5rem)] w-56 overflow-y-auto bg-slate-900
        transition-transform duration-200
        ${open ? "translate-x-0" : "-translate-x-full"}`}
    >
      <nav className="py-2">
        <SidebarSectionLabel>Core</SidebarSectionLabel>
        <SidebarNavLink icon={LayoutDashboard} label="Dashboard" href="/dashboard" />
        <SidebarNavLink icon={User} label="Profile" href="/dashboard/profile" />

        <SidebarSectionLabel>Interface</SidebarSectionLabel>
        <SidebarDropdown icon={Columns} label="Layouts" />
        <SidebarDropdown icon={FileText} label="Pages" />

        <SidebarSectionLabel>Addons</SidebarSectionLabel>
        <SidebarNavLink icon={BarChart2} label="Charts" href="/dashboard/charts" />
        <SidebarNavLink icon={Table} label="Tables" href="/dashboard/tables" />
      </nav>
    </aside>
  );
}
