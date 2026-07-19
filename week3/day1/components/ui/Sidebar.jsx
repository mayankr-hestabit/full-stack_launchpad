"use client";

import { LayoutDashboard, Columns, FileText, ChevronDown, BarChart2, Table } from "lucide-react";
import { useState } from "react";

// Small reusable piece: a section label like "CORE" / "INTERFACE" / "ADDONS"
function SidebarSectionLabel({ children }) {
  return (
    <p className="px-4 pt-4 pb-2 text-xs font-semibold uppercase tracking-wider text-slate-500">
      {children}
    </p>
  );
}

// Small reusable piece: one clickable nav row (icon + label, optional dropdown chevron)
function SidebarLink({ icon: Icon, label, hasDropdown = false, active = false }) {
  const [open, setOpen] = useState(false);

  return (
    <div>
      <button
        onClick={() => hasDropdown && setOpen(!open)}
        className={`flex w-full items-center justify-between px-4 py-2.5 text-sm transition-colors
          ${active ? "bg-slate-800 text-white" : "text-slate-300 hover:bg-slate-800 hover:text-white"}`}
      >
        <span className="flex items-center gap-3">
          <Icon size={16} />
          {label}
        </span>
        {hasDropdown && (
          <ChevronDown
            size={14}
            className={`transition-transform ${open ? "rotate-180" : ""}`}
          />
        )}
      </button>

      {/* Collapsible sub-items — only rendered when this link has a dropdown and it's open */}
      {hasDropdown && open && (
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
        <SidebarLink icon={LayoutDashboard} label="Dashboard" active />

        <SidebarSectionLabel>Interface</SidebarSectionLabel>
        <SidebarLink icon={Columns} label="Layouts" hasDropdown />
        <SidebarLink icon={FileText} label="Pages" hasDropdown />

        <SidebarSectionLabel>Addons</SidebarSectionLabel>
        <SidebarLink icon={BarChart2} label="Charts" />
        <SidebarLink icon={Table} label="Tables" />
      </nav>
    </aside>
  );
}